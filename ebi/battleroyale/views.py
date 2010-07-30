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

    target = get_object_or_404(Player, id=int(playerid))

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

        # Create Round object
        d = Duel(challenger=challenger, challenge_move=move, challenge_message=message, target=target)

        awesomeness = d.get_challenge_awesomeness()
        d.challenge_awesomeness = awesomeness
        d.save()

        actstream.action.send(request.user, verb='heeft net %s uitgedaagd voor een duel' % target.user.username, target=d)

        d.send_target_message()
        
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
        d.response_awesomeness = d.get_response_awesomeness()
        
        d.save()
    
        # TODO send back specific winphrase too
        
        result = {
            'awesomeness': d.response_awesomeness
        }
        
        # TODO handle winner and loser
        
        d.send_winner_loser_messages()
        
        return HttpResponse(json.dumps(result), mimetype="text/json")
        
def challenge_detail_redirect(request, id):
    return HttpResponseRedirect('/challenge/%s/' % id)