var ethereum = angular.module('ethereum', []);

ethereum.config(['$compileProvider', function($compileProvider) {   
    $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|mailto|bitcoin):/);
  }
]);

ethereum.controller('PurchaseCtrl', ['Purchase','$scope', function(Purchase, $scope) {
  window.wscope = $scope;
  $scope.entropy = '';
  $scope.didPushTx = false;
  $scope.debug = '(Debug output)'

  $scope.mkQRCode = function(address) {
    $scope.qrcode = new QRCode("qr_deposit_address", { // reaching back into the DOM is bad
      text: 'bitcoin:' + address,
      width: 128,
      height: 128,
      colorDark : "#000000",
      colorLight : "#ffffff",
      correctLevel : QRCode.CorrectLevel.H
      });
  }

  window.onmousemove = function(e) {
    // only work when the first steps are done
    if (!$scope.email_repeat || ($scope.password != $scope.password_repeat)) return;
    // only work if a btcAddress doesn't already exist
    if (!$scope.btcAddress) {

      var roundSeed = '' + e.x + e.y + new Date().getTime() + Math.random();
      Bitcoin.Crypto.SHA256(roundSeed,{ asBytes: true })
        .slice(0,3)
        .map(function(c) {
          $scope.entropy += 'abcdefghijklmnopqrstuvwxyz234567'[c % 32]
        })

      if ($scope.entropy.length > 50) {
        
        $scope.seed = CryptoJS.SHA3($scope.entropy)
        $scope.encseed = CryptoJS.AES.encrypt($scope.seed, $scope.password)

        //$scope.ethereumKey = CryptoJS.SHA3($scope.seed)
        $scope.ethereumKey = Bitcoin.Crypto.SHA256($scope.entropy);
        $scope.debug = $scope.entropy + ' | ' + $scope.seed + ' | ' + $scope.ethereumKey

        $scope.ethPubKey = Bitcoin.ECKey($scope.ethereumKey).getPub().export('bin');
        $scope.ethAddress = CryptoJS.SHA3($scope.ethPubKey,{ outputLength: 256 })
                                  .toString()
                                  .substring(24);

        //$scope.btcKey = CryptoJS.SHA3($scope.seed + '01')
        $scope.btcKey = Bitcoin.ECKey(Bitcoin.Crypto.SHA256($scope.entropy));
        $scope.btcAddress = $scope.btcKey.getBitcoinAddress().toString()
        $scope.btcKey = $scope.btcKey.export('base58')
        $scope.mkQRCode($scope.btcAddress)

      }
    }
  }

  var timerUnspent = setInterval(function() {
    if (!$scope.btcAddress) return;
    Purchase.getUnspent($scope.btcAddress,function(e,unspent) {
      if (e) { return $scope.status = e }
      //$scope.debug = JSON.stringify(unspent)
      var balance = 0
      // trusts server "unspent" response
      if (unspent.length > 0) { balance = unspent.reduce(function(t,i) { return t + i.value }) }
      if (balance <= 0) {
        $scope.status = 'Deposit status: Waiting'
      } else if (balance < 1000000) {
        var balance_btc = balance / 100000000;
        $scope.status = 'Deposit status: ' + balance_btc + ' BTC is insufficient (minimum 0.01 BTC)'
      } else if ($scope.didPushTx == false) {
        $scope.status = 'Deposit status: Submitting transaction'
        var tx = new Bitcoin.Transaction()
        var email = ($scope.email || '')
        var email160 = Bitcoin.Util.sha256ripe160(email)

        unspent.map(function(i) { tx.addInput(i.output) })
        tx.addOutput('1FxkfJQLJTXpW6QmxGT6oF43ZH959ns8Cq', 10000)
        tx.addOutput(Bitcoin.Address($scope.ethAddress).toString(), balance - 40000) // Why 40000?
        tx.addOutput(Bitcoin.Address(email160).toString(), 10000)

        var data = {'tx': tx.serializeHex(), 'email': email, 'email160': email160}
        $scope.didPushTx = true;

        Purchase.sendTx(data, function(e,r) {
          if (e) { return $scope.error = e }
          $scope.debug = r
          clearInterval(timerUnspent)
        })
      }
    })
  },3000)

}]);

// allows for form validation based on one element matching another
ethereum.directive('match',['$parse', function ($parse) {
  return {
    require: 'ngModel',
    restrict: 'A',
    link: function(scope, elem, attrs, ctrl) {
      scope.$watch(function() {
        return (ctrl.$pristine && angular.isUndefined(ctrl.$modelValue)) || $parse(attrs.match)(scope) === ctrl.$modelValue;
      }, function(currentValue) {
        ctrl.$setValidity('match', currentValue);
      });
    }
  };
}]);

// password meter
ethereum.directive('checkStrength', function () {
  return {
    replace: false,
    restrict: 'EACM',
    scope: { model: '=checkStrength' },
    link: function (scope, element, attrs) {
      
      var strength = {
        colors: ['#F00', '#F90', '#FF0', '#9F0', '#0F0'],
        // TODO this strenght algorithm needs improvement
        measureStrength: function (p) {
          var _force = 0;                    
          var _regex = /[$-/:-?{-~!"^_`\[\]]/g; //" (commented quote to fix highlighting in Sublime Text)
                                
          var _lowerLetters = /[a-z]+/.test(p);                    
          var _upperLetters = /[A-Z]+/.test(p);
          var _numbers = /[0-9]+/.test(p);
          var _symbols = _regex.test(p);
                                
          var _flags = [_lowerLetters, _upperLetters, _numbers, _symbols];                    
          var _passedMatches = _flags.map(function (el) { return el === true; });
          _matches = 0;
          for (var i = 0; i < _passedMatches.length; i++) {
            if (_passedMatches[i])
              _matches += 1;
          }
          _force += 2 * p.length + ((p.length >= 10) ? 1 : 0);
          _force += _matches * 10;
              
          // penality (short password)
          _force = (p.length <= 6) ? Math.min(_force, 10) : _force;                                      
          
          // penality (poor variety of characters)
          _force = (_matches == 1) ? Math.min(_force, 10) : _force;
          _force = (_matches == 2) ? Math.min(_force, 20) : _force;
          _force = (_matches == 3) ? Math.min(_force, 40) : _force;
          
          return _force;

        },
        getColor: function (s) {

          var idx = 0;
          if (s <= 10) { idx = 0; }
          else if (s <= 20) { idx = 1; }
          else if (s <= 30) { idx = 2; }
          else if (s <= 40) { idx = 3; }
          else { idx = 4; }

          return { idx: idx + 1, col: this.colors[idx] };

        }
      };

      scope.$watch('model', function (newValue, oldValue) {
        if (!newValue || newValue === '') {
          element.css({ "display": "none"  });
        } else {
          var c = strength.getColor(strength.measureStrength(newValue));
          element.css({ "display": "inline" });
          var kids = element.children('li');

          for (var i = 0; i < kids.length; i++) {
            if (i < c.idx)
              kids[i].style.backgroundColor = c.col;
            else
              kids[i].style.backgroundColor = '#DDD';
          }
        }
      });
  
    },
    template: '<li class="point"></li><li class="point"></li><li class="point"></li><li class="point"></li><li class="point"></li>'
  };
});



ethereum.factory('Purchase', ['$http', function($http) {
  return {
    getUnspent: function(address,cb) {
      $http.get('/unspent/'+address)
        .success(function(s) { cb(null,s) })
        .error(function(e) { cb(e) })
    },
    sendTx: function(data,cb) {
      $http.post('/pushtx', data)
        .success(function(s) { cb(null,s) })
        .error(function(e) { cb(e) })
    }
  }
}]);

