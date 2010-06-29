from ebi.metagame.models import Maker, Festival, Game, Player
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
