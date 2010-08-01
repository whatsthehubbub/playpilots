import feedparser

def feed_first_entry(url):
    blogparsed = feedparser.parse(url)
    
    if len(blogparsed['entries']) > 0:
        return blogparsed['entries'][0]
    
    return {}
    
def feed_entries(url):
    parsed = feedparser.parse(url)
    
    if len(parsed['entries']) > 0:
        return parsed['entries']
    
    return {}