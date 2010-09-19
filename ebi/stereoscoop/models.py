from django.db import models
from metagame.models import Player

class StereoscoopCodes(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    
    player = models.ForeignKey(Player, related_name='stereoscoopcodes')
    
    code = models.CharField(max_length=255)
    
    def __unicode__(self):
        return '%s' % self.code

class StereoscoopUnlocks(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    code = models.CharField(max_length=255)
    
    time = models.DateTimeField()
    
    badge = models.ForeignKey(StereoscoopBadge)
    
    movie1 = models.CharField(max_length=255)
    movie2 = models.CharField(max_length=255)
    
    scene1 = models.IntegerField(blank=True, null=True)
    scene2 = models.IntegerField(blank=True, null=True)
    
    cue1 = models.IntegerField(blank=True, null=True)
    cue2 = models.IntegerField(blank=True, null=True)
    

class StereoscoopBadge(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    
    # Are we going to use this? What is the catcher going to receive?
    badgeid = models.IntegerField(blank=True, null=True)
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    
    blurb = models.CharField(max_length=255)
    
    image = models.ImageField(upload_to='stereoscoop_badges', blank=True)