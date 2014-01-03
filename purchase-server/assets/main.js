var restify = require('restify');
var cp = require('child_process');

var pybtctool = function(command, argz) {
    var cb = arguments[arguments.length - 1] 
        args = Array.prototype.slice.call(arguments,1,arguments.length-1) 
                    .map(function(x) {  
                        return (''+x).replace('\\','\\\\').replace(' ','\\ '    )             
                     }) 
    cp.exec('pybtctool '+command+' '+args.join(' '),cb); 
}

var eh = function(fail, success) {
    return function(err, res) {
        if (err) {
            console.log('e',err,'f',fail,'s',success);
            if (fail) { fail(err); }
        }
        else {
            success.apply(this,Array.prototype.slice.call(arguments,1));
        }
    };
};

var mkrespcb = function(res,code,success) {
    return eh(function(msg) { res.json(msg,code);  },success);
}


function send(req, res, next) {
res.send('hello ' + req.params.name);
return next();
}

function gethistory(req, res, next) {
    pybtctool('history',req.param('address'),mkrespcb(res,400,function(h) {
        res.json(h)
        return next();
    }))
}

function pushtx(req, res, next) {
    pybtctool('pushtx',req.param('tx'),mkrespcb(res,400,function(r) {
        res.json(r)
        return next();
    }))
}

function getDepositAddress(req, res, next) {
  // upsert req.params.userId
  // get deposit address from external service and build payment object
  // update user with new payments[] object
  // return payment object
  return next();
}

function notAllowed(req, res, next) {
   res.send(405);
   return next();
 }

server.get(/\/static\/?.*/, restify.serveStatic({
  directory: './static'
}));

server.get('/tx/:address', gethistory);
server.get('/tx/:tx', pushtx);
server.get('/user/:userId', send);
server.head('/user/:userId', send);
server.post('/user/:userId', getDepositAddress);
server.put('/user', notAllowed);
server.del('/user/:userId', notAllowed);

server.listen(8080, function() {
  console.log('%s listening at %s', server.name, server.url);
});


