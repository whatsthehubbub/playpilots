from django.db import models
from metagame.models import Player

class BandjeslandSessie(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    
    mp3 = models.FileField(upload_to='bandjesland_sessions')

    label = models.CharField(max_length=255)
    
    soundcloudURL = models.URLField(verify_exists=False, blank=True)
    
    specials = models.ManyToManyField('BandjeslandSpecial', through='BandjeslandSpecialOccurrence', related_name='sessions')
    
    def __unicode__(self):
        return self.label
        
class BandjeslandSpecial(models.Model):
    created = models.DateTimeField()
    
    mp3 = models.FileField(upload_to='bandjesland_specials')
    
    likers = models.ManyToManyField(Player, through='BandjeslandLike')
    
    def __unicode__(self):
        return str(self.created)
    
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