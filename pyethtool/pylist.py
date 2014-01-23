import python_sha3
import aes
import os
import sys
import json
import pbkdf2 as PBKDF2
from pybitcointools import *

our_privkey = sha256("my magic awesome long password")
exodus = '1LUyRNhvrqFyvSBGxK68CiUZMdiwE3gvg5'

def pbkdf2(x): return PBKDF2._pbkdf2(x,x,1000)[:16]

outs = history(exodus)

txs = {}

for o in outs:
    if o['output'][65:] == '0':
        h = o['output'][:64]
        txs[h] = fetchtx(h)

def processtx(txhex):
        tx = deserialize(txhex)
        ethaddr = b58check_to_hex(script_to_address(tx['outs'][1]['script']))
        data = ''
        for o in tx['outs'][2:]:
            data += b58check_to_bin(script_to_address(o['script']))
        data = data[1:1 + ord(data[0])]
        pubkey = data[-33:]
        shared = multiply(pubkey,our_privkey)
        email = aes.decryptData(shared[:16],data[:-33])
        print "Tx:",h
        print "Ethereum address:",ethaddr
        print "Email:",email
    

for h in txs:
    txhex = txs[h]
    try:
        processtx(tx)
    except:
        pass
