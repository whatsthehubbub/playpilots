import feedparser

from ebi import twitter
import logging

def feed_first_entry(url):
    blogparsed = feedparser.parse(url)
    
    if len(blogparsed['entries']) > 0:
        return blogparsed['entries'][0]
    
    return {}
    
def feed_entries(url):
    if url:
        parsed = feedparser.parse(url)
    
        if len(parsed['entries']) > 0:
            return parsed['entries']
    
    return []
    
def send_tweet(msg):
    api = twitter.Api(username='playpilots', password='boarding45paris')
    
    try:
        status = api.PostUpdate(msg)
    except:
        logging.error('sending tweet %s failed', msg)
    
    logging.info('sent tweet %d', status.id)
    