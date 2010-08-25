from ebi.kipwip.models import KippenrenCode, Kippenrace, Kippenrijder
from django.contrib import admin

class KippenrenCodeAdmin(admin.ModelAdmin):
    list_display = ('created', 'code', 'player')
admin.site.register(KippenrenCode, KippenrenCodeAdmin)

class KippenraceAdmin(admin.ModelAdmin):
    list_display = ('raceid', 'movie_filename', 'movie_vimeo_code')
admin.site.register(Kippenrace, KippenraceAdmin)

class KippenrijderAdmin(admin.ModelAdmin):
    list_display = ('race', 'name', 'kipid', 'raceid', 'position', 'code', 'time')
admin.site.register(Kippenrijder, KippenrijderAdmin)