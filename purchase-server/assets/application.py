#!/usr/bin/env python
from flask import Flask, json, abort
import pybitcointools

app = Flask(__name__)
#BITCOIN_REGEX = '^[13][1-9A-HJ-NP-Za-km-z]{20,40}$'

@app.route('/pushtx/<tx>', methods=['POST'])
def pushtx(tx):
    result = {}
    try:
        result = pybitcointools.pushtx(tx)
    except Exception as e:
        abort(500)

    return json.dumps(result)

@app.route('/addresshistory/<address>')
def gethistory(address):
    result = {}
    try:
        result = pybitcointools.history(address)
    except Exception as e:
        abort(500)

    return json.dumps(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)