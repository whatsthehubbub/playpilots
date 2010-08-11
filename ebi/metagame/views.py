from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.cache import cache
from django import forms
from django.core.signals import request_finished

from ebi.metagame.models import Maker, Festival, Game, Player
from ebi.battleroyale.models import Skill
from metagame.services import send_tweet

import actstream
from actstream.models import Action, actor_stream
from services import feed_entries, feed_first_entry

import datetime, random, math, json

from django.views.decorators.cache import cache_page

import logging

def index(request):
    if False and request.user.is_anonymous():
        return render_to_response('metagame/index_splash.html', {
        }, context_instance=RequestContext(request))
    else:
        blogentry = cache.get('blogentry')
        if not blogentry:
            blogentry = feed_first_entry('http://ebi.posterous.com/rss.xml')
            cache.set('blogentry', blogentry, 60*60*4)
    
        # Rough code to get 4 actions with unique actors in this list
        action_list = []
        actions = Action.objects.all().order_by('-timestamp')
        for action in actions:
            if len(action_list) > 3:
                break
                
            if not action.actor_object_id in [a.actor_object_id for a in action_list]:
                action_list.append(action)
            
        
        nextgame = Game.objects.filter(start__gt=datetime.datetime.now()).order_by('start')[0]
        
        templateName = 'metagame/index.html'
        
        if request.GET.get('staging', 0) == 'yes':
            templateName = 'metagame/index2.html'
        
        return render_to_response(templateName, {
            'current': 'home',
            'blogentry': blogentry,
            'actions': action_list,
            'nextgame': nextgame
        }, context_instance=RequestContext(request))

def flatpage(request):
    raise Http404

def player_detail(request, id):
    player = get_object_or_404(Player, id=id)
    
    try:
        player = Player.objects.get(id=id)
    except Player.DoesNotExist:
        pass
    
    skills = Skill.objects.all().filter(player=player).order_by('style__name')
    
    return render_to_response('metagame/player_detail.html', {
        'player': player,
        'skills': skills
    }, context_instance=RequestContext(request))
    
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
        
        # actstream.action.send(user.get_profile(), verb='heeft net ingecheckt voor PLAY!')
        
        send_mail('Account voor Play Pilots aangemaakt!', 'Bericht', 'alper@whatsthehubbub.nl', form.cleaned_data['email'])
        
        if form.is_valid():
            return HttpResponse('/players/%s/' % user.username)
    else:
        form = RegisterForm()
        
    return render_to_response('registration/register.html', {
        'form': form
    }, context_instance=RequestContext(request))


def logout_view(request):
    # actstream.action.send(request.user, verb='is uitgelogd. Spater ouwe!')
    
    logout(request)
    
    return HttpResponseRedirect('/')
    
def game_list(request):
    return render_to_response('metagame/game_list.html', {
        'games': Game.objects.all().order_by('-start'),
        'current': 'games'
    }, context_instance=RequestContext(request))

def game_detail(request, slug):
    game = get_object_or_404(Game, slug=slug)
    
    feedURL = game.maker.updatesFeed
    feedEntries = cache.get(feedURL)
    if not feedEntries:
        feedEntries = feed_entries(feedURL)
        cache.set(feedURL, feedEntries, 60*60*24)
    
    interest = False
    if request.user.is_authenticated() and request.user.get_profile() in game.interested.all():
        interest = True
    
    
    templateName = 'metagame/game_detail.html'
    
    if request.GET.get('staging', 0) == 'yes':
        templateName = 'metagame/game_detail2.html'
    
    
    return render_to_response(templateName, {
        'game': game,
        'current': 'games',
        'interest': interest,
        'feed': feedEntries[:3]
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
        
        if action == 'add':
            game.interested.add(player)
            
            actstream.action.send(player, verb="doet mee met", target=game)
            
            if player.get_twitter_name():
                send_tweet('@%(player)s je doet mee met %(game)s, kijk op: http://playpilots.nl%(url)s en vertel je vrienden!' % {
                    'player': player.get_twitter_name(),
                    'game': game.name,
                    'url': game.get_absolute_url()
                })
            
        elif action == 'remove':
            game.interested.remove(player)
            actstream.action.send(player, verb='doet niet meer mee met', target=game)
            
            if player.get_twitter_name():
                send_tweet('@%(player)s doet helaas niet meer mee met %(game)s, maar wil je wel al je vrienden vertellen over: http://playpilots.nl%(url)s ?' % {
                    'player': player.get_twitter_name(),
                    'game': game.name,
                    'url': game.get_absolute_url()
                })
        
        if 'json' in request.META.get("HTTP_ACCEPT", ""):
            return HttpResponse(json.dumps({'success': 1}))
        else:
            return HttpResponseRedirect('/games/%s/' % game.slug)
        
    return HttpResponse(json.dumps({'success': 0}))