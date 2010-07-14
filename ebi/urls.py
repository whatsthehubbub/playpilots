from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Example:
    # (r'^shohaiti/', include('shohaiti.haiti.urls')),

    (r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('ebi.metagame.views',
    (r'^$', 'index'),
	
	(r'^players/$', 'player_list'),
	(r'^players/(?P<id>\d+)/$', 'player_detail'),
	(r'^players/(?P<username>\S+?)/$', 'user_detail'),
	
	(r'^games/(?P<slug>\S+?)/$', 'game_detail'),
	(r'^games/$', 'game_list'),
	
	(r'^makers/(?P<slug>\S+?)/$', 'maker_detail'),
	(r'^makers/$', 'maker_list'),
	
	(r'^festivals/(?P<slug>\S+?)/$', 'festival_detail'),
	(r'^festivals/$', 'festival_list'),
	
	(r'^register/$', 'register'),
	(r'^logout/$', 'logout_view'),
	
	(r'^challenge/$', 'challenge'),
	(r'^challenge/resolve/$', 'challenge_resolve'),
	(r'^challenge/(?P<id>\d+)/$', 'challenge_detail'),
	(r'^c/(?P<id>\d+)/$', 'challenge_detail'),
)


urlpatterns += patterns('',
    (r'^login/$', 'django.contrib.auth.views.login')
)

# TODO configure static file serving for deployment server
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/alper/Documents/projects/play/site/media'})
    )