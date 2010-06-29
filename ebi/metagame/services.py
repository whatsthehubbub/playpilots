import feedparser

def feed_first_entry(url):
    blogparsed = feedparser.parse(url)
    
    if len(blogparsed['entries']) > 0:
        return blogparsed['entries'][0]
    
    return {}