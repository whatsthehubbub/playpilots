from django.db import models
from django.db.models import F, Q
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save

from django.conf import settings
from socialregistration.models import TwitterProfile

import datetime, os

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
    
    # TODO maybe turn this into a foreign key again
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

    # maybe turn this into a foreign key again
    photos = models.ManyToManyField(Photo, blank=True)
    logo = models.ImageField(upload_to='festival_logos', blank=True)
    
    location = models.CharField(max_length=255, help_text="A geo-codable address", blank=True)

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
        return '/games/%s/' % self.slug
        
    def get_first_photo(self):
        if self.photos.all():
            return self.photos.all()[0].photo.url
        else:
            return ''
            
    def get_days_till(self):
        delta = self.start - datetime.datetime.now()
        
        if delta.days > 0:
            return delta.days
        else:
            return 0
        
    def get_hours_till(self):
        delta = self.start - datetime.datetime.now()
        
        if delta.seconds > 0:
            return delta.seconds / 60 / 60
        else:
            return 0


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
    
    rating = models.IntegerField(blank=True, null=True, default=0)
    
    def get_display_name(self):
        if self.twitter_name:
            return self.twitter_name
        else:
            return self.user.username
            
    def get_avatar_url(self):
        try:
            t = TwitterProfile.objects.get(user=self.user)
            
            return t.avatar
        except TwitterProfile.DoesNotExist:
            pass
            
        return os.path.join(settings.MEDIA_URL, 'image/tag_jij.png')
    
    def get_rank(self):
        players = Player.objects.all().order_by('-rating')
        
        # TODO this won't scale, but for now it works
        # Swap in later for http://www.artfulsoftware.com/infotree/queries.php?&bw=1024#460
        rank = 1
        for player in players:
            if player == self:
                return rank
            rank += 1
    
    def get_challenger_duels(self):
        return self.challenger_duel.all().filter(open=True).order_by('created')
        
    def get_responder_duels(self):
        return self.responder_duel.all().filter(open=True).order_by('created')
        
    def get_finished_duels(self):
        from battleroyale.models import Duel
        return Duel.objects.all().filter(open=False).filter(Q(challenger=self) | Q(target=self)).order_by('-created')
        
    def get_skills(self):
        from battleroyale.models import Skill, Style
        
        styles = Style.objects.all()
        
        for style in styles:
            # Create all the skills for this player
            try:
                s = Skill.objects.get(player=self, style=style)
            except Skill.DoesNotExist:
                s = Skill.objects.create(player=self, style=style)
                
        skills = Skill.objects.filter(player=self).order_by('style__name')
        
        return skills
        
    def get_win_count(self):
        return self.challenger_duel.filter(challenge_awesomeness__gt=F('response_awesomeness')).count() + self.responder_duel.filter(response_awesomeness__gt=F('challenge_awesomeness')).count()
        
    def get_loss_count(self):
        return self.challenger_duel.filter(challenge_awesomeness__lt=F('response_awesomeness')).count() + self.responder_duel.filter(response_awesomeness__lt=F('challenge_awesomeness')).count()
    
    def get_tie_count(self):
        return self.challenger_duel.filter(challenge_awesomeness=F('response_awesomeness')).count() + self.responder_duel.filter(response_awesomeness=F('challenge_awesomeness')).count()
    
    def __unicode__(self):
        return self.user.username
        
    def get_absolute_url(self):
        return '/players/%d/' % self.user.id