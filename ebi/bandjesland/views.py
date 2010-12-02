from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.shortcuts import render_to_response, get_object_or_404

from django.template import RequestContext, Template
from django.template.loader import get_template, render_to_string

from django.contrib.auth.decorators import login_required


from ebi.metagame.models import Player
from bandjesland.models import *

from actstream.models import Action

import datetime, random, math, json, os

import logging


def toggle_like(request):
    playerid = request.POST.get('playerid', '')
    specialid = request.POST.get('specialid', '')

    if playerid and specialid:
        player = Player.objects.get(id=playerid)
        special = BandjeslandSpecial.objects.get(id=specialid)
        
        likes = BandjeslandLike.objects.filter(special=special, player=player)
        
        if likes:
            for like in likes:
                logging.debug('deleting bandjesland like %s', str(like))
                like.delete()
                
            action = 'removed'
        else:
            b = BandjeslandLike.objects.create(special=special, player=player)
            logging.debug('created bandjesland like %s', str(b))
            
            action = 'added'
            
        return HttpResponse(json.dumps({
            'error': '0',
            'specialid': specialid,
            'action': action
        }), mimetype='text/json')
        
    return HttpResponse(json.dumps({'error': '1'}), mimetype='text/json')
    
def special_occurrences(request):
    specialid = request.GET.get('specialid', '')
    sessionLabel = request.GET.get('sessionlabel', '')
    
    special = BandjeslandSpecial.objects.get(id=int(specialid))
    session = BandjeslandSessie.objects.get(label=sessionLabel)
    
    logging.debug('occurrences for special %d', special.id)
    logging.debug('occurrences for session %d', session.id)
    
    # print session.start
    
    occurrenceTimes = BandjeslandSpecialOccurrence.objects.filter(session=session).filter(special=special).order_by('-time').values('time')
    
    # print occurrenceTimes
    
    return HttpResponse(json.dumps({
        'label': sessionLabel,
        'offsets': [(occ['time']-session.start).seconds for occ in occurrenceTimes]
    }), mimetype='text/json')