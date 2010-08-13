from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.shortcuts import render_to_response, get_object_or_404

from django.template import RequestContext, Template
from django.template.loader import get_template, render_to_string

from kipwip.models import KippenrenCode

import json

def kipwip_code(request):
    if request.user.is_authenticated() and request.method=="POST":
        player = request.user.get_profile()
        
        code = request.POST.get('codeinput', '')
        
        KippenrenCode.objects.create(player=player, code=code)
        
        return HttpResponse(json.dumps({'result': 1}))