async_mode = None
if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass
    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass
    if async_mode is None:
        async_mode = 'threading'

    print('The server in on asychonrize State:' + async_mode)

if async_mode == 'eventlet':
    import eventlet

    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey

    monkey.patch_all()

import json
import time
from threading import Thread
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from tweepy.streaming import StreamListener
from tweepy import Stream
import tweepy
from datetime import datetime
from flask import render_template
from flask import Flask, request, render_template, jsonify
import os
import re
import pandas as pd
from twitter_crawler import TwitterClient
from index_helper import processTweet,tweetProcessing
from nltk.tokenize import TweetTokenizer


app = Flask(__name__)
api = TwitterClient('@TheAthest')

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

cred = {
    "access_key": "3720728952-zBkjKHV6EIzOtbnuZz4M4kpUuf0rLe9lBCjtdqG",
    "access_secret": "q5lqi72PFLZU6YALPXk5tFfB3p8maXabeEe1hbkTmfPZE",
    "consumer_key": "1MfhNUc61eAX63bIuAnc9JLE5",
    "consumer_secret": "gvKJ5i8meMfCOM6nQuscUuZtxELmZLwKuPVi80H4Tiq3MS10yI"
}
auth = tweepy.OAuthHandler(cred['consumer_key'], cred['consumer_secret'])
auth.set_access_token(cred['access_key'], cred['access_secret'])

tweetTokenizer = TweetTokenizer()
#Tracker = ['Earthquake', 'shaking']
tracker = ['trump']

class StdOutListener(StreamListener):

    def __init__(self):
        pass

    def on_data(self, data):
        try:
            tweet = json.loads(data)
            tweet = json.loads(data)
            # print tweet['created_at']
            text = tweet['text'].lower()
            # print text
            tokens = set(tweetTokenizer.tokenize(text))
            # print tweet
            if len(tokens & set(tracker)) > 0:
               #if tweet['coordinates'] != None or tweet['user']['location'] != None:
               if tweet['coordinates'] != None or tweet['user']['location'] != None:
                print "Got a Tweet related to Earthquake.!"
                saveFile = open('EarthQuakeTweet.txt', 'a')
                print text
                saveFile.write(data)
                saveFile.write('\n')
                saveFile.close()
                coordinates = tweet['coordinates']
                #print(tweet['coordinates'])
                #print(tweet['text'])
                loc=(tweet['user']['location'])
                print loc
                #print tweet['created_at']
                text = tweetProcessing(tweet['text'])
                socketio.emit('stream_channel',
                          {'data': text,'location':loc,'copordinates': tweet['coordinates'], 'time': tweet['created_at']},namespace='/demo_streaming')

        except:
            pass

    def on_error(self, status):
        print 'Error status code', status
        exit()

def keyword_thread():
    stream = Stream(auth, l)
    _keywords = ['earthquake']
    stream.filter(track=_keywords)

def location_tweet():
    stream = Stream(auth, l)
    twitterStream = Stream(auth, l)
    GEOBOX = [5.0770049095, 47.2982950435, 15.0403900146, 54.9039819757]
    twitterStream.filter(locations=GEOBOX)

def strtobool(v):
    return v.lower() in ["yes", "true", "t", "1"]

@app.route('/')
@app.route('/home')
def home():
    return render_template(
        'home.html',
        title = 'Home Page',
        year = datetime.now().year)

@app.route('/')
def menu():
    return render_template(
        'mylayout.html',
        title = 'Home Page',
        year = datetime.now().year)

@app.route('/tweets')
def tweets():
        retweets_only = request.args.get('retweets_only')
        api.set_retweet_checking(strtobool(retweets_only.lower()))
        with_sentiment = request.args.get('with_sentiment')
        api.set_with_sentiment(strtobool(with_sentiment.lower()))
        query = request.args.get('query')
        api.set_query(query)
        tweets = api.get_tweets()
        return jsonify({'data': tweets, 'count': len(tweets)})


@app.route('/cQuery')
def cQuery():
    return render_template('tweetcrawl.html')

@app.route('/crawling', methods=['POST'])
def crawling():
    global thread
    keyword = request.form['inputName']
    if keyword == "earthquake":
        print "Tweet is crawling with keyword:"+keyword
        #global thread
        thread = Thread(target=location_tweet)
        thread.daemon = True
        thread.start()
    else:
        print "Tweet is crawling with keyword:"

        thread = Thread(target=location_tweet)
        thread.daemon = True
        thread.start()

    return render_template(
        'tweetCrawlShow.html',
        title = 'Tweet Crawler: We can Crawl Tweet As we Want.',
        year = datetime.now().year)

def tweet_read():
    print('Reading Tweets\n');
    tweets_data_path = 'Earthquake_Preci_Umbria_Italy.txt';
    tweets_data = []
    tweets_file = open(tweets_data_path, "r");
    for line in tweets_file:
        try:
            data = json.loads(line)
            tweets_data.append(data)
            tweet = data['text']
            location = data['user']['location']
            time = data['created_at']
            print tweet
            protweet = processTweet(tweet)
            print protweet
            socketio.sleep(1)
            socketio.emit('tweet', {'tweet': protweet,'location':location,'time':time}, namespace='/tweet')

        except:
            continue

@app.route('/crawlingDataShow', methods=['GET', 'POST'])
def datafetch():
    global thread
    if thread is None:
        thread = Thread(target=tweet_read)
        thread.daemon = True
        thread.start()
    return render_template('crawlingDataShow.html',title='Tweet Crawler: We can Crawl Tweet As we Want.',
        year=datetime.now().year)

def tclassRead():
    print('Reading Classified Tweets\n');
    count = 0
    df = pd.read_csv('classifiedTweet.csv', header=None, usecols=[0,1,2,3,4])
    for i in xrange(1, len(df)):
        if df[0][i] == '0':
            tweet = df[4][i]
            tclass = df[0][i]
            #location = df[4][i]
            time = df[3][i]
            lat = df[1][i]
            lon = df[2][i]
            socketio.sleep(1)
            socketio.emit('tweetclass', {'tweet':tweet,'tclass':tclass,'time':time,'lat':lat,'lon':lon},
                          namespace='/tweetclass')
        else:
            tweet = df[4][i]
            tclass = df[0][i]
            # location = df[4][i]
            time = df[3][i]
            lat = df[1][i]
            lon = df[2][i]
            #print tweet,tclass,time,lat,lon
            count +=count
            #print count
            socketio.sleep(1)
            socketio.emit('tweetclass', {'tweet':tweet,'tclass':tclass,'time':time,'lat':lat,'lon':lon},
                          namespace='/tweetclass')
    print count
    socketio.emit('tweetclass', {'count': count}, namespace='/tweetclass')

@app.route('/tweetClassification', methods=['GET', 'POST'])
def tweetClassification():
    global thread
    if thread is None:
        thread = Thread(target=tclassRead)
        thread.daemon = True
        thread.start()
    return render_template('classification.html',title='Tweet Crawler: We can Crawl Tweet As we Want.',
        year=datetime.now().year)

@app.route('/alert')
def alert():
    return render_template(
        'classification.html',
        title = 'Twitter Alert',
        year = datetime.now().year,
    )
def read_lda_topic():
    print('Reading Tweets\n');
    tweets_data_path = 'Earthquake_Preci_Umbria_Italy.txt';
    tweets_data = []
    tweets_file = open(tweets_data_path, "r");
    for line in tweets_file:
        try:
            data = json.loads(line)
            tweets_data.append(data)
            tweet = data['text']
            location = data['user']['location']
            time = data['created_at']
            print tweet
            protweet = processTweet(tweet)
            print protweet
            socketio.sleep(1)
            socketio.emit('tweet', {'tweet': protweet,'location':location,'time':time}, namespace='/tweet')

        except:
            continue


@app.route('/topicDetectionLDA')
def topicDetectionLDA():
    return render_template(
        'topicDetection_LDA.html',
        title = 'Topic Detection LDA',
        year = datetime.now().year,
    )

@app.route('/topicDetectionLSI')
def topicDetectionSI():
    return render_template(
        'toppicDetection_LSI.html',
        title = 'Topic Detection LSI',
        year = datetime.now().year)

@app.route('/topicDetectionHDP')
def topicDetectionHDP():
    return render_template(
        'topicDetection_HDP.html',
        title = 'Topic Detection HDP',
        year = datetime.now().year)

def tclassReadpro():
    print('Reading Classified Tweets\n');
    count = 1
    df = pd.read_csv('dataToshow/classifiedTweet.csv', header=None, usecols=[0, 1, 2, 3, 4])
    for i in xrange(1, len(df)):
        if df[0][i] == '0':
            tweet = df[4][i]
            tclass = df[0][i]
            # location = df[4][i]
            time = df[3][i]
            lat = df[1][i]
            lon = df[2][i]
            socketio.sleep(1)
            socketio.emit('tweetclasspro', {'tweet':tweet,'tclass':tclass,'time':time,'lat':lat,'lon':lon},
                         namespace='/tweetclasspro')
        else:

            tweet = df[4][i]
            tclass = df[0][i]
            # location = df[4][i]
            time = df[3][i]
            lat = df[1][i]
            lon = df[2][i]
            socketio.sleep(1)
            socketio.emit('tweetclasspro', {'tweet':tweet,'tclass':tclass,'lat':lat,'lon':lon,'count':count},
                          namespace='/tweetclasspro')
            count = count + 1
    socketio.emit('tweetclass1', {'count1': count}, namespace='/tweetclass1')



@app.route('/topicDetectionProb')
def topicDetectionProb():
    global thread
    if thread is None:
        thread = Thread(target=tclassReadpro)
        thread.daemon = True
        thread.start()

    return render_template(
        'topicDetection_prob.html',
        title = 'Topic Detection Probablity',
        year = datetime.now().year,
    )

def coordinates():

    df = pd.read_csv('dataToshow/twiloc_mytweet_coordinates.csv', header=None, usecols=[0, 1, 2])
    df1 = pd.read_csv('dataToshow/twiloc_mytweet_coordinates_all.csv', header=None, usecols=[0, 1, 2])
    count = 1
    for i in xrange(1, len(df)):
        id = df[0][i]
        lat = df[1][i]
        lon = df[2][i]
        print id,lat,lon
        socketio.sleep(1)
        socketio.emit('coordinates', {'lat': lat, 'lon': lon, 'id':id ,'count':count}, namespace='/coordinates')
        count = count +1

        count1 = 1
    for i in xrange(1, len(df1)):
        id = df1[0][i]
        lat = df1[1][i]
        lon = df1[2][i]
        print id,lat,lon
        socketio.sleep(1)
        socketio.emit('coordinates1', {'lat': lat, 'lon': lon, 'id':id,'count1':count1}, namespace='/coordinates1')
        count1 = count1+1

@app.route('/twiloc')
def coordinateplot():
    global thread
    if thread is None:
        thread = Thread(target=coordinates)
        thread.daemon = True
        thread.start()
    return render_template(
        'twiloc.html',
        title = 'Tweet Crawler: We can Crawl Tweet As we Want.',
        year = datetime.now().year,
    )

def myalgorithm():
    df = pd.read_csv('dataToshow/Preci_Umbria_Italy_Sunday_October.csv', header=None, usecols=[0, 7, 8])
    dfavg = pd.read_csv('dataToshow/Preci_Umbria_Italy_Sunday_October.csv', header=None, usecols=[0, 9, 10])
    df1 = pd.read_csv('dataToshow/Preci_Umbria_Italy_Sunday_October.csv', header=None, usecols=[0, 3, 4])
    df1avg = pd.read_csv('dataToshow/Preci_Umbria_Italy_Sunday_October.csv', header=None, usecols=[0, 11, 12])
    count = 1
    for i in xrange(1, len(df)):
        id = df[0][i]
        lat = df[7][i]
        lon = df[8][i]
        print id,lat,lon
        socketio.sleep(1)
        socketio.emit('coordinates2', {'lat': lat, 'lon': lon, 'id':id ,'count':count}, namespace='/coordinates2')
        count = count +1
        count = 1
    for i in xrange(1, len(dfavg)):
        id = df[0][i]
        lat = df[9][i]
        lon = df[10][i]
        print id, lat, lon
        socketio.sleep(1)
        socketio.emit('coordinates4', {'lat': lat, 'lon': lon, 'id': id, 'count': count}, namespace='/coordinates4')
        count = count + 1

        count1 = 1
    for i in xrange(1, len(df1)):
        id = df1[0][i]
        lat = df1[3][i]
        lon = df1[4][i]
        print id,lat,lon
        socketio.sleep(1)
        socketio.emit('coordinates3', {'lat': lat, 'lon': lon, 'id':id,'count1':count1}, namespace='/coordinates3')
        count1 = count1+1

    for i in xrange(1, len(df1avg)):
        id = df1[0][i]
        lat = df1[11][i]
        lon = df1[12][i]
        print id,lat,lon
        socketio.sleep(1)
        socketio.emit('coordinates5', {'lat': lat, 'lon': lon, 'id':id,'count1':count1}, namespace='/coordinates5')
        count1 = count1+1


@app.route('/myalgorithm')
def mycoordinateplot():
    global thread
    if thread is None:
        thread = Thread(target=myalgorithm)
        thread.daemon = True
        thread.start()
    return render_template(
        'myalgorithm.html',
        title = 'Tweet Crawler: We can Crawl Tweet As we Want.',
        year = datetime.now().year,
    )


def DBSCANdata():
    df = pd.read_csv('dataToshow/OnlyPoss.csv', header=None, usecols=[0,1,2])
    dfcent = pd.read_csv('dataToshow/Estimation of location_OnlyPoss.csv', header=None, usecols=[0,1,2])
    for i in xrange(1, len(df)):
        id = df[0][i]
        lat = df[2][i]
        lon = df[1][i]
        print id,lat,lon
        socketio.sleep(1)
        socketio.emit('coordinates1', {'lat': lat, 'lon': lon,'id':id}, namespace='/coordinates1')
    for i in xrange(1, len(dfcent)):
        id = df[0][i]
        lat = df[2][i]
        lon = df[1][i]
        print id, lat, lon
        socketio.sleep(1)
        socketio.emit('coordinates2', {'lat': lat, 'lon': lon,'id':id}, namespace='/coordinates2')

@app.route('/DBSCAN')
def DBSCAN():
    global thread
    if thread is None:
        thread = Thread(target=DBSCANdata)
        thread.daemon = True
        thread.start()
    return render_template(
        'DBSCAN.html',
        title = 'Tweet Crawler: We can Crawl Tweet As we Want.',
        year = datetime.now().year,
    )


def HDBSCANdata():
    df = pd.read_csv('dataToshow/OnlyPos.csv', header=None, usecols=[0,1,2])
    dfcent = pd.read_csv('dataToshow/OnlyPoss_label_exceptNoise.csv', header=None, usecols=[0,1,2])
    for i in xrange(1, len(df)):
        id = df[0][i]
        lat = df[2][i]
        lon = df[1][i]
        print id,lat,lon
        socketio.sleep(1)
        socketio.emit('coordinates1', {'lat': lat, 'lon': lon,'id':id}, namespace='/coordinates1')
    for i in xrange(1, len(dfcent)):
        id = df[0][i]
        lat = df[2][i]
        lon = df[1][i]
        print id, lat, lon
        socketio.sleep(1)
        socketio.emit('coordinates2', {'lat': lat, 'lon': lon,'id':id}, namespace='/coordinates2')

@app.route('/HDBSCAN')
def HDBSCAN():
    global thread
    if thread is None:
        thread = Thread(target=HDBSCANdata)
        thread.daemon = True
        thread.start()
    return render_template(
        'HDBSCAN.html',
        title = 'Tweet Crawler: We can Crawl Tweet As we Want.',
        year = datetime.now().year,
    )


def kalman():
    df = pd.read_csv('dataToshow/Oktoberfestger.csv', header=None, usecols=[0,1,2])
    for i in xrange(1, len(df)):
        id = df[0][i]
        lat = df[1][i]
        lon = df[2][i]
        print id,lat,lon
        socketio.sleep(1)
        socketio.emit('coordinates1', {'lat': lat, 'lon': lon,'id':id}, namespace='/coordinates1')

@app.route('/Kalman')
def Kalman():
    global thread
    if thread is None:
        thread = Thread(target=kalman)
        thread.daemon = True
        thread.start()
    return render_template(
        'kalman.html',
        title = 'Tweet Crawler: We can Crawl Tweet As we Want.',
        year = datetime.now().year,
    )






@app.route('/contact')
def contact():
    return render_template(
        'about.html',
        title = 'About',
        year = datetime.now().year,
        message = 'Your contact page.'
    )

@app.route('/layout')
def layout():
    return render_template(
        'mylayout.html',
        title = 'Layout',
        message = 'Your application layout page.')

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return "tweetcrawl.html"

@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Websocket view that launches a background thread when client notifies the server that it has connected
@socketio.on('client_connected', namespace='/counter')
def start_counter(message):
    room_name = request.sid
    #thread = socketio.start_background_task(target=background_thread, room_name=room_name)
    emit('number_counter_msg', 'Thread Started...')

@socketio.on('connect')
def test_connect():
    print('Server Detected Connection from Client.')

l = StdOutListener()
#app.run(host="127.0.0.1", port=5000, debug=True)
socketio.run(app, host='127.0.0.1')
