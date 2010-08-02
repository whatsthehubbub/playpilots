from django.db import models
from django.core.mail import send_mail
from django.db.models import Q

from ebi.metagame.models import Player

import random
import smtplib

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
    
    
# class Move(models.Model):
#     style = models.ForeignKey(Style)
#     
#     name = models.CharField(max_length=255, blank=True)
#     
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
# 
#     def __unicode__(self):
#         return self.name
        

class Skill(models.Model):
    player = models.ForeignKey(Player)
    style = models.ForeignKey(Style)
    
    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=0)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def get_play_count(self):
        '''Returns the number of times this player/skill combination have played.'''
        return Duel.objects.all().filter(open=False).filter((Q(challenger=self.player) & Q(challenge_move__style=self.style)) | (Q(target=self.player) & Q(response_move__style=self.style))).count()
        
    def progress(self, record):
        old_exp = self.experience
        
        '''
        if record=='W':
            self.experience += 3
        elif record=='L':
            self.experience += 1
        elif record=='T':
            self.experience += 2
        '''
        
        self.experience += 1
        
        # TODO balance experience in the future using total experience for the group
        if self.level==1:
            if self.experience >= 25:
                self.level += 1
        elif self.level==2:
            if self.experience >= 50:
                self.level += 1
        elif self.level==3:
            if self.experience >= 100:
                self.level += 1
        elif self.level==4:
            if self.experience >= 200:
                self.level += 1
        elif self.level==5:
            pass # No higher levels yet
            
        self.save()
        
        return (old_exp, self.experience)

        
    def get_probability_text(self):
        if self.level==1:
            return 'Je begint pas net als %s; de kans dat je wint is klein.' % self.style.name
             
        return ''
    
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
        return '%s' % self.challenge_move.phrase
        
    def get_absolute_url(self):
        return '/c/%d/' % self.id
        
    def get_challenge_move(self):
        return self.challenge_move.phrase.replace('X', self.target.user.username.capitalize())
        
    def get_response_move(self):
        return self.response_move.phrase.replace('X', self.challenger.user.username.capitalize())
    
    def get_challenge_awesomeness(self):
        return self.get_awesomeness(self.challenger, self.challenge_move.style)
        
    def get_response_awesomeness(self):
        return self.get_awesomeness(self.target, self.response_move.style)
        
    def get_awesomeness(self, player, style):
        # Get a skill or make one if it doesn't exist yet
        try:
            skill = Skill.objects.get(player=player, style=style)
        except Skill.DoesNotExist:
            skill = Skill.objects.create(player=player, style=style)
        
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
            return self.win_phrase.phrase.replace('X', self.get_loser().user.username.capitalize())
                    
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
            return '%s en %s zijn aan elkaar gewaagd, maar de jury komt er niet uit. Het duel blijft onbeslist.' % (self.challenger.user.username.capitalize(), self.target.user.username.capitalize())
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
        # TODO this also assumes e-mail as communications medium
        try:
            send_mail('Je bent uitgedaagd door %s' % self.challenger.user.username,
            '''Hoi %(target)s,

Je bent uitgedaagd voor een duel door %(challenger)s.

Ga naar %(url)s om te duelleren!

Namens PLAY Pilots,

Uw gezagvoerder''' % {'target': self.target.user.username, 
                            'challenger': self.challenger.user.username, 
                            'url': 'http://playpilots.nl/c/%d/' % self.id}, 
            'Your Captain Speaking <captain@playpilots.nl>', 
            [self.target.user.email])
        except smtplib.SMTPException:
            logging.error('sending target e-mail failed')

    
    def send_winner_loser_messages(self):
        if self.get_winner():
            # We have a winner and a loser
            winner = self.get_winner()
            loser = self.get_loser()
            
            
            # TODO For now assume e-mail is the only medium
            try:
                send_mail('Gefeliciteerd! Je hebt gewonnen van %s!' % loser.user.username, 
                '''Hoi %(winner)s,

Gefeliciteerd! Je hebt het duel met %(loser)s gewonnen.

Ga naar %(url)s om de uitkomst te zien!

Namens PLAY Pilots,

Uw gezagvoerder''' % {
                'winner': winner.user.username,
                'loser': loser.user.username,
                'url': 'http://playpilots.nl/c/%d/' % self.id 
            }, 
                'Your Captain Speaking <captain@playpilots.nl>', 
                [winner.user.email])
            
                send_mail('Helaas! Je hebt verloren van %s!' % winner.user.username,
                '''Hoi %(loser)s,

Helaas! Je hebt het duel met %(winner)s verloren.

Ga naar %(url)s om de uitkomst te zien!

Namens PLAY Pilots,

Uw gezagvoerder''' % {
                    'loser': loser.user.username,
                    'winner': winner.user.username,
                    'url': 'http://playpilots.nl/c/%d/' % self.id
                }, 
                'Your Captain Speaking <captain@playpilots.nl>', 
                [loser.user.email])
            except smtplib.SMTPException:
                logging.error('sending winner loser e-mail failed')