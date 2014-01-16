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
    #try:
    client = MongoClient()
    db = client.fundraiser
    post = db.users.find_one({'email': request.json['email']})
    if not post:
        post = {'email': request.json['email'], 'email160': request.json['email160']}
        post_id = db.users.insert(post)
        print post_id

    result = pybitcointools.pushtx(request.json['tx'])
    # except Exception as e:
    #     raise
    #     abort(500)

    return json.dumps(result)

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