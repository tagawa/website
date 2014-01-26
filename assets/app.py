#!/usr/bin/env python
from flask import Flask, json, abort, request
from pymongo import MongoClient
from bson.objectid import ObjectId
import pybitcointools

app = Flask(__name__)

@app.route('/download/<dbid>')
def getbackup(dbid):
    result = {}
    try:
        client = MongoClient()
        db = client.fundraiser
        post = db.users.find_one({'_id': ObjectId(dbid)})
        if post:
            result = post
    except Exception as e:
        print e

    return post_id

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
        print 'pushing transaction '+request.json['tx']
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
        post_id = db.users.insert(json['downloadjson'])
    except Exception as e:
        print e

    return post_id

def sendemail(json):
    text = 'Thanks for participating in the Ethereum fundraiser. Attached is an encrypted backup of important transaction data.'
    msg = MIMEMultipart()
    msg['From'] = 'donotreply@fund.ethereum.org'
    msg['To'] = json['email']
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = 'Ethereum Fundraiser backup'

    msg.attach( MIMEText(text) )

    part = MIMEBase('application', "octet-stream")
    part.set_payload( json['emailjson'] )
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="%s"' % 'emailbackup.json')
    msg.attach(part)

    smtp = smtplib.SMTP('localhost')
    smtp.sendmail(msg['From'], msg['To'], msg.as_string())
    smtp.close()

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
    app.run(host='127.0.0.1', debug=True)
