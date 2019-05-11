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

    print('async_mode is ' + async_mode)

if async_mode == 'eventlet':
    import eventlet

    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey

    monkey.patch_all()


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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
import pandas as pd
def background_thread(room_name):
    count = 0
    df = pd.read_csv('C:/Users/IsMehedi/PycharmProjects/classification/sentimentss1.csv', header=None, usecols=[1, 2])
    for i in xrange(1, len(df)):
        if df[2][i] == '0':
            tweet = df[1][i]
            sent = df[2][i]
            socketio.emit('number_counter_msg', tweet, namespace='/counter', room=room_name)
            socketio.emit('number_counter_msg', sent, namespace='/counter', room=room_name)
        else:
            print df[1][i]
            tweet = df[1][i]
            sent = df[2][i]
            print sent
            socketio.emit('number_counter_msg', tweet, namespace='/counter', room=room_name)
            socketio.emit('number_counter_msg', sent, namespace='/counter', room=room_name)
            count = count + 1
    socketio.emit('number_counter_msg', count, namespace='/counter', room=room_name)



@app.route('/', methods=['GET', 'POST'])
def datafetch():
    return render_template("classification.html",async_mode=socketio.async_mode)

# Websocket view that launches a background thread when client notifies the server that it has connected
@socketio.on('client_connected', namespace='/counter')
def start_counter(message):
    room_name = request.sid
    thread = socketio.start_background_task(target=background_thread, room_name=room_name)
    emit('number_counter_msg', 'Thread Started...')

@socketio.on('connect')
def test_connect():
    print('Server Detected Connection from Client.')

#app.run(host="127.0.0.1", port=5000, debug=True)
socketio.run(app, host='127.0.0.1')
