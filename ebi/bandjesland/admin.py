from ebi.bandjesland.models import *
from django.contrib import admin

class BandjeslandSessieAdmin(admin.ModelAdmin):
    list_display = ('start', 'end', 'mp3', 'label', 'soundcloudURL', )
admin.site.register(BandjeslandSessie, BandjeslandSessieAdmin)

class BandjeslandSpecialAdmin(admin.ModelAdmin):
    list_display = ('created', 'mp3', )
admin.site.register(BandjeslandSpecial, BandjeslandSpecialAdmin)

class BandjeslandSpecialOccurrenceAdmin(admin.ModelAdmin):
    list_display = ('time', 'session', 'special', )
admin.site.register(BandjeslandSpecialOccurrence, BandjeslandSpecialOccurrenceAdmin)

class BandjeslandLikeAdmin(admin.ModelAdmin):
    list_display = ('special', 'player', 'created')
admin.site.register(BandjeslandLike, BandjeslandLikeAdmin)