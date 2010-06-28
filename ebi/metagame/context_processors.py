# from haiti.models import Blog, NewsItem
# from django.contrib.sites.models import Site
# import datetime
# 
# from django.core.cache import cache
# 
# from services import get_tweets
# 
# # Processor to add variables that need to be visible on every template render (for the base template)
# 
# def base(request):    
#     # This already is cached by Django.
#     site = Site.objects.get_current()
#     
#     # Cache all this stuff aggressively
#     CACHE_DURATION = 60*15
#     
#     context_blogs = cache.get('context_blogs')
#     if not context_blogs:
#         context_blogs = Blog.objects.all().exclude(slug='pers').exclude(slug='nieuws')[:2]
#         cache.set('context_blogs', context_blogs, CACHE_DURATION)
#     
#     # tweets are already cached in services
#     
#     context_lastnews = cache.get('context_lastnews')
#     if not context_lastnews:
#         try:
#             blog = Blog.objects.get(slug='nieuws')
#             context_lastnews = blog.newsitems.order_by('-datecreated')[:3]
#         except Blog.DoesNotExist:
#             context_lastnews = NewsItem.objects.all().filter(content_type__name='project').order_by('-datecreated')[:3]
#         cache.set('context_lastnews', context_lastnews, CACHE_DURATION)
#     
#     context_featured = cache.get('context_featured')
#     if not context_featured:
#         context_featured = NewsItem.objects.filter(featureduntil__gt=datetime.datetime.now()).order_by('-datecreated')[:3]
#         cache.set('context_featured', context_featured, 60*10)
#     
#     tweets = cache.get('tweets')
#     if not tweets:
#         tweets = get_tweets()[:3]
#         cache.set('tweets', tweets, CACHE_DURATION)
# 
#     return {
#         'SITE_DOMAIN': 'http://' + site.domain,
#         'bottomblogs': context_blogs,
#         'tweets': tweets,
#         'show_update': True,
#         'lastnews': context_lastnews,
#         'featured': context_featured
#     }