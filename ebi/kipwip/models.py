from django.db import models
from metagame.models import Player

class KippenrenCode(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    
    code = models.CharField(max_length=255)
    
    player = models.ForeignKey(Player, related_name="kippenrencodes")
    
    
    def __unicode__(self):
        return '%s' % self.code
        
        
class Kippenrace(models.Model):
    raceid = models.IntegerField(blank=True, null=True)
    
    movie_filename = models.CharField(max_length=255, blank=True)
    movie_vimeo_code = models.CharField(max_length=255, blank=True)
    
    def __unicode__(self):
        return '%d' % self.raceid
        
    def get_time_of_day(self):
        timestring = self.movie_filename.split('_')[2].split('.')[0]
        
        return '%s:%s' % (timestring[0:2], timestring[3:5])
        
    def get_riders(self):
        return self.kippenrijder_set.all().order_by('position')


class Kippenrijder(models.Model):
    race = models.ForeignKey(Kippenrace, blank=True, null=True)
    
    name = models.CharField(max_length=255, blank=True)
    
    kipid = models.IntegerField(blank=True, null=True)
    raceid = models.IntegerField(blank=True, null=True)
    
    position = models.IntegerField(blank=True, null=True)
    
    code = models.CharField(max_length=255, blank=True)
    
    time = models.IntegerField(blank=True, null=True)
    
    def __unicode__(self):
        return '%s' % self.name
        
    def get_time(self):
        if self.time:
            return '%s:%s' % (str(self.time)[0], str(self.time)[1:])
        else:
            return '5:00'
            
    def get_player(self):
        pass
        
    def get_color_class(self):
        if self.kipid == 1:
            return 'blue'
        elif self.kipid == 2:
            return 'purple'
        elif self.kipid == 3:
            return 'orange'