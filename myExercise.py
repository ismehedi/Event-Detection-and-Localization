from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import time
import json
from nltk.tokenize import TweetTokenizer

tweetTokenizer = TweetTokenizer()
#Tracker = ['Earthquake', 'shaking']
tracker = ['trump','Brexit','Europian Union','Nato','Climate','Paris']
ckey="1MfhNUc61eAX63bIuAnc9JLE5"
csecret="gvKJ5i8meMfCOM6nQuscUuZtxELmZLwKuPVi80H4Tiq3MS10yI"
atoken="3720728952-zBkjKHV6EIzOtbnuZz4M4kpUuf0rLe9lBCjtdqG"
asecret="q5lqi72PFLZU6YALPXk5tFfB3p8maXabeEe1hbkTmfPZE"

class listener(StreamListener):

    def on_data(self, data):
        try:
            #print(data)
            tweet = json.loads(data)
            #print tweet['created_at']
            text = tweet['text'].lower()
            #print text
            tokens = set(tweetTokenizer.tokenize(text))
            if len(tokens & set(tracker)) > 0:
                print "Got a Tweet related!"
                saveFile = open('Germany_all.txt', 'a')
                saveFile.write(data)
                saveFile.write('\n')
                saveFile.close()
                return (True)

        except Exception as e:
            print ("Failed on data",str(e))
            time.sleep(5)

    def on_error(self, status):
        print (status)


auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

twitterStream = Stream(auth, listener())
GEOBOX= [5.0770049095, 47.2982950435, 15.0403900146, 54.9039819757]
twitterStream.filter(locations=GEOBOX)

