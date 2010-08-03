from django.db import models
from django.core.mail import send_mail
from django.db.models import Q

from ebi.metagame.models import Player

import random
import smtplib
import logging

class Style(models.Model):
    name = models.CharField(max_length=255, blank=True)
    
    description = models.TextField(blank=True)
    
    image = models.ImageField(upload_to="culture_images", blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.name
        
    def get_action_phrases(self):
        return self.actionphrase_set.filter(action=True).order_by('style__name')
        
    def get_reaction_phrases(self):
        return self.actionphrase_set.filter(action=False).order_by('style__name')
        

class Skill(models.Model):
    player = models.ForeignKey(Player, related_name="skills")
    style = models.ForeignKey(Style, related_name='skills')
    
    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=0)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def get_play_count(self):
        '''Returns the number of times this player/skill combination have played.'''
        return Duel.objects.all().filter(open=False).filter((Q(challenger=self.player) & Q(challenge_move__style=self.style)) | (Q(target=self.player) & Q(response_move__style=self.style))).count()
    
    def progress(self):
        old_exp = self.experience
        
        self.experience += 1
        
        # TODO balance experience in the future using total experience for the group
        if self.level==1:
            if self.experience >= 10:
                self.level += 1
        elif self.level==2:
            if self.experience >= 25:
                self.level += 1
        elif self.level==3:
            if self.experience >= 50:
                self.level += 1
        elif self.level==4:
            if self.experience >= 100:
                self.level += 1
        elif self.level==5:
            pass # No higher levels yet
            
        self.save()
        
        return (old_exp, self.experience)

    
    def get_probability_texts(self):
        return {1: 'Je begint pas net als %s; de kans dat je wint is klein.' % self.style.name,
                2: 'Je bent aardig op weg als %s; je zult niet snel winnen, maar daar staat wel een behoorlijke bak punten tegenover.' % self.style.name,
                3: 'Je bent een goede middenmoter als %s; je winkans en te vergaren punten zijn nominaal.' % self.style.name,
                4: 'Je bent landelijk bekend als %s; je hebt een behoorlijke kans om te winnen, maar echt veel punten zul je niet krijgen.' % self.style.name,
                5: 'Je staat op eenzame hoogte als %s; de kans dat je wint is groot maar als het lukt scoor je weinig punten.' % self.style.name}
    
    def get_probability_text(self):
        return self.get_probability_texts()[self.level]

    
    def __unicode__(self):
        return '%d' % self.level
    
    
class Phrase(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    style = models.ForeignKey(Style)
    
    phrase = models.CharField(max_length=255, blank=True)
    
    class Meta:
        abstract = True
        
    def __unicode__(self):
        return '%s' % self.phrase
    
class ActionPhrase(Phrase):
    # Set to False for a reaction phrase
    action = models.BooleanField(default=True)

class WinPhrase(Phrase):
    pass


class Duel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    challenger = models.ForeignKey(Player, related_name='challenger_duel')
    challenge_move = models.ForeignKey(ActionPhrase, related_name='challenger_move')
    challenge_message = models.CharField(max_length=255, blank=True)
    challenge_awesomeness = models.IntegerField(blank=True, null=True)
    
    # If this move is still open
    open = models.BooleanField(default=True)
    
    target = models.ForeignKey(Player, blank=True, null=True, related_name='responder_duel')
    target_text = models.CharField(max_length=255, blank=True)
    
    responded = models.DateTimeField(blank=True, null=True)
    response_move = models.ForeignKey(ActionPhrase, blank=True, null=True, related_name='responder_move')
    response_message = models.CharField(max_length=255, blank=True)
    response_awesomeness = models.IntegerField(blank=True, null=True)
    
    win_phrase = models.ForeignKey(WinPhrase, blank=True, null=True)
    
    # Need to save snapshot states for the various player stats
    challenger_skilllevel = models.IntegerField(blank=True, null=True)
    challenger_oldrank = models.IntegerField(blank=True, null=True)
    challenger_newrank = models.IntegerField(blank=True, null=True)
    challenger_oldrating = models.IntegerField(blank=True, null=True)
    challenger_newrating = models.IntegerField(blank=True, null=True)
    
    responder_skilllevel = models.IntegerField(blank=True, null=True)
    responder_oldrank = models.IntegerField(blank=True, null=True)
    responder_newrank = models.IntegerField(blank=True, null=True)
    responder_oldrating = models.IntegerField(blank=True, null=True)
    responder_newrating = models.IntegerField(blank=True, null=True)
    
    def __unicode__(self):
        # Complex conditional branch to create a useful string representation for various situations
        if self.open:
            return '%s' % self.get_challenge_move()
        else:
            if self.is_tie():
                return '%s' % self.get_response_move()
            else:
                return '%s' % self.get_win_phrase()
                
        return '%s' % self.get_challenge_move()
        
    def get_absolute_url(self):
        return '/c/%d/' % self.id
        
    def get_challenge_move(self):
        return self.challenge_move.phrase.replace('X', self.target.get_display_name().capitalize())
        
    def get_response_move(self):
        return self.response_move.phrase.replace('X', self.challenger.get_display_name().capitalize())
    
    def get_challenge_awesomeness(self):
        return self.get_awesomeness(self.challenger, self.challenge_move.style)
        
    def get_challenger_rating_difference(self):
        return self.challenger_newrating - self.challenger_oldrating
        
    def get_responder_rating_difference(self):
        return self.responder_newrating - self.responder_oldrating
        
    def get_response_modifier(self):
        modifier = 0
        
        if self.response_move.style.id == 1:
            if self.challenge_move.style.id == 8:
                modifier = 0.2
        elif self.response_move.style.id == 2:
            if self.challenge_move.style.id == 10:
                modifier = -0.2
            elif self.challenge_move.style.id == 5:
                modifier = 0.2
        elif self.response_move.style.id == 3:
            if self.challenge_move.style.id == 6:
                modifier = -0.2
            elif self.challenge_move.style.id == 11:
                modifier = 0.2
        elif self.response_move.style.id == 4:
            if self.challenge_move.style.id == 1:
                modifier = -0.2
            elif self.challenge_move.style.id == 8:
                modifier = 0.2
        elif self.response_move.style.id == 5:
            if self.challenge_move.style.id == 9:
                modifier = -0.2
            elif self.challenge_move.style.id == 2:
                modifier = 0.2
        elif self.response_move.style.id == 6:
            if self.challenge_move.style.id == 9:
                modifier = -0.2
            elif self.challenge_move.style.id == 3:
                modifier = 0.2
        elif self.response_move.style.id == 7:
            if self.challenge_move.style.id == 11:
                modifier = -0.2
            elif self.challenge_move.style.id == 4:
                modifier = 0.2
        elif self.response_move.style.id == 8:
            if self.challenge_move.style.id == 1:
                modifier = -0.2
            elif self.challenge_move.style.id == 4:
                modifier = 0.2
        elif self.response_move.style.id == 9:
            if self.challenge_move.style.id == 5:
                modifier = -0.2
            elif self.challenge_move.style.id == 6:
                modifier = 0.2
        elif self.response_move.style.id == 10:
            if self.challenge_move.style.id == 2:
                modifier = -0.2
            elif self.challenge_move.style.id == 5:
                modifier = 0.2
        elif self.response_move.style.id == 11:
            if self.challenge_move.style.id == 7:
                modifier = -0.2
            elif self.challenge_move.style.id == 3:
                modifier = 0.2
        return modifier
        
    def get_response_awesomeness(self):
        # Response awesomeness is dependent on some stuff
        modifier = self.get_response_modifier()
        
        awesomeness = self.get_awesomeness(self.target, self.response_move.style)
        
        if modifier > 0:
            if random.random() < modifier:
                awesomeness += 1
            
            return min(awesomeness, 5)
        elif modifier < 0:
            if random.random() < abs(modifier):
                awesomeness -= 1
                
            return max(awesomeness, 0)
            
        return awesomeness
        
    def get_awesomeness(self, player, style):
        # Get a skill or make one if it doesn't exist yet
        try:
            skill = Skill.objects.get(player=player, style=style)
        except Skill.DoesNotExist:
            skill = Skill.objects.create(player=player, style=style)
        
        logging.info('skill level for %s is %d', player.get_display_name(), skill.level)
        
        # For each level a probability distribution
        level_choices = {
                    1: 10*[1] + 6*[2] + 3*[3] + 1*[4],
                    2: 8*[1] + 5*[2] + 4*[3] + 2*[4] + 1*[5],
                    3: 5*[1] + 5*[2] + 5*[3] + 3*[4] + 2*[5],
                    4: 3*[1] + 4*[2] + 6*[3] + 4*[4] + 3*[5],
                    5: 2*[1] + 3*[2] + 4*[3] + 6*[4] + 5*[5]
                }

        choices = level_choices[skill.level]
        
        return random.choice(choices)
        
    
    def challenger_won(self):
        return self.challenge_awesomeness > self.response_awesomeness
        
    def responder_won(self):
        return self.response_awesomeness > self.challenge_awesomeness
    
    def is_tie(self):
        return self.challenge_awesomeness == self.response_awesomeness
    
    def get_winner(self):
        if self.challenger_won():
            return self.challenger
        elif self.responder_won():
            return self.target
            
    def get_winner_style(self):
        if self.challenger_won():
            return self.challenge_move.style
        elif self.responder_won():
            return self.response_move.style
            
    def get_win_phrase(self):
        if self.win_phrase:
            return self.win_phrase.phrase.replace('X', '<span class="player">%s</span>' % self.get_loser().get_display_name())

        return ''
            
    def get_loser(self):
        if self.challenger_won():
            return self.target
        elif self.responder_won():
            return self.challenger
    
    def get_loser_style(self):
        if self.challenger_won():
            return self.response_move.style
        elif self.responder_won():
            return self.challenge_move.style
    
    # TODO probably is not being used
    def get_result_phrase(self):
        if self.is_tie():
            return '%s en %s zijn aan elkaar gewaagd, maar de jury komt er niet uit. Het duel blijft onbeslist.' % (self.challenger.get_display_name().capitalize(), self.target.get_display_name().capitalize())
        else:
            style = self.get_winner_style()
            
            phrase = 'default win phrase'
            try:
                w = WinPhrase.objects.get(style=style)
                phrase = w.phrase
            except WinPhrase.DoesNotExist:
                pass
                
            return phrase
    
    def send_target_message(self):
        self.target.send_challenge_message(self)
    
    def send_winner_loser_messages(self):
        self.get_winner().send_win_message(self)
        self.get_loser().send_lose_message(self)