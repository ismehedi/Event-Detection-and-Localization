from datetime import datetime
from flask import render_template
from flask import Flask, request, render_template, jsonify
import os
from twitter_crawler import TwitterClient

app = Flask(__name__)
api = TwitterClient('@TheAthest')


@app.route('/')
def home():
    return render_template(
        'tweetcrawl.html',
        title = 'Home Page',
        year = datetime.now().year,
    )
app.run(host="127.0.0.1", port=5000, debug=True)
