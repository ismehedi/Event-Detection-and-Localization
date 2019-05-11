
import pandas as pd

def tclassReadpro():
    print('Reading Classified Tweets\n');
    count = 1
    df = pd.read_csv('classifiedTweet.csv', header=None, usecols=[0, 1, 2, 3, 4])
    for i in xrange(1, len(df)):
        if df[0][i] == '0':
            tweet = df[4][i]
            tclass = df[0][i]
            # location = df[4][i]
            time = df[3][i]
            lat = df[1][i]
            lon = df[2][i]
            print tweet,tclass,time,lat,lon

        else:
            tweet = df[4][i]
            tclass = df[0][i]
            # location = df[4][i]
            time = df[3][i]
            lat = df[1][i]
            lon = df[2][i]
            count = count + 1
            print tweet, tclass, time, lat, lon

tclassReadpro()
