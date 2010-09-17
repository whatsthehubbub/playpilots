from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseBadRequest

from django.shortcuts import render_to_response, get_object_or_404

from django.template import RequestContext, Template
from django.template.loader import get_template, render_to_string

import logging

import json

def token_catcher(request):
    if request.method == "POST":
        # TODO log all the stuff that we catch
        
        return HttpResponse('success\r\n' + json.dumps(request.POST))
        
    return HttpResponseBadRequest()