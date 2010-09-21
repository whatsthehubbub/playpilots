from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseBadRequest

from django.shortcuts import render_to_response, get_object_or_404

from django.template import RequestContext, Template
from django.template.loader import get_template, render_to_string

from stereoscoop.models import StereoscoopUnlock, StereoscoopCode, StereoscoopBadge, StereoscoopMovie

import datetime
import logging

import json

def token_catcher(request):
    if request.method == "POST":
        receivedParams = str(request.POST)
        logging.debug('stereoscoop catcher received %s', receivedParams)
        
        token = request.POST.get('token')
        dt = datetime.datetime.strptime(request.POST.get('datetime', ''), '%Y-%m-%d %H:%M:%S')
        
        logging.debug('got token %s and datetime %s', token, str(dt))
        
        badgeid = int(request.POST.get('badgeid', ''))
        badge = StereoscoopBadge.objects.get(badgeid=badgeid)
        
        logging.debug('got badgeid %d and badge %s', badgeid, str(badge))
        
        movie1Title = request.POST.get('movie1', '')
        movie2Title = request.POST.get('movie2', '')
        
        logging.debug('got movie titles %s and %s', movie1Title, movie2Title)
        
        movie1 = StereoscoopMovie.objects.get(title=movie1Title)
        movie2 = StereoscoopMovie.objects.get(title=movie2Title)
        
        logging.debug('resolved to movies %s and %s', str(movie1), str(movie2))
        
        s = StereoscoopUnlock.objects.create(code=token, time=dt, badge=badge, movie1=movie1, movie2=movie2)
        
        logging.debug('created stereoscoop unlock %d', s.id)
        
        scene1 = request.POST.get('scene1', '')
        scene2 = request.POST.get('scene2', '')
        
        if scene1 and scene2:
            try:
                s.scene1 = int(scene1)
                s.scene2 = int(scene2)
            except:
                pass
        
        cue1 = request.POST.get('cue1', '')
        cue2 = request.POST.get('cue2', '')
        
        if cue1 and cue2:
            try:
                s.cue1 = int(cue1)
                s.cue2 = int(cue2)
            except:
                pass
                
        s.save()
        
        return HttpResponse('success\r\n' + receivedParams, mimetype='text/plain')
        
    return HttpResponseBadRequest()
    
    
def stereoscoop_badge(request):
    return render_to_response('stereoscoop/badge.html', {}, context_instance=RequestContext(request))