from ebi.metagame.models import Maker, Festival, Game, Player, Photo

# from ebi.metagame.models import Culture, Move, SpecificWinPhrase, Round

from django.contrib import admin


class PhotoAdmin(admin.ModelAdmin):
    pass
admin.site.register(Photo, PhotoAdmin)

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