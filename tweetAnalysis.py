import json
import pandas as pd
import matplotlib.pyplot as plt
import re
from nltk.tokenize import TweetTokenizer


tweetTokenizer = TweetTokenizer()
#Tracker = ['Earthquake', 'shaking']
tracker = ['URL']

def processTweet(tweet):
        tweet = tweet.lower()
        tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet)
        tweet = re.sub('@[^\s]+', '@', tweet)
        tweet = re.sub('[\s]+', ' ', tweet)
        tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
        tweet = tweet.strip('\'"')
        # tweet = tweet.strip('\'"!?,.')
        return tweet


print('Reading Tweets\n');
tweets_data_path = 'testflask.txt';
tweets_data = []
tweets_file = open(tweets_data_path, "r");
for line in tweets_file:
    try:
        data = json.loads(line)
        tweets_data.append(data)
        tweet = data['text']
        #print tweet
        protweet = processTweet(tweet)
        print protweet
        tokens = set(tweetTokenizer.tokenize(protweet))
        #print tokens
        if len(tokens & set(tracker)) > 0:
            print "Got a Tweet related to Earthquake.!"
    except:
        continue

