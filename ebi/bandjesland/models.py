from django.db import models
from metagame.models import Player

class BandjeslandSessie(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    
    mp3 = models.FileField(upload_to='bandjesland_sessions', blank=True)

    label = models.CharField(max_length=255)
    
    soundcloudURL = models.URLField(verify_exists=False, blank=True)
    
    specials = models.ManyToManyField('BandjeslandSpecial', through='BandjeslandSpecialOccurrence', related_name='sessions')
    
    def __unicode__(self):
        return self.label
        
    def get_specials_for_session(self):
        return self.specials.all().distinct().order_by('created')
        
    def duration(self):
        return (self.end-self.start).seconds
        
class BandjeslandSpecial(models.Model):
    created = models.DateTimeField()
    
    mp3 = models.FileField(upload_to='bandjesland_specials')
    
    likers = models.ManyToManyField(Player, through='BandjeslandLike')
    
    def __unicode__(self):
        return str(self.created)
        
    def get_like_count(self):
        '''aka heart rate'''
        return BandjeslandLike.objects.filter(special=self).count()
        
    def get_likers(self):
        return Player.objects.filter(bandjeslandlike__special=self)
    
class BandjeslandSpecialOccurrence(models.Model):
    time = models.DateTimeField()
    
    session = models.ForeignKey(BandjeslandSessie)
    special = models.ForeignKey(BandjeslandSpecial)
    
    def __unicode__(self):
        return str(self.time)

class BandjeslandLike(models.Model):
    special = models.ForeignKey(BandjeslandSpecial)
    player = models.ForeignKey(Player)
    
    created = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return str(self.created)