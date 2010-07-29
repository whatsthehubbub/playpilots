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
    playerid = request.GET.get('target', None)

    target = get_object_or_404(Player, id=playerid)

    styles = Style.objects.all().order_by('name')

    return render_to_response('metagame/challenge_start.html', {
        'target': target,
        'styles': styles,
        'current': 'klassement'
    }, context_instance=RequestContext(request))


def challenge_detail(request, id):
    d = get_object_or_404(Duel, id=id)

    if d.open:
        styles = Style.objects.all().order_by('name')

        return render_to_response('metagame/challenge_open.html', {
            'duel': d,
            'styles': styles,
            'current': 'klassement'
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('metagame/challenge_closed.html', {
            'duel': d,
            'current': 'klassement'
        }, context_instance=RequestContext(request))


def challenge_create(request):
    if request.method == 'POST':
        logging.debug('challenge post')
        # Trying to store a challenge

        challenger = request.user.get_profile()

        move_id = request.POST.get('move', None)
        logging.debug('got move id: %s', move_id)

        move = Move.objects.get(id=int(move_id))

        message = request.POST.get('message', '')
        logging.debug('got message: %s', message)

        target_id = request.POST.get('target', None)
        target = Player.objects.get(id=int(target_id))

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

def challenge_resolve(request):
    if request.method == 'POST':
        duel_id = int(request.POST.get('duel', None))
        d = Duel.objects.get(id=duel_id)
    
        d.open = False
        d.responded = datetime.datetime.now()
    
        move_id = int(request.POST.get('move', None))
        d.response_move = Move.objects.get(id=move_id)
    
        d.response_message = request.POST.get('message', '')
    
        d.response_awesomeness = random.randint(1, 5)
        
        d.save()
    
        result = {
            'awesomeness': d.response_awesomeness
        }
        
        # TODO handle winner and loser
        """
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
        """
        
        return HttpResponse(json.dumps(result), mimetype="text/json")
        
def challenge_detail_redirect(request, id):
    return HttpResponseRedirect('/challenge/%s/' % id)