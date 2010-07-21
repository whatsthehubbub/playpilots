from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import pre_save, post_save


class Photo(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    
    photo = models.ImageField(upload_to='game_photos', blank=True)
    

class Maker(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    
    description = models.TextField(blank=True)
    
    link = models.URLField(verify_exists=False, blank=True)
    updatesFeed = models.URLField(verify_exists=False, blank=True)
    
    photos = models.ManyToManyField(Photo, blank=True)
    logo = models.ImageField(upload_to='maker_logos', blank=True)
    
    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return '/makers/%s' % self.slug
        
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
    photos = models.ManyToManyField(Photo, blank=True)
    logo = models.ImageField(upload_to='festival_logos', blank=True)
    
    location = models.CharField(max_length=255, help_text="A geo-codable address")

    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return '/festivals/%s' % self.slug
        
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
    
    photos = models.ManyToManyField(Photo, blank=True)
    logo = models.ImageField(upload_to='game_logos', blank=True)
    
    maker = models.ForeignKey('Maker', related_name='games', blank=True, null=True)

    festival = models.ForeignKey('Festival', related_name='games', blank=True, null=True)
    
    interested = models.ManyToManyField('Player', blank=True)

    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return '/games/%s' % self.slug



# Creates player instances whenever you create a user
def user_post_save_callback(sender, instance, created, **kwargs):
    if created:
        try:
            Player.objects.get(user=instance)
        except Player.DoesNotExist:
            Player.objects.create(user=instance)
post_save.connect(user_post_save_callback, sender=User)


class Player(models.Model):
    # Player profile class
    user = models.ForeignKey(User, unique=True)
    
    twitter_name = models.CharField(max_length=255, blank=True)
    
    avatar = models.ImageField(upload_to="player_avatars", blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    
    rating = models.IntegerField(blank=True, null=True, default=100)
    # culture = models.ForeignKey('Culture', null=True, blank=True)
    
    # game_set.all()
    
    def __unicode__(self):
        return self.user.username
        
    def get_absolute_url(self):
        return '/players/%d/' % self.user.id
        
        
# GAME BASED MODELS

'''
class Culture(models.Model):
    name = models.CharField(max_length=255, blank=True)
    
    description = models.TextField(blank=True)
    
    image = models.ImageField(upload_to="culture_images", blank=True)
    
    win_phrase = models.CharField(max_length=255, blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.name
    
    
class Move(models.Model):
    culture = models.ForeignKey(Culture)
    
    name = models.CharField(max_length=255, blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return self.name
    
    
class SpecificWinPhrase(models.Model):
    winner = models.ForeignKey(Culture, related_name="winnerphrase")
    loser = models.ForeignKey(Culture, related_name="loserphrase")
    
    phrase = models.CharField(max_length=255, blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __unicode__(self):
        return '%s x %s -> %s' % (self.winner.name, self.loser.name, self.phrase)
        
    
class Round(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    challenger = models.ForeignKey(Player, related_name='challenged_round')
    challenge_move = models.ForeignKey(Move, related_name='challenged_move')
    challenge_message = models.CharField(max_length=255, blank=True)
    
    # If this move is still open
    open = models.BooleanField(default=True)
    
    target = models.ForeignKey(Player, blank=True, null=True, related_name='targeted_round')
    target_text = models.CharField(max_length=255, blank=True)
    
    responded = models.DateTimeField(blank=True, null=True)
    response_move = models.ForeignKey(Move, blank=True, null=True, related_name='responded_move')
    response_message = models.CharField(max_length=255, blank=True)
    
    # TODO add winner loser, old rating, new rating
    
    def __unicode__(self):
        return '%s with %s' % (self.challenger.user.username, self.challenge_move.name)
        
'''