from django.db import models
from ebi.metagame.models import Player

class Style(models.Model):
    name = models.CharField(max_length=255, blank=True)
    
    description = models.TextField(blank=True)
    
    image = models.ImageField(upload_to="culture_images", blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.name
    
    
class Move(models.Model):
    style = models.ForeignKey(Style)
    
    name = models.CharField(max_length=255, blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name
        

class Skill(models.Model):
    player = models.ForeignKey(Player)
    style = models.ForeignKey(Style)
    
    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=0)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
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
    challenge_move = models.ForeignKey(Move, related_name='challenger_move')
    challenge_message = models.CharField(max_length=255, blank=True)
    challenge_awesomeness = models.IntegerField(blank=True, null=True)
    
    # If this move is still open
    open = models.BooleanField(default=True)
    
    target = models.ForeignKey(Player, blank=True, null=True, related_name='responder_duel')
    target_text = models.CharField(max_length=255, blank=True)
    
    responded = models.DateTimeField(blank=True, null=True)
    response_move = models.ForeignKey(Move, blank=True, null=True, related_name='responder_move')
    response_message = models.CharField(max_length=255, blank=True)
    response_awesomeness = models.IntegerField(blank=True, null=True)
    
    # Blob to store the result in
    result = models.TextField(blank=True)
    
    def __unicode__(self):
        return '%s with %s' % (self.challenger.user.username, self.challenge_move.name)
        
    def get_absolute_url(self):
        return '/c/%d/' % self.id
        
    def get_challenge_move(self):
        return self.challenge_move.name.replace('X', self.target.user.username)
        
    def get_response_move(self):
        return self.response_move.name.replace('X', self.challenger.user.username)