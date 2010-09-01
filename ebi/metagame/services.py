import feedparser

from ebi import oauthtwitter
import logging
import urllib2

from django.conf import settings

def get_feed(url):
    if url:
        try:
            feed = urllib2.urlopen(url, timeout=2)
            content = feed.read()
        except:
            content = ''
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
    api = oauthtwitter.OAuthApi('E0iCfzFo5Xzx64kYGvIa8w', 'yHKc2oOpxg73isTyVPNPpN5UMdm6vGUwUxfeSTJY', token='163033853-fZLBb7czDySTztYtEC2ig5Rn4HVmpWmCZFzDdGix', token_secret='DmLKAPqZBihdELE9Z2OqGsWlGPZWj5PmD5dKDbrOI')
    
    try:
        status = api.UpdateStatus(msg.encode('utf-8'))
        logging.info('sent tweet %s', str(status))
    except:
        logging.error('sending tweet %s failed', msg)

    return status