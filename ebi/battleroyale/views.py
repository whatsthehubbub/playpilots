from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from django.core.mail import send_mail
from django.core.cache import cache
from django.contrib.auth.decorators import login_required

from django import forms

from ebi.metagame.models import Player
from battleroyale.models import *

import actstream
from actstream.models import Action

import datetime, random, math, json

import logging

@login_required
def klassement(request):
    c = {
        'styles': Style.objects.all(),
        'current': 'klassement'
    }
    
    if not request.GET.get('style'):
        c['players'] = Player.objects.all().order_by('-rating')
    
        return render_to_response('metagame/klassement.html', c, context_instance=RequestContext(request))
    else:
        styleid = int(request.GET.get('style'))
        
        c['currentStyle'] = Style.objects.get(id=styleid)
        
        skills = []
        for count in range(5, 0, -1):
            skills.append((count, 
                        Player.objects.filter(skills__style=c['currentStyle'], skills__level=count).order_by('skills__experience')
                    ))
        # c['currentStyle'].skills.all()[0].get_probability_texts()[count]
        
        c['skills'] = skills
        
        return render_to_response('metagame/klassement.html', c, context_instance=RequestContext(request))
    
@login_required
def challenge(request):
    playerid = request.GET.get('target', None)

    target = get_object_or_404(Player, id=int(playerid))

    styles = Style.objects.all().order_by('name')

    return render_to_response('metagame/challenge_start.html', {
        'target': target,
        'styles': styles,
        'current': 'klassement'
    }, context_instance=RequestContext(request))

@login_required
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

@login_required
def challenge_create(request):
    if request.method == 'POST':
        challenger = request.user.get_profile()

        action_id = request.POST.get('action', None)
        logging.debug('got move id: %s', action_id)

        action = ActionPhrase.objects.get(id=int(action_id))

        message = request.POST.get('message', '')
        logging.debug('got message: %s', message)

        target_id = request.POST.get('target', None)
        target = Player.objects.get(id=int(target_id))

        # Create Round object
        d = Duel.objects.create(challenger=challenger, 
                            challenge_move=action, 
                            challenge_message=message, 
                            target=target)

        awesomeness = d.get_challenge_awesomeness()
        d.challenge_awesomeness = awesomeness
        d.save()

        actstream.action.send(challenger, verb='heeft net %s uitgedaagd voor een duel' % target.get_display_name(), target=d)

        d.send_target_message()
        
        return HttpResponse(json.dumps({
            'awesomeness': awesomeness
        }), mimetype='text/json')

@login_required
def challenge_resolve(request):
    if request.method == 'POST':
        duel_id = int(request.POST.get('duel', None))
        d = Duel.objects.get(id=duel_id)
    
        d.open = False
        d.responded = datetime.datetime.now()
    
        action_id = int(request.POST.get('action', None))
        d.response_move = ActionPhrase.objects.get(id=action_id)
    
        d.response_message = request.POST.get('message', '')
        d.response_awesomeness = d.get_response_awesomeness()
        d.save()
        
        result = {
            'awesomeness': d.response_awesomeness
        }
        
        # Simplified ELO table
        # Source: http://www.chesselo.com/probabil.html
        def getWinProb(diff):
            '''Returns the win probability for the stronger player. The probability for the weaker player is 1-prob.'''
            if diff == 0:
                return 0.5
            elif diff < 4:
                return 0.53
            elif diff < 10:
                return 0.57
            elif diff < 20:
                return 0.64
            elif diff < 30:
                return 0.70
            elif diff < 40:
                return 0.76
            elif diff < 50:
                return 0.81
            elif diff < 60:
                return 0.85
            elif diff < 70:
                return 0.89
            elif diff < 80:
                return 0.92
            elif diff < 90:
                return 0.94
            elif diff < 100:
                return 0.96
            elif diff < 150:
                return 0.99
            else:
                return 1.00
        Kfactor = 20
        
        d.challenger_oldrank = d.challenger.get_rank()
        d.responder_oldrank = d.target.get_rank()
        
        d.challenger_oldrating = d.challenger.rating
        d.responder_oldrating = d.target.rating
        
        ratingDifference = abs(d.challenger.rating-d.target.rating)
        
        challengerSkill = Skill.objects.get(player=d.challenger, style=d.challenge_move.style)
        responderSkill = Skill.objects.get(player=d.target, style=d.response_move.style)
        
        d.challenger_skilllevel = challengerSkill.level
        d.responder_skilllevel = responderSkill.level
        
        skillDifference = abs(challengerSkill.level-responderSkill.level)
        
        # TODO maybe still progress skill based on performance
        challengerSkill.progress()
        responderSkill.progress()
        
        prob = getWinProb(ratingDifference + skillDifference*10)
        
        if d.is_tie():
            if d.challenger.rating > d.target.rating:
                stronger = d.challenger
                weaker = d.target
            else:
                stronger = d.target
                weaker = d.challenger
            
            stronger.rating += Kfactor * (0.5-prob)
            weaker.rating += Kfactor * (0.5-(1-prob))

            result['phrase'] = 'Helaas, gelijkspel. Probeer het nog eens!'
                
            actstream.action.send(d.target, verb='heeft net gelijkgespeeld met %s in duel' % d.challenger.get_display_name(), target=d)
        else:
            winner = d.get_winner()
            loser = d.get_loser()
            
            result['winner'] = winner.get_display_name()
            result['loser'] = loser.get_display_name()
            
            try:
                # Get a random win phrase
                d.win_phrase = WinPhrase.objects.filter(style=d.get_winner_style()).order_by('?')[0]
                result['phrase'] = self.get_win_phrase()
            except:
                result['phrase'] = 'Generic win phrase.'

            # Reverse probability if the winner had a lower rating (they were the underdog)
            if winner.rating < loser.rating:
                prob = 1-prob

            winner.rating += round(Kfactor * (1-prob))
            loser.rating += round(Kfactor * (0-(1-prob)))

            actstream.action.send(winner, verb='heeft net gewonnen van %s en' % loser.user.username, target=d)
        
        d.challenger.save()
        d.target.save()
        
        d.challenger_newrating = d.challenger.rating
        d.responder_newrating = d.target.rating
        
        # Invalidate ranks
        cache.set('player_%d_rank' % d.challenger.id, None, 1)
        cache.set('player_%d_rank' % d.target.id, None, 1)
        
        d.challenger_newrank = d.challenger.get_rank()
        d.responder_newrank = d.target.get_rank()
        
        d.save()
        
        if not d.is_tie():
            d.send_winner_loser_messages()
        else:
            # TODO implement
            # d.send_tie_messages()
            pass
        
        return HttpResponse(json.dumps(result), mimetype="text/json")
        
@login_required
def challenge_detail_redirect(request, id):
    return HttpResponseRedirect('/challenge/%s/' % id)