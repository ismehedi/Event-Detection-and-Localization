import re
def tweetProcessing(text):
    return ('%s' % (text)).encode('utf-8')

def processTweet(tweet):
        tweet = tweet.lower()
        tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet)
        tweet = re.sub('@[^\s]+', '@', tweet)
        tweet = re.sub('[\s]+', ' ', tweet)
        tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
        tweet = tweet.strip('\'"')
        # tweet = tweet.strip('\'"!?,.')
        return tweet

## Need to write down a code to find it
def retweetcount(tweet):
    tweet = len(tweet.split())
    return tweet

def userTextLocation(tweet):
    tweet = tweet.upper()
    return tweet

def rankerkeyword(tweet):
    tweet = tweet.upper()
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet)
    tweet = re.sub('@[^\s]+', '@', tweet)
    tweet = re.sub('[\s]+', ' ', tweet)
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    tweet = tweet.strip('\'"')
    # tweet = tweet.strip('\'"!?,.')
    return tweet