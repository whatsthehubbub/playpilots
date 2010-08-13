from django.db import models
from metagame.models import Player

class KippenrenCode(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    
    code = models.CharField(max_length=255)
    
    player = models.ForeignKey(Player, related_name="kippenrencodes")
    
    
    def __unicode__(self):
        return '%s' % self.code