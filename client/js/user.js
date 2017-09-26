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

app.factory('Session', ['$window', function ($window) {
    var email = '';
    var token = '';

    var state, stateEncoded = $window.localStorage.getItem('ptssession');
    if (stateEncoded) {
	var split = stateEncoded.split(',');
	try {
	    for (var i=0; i<split.length; ++i) { split[i] = atob(split[i]); }
	    console.log('decoded', split);
	    email = split[0];
	    token= split[1];
	} catch(e) { console.log('Broken local storage token', stateEncoded, e); }
    }
    return {
	getEmail: function () { return email; },
	getToken: function () { return token; },
	setCredentials: function (email, token) {
	    var encoded = btoa(email) + ',' + btoa(token);
	    $window.localStorage.setItem('ptssession',  encoded);
	},
	clearCredentials: function () {
	    email = token = '';
	    $window.localStorage.clear();
	}
    };
}]);

/** AuthController */
app.controller('AuthController', function ($http, Session) {
    var ctrl = this;
    ctrl.authenticated = !!Session.getToken();
    ctrl.email = '';
    ctrl.password = '';
    ctrl.login = function () {
	$http.post('user/auth', {email: ctrl.email, password: ctrl.password}).then(
	    function (response) {
		ctrl.authenticated = true;
		if (ctrl.remember) {
		    Session.setCredentials(ctrl.email, response.data.token);
		    ctrl.authmessage = '';
		}
	    }).catch (function (err) {
		console.log('auth failed', err);
		ctrl.authmessage = 'Access denied';
	    });
    };

    ctrl.logout = function () {
	ctrl.authenticated = false;
	Session.clearCredentials();
    };

});

/** Week view component */

function WeekViewController($http, Session) {
    var ctrl = this;
    ctrl.days = [];
    $http.get('user/' + Session.getEmail() + '/day')
	.then(function (response) {
	    ctrl.days = response.data.dl;
	}).catch(function (err) {
	    console.log('got error', err);
	});

    ctrl.update = function (day) {
	$http.post('user/' + Session.getEmail() + '/day', day)
	.then(function (response) {
	    console.log('Patch succeeded', response);
	}).catch(function (err) {
	    console.log('Update got error', err);
	});
    };
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
