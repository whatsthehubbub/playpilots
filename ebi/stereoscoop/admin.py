from ebi.stereoscoop.models import StereoscoopUnlock, StereoscoopCode, StereoscoopBadge, StereoscoopMovie
from django.contrib import admin

class StereoscoopUnlockAdmin(admin.ModelAdmin):
    list_display = ('code', 'time', 'badge', 'movie1', 'movie2')
admin.site.register(StereoscoopUnlock, StereoscoopUnlockAdmin)

class StereoscoopCodeAdmin(admin.ModelAdmin):
    list_display = ('player', 'code')
admin.site.register(StereoscoopCode, StereoscoopCodeAdmin)

class StereoscoopBadgeAdmin(admin.ModelAdmin):
    list_display = ('badgeid', 'title', 'slug', 'blurb', 'image')
    prepopulated_fields = {"slug": ("title",)}
admin.site.register(StereoscoopBadge, StereoscoopBadgeAdmin)

class StereoscoopMovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'imdb', 'year')
admin.site.register(StereoscoopMovie, StereoscoopMovieAdmin)
