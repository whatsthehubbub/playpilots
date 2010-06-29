import feedparser

from django.core.cache import cache

#TODO add caching and stuff here

def feed_first_entry(url):
    blogparsed = cache.get('blogparsed')
    
    if not blogparsed:    
        try:
            blogparsed = feedparser.parse(url)
            cache.set('blogparsed', blogparsed, 60*60)
        except:
            return {} # TODO log error
    
    if len(blogparsed['entries']) > 0:
        return blogparsed['entries'][0]
    
    return {}