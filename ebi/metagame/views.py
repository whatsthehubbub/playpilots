from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.contrib.auth.models import User
from django.core.mail import send_mail

from django import forms
from django.core.signals import request_finished

from ebi.metagame.models import Maker, Festival, Game, Player

import actstream
from actstream.models import Action, actor_stream

# from ebi.metagame.models import Culture, Move, Round, SpecificWinPhrase

import datetime, random, math, json

from django.views.decorators.cache import cache_page

import logging

# @cache_page
def index(request):
    if request.user.is_anonymous():
        return render_to_response('metagame/index_splash.html', {
        }, context_instance=RequestContext(request))
    else:
        games = Game.objects.all()
    
        return render_to_response('metagame/index.html', {
            'games': games,
            'current': 'home'
        }, context_instance=RequestContext(request))

@login_required
def player_list(request):
    players = Player.objects.all().order_by('-rating')
    
    cultures = Culture.objects.all().order_by('name')
    
    return render_to_response('metagame/player_list.html', {
        'players': players,
        'cultures': cultures
    }, context_instance=RequestContext(request))

@login_required
def player_detail(request, id):
    player = get_object_or_404(Player, id=id)

    # TODO if player does not exist create (here or on registration)
    
    try:
        player = Player.objects.get(id=id)
    except Player.DoesNotExist:
        pass
    
    actions = actor_stream(player.user)
    
    
    return render_to_response('metagame/player_detail.html', {
        'player': player,
        'actions': actions
    }, context_instance=RequestContext(request))
    
@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username)
    
    # from django.contrib.auth.models import SiteProfileNotAvailable
    
    try:
        player = user.get_profile()
    except Player.DoesNotExist:
        player = Player(user=user)
        player.save()
        
    return HttpResponseRedirect('/players/%d/' % player.id)

@login_required
def register(request):    
    class RegisterForm(forms.Form):
        username = forms.CharField()
        email = forms.EmailField()
        password = forms.CharField(widget=forms.PasswordInput)
        
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        
        # Check for username duplication
        
        # Create user
        user = Users.object.create_user(form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password'])
        
        login(request, user)
        
        actstream.action.send(user, verb='heeft net ingecheckt voor PLAY!')
        
        send_mail('Account voor Play Pilots aangemaakt!', 'Bericht', 'alper@whatsthehubbub.nl', form.cleaned_data['email'])
        
        if form.is_valid():
            return HttpResponse('/players/%s/' % user.username)
    else:
        form = RegisterForm()
        
    return render_to_response('registration/register.html', {
        'form': form
    }, context_instance=RequestContext(request))


''' TODO catch the login view and do an action.send()
def user_logged_in(sender, **kwargs):
    # print sender
    # print 'test request finished'
    print sender.request_class.get_full_path(sender.request_class)
    #print sender.request_class
request_finished.connect(user_logged_in)
'''

@login_required
def logout_view(request):
    actstream.action.send(request.user, verb='is uitgelogd. Spater ouwe!')
    
    logout(request)
    
    return HttpResponseRedirect('/')
    
@login_required
# @cache_page
def game_list(request):
    return render_to_response('metagame/game_list.html', {
        'games': Game.objects.all().order_by('-start'),
        'current': 'games'
    }, context_instance=RequestContext(request))

@login_required
# @cache_page
def game_detail(request, slug):
    game = get_object_or_404(Game, slug=slug)
    
    interest = False
    if request.user.get_profile() in game.interested.all():
        interest = True
    
    return render_to_response('metagame/game_detail.html', {
        'game': game,
        'current': 'games',
        'interest': interest
    }, context_instance=RequestContext(request))

@login_required
def game_interest(request, slug):
    action = request.POST.get('action', 'add')
    game = get_object_or_404(Game, slug=slug)
    
    if request.user.is_authenticated():
        try:
            player = request.user.get_profile()
        except django.contrib.auth.models.SiteProfileNotAvailable:
            pass
            
        # TODO check if not already interested
        game.interested.add(player)
        
        actstream.action.send(request.user, verb="doet mee met", target=game)
        
        return HttpResponse('1')
        
    return HttpResponse('0')