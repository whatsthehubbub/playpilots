from ebi.kipwip.models import KippenrenCode
from django.contrib import admin

class KippenrenCodeAdmin(admin.ModelAdmin):
    list_display = ('created', 'code', 'player')
admin.site.register(KippenrenCode, KippenrenCodeAdmin)