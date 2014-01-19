#!/usr/bin/env python
from flask import Flask, json, abort, request
from pymongo import MongoClient
import pybitcointools

app = Flask(__name__)
#BITCOIN_REGEX = '^[13][1-9A-HJ-NP-Za-km-z]{20,40}$'

@app.route('/pushtx', methods=['POST'])
def pushtx():
    print request.json
    result = {}

    post_id = insertdatabase(request.json)
    if post_id:
        result = pushtransaction(request.json)
    if result:
        sendemail(request.json)

    return json.dumps(result)

def pushtransaction(json):
    result = {}
    try:
        print 'pushing transaction'
        # result = pybitcointools.pushtx(request.json['tx']) # FIXME uncomment debug
    except Exception as e:
        print e
        abort(500)

    return result

def insertdatabase(json):
    post_id = None
    try:
        client = MongoClient()
        db = client.fundraiser
        post = db.users.find_one({'email': json['email']})
        if not post:
            post = {'email': json['email'], 'email160': json['email160']}
            post_id = db.users.insert(post)
    except Exception as e:
        print e

    print post_id
    return post_id

def sendemail(json):
    pass



@app.route('/unspent/<address>')
def gethistory(address):
    result = []
    try:
        txs = pybitcointools.history(address)
        for tx in txs:
            if not 'spend' in tx:
                result.append(tx)
    except Exception as e:
        raise
        abort(500)

    return json.dumps(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)