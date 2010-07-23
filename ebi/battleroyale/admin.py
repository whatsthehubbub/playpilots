from ebi.battleroyale.models import *
from django.contrib import admin

class StyleAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(Style, StyleAdmin)

class MoveAdmin(admin.ModelAdmin):
    list_display = ('style', 'name')
admin.site.register(Move, MoveAdmin)

class SkillAdmin(admin.ModelAdmin):
    list_display = ('player', 'style', 'level', 'experience')
admin.site.register(Skill, SkillAdmin)

class ActionPhraseAdmin(admin.ModelAdmin):
    list_display = ('style', 'phrase', 'action')
admin.site.register(ActionPhrase, ActionPhraseAdmin)

class WinPhraseAdmin(admin.ModelAdmin):
    list_display = ('style', 'phrase')
admin.site.register(WinPhrase, WinPhraseAdmin)

class DuelAdmin(admin.ModelAdmin):
    list_display = ('created', 
                    'open', 
                    'challenger', 
                    'challenge_move', 
                    'challenge_awesomeness', 
                    'target', 
                    'responded', 
                    'response_move',
                    'response_awesomeness')
admin.site.register(Duel, DuelAdmin)