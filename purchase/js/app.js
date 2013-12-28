var ethereum = angular.module('ethereum', []);

ethereum.config(['$compileProvider', function($compileProvider) {   
        $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|chrome-extension|bitcoin):/);
    }
]);

ethereum.controller('PurchaseCtrl', ['Purchase', function(Purchase) {
  this.step = 1;
  this.userId = '1DevAddress8989898989';
  this.BITCOIN_REGEX = /^[13][1-9A-HJ-NP-Za-km-z]{20,40}$/;
  this.paymentLinkText = "#";
  var qrcode = new QRCode("qr_deposit_address", { // reaching back into the DOM is bad
      text: 'bitcoin:',
      width: 128,
      height: 128,
      colorDark : "#000000",
      colorLight : "#ffffff",
      correctLevel : QRCode.CorrectLevel.H
    });

  this.getDepositAddress = function(userId) {
    this.paymentRequest = Purchase.makeRequest(userId);
    this.paymentLinkText = 'bitcoin:' + this.paymentRequest.depositAddress;
    qrcode.makeCode(this.paymentLinkText);
    this.step = 2;
  };

  this.getStatus = function(userId) {
    // FIXME Determines which payment we're checking on. Depends on backend structure
    var refCode = this.paymentRequest.depositAddress;
    this.paymentRequest = Purchase.getStatus(userId, refCode);
    this.paymentLinkText = 'bitcoin:' + this.paymentRequest.depositAddress; // in case it changes
    qrcode.makeCode(this.paymentLinkText);
    if (this.paymentRequest.paidSatoshis > 0) {
      this.step = 3;
    } else {
      alert('You have not paid anything.');
    }
  };

}]);

ethereum.factory('Purchase', ['$http', function($http) {
  var XHR_BASEURI = 'http://localhost:3000/';

  return {
    makeRequest: function(userId) {
      // FIXME This literal needs to be replaced with a call to a backend service
      var paymentRequest = {depositAddress: '1ThisIsAFakePaymentAddress', paidSatoshis: 0};

      return paymentRequest;
    },
    getStatus: function(userId, refCode) {
      // FIXME This literal needs to be replaced with a call to a backend service
      var paymentRequest = {depositAddress:'1ThisIsAFakePaymentAddress', paidSatoshis: 100000000};
      return paymentRequest;
    }

  }
}]);

