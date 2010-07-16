from ebi.metagame.models import Maker, Festival, Game, Player, Culture, Move, SpecificWinPhrase, Round
from django.contrib import admin


class MakerAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
admin.site.register(Maker, MakerAdmin)


class FestivalAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
admin.site.register(Festival, FestivalAdmin)


class GameAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
admin.site.register(Game, GameAdmin)


class PlayerAdmin(admin.ModelAdmin):
    pass
admin.site.register(Player, PlayerAdmin)


class CultureAdmin(admin.ModelAdmin):
    list_display = ('name', 'win_phrase')
admin.site.register(Culture, CultureAdmin)


class MoveAdmin(admin.ModelAdmin):
    list_display = ('culture', 'name')
admin.site.register(Move, MoveAdmin)


class SpecificWinPhraseAdmin(admin.ModelAdmin):
    pass
admin.site.register(SpecificWinPhrase, SpecificWinPhraseAdmin)


class RoundAdmin(admin.ModelAdmin):
    list_display = ('created', 'open', 'challenger', 'challenge_move', 'target', 'responded', 'response_move')
admin.site.register(Round, RoundAdmin)