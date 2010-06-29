from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from ebi.metagame.models import Maker, Festival, Game, Player
from services import feed_first_entry

def index(request):
    games = Game.objects.all()
    
    return render_to_response('metagame/index.html', {
        'games': games,
        'blogentry': feed_first_entry('http://ebi.posterous.com/rss.xml')
    }, context_instance=RequestContext(request))


def player_list(request):
    players = Player.objects.all()
    
    return render_to_response('metagame/player_list.html', {
        'players': players
    }, context_instance=RequestContext(request))

def player_detail(request, id):
    player = get_object_or_404(Player, id=id)
    
    return render_to_response('metagame/player_detail.html', {
        'player': player
    }, context_instance=RequestContext(request))


def game_detail(request, slug):
    game = get_object_or_404(Game, slug=slug)
    
    return render_to_response('metagame/game_detail.html', {
        'game': game
    }, context_instance=RequestContext(request))
    

def maker_detail(request, slug):
    maker = get_object_or_404(Maker, slug=slug)
    
    return render_to_response('metagame/maker_detail.html', {
        'maker': maker
    }, context_instance=RequestContext(request))
        
def festival_detail(request, slug):
    festival = get_object_or_404(Festival, slug=slug)
    
    return render_to_response('metagame/festival_detail.html', {
        'festival': festival
    }, context_instance=RequestContext(request))