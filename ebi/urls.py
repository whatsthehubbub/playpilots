from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

import socialregistration.urls


urlpatterns = patterns('',
    # Example:
    # (r'^shohaiti/', include('shohaiti.haiti.urls')),

    (r'^admin/', include(admin.site.urls)),
)

# Include socialregistration url patterns
urlpatterns += socialregistration.urls.urlpatterns


urlpatterns += patterns('ebi.metagame.views',
    (r'^$', 'index'),
	
	(r'^users/(?P<username>\S+?)/$', 'user_detail'),
	(r'^players/(?P<id>\d+)/$', 'player_detail'),
	(r'^players/(?P<username>\S+?)/$', 'user_detail'),
	
	(r'^games/(?P<slug>\S+?)/interested/$', 'game_interest'),
	(r'^games/(?P<slug>\S+?)/$', 'game_detail'),
	(r'^games/$', 'game_list'),
	
	(r'^register/$', 'register'),
	(r'^logout/$', 'logout_view')
)

urlpatterns += patterns('django.views.generic.simple',
    (r'^players/$', 'redirect_to', {'url': '/klassement/'}),
)

urlpatterns += patterns('ebi.battleroyale.views',
    (r'^klassement/$', 'klassement'),

    (r'^challenge/$', 'challenge'),
    (r'^challenge/create/$', 'challenge_create'),
	(r'^challenge/resolve/$', 'challenge_resolve'),
	(r'^challenge/(?P<id>\d+)/$', 'challenge_detail'),
	(r'^c/(?P<id>\d+)/$', 'challenge_detail_redirect'),
)


urlpatterns += patterns('',
    (r'^secretlogin/$', 'django.contrib.auth.views.login')
)

# TODO configure static file serving for deployment server
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/alper/Documents/projects/play/site/media'})
    )