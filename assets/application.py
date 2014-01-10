#!/usr/bin/env python
from flask import Flask, json, abort
from pymongo import MongoClient
import pybitcointools

app = Flask(__name__)
#BITCOIN_REGEX = '^[13][1-9A-HJ-NP-Za-km-z]{20,40}$'

@app.route('/pushtx', methods=['POST'])
def pushtx():
    result = {}
    try:
        client = MongoClient()
        db = client.fundraiser
        post = db.users.find_one({'email': request.form['email']})
        if not post:
            post = {'email': request.form['email'], 'email160': request.form['email160']}
            post_id = posts.insert(post)
            print post_id

        result = pybitcointools.pushtx(request.form['tx'])
    except Exception as e:
        abort(500)

    return json.dumps(result)

@app.route('/unspent/<address>')
def gethistory(address):
    result = {}
    try:
        # TODO should be returning only unspent
        result = pybitcointools.history(address)
        print result
    except Exception as e:
        abort(500)

    return json.dumps(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)