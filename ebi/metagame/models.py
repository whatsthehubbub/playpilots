#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
from django.db import models
from django.db.models import F, Q
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_save

from django.conf import settings
from socialregistration.models import TwitterProfile

from django.core.cache import cache
from django.core.mail import send_mail
import datetime, os, smtplib

from metagame.services import send_tweet
import logging

import actstream

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
            p = Player.objects.create(user=instance)
            
            actstream.action.send(p, verb='heeft net ingecheckt voor PLAY Pilots!')
            
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
            # username is filled in with your twittername
            return self.user.username
            
    def get_twitter_name(self):
        twittername = cache.get('player_%d_twittername' % self.id)
        if not twittername:
            try:
                t = TwitterProfile.objects.get(user=self.user)
                twittername = t.username
                cache.set('player_%d_twittername' % self.id, twittername, 60*60)
            except TwitterProfile.DoesNotExist:
                pass
            
        if twittername:
            return twittername
        else:
            return ''
            
    def get_avatar_url(self):
        try:
            t = TwitterProfile.objects.get(user=self.user)
            
            if t.avatar:
                return t.avatar
        except TwitterProfile.DoesNotExist:
            pass
            
        return os.path.join(settings.MEDIA_URL, 'image/buddy-icon-login-box.png')
    
    def send_challenge_message(self, duel):
        url = 'http://playpilots.nl/c/%d/' % duel.id
        
        if self.user.email:
            try:
                send_mail('Je bent uitgedaagd door %s' % duel.challenger.get_display_name(),
                '''Hoi %(target)s,

Je bent uitgedaagd voor een duel door %(challenger)s.

Ga naar %(url)s om te duelleren!

Namens PLAY Pilots,

Uw gezagvoerder''' % {'target': self.get_display_name(), 
                        'challenger': duel.challenger.get_display_name(), 
                        'url': url}, 
                'Your Captain Speaking <captain@playpilots.nl>', 
                [self.user.email])
            except smtplib.SMTPException:
                logging.error('sending target e-mail failed')
            logging.info('sent challenge e-mail to %s', self.user.username)
        elif self.get_twitter_name():
            logging.info('trying to send challenge tweet')
            
            challenger_name = duel.challenger.get_twitter_name() or duel.challenger.get_display_name()
            
            modifiers = {
                1: ' zwak',
                2: ' matig',
                3: '',
                4: ' goed',
                5: ' hard'
            }
            modifier = modifiers[duel.challenge_awesomeness]
            
            messageParts = [
                u'@%(target)s' % {'target': self.get_twitter_name()}
            ]
            
            if duel.challenge_message:
                message = duel.challenge_message
                if len(message) > 25:
                    message = duel.challenge_message[:25] + u'…'
                    
                messageParts.append(u'“%(style)s” @%(challenger)s daagt je%(modifier)s uit en zegt: %(message)s' % {'style': duel.challenge_move.style.name, 'challenger': challenger_name, 'message': message, 'modifier': modifier})
            else:
                messageParts.append(u'Je bent%(modifier)s uitgedaagd door “%(style)s” @%(challenger)s.' % {'style': duel.challenge_move.style.name, 'challenger': challenger_name, 'modifier': modifier})
                
            messageParts.append(u'Doe iets terug op: %(url)s' % {'url': url})
            
            send_tweet(' '.join(messageParts))
            
    def send_win_message(self, duel):
        logging.info('sending win message to %s', self.get_display_name())
        url = 'http://playpilots.nl/c/%d/' % duel.id
        
        if self.user.email:
            try:
                send_mail('Gefeliciteerd! Je hebt gewonnen van %s!' % duel.get_loser().get_display_name(), 
                '''Hoi %(winner)s,

Gefeliciteerd! Je hebt het duel met %(loser)s gewonnen.

Ga naar %(url)s om de uitkomst te zien!

Namens PLAY Pilots,

Uw gezagvoerder''' % {
                'winner': duel.get_winner().get_display_name(),
                'loser': duel.get_loser().get_display_name(),
                'url':  url
                },
                'Your Captain Speaking <captain@playpilots.nl>', 
                [self.user.email])
            except smtplib.SMTPException:
                logging.error('sending win e-mail to user %s failed' % self.get_display_name())
        elif self.get_twitter_name():
            logging.info('trying to send twitter win message to @%s', self.get_twitter_name())
            loser_name = duel.get_loser().get_twitter_name() or duel.get_loser().get_display_name()
            
            # TODO add twitter '@' for the other
            message = u'@%(winner)s, je bent de baas! Je hebt als “%(style)s” gewonnen van @%(loser)s. Ga naar %(url)s om het resultaat te zien.' % {
                'winner': self.get_twitter_name(),
                'style': duel.get_winner_style().name,
                'loser': loser_name,
                'url': url
            }

            send_tweet(message)
        
    def send_lose_message(self, duel):
        logging.info('sending lose message to %s', self.get_display_name())
        
        url = 'http://playpilots.nl/c/%d/' % duel.id
        
        if self.user.email:
            try:
                send_mail('Helaas! Je hebt verloren van %s!' % self.get_display_name(), 
                '''Hoi %(loser)s,

Helaas! Je hebt het duel met %(winner)s verloren.

Ga naar %(url)s om de uitkomst te zien!

Namens PLAY Pilots,

Uw gezagvoerder''' % {
                'winner': duel.get_winner().get_display_name(),
                'loser': duel.get_loser().get_display_name(),
                'url':  url
                },
                'Your Captain Speaking <captain@playpilots.nl>', 
                [self.user.email])
            except smtplib.SMTPException:
                logging.error('sending lose e-mail to user %s failed' % self.get_display_name())
        elif self.get_twitter_name():
            logging.info('trying to send twitter lose message to @%s', self.get_twitter_name())
            
            winner_name = duel.get_winner().get_twitter_name() or duel.get_winner().get_display_name()
            
            message = u'@%(loser)s jammer! Je hebt verloren van “%(style)s” @%(winner)s. Ga naar %(url)s om het resultaat te zien.' % {
                'loser': self.get_twitter_name(),
                'style': duel.get_winner_style().name,
                'winner': winner_name,
                'url': url
            }

            send_tweet(message)
    
    def get_rank(self, fresh=False):
        # TODO implement fresh method, so we can get accurate ratings whenever we want 'em
        rank = cache.get('player_%d_rank' % self.id)
        if not rank:        
            players = Player.objects.all().order_by('-rating')
        
            # TODO this won't scale, but for now it works
            # Swap in later for http://www.artfulsoftware.com/infotree/queries.php?&bw=1024#460
            rank = 1
            for player in players:
                if player == self:
                    break
                rank += 1
                
            cache.set('player_%d_rank' % self.id, rank, 60*5)
        return rank

    def get_win_count(self):
        count = cache.get('player_%d_wincount' % self.id)
        
        if not count:
            count = self.challenger_duel.filter(challenge_awesomeness__gt=F('response_awesomeness')).count() + self.responder_duel.filter(response_awesomeness__gt=F('challenge_awesomeness')).count()
            cache.set('player_%d_wincount' % self.id, count, 60*15)
            
        return count

    def get_loss_count(self):
        count = cache.get('player_%d_losscount' % self.id)
        
        if not count:
            count = self.challenger_duel.filter(challenge_awesomeness__lt=F('response_awesomeness')).count() + self.responder_duel.filter(response_awesomeness__lt=F('challenge_awesomeness')).count()
            cache.set('player_%d_losscount' % self.id, count, 60*15)
            
        return count

    def get_tie_count(self):
        count = cache.get('player_%d_tiecount' % self.id)
        
        if not count:
            count = self.challenger_duel.filter(challenge_awesomeness=F('response_awesomeness')).count() + self.responder_duel.filter(response_awesomeness=F('challenge_awesomeness')).count()
            cache.set('player_%d_tiecount' % self.id, count, 60*15)
            
        return count
        
    def invalidate_winlosstie_counts(self):
        cache.set('player_%d_wincount' % self.id, None, 5)
        cache.set('player_%d_losscount' % self.id, None, 5)
        cache.set('player_%d_tiecount' % self.id, None, 5)

    def get_challenger_duels(self):
        return self.challenger_duel.all().filter(open=True).order_by('-created')
        
    def get_responder_duels(self):
        return self.responder_duel.all().filter(open=True).order_by('-created')
        
    def get_finished_duels(self):
        from battleroyale.models import Duel
        return Duel.objects.all().filter(open=False).filter(Q(challenger=self) | Q(target=self)).order_by('-responded')
        
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
    
    def __unicode__(self):
        return self.user.username
        
    def get_absolute_url(self):
        return '/players/%d/' % self.user.id