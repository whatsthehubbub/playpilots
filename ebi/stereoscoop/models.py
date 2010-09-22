from django.db import models
from metagame.models import Player

class StereoscoopCode(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    
    player = models.ForeignKey(Player, related_name='stereoscoopcodes')
    
    code = models.CharField(max_length=255)
    
    def __unicode__(self):
        return '%s' % self.code
        
    def getUnlock(self):
        try:
            return StereoscoopUnlock.objects.filter(code=self.code)[0]
        except:
            pass

class StereoscoopUnlock(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    code = models.CharField(max_length=255)
    
    time = models.DateTimeField()
    
    badge = models.ForeignKey('StereoscoopBadge')
    
    movie1 = models.ForeignKey('StereoscoopMovie', related_name='stereoscoop_unlocks1')
    movie2 = models.ForeignKey('StereoscoopMovie', related_name='stereoscoop_unlocks2')
    
    scene1 = models.IntegerField(blank=True, null=True)
    scene2 = models.IntegerField(blank=True, null=True)
    
    cue1 = models.IntegerField(blank=True, null=True)
    cue2 = models.IntegerField(blank=True, null=True)
    
    def __unicode__(self):
        return self.code
        
    def byUser(self):
        try:
            return StereoscoopCode.objects.filter(code__iexact=self.code.lower())[0].player
        except:
            pass
    

class StereoscoopBadge(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    
    # Are we going to use this? What is the catcher going to receive?
    badgeid = models.IntegerField(blank=True, null=True)
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    
    blurb = models.CharField(max_length=255)
    
    image = models.ImageField(upload_to='stereoscoop_badges', blank=True)
    
    def __unicode__(self):
        return self.title
        
    def isUnlocked(self):
        if bool(self.finds()):
            return True        
        return False
        
    def finds(self):
        # Roughly filter to only return claimed finds
        results = []
        
        for obj in self.stereoscoopunlock_set.all().order_by('time'):
            if StereoscoopCode.objects.filter(code__iexact=obj.code.lower()).exists() > 0:
                results.append(obj)
                
        return results
        
    # def firstFind(self):
    #     try:
    #         return self.stereoscoopunlock_set.all().order_by('time')[0]
    #     except:
    #         pass
    

class StereoscoopMovie(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    title = models.CharField(max_length=255)
    imdb = models.CharField(max_length=255, blank=True)
    
    year = models.IntegerField(blank=True, null=True)
    
    def __unicode__(self):
        return self.title