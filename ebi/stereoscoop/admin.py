from ebi.stereoscoop.models import StereoscoopUnlock, StereoscoopCode, StereoscoopBadge, StereoscoopMovie
from django.contrib import admin

class StereoscoopUnlockAdmin(admin.ModelAdmin):
    pass # list_display = ('created', 'code', 'player')
admin.site.register(StereoscoopUnlock, StereoscoopUnlockAdmin)

class StereoscoopCodeAdmin(admin.ModelAdmin):
    pass # list_display = ('raceid', 'movie_filename', 'movie_vimeo_code')
admin.site.register(StereoscoopCode, StereoscoopCodeAdmin)

class StereoscoopBadgeAdmin(admin.ModelAdmin):
    pass # list_display = ('race', 'name', 'kipid', 'raceid', 'position', 'code', 'time')
    prepopulated_fields = {"slug": ("title",)}
admin.site.register(StereoscoopBadge, StereoscoopBadgeAdmin)

class StereoscoopMovieAdmin(admin.ModelAdmin):
    pass # list_display = ('race', 'name', 'kipid', 'raceid', 'position', 'code', 'time')
admin.site.register(StereoscoopMovie, StereoscoopMovieAdmin)