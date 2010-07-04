from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import pre_save


class Maker(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    
    description = models.TextField(blank=True)
    
    link = models.URLField(verify_exists=False, blank=True)
    updatesFeed = models.URLField(verify_exists=False, blank=True)
    
    photo = models.ImageField(upload_to='maker_photos', blank=True)
    logo = models.ImageField(upload_to='maker_logos', blank=True)
    
    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return '/maker/%s' % self.slug
        
    def first_game(self):
        if self.games.all():
            return self.games.all()[0]
        else:
            return None
    

class Festival(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=255)
    slug = models.SlugField()

    description = models.TextField(blank=True)
    
    link = models.URLField(verify_exists=False, blank=True)
    
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)

    # Probably want to attach more than one photo ? TODO
    photo = models.ImageField(upload_to='festival_photos', blank=True)
    logo = models.ImageField(upload_to='festival_logos', blank=True)

    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return '/maker/%s' % self.slug
        
    def first_game(self):
        if self.games.all():
            return self.games.all()[0]
        else:
            return None
    

class Game(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=255)
    slug = models.SlugField()
    
    description = models.TextField(blank=True)
    
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    
    # Probably want to attach more than one photo ? TODO
    photo = models.ImageField(upload_to='game_photos', blank=True)
    logo = models.ImageField(upload_to='game_logos', blank=True)
    
    maker = models.ForeignKey('Maker', related_name='games', blank=True, null=True)

    festival = models.ForeignKey('Festival', related_name='games', blank=True, null=True)
    
    players = models.ManyToManyField('Player', related_name='games_played', blank=True)
    interested = models.ManyToManyField('Player', related_name='games_interested', blank=True)

    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return '/maker/%s' % self.slug


class Player(models.Model):
    # Player profile class
    user = models.ForeignKey(User, unique=True)
    
    # TODO rename to twitter_name
    twitterName = models.CharField(max_length=255, blank=True)
    
    def __unicode__(self):
        return self.user.username
        
    def get_absolute_url(self):
        return '/players/%d/' % self.user.id