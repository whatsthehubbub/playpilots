from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from django.core.mail import send_mail

from django import forms

from ebi.metagame.models import Player
from battleroyale.models import *

import actstream
from actstream.models import Action, actor_stream

import datetime, random, math, json

import logging

def klassement(request):
    styles = Style.objects.all()
    
    players = Player.objects.all().order_by('-rating')
    
    return render_to_response('metagame/klassement.html', {
        'players': players,
        'styles': styles,
        'current': 'klassement'
    }, context_instance=RequestContext(request))
    

def challenge(request):
    if request.method == 'POST':
        # Trying to store a challenge
        
        challenger = request.user.get_profile()
        
        move_id = request.POST.get('move', None)
        logging.debug('got move id: %s', move_id)
        
        move = Move.objects.get(id=move_id)
        
        message = request.POST.get('message', '')
        logging.debug('got message: %s', message)
        
        target_id = request.POST.get('target', None)
        target = Player.objects.get(id=target_id)
        
        # Calculate the awesomeness
        # TODO calculate the awesomeness based on player skill
        awesomeness = random.randint(1, 5)
        
        # Create Round object
        d = Duel(challenger=challenger, challenge_move=move, challenge_message=message, challenge_awesomeness=awesomeness, target=target)
        d.save()
        
        actstream.action.send(request.user, verb='heeft net gebruiker uitgedaagd voor een duel', target=d)
        
        # One to the target
        send_mail('Je bent uitgedaagd door %s' % challenger.user.username,
            '''Hoi %(target)s,

Je bent uitgedaagd voor een duel door %(challenger)s.

Ga naar %(url)s om te duelleren!

Namens PLAY Pilots,

Uw gezagvoerder''' % {'target': target.user.username, 
                            'challenger': challenger.user.username, 
                            'url': 'http://playpilots.nl/c/%d/' % d.id}, 
            'Your Captain Speaking <captain@playpilots.nl>', 
            [target.user.email])
        
        return HttpResponse(json.dumps({
            'awesomeness': awesomeness
        }), mimetype='text/json')
    else:
        playerid = request.GET.get('target', None)

        target = get_object_or_404(Player, id=playerid)
    
        styles = Style.objects.all().order_by('name')
    
        return render_to_response('metagame/challenge.html', {
            'target': target,
            'styles': styles,
            'current': 'klassement'
        }, context_instance=RequestContext(request))
        
def challenge_resolve(request):
    if request.method == 'POST':
        round_id = int(request.POST.get('round_id', None))
        r = Round.objects.get(id=round_id)
    
        r.open = False
        r.responded = datetime.datetime.now()
    
        move_id = int(request.POST.get('move', None))
        r.response_move = Move.objects.get(id=move_id)
    
        r.response_message = request.POST.get('message', '')
    
        # Also TODO update dominant style
    
        winner_modifier = 0
    
        if random.random() < 0.5:
            winner = r.challenger
            winner_modifier += 10
        
            loser = r.target
        else:
            winner = r.target
            loser = r.challenger
        
        # Modify winner points if style penalty
        if winner.culture and r.challenger==winner and winner.culture==r.challenge_move.culture:
            winner_modifier -= 10
            
        # TODO implement log
        # print 'winner', winner, winner.rating
        # print 'loser', loser, loser.rating
    
        difference = abs(winner.rating - loser.rating)
        difference_mod = round(math.log(difference) * 5)
    
        if winner.rating > loser.rating:
            winner.rating += 10
            loser.rating -= 10
        elif winner.rating < loser.rating:
            winner.rating += difference + 10
            loser.rating -= difference - 10
        
        winner.rating = winner.rating + winner_modifier
        
        r.save()
        
        # Also save winner and loser in the round objcet? TODO
        winner.save()
        loser.save()
    
        result = {
            'winner': {
                'username': winner.user.username,
                'rating': winner.rating
            },
            'loser': {
                'username': loser.user.username,
                'rating': loser.rating
            },
        }
        
        # TODO template this text based on a to be agreed upon variable
        winphrase = ''
        
        try:
            swp = SpecificWinPhrase.objects.get(winner=r.challenge_move.culture, loser=r.response_move.culture)
            
            winphrase = swp.winphrase
        except SpecificWinPhrase.DoesNotExist:
            if winner == r.challenger:
                winculture = r.challenge_move.culture
            else:
                winculture = r.response_move.culture
            winphrase = winculture.win_phrase
            
        if winphrase:
            result['winphrase'] = winphrase
        
        # One to the winner
        send_mail('Gefeliciteerd! Je hebt gewonnen van %s!' % loser.user.username, 
            '''Hoi %(winner)s,

Gefeliciteerd! Je hebt het duel met %(loser)s gewonnen.

Ga naar %(url)s om de uitkomst te zien!

Namens PLAY Pilots,

Uw gezagvoerder''' % {
            'winner': winner.user.username,
            'loser': loser.user.username,
            'url': 'http://playpilots.nl/c/%d/' % r.id 
        }, 
            'Your Captain Speaking <captain@playpilots.nl>', 
            [winner.user.email])

        # One to the l0ser
        send_mail('Helaas! Je hebt verloren van %s!' % winner.user.username,
            '''Hoi %(loser)s,

Helaas! Je hebt het duel met %(winner)s verloren.

Ga naar %(url)s om de uitkomst te zien!

Namens PLAY Pilots,

Uw gezagvoerder''' % {
                'loser': loser.user.username,
                'winner': winner.user.username,
                'url': 'http://playpilots.nl/c/%d/' % r.id
            }, 
            'Your Captain Speaking <captain@playpilots.nl>', 
            [loser.user.email])
    
        return HttpResponse(json.dumps(result), mimetype="text/json")


def challenge_detail(request, id):
    r = get_object_or_404(Duel, id=id)
    
    if r.open:
        cultures = Style.objects.all().order_by('name')
    
        return render_to_response('metagame/challenge.html', {
            'round': r,
            'cultures': cultures
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('metagame/challenge_closed.html', {
            'round': r
        }, context_instance=RequestContext(request))
        
def challenge_detail_redirect(request, id):
    return HttpResponseRedirect('/challenge/%s/' % id)