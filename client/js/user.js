/** @file user.js provides methods and components used by the user view. etc. */
var app = angular.module('PtsUser', ['ngRoute']);

app.config(['$routeProvider', function ($routeProvider) {
    $routeProvider
        .when('/', {
            template: '<week-view></week-view>',
        })
        .when('/status', {
            template: '<user-status></user-status>',
        })
        .when('/profile', {
            template: '<user-profile></user-profile>',
        })
        .otherwise({ redirectTo: '/' });
}]);

/** AuthController */
app.controller('AuthController', function ($http, $window) {
    var ctrl = this;
    var state, stateEncoded = $window.localStorage.getItem('ptssession');
    if (stateEncoded) {
	var split = stateEncoded.split(',');
	try {
	    for (var i=0; i<split.length; ++i) { split[i] = atob(split[i]); }
	    console.log('decoded', split);
	    state = {email: split[0], password: split[1]};
	} catch(e) { console.log('Broken local storage token', stateEncoded, e); }
    }
    ctrl.authenticated = !!(state && state.password == 'pks');
    ctrl.email = '';
    ctrl.password = '';
    ctrl.login = function () {
	$http.post('user/auth', {email: ctrl.email, password: ctrl.password}).then(
	    function (response) {
		ctrl.authenticated = true;
		if (ctrl.remember) {
		    var encoded = btoa(ctrl.email) + ',' + btoa(ctrl.password);
		    $window.localStorage.setItem('ptssession',  encoded);
		    console.log('authenticated', ctrl.authenticated);
		    ctrl.authmessage = '';
		}
	    }).catch (function (err) {
		console.log('auth failed', err);
		ctrl.authmessage = 'Access denied';
	    });
    };

    ctrl.logout = function () {
	ctrl.authenticated = false;
	$window.localStorage.clear();
    };

});

/** Week view component */

function WeekViewController($http) {
    var ctrl = this;
    ctrl.days = [ {date: '2017-09-12', arrival: '8:00', break: '15', departure: '16:00'},
		  {date: '2017-09-13', arrival: '8:00', break: '15', departure: '16:00'}];
};

angular.module('PtsUser').component('weekView', {
    templateUrl: 'weekView.html',
    controller: WeekViewController,
    bindings: {
    }
});

/* Day type selector */
function DayTypeController () {
    var ctrl = this;
    ctrl.types = ['work', 'flex', 'vacation', 'sick' ];
};

var DayTypeTemplate = "<select>" +
    "<option ng-repeat='t in $ctrl.types'>{{ t }}</option>";

angular.module('PtsUser').component('dayTypeSelector', {
    template: DayTypeTemplate,
    controller: DayTypeController,
});
