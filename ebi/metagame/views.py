from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from django.contrib.auth import logout, login
from django.contrib.auth.models import User
from django.core.mail import send_mail

from django import forms

from ebi.metagame.models import Maker, Festival, Game, Player, Culture, Move, Round

import datetime, random, math, json

def index(request):
    games = Game.objects.all()
    
    return render_to_response('metagame/index.html', {
        'games': games,
        'current': 'home'
    }, context_instance=RequestContext(request))


def player_list(request):
    players = Player.objects.all().order_by('-rating')
    
    cultures = Culture.objects.all().order_by('name')
    
    return render_to_response('metagame/player_list.html', {
        'players': players,
        'cultures': cultures
    }, context_instance=RequestContext(request))

def player_detail(request, id):
    player = get_object_or_404(Player, id=id)
    
    # TODO if player does not exist create (here or on registration)
    
    return render_to_response('metagame/player_detail.html', {
        'player': player
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
        
        send_mail('Account voor Play Pilots aangemaakt!', 'Bericht', 'alper@whatsthehubbub.nl', form.cleaned_data['email'])
        
        if form.is_valid():
            return HttpResponse('/players/%s/' % user.username)
    else:
        form = RegisterForm()
        
    return render_to_response('registration/register.html', {
        'form': form
    }, context_instance=RequestContext(request))
    
    
def logout_view(request):
    logout(request)
    
    return HttpResponseRedirect('/')
    

def game_list(request):
    return render_to_response('metagame/game_list.html', {
        'games': Game.objects.all().order_by('start'),
        'current': 'games'
    }, context_instance=RequestContext(request))

def game_detail(request, slug):
    game = get_object_or_404(Game, slug=slug)
    
    return render_to_response('metagame/game_detail.html', {
        'game': game,
        'current': 'games'
    }, context_instance=RequestContext(request))

def maker_list(request):
    return render_to_response('metagame/maker_list.html', {
        'makers': Maker.objects.all(),
        'current': 'makers'
    }, context_instance=RequestContext(request))

def maker_detail(request, slug):
    maker = get_object_or_404(Maker, slug=slug)
    
    return render_to_response('metagame/maker_detail.html', {
        'maker': maker,
        'current': 'makers'
    }, context_instance=RequestContext(request))
        
def festival_list(request):
    return render_to_response('metagame/festival_list.html', {
        'festivals': Festival.objects.all().order_by('start'),
        'current': 'festivals'
    }, context_instance=RequestContext(request))

def festival_detail(request, slug):
    festival = get_object_or_404(Festival, slug=slug)
    
    return render_to_response('metagame/festival_detail.html', {
        'festival': festival,
        'current': 'festivals'
    }, context_instance=RequestContext(request))
    
def challenge(request):
    if request.method == 'POST':
        # Trying to store a challenge
        
        challenger = request.user.get_profile()
        
        culture_id = request.POST.get('culture', None)
        culture = Culture.objects.get(id=culture_id)
        
        move_id = request.POST.get('move', None)
        move = Move.objects.get(id=move_id)
        
        message = request.POST.get('message', '')
        
        target_id = request.POST.get('target', None)
        target = Player.objects.get(id=target_id)
        
        # Create Round object
        round = Round(challenger=challenger, challenge_move=move, challenge_message=message, target=target)
        round.save()
        
        # TODO Send out message about challenge
        
        return HttpResponseRedirect('/players/%s/' % request.user.username)
    else:
        playerid = request.GET.get('target', None)

        target = get_object_or_404(Player, id=playerid)
    
        cultures = Culture.objects.all().order_by('name')
    
        return render_to_response('metagame/challenge.html', {
            'target': target,
            'cultures': cultures
        }, context_instance=RequestContext(request))
        
def challenge_resolve(request):
    if request.method == 'POST':
        try:
            round_id = int(request.POST.get('round_id', None))
            r = Round.objects.get(id=round_id)
        
            r.open = False
            r.responded = datetime.datetime.now()
        
            move_id = int(request.POST.get('move', None))
            r.response_move = Move.objects.get(id=move_id)
        
            r.response_message = request.POST.get('message', '')
        
            # Also TODO update dominant style
        
            winner_attack_bonus = 0
            winner_style_penalty = 0
        
            if random.random() < 0.5:
                winner = r.challenger
                winner_attack_bonus = 10
            
                loser = r.target
            else:
                winner = r.target
                loser = r.challenger
                
            print 'winner', winner, winner.rating
            print 'loser', loser, loser.rating
            
            print 'bonus', winner_attack_bonus
        
            difference = abs(winner.rating - loser.rating)
        
            if winner.rating > loser.rating:
                winner.rating += 10
                loser.rating -= 10
            elif winner.rating < loser.rating:
                winner.rating += difference + 10
                loser.rating -= difference - 10
            
            winner.rating = winner.rating + winner_attack_bonus + winner_style_penalty
            
            r.save()
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
                }
            }
        
            return HttpResponse(json.dumps(result), mimetype="text/plain")
        except:
            pass # TODO log

def challenge_detail(request, id):
    r = get_object_or_404(Round, id=id)
    
    if r.open:
        cultures = Culture.objects.all().order_by('name')
    
        return render_to_response('metagame/challenge_open.html', {
            'round': r,
            'cultures': cultures
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('metagame/challenge_closed.html', {
            'round': r
        }, context_instance=RequestContext(request))