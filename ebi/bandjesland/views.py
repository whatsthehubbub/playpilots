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


def add_like(request):
    pass


def remove_like(request):
    pass