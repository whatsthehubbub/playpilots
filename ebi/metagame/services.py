import feedparser

from ebi import twitter
import logging
import urllib2

def get_feed(url):
    if url:
        feed = urllib2.urlopen(url, timeout=2)
        content = feed.read()
        return feedparser.parse(content)

def feed_first_entry(url):
    try:
        return feed_entries(url)[0]
    except:
        pass

    return {}
    
def feed_entries(url):
    feed = get_feed(url)

    if len(feed['entries']) > 0:
        return feed['entries']

    return []
    
def send_tweet(msg):
    api = twitter.Api(username='playpilots', password='boarding45paris')
    
    try:
        status = api.PostUpdate(msg)
        logging.info('sent tweet %d', status.id)
    except:
        logging.error('sending tweet %s failed', msg)
