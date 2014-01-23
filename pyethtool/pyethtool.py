#!/usr/bin/python
import python_sha3, aes
import os, sys, json, getpass
import pbkdf2 as PBKDF2
from pybitcointools import *

def sha3(x): return python_sha3.sha3_256(x).digest()

def pbkdf2(x): return PBKDF2._pbkdf2(x,'',1000)[:16]

if len(sys.argv) == 1: sys.argv.append('help')

opts = { "pw": None, "seed": None, "wallet": 'ethwallet.json', 'backup': None, 'email': None }
for i in range(len(sys.argv)-1):
    if sys.argv[i] == '-p': opts['pw'] = sys.argv[i+1]
    if sys.argv[i] == '-s': opts['seed'] = sys.argv[i+1]
    if sys.argv[i] == '-w': opts['wallet'] = sys.argv[i+1]
    if sys.argv[i] == '-b': opts['backup'] = sys.argv[i+1]
    if sys.argv[i] == '-e': opts['email'] = sys.argv[i+1]

if len(sys.argv) == 2: sys.argv.append('ethwallet.json')
if len(sys.argv) == 3: sys.argv.append('ethwallet.bkp.json')

exodus = '1FxkfJQLJTXpW6QmxGT6oF43ZH959ns8Cq'
our_pubkey = compress(privtopub(sha256("my magic awesome long password")).decode('hex'))

def tryopen(f):
    try:
        assert f
        t = open(f).read()
        try: return json.loads(t)
        except: raise Exception("Corrupted file: "+f)
    except:
        return None

def eth_privtoaddr(priv):
    return sha3(encode_pubkey(privtopub(priv),'bin_electrum'))[12:].encode('hex')

def getseed(encseed,pw,ethaddr):
    seed = aes.decryptData(pbkdf2(pw),encseed.decode('hex'))
    ethpriv = sha3(seed)
    if eth_privtoaddr(ethpriv) != ethaddr: raise Exception("ethaddr does not match!")
    return seed

def mkbackup(wallet,pw):
    seed = getseed(wallet['encseed'],pw,wallet['ethaddr'])
    return {
        "withpw": aes.encryptData(pbkdf2(pw),seed).encode('hex'),
        "withwallet": aes.encryptData(pbkdf2(wallet['bkp']),seed).encode('hex'),
        "ethaddr": wallet['ethaddr']
    }

def genwallet(seed,pw,email):
    if not seed:
        seed = random_key().decode('hex') # uses pybitcointools' 3-source random generator
    encseed = aes.encryptData(pbkdf2(pw),seed)
    ethpriv = sha3(seed)
    btcpriv = sha3(seed + '\x01')
    ethaddr = sha3(privtopub(ethpriv)[1:])[12:].encode('hex')
    btcaddr = privtoaddr(btcpriv)
    bkp = sha3(seed + '\x02').encode('hex')
    return {
        "encseed": encseed.encode('hex'),
        "bkp": bkp,
        "ethaddr": ethaddr,
        "btcaddr": btcaddr,
        "email": email
    }

def finalize(wallet,unspent,pw):
    seed = getseed(wallet["encseed"],pw,wallet["ethaddr"]) 
    balance = sum([o["value"] for o in unspent])
    if balance == 0:
        raise Exception("No funds in address")
    if balance < 1000000:
        raise Exception("Insufficient funds. Need at least 0.01 BTC")
    ephem = random_key().decode('hex')
    shared = multiply(our_pubkey,ephem)
    data = aes.encryptData(shared[:16],wallet["email"]) + compress(privtopub(ephem))
    data = chr(len(data)) + data
    outs = [
        exodus+':'+str(balance - 70000),
        hex_to_b58check(wallet["ethaddr"])+':10000'
    ]
    while len(data) > 0:
        d = data[:20] + '\x00' * max(0,20 - len(data))
        outs.append(bin_to_b58check(d)+':10000')
        data = data[20:]
    tx = mktx(unspent,outs)
    btcpriv = sha3(seed+'\x01')
    for i in range(len(unspent)):
        tx = sign(tx,i,btcpriv)
    return tx

def recover_bkp_pw(bkp,pw):
    return getseed(bkp['withpw'],pw,bkp['ethaddr'])

def recover_bkp_wallet(bkp,wallet):
    return getseed(bkp['withwallet'],wallet['bkp'],bkp['ethaddr'])

def password(twice=False):
    if opts['pw']: return opts['pw']
    pw = getpass.getpass()
    if twice:
        pw2 = getpass.getpass()
        if pw != pw2: raise Exception("Passwords do not match")
    return pw

def checkwrite(f,thunk):
    try:
        open(f)
        are_you_sure = raw_input("File "+f+" already exists. Overwrite? (y/n) ")
        if are_you_sure not in ['y','yes']:
            sys.exit()
    except:
        pass
    open(f,'w').write(thunk())

w = tryopen(opts['wallet'])
b = tryopen(opts['backup'])

if sys.argv[1] == 'genwallet':
    pw = password(True)
    if opts['email']:
        email = opts['email']
    else:
        email = raw_input("Email: ")
    if len(email) > 31: raise Exception("Maximum email length 31 chars")
    newwal = genwallet(opts['seed'],pw,email)
    checkwrite(opts['wallet'],lambda: json.dumps(newwal))
    if opts['backup']:
        checkwrite(opts['backup'],lambda: json.dumps(mkbackup(newwal)))
    print "Your intermediate Bitcoin address is:",newwal['btcaddr']
elif sys.argv[1] == 'mkbackup':
    if not w: print "Must specify wallet with -w"
    if not opts['backup']: opts['backup'] = 'ethwallet.bkp.json'
    pw = password()
    checkwrite(opts['backup'],lambda: json.dumps(mkbackup(w,pw)))
elif sys.argv[1] == 'getbtcaddress':
    if not w: print "Must specify wallet with -w"
    print w["btcaddr"]
elif sys.argv[1] == 'getbtcprivkey':
    pw = password()
    print sha3(getseed(w['encseed'],pw,w['ethaddr'])+'\x01')
elif sys.argv[1] == 'recover':
    if not w and not b:
        print "Must have wallet or backup file"
    elif not b:
        pw = password()
        print "Your seed is:", getseed(w['encseed'],pw,w['ethaddr'])
    elif not w:
        pw = password()
        print "Your seed is:", getseed(b['withpw'],pw,b['ethaddr'])
    else:
        print "Your seed is:", getseed(b['withwallet'],w['bkp'],b['ethaddr'])
elif sys.argv[1] == 'finalize':
    u = unspent(w["btcaddr"])
    pw = password()
    print finalize(w,u,pw)
elif sys.argv[1] == 'help':
    print 'Use "pyethtool genwallet" to generate a wallet'
    print 'Use "pyethtool getbtcaddress" to output the intermediate Bitcoin address you need to send funds to'
    print 'Use "pyethtool getbtcprivkey" to output the private key to your intermediate Bitcoin address'
    print 'Use "pyethtool finalize" to finalize the funding process once you have deposited to the intermediate address'
    print 'Use "pyethtool recover" to recover the seed if you are missing either your wallet or your password'
    print 'Use -s to specify a seed, -w to specify a wallet file, -b to specify a backup file, -e to specify an email address and -p to specify a password when creating a wallet. The -w, -b and -p options also work with other commands.'
