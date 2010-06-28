from ebi.metagame.models import Maker, Festival, Game, Player
from django.contrib import admin


class MakerAdmin(admin.ModelAdmin):
    pass
admin.site.register(Maker, MakerAdmin)


class FestivalAdmin(admin.ModelAdmin):
    pass
admin.site.register(Festival, FestivalAdmin)


class GameAdmin(admin.ModelAdmin):
    pass
admin.site.register(Game, GameAdmin)


class PlayerAdmin(admin.ModelAdmin):
    pass
admin.site.register(Player, PlayerAdmin)
