var restify = require('restify');

function send(req, res, next) {
res.send('hello ' + req.params.name);
return next();
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

server.get('/user/:userId', send);
server.head('/user/:userId', send);
server.post('/user/:userId', getDepositAddress);
server.put('/user', notAllowed);
server.del('/user/:userId', notAllowed);

server.listen(8080, function() {
  console.log('%s listening at %s', server.name, server.url);
});


