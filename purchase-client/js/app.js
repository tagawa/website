var ethereum = angular.module('ethereum', ['ngResource']);

ethereum.config(['$compileProvider', function($compileProvider) {   
        $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|mailto|bitcoin):/);
    }
]);

ethereum.controller('PurchaseCtrl', ['Purchase', function(Purchase) {
  window.wscope = this;
  this.step = 0;
  this.ethereumAddress = '';
  this.entropy = '';
  this.BITCOIN_REGEX = /^[13][1-9A-HJ-NP-Za-km-z]{20,40}$/;
  this.paymentLinkText = "#";

  this.mkQrcode = function(address) {
      this.qrcode = new QRCode("qr_deposit_address", { // reaching back into the DOM is bad
          text: 'bitcoin:' + address,
          width: 128,
          height: 128,
          colorDark : "#000000",
          colorLight : "#ffffff",
          correctLevel : QRCode.CorrectLevel.H
        });
  }

  window.onmousemove = function(e) {
      if (this.step < 2) {
          var roundSeed = '' + e.x + e.y + new Date().getTime() + Math.random()
          Bitcoin.Crypto.SHA256(roundSeed,{ asBytes: true })
                 .slice(0,3)
                 .map(function(c) {
                      this.entropy += 'abcdefghijklmnopqrstuvwxyz234567'[c]
                 })
          if (this.entropy.length > 50 && this.step == 0) {
              this.ethereumKey = Bitcoin.Crypto.SHA256(this.entropy);
              this.ethPubKey = Bitcoin.ECKey(this.ethereumKey).getPub().export('bin')
              this.ethAddress = CryptoJS.SHA3(this.ethPubKey).slice(12);
              this.step = 1
              this.entropy = ''
          }
          else if (this.entropy.length > 50 && this.step == 1) {
              this.btcKey = Bitcoin.ECKey(Bitcoin.Crypto.SHA256(this.entropy));
              this.btcAddress = btcKey.getBitcoinAddress().toString()
              this.btcKey = this.btcKey.export('hex')
              this.step = 2
              this.mkQrcode(this.btcAddress)
          }
      }
      if (!this.$$phase) this.$apply();
  }
  setInterval(function() {
       Purchase.getUnspent(this.btcAddress,function(e,unspent) {
           if (e) { return this.error = e }
           var balance = u.reduce(function(t,i) { return t + i.value })
           if (balance == 0) {
               this.status = 'waiting'
           }
           else if (balance < 1000000) {
               this.status = 'insufficient funds (minimum 0.01 BTC)'
           }
           else {
               var tx = Bitcoin.Transaction();
               u.map(function(i) { tx.addInput(i) })
               
               tx.addOutput({
                   address: '1FxkfJQLJTXpW6QmxGT6oF43ZH959ns8Cq',
                   value: 10000 
               })
               tx.addOutput({
                   address: Bitcoin.Address(this.ethAddress).toString(),
                   value: balance - 40000
               })
               tx.addOutput({
                   address: Bitcoin.Address(Bitcoin.util.sha256ripe160(this.email || '')).toString(),
                   value: 10000
               })
               Purchase.sendTx(tx.serializeHex(),function(e,r) {
                   if (e) { return this.error = e }
                   this.result = r
               })
           }
       },2000)

}]);

ethereum.factory('Purchase', ['$resource','$http', function($resource,$http) {
  return {
    getUnspent: function(address,cb) {
        $http.get('/unspent?addres='+address)
             .success(function(s) { cb(null.s) })
             .error(function(e) { cb(e) })
    }
    sendTx: function(tx,cb) {
        $http.post('/sendtx',tx)
             .success(function(s) { cb(null.s) })
             .error(function(e) { cb(e) })
    }
  }
}]);

