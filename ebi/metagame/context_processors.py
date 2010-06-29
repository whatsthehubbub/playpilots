from django.core.cache import cache
from django.contrib.sites.models import Site

from services import feed_first_entry

def base(request):    
    # This already is cached by Django.
    site = Site.objects.get_current()
    
    # Cache all this stuff aggressively
    CACHE_DURATION = 60*15

    blogentry = cache.get('blogentry')
    if not blogentry:
        blogentry = feed_first_entry('http://ebi.posterous.com/rss.xml')
        cache.set('blogentry', blogentry, CACHE_DURATION)

    return {
        'SITE_DOMAIN': 'http://' + site.domain,
        'blogentry': blogentry
    }