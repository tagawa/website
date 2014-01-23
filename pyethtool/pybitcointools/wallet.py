from transaction import *
from main import *
from bci import *

def get_enough_utxo(address,value):
    value = int(value)
    h = filter(lambda x: "spend" not in x, history(address))
    h.sort(key=lambda x: x["value"])
    if h[-1]["value"] >= value:
        for i in range(len(h)-1,-1,-1):
            if h[i]["value"] < value:
                return [h[i+1]]
        return [h[0]]
    tot = 0
    for i in range(len(h)):
        tot += h[i]["value"]
        if tot >= value:
            return h[:i+1]
    raise Exception("Not enough unspent value")
        
# (address, [outs], changeIndex) or (address, out1, out2 ..., changeIndex)
def send_to_outputs(*args): 
    address = args[0]
    if isinstance(args[1],list):
        outs = args[1]
        change = args[2] if len(args) > 2 else len(outs)-1
        fee = args[3] if len(args) > 3 else 10000
    else:
        def parseout(arg):
            if isinstance(arg,dict): return arg
            else: 
                s = arg.split(':')
                return { "address": s[0], "value": int(s[1]) }
        outs = [parseout(arg) for arg in args[1:-1]]
        if isinstance(args[-1],(int,long)):
            change = args[-1]
        elif isinstance(args[-1],dict) or len(args[-1]) > 27:
            outs.append(parseout(args[-1]))
            change = len(outs) - 1
        else:
            raise Exception("Invalid argument")
    totvalue = sum(map(lambda x:x["value"],outs))
    ins = get_enough_utxo(address,totvalue)
    insum = sum(map(lambda x:x["value"],ins))
    ins[change] += insum - totvalue
    return mktx(ins,outs)
