/** @file user.js provides methods and components used by the user view. etc. */
var app = angular.module('PtsUser', ['ngRoute']);

app.config(['$routeProvider', function ($routeProvider) {
    $routeProvider
        .when('/', {
            template: '<week-view></week-view>',
        })
        .when('/weeks', {
            template: '<weekly-reports></weekly-reports>',
        })
        .when('/monthly', {
            template: '<monthly-report></monthly-report>',
        })
        .when('/profile', {
            template: 'FIXME profile <user-profile></user-profile>',
        })
        .otherwise({ redirectTo: '/' });
}]);

/** Provides a filter to convert minutes to hours, with 2 decimal points. */
app.filter('minutesToHours', function() {
  return function(input) {
      return parseFloat(Math.round(input * 100/60) / 100).toFixed(2);
  };
});

app.factory('Session', ['$window', function ($window) {
    var email = '';
    var token = '';

    var state, stateEncoded = $window.localStorage.getItem('ptssession');
    if (stateEncoded) {
	var split = stateEncoded.split(',');
	try {
	    for (var i=0; i<split.length; ++i) { split[i] = atob(split[i]); }
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
		ctrl.authmessage = err.xhrStatus == 'complete' ? 'Access denied' : 'Network error';
	    });
    };

    ctrl.logout = function () {
	ctrl.authenticated = false;
	Session.clearCredentials();
    };

});

/** Week-view component is defined by its controller and its
 * template. */

function WeekViewController($http, Session) {
    var ctrl = this;
    ctrl.days = [];

    function timeToMin(timeString) {
	return (new Date('1970-01-01T'+timeString + 'Z')).getTime()/60000;
    }

    function minutesFlexDiff(day) {
	var retval = day['extra'];
	var WORKDAY_MINUTES = 60*8;
	switch (day['type']) {
	case 'work':
	    retval += (timeToMin(day['departure']) - timeToMin(day['arrival'])
		       - day['break'] - WORKDAY_MINUTES);
	    break;
	case 'flex':
	case 'sick':
	case 'vacation':
	case 'off':
	};
	return retval || 0;
    }

    /** Helper function computing current flex status.
	FIXME maybe this calculation should be done in backend only?
	@param initial: The flex status before the week start
	@param days: days array.
	@returns: Flex in hours, rounded to 2 decimal places
    */
    function computeFlex(initial, days) {
	var retval = initial || 0;
	for(var i=0; i<days.length; ++i) {
	    retval += minutesFlexDiff(days[i]);
	}
	return retval;
    };

    function init() {
	$http.get('user/' + Session.getEmail() + '/day')
	    .then(function (response) {
		ctrl.initialFlex = response.data.flex || 0;
		ctrl.days = response.data.dl;
		ctrl.flexhours = computeFlex(ctrl.initialFlex, ctrl.days);
	    }).catch(function (err) {
		console.log('got error', err);
	    });
    }

    ctrl.update = function (day) {
	$http.post('user/' + Session.getEmail() + '/day', day)
	    .then(function (response) {
		ctrl.flexhours = computeFlex(ctrl.initialFlex, ctrl.days);
		console.log('Patch succeeded', response);
	    }).catch(function (err) {
		console.log('Update got error', err);
	    });
    };

    ctrl.lock = function () {
	var range = {start: ctrl.days[0]['date'],
		     end: ctrl.days[ctrl.days.length-1]['date']};
	$http.post('user/' + Session.getEmail() + '/report', range)
	    .then(function (response) {
		init(); /* load data of next week! */
	    }).catch(function (err) {
		console.log('Update got error', err);
	    });
    };

    init();
};

angular.module('PtsUser').component('weekView', {
    templateUrl: 'weekView.html',
    controller: WeekViewController,
    bindings: {
    }
});


/** Weekly report, used mostly to get overview over vacation and
 * overtime status. */
function WeeklyReportsController($http, Session) {
    var ctrl = this;
    ctrl.days = [];
    $http.get('user/' + Session.getEmail() + '/report')
	.then(function (response) {
	    ctrl.reports = response.data.report;
	}).catch( function (err) {
	    console.log('got error', err);
	});
};

angular.module('PtsUser').component('weeklyReports', {
    templateUrl: 'weeklyReport.html',
    controller: WeeklyReportsController,
    bindings: {
    }
});


/* Simple day type selector */
function DayTypeController () {
    var ctrl = this;
    ctrl.types = ['work', 'flex', 'vacation', 'sick', 'off' ];
};

var DayTypeTemplate = "<select ng-model='$ctrl.type' ng-options='t for t in $ctrl.types'></select>";

angular.module('PtsUser').component('dayTypeSelector', {
    template: DayTypeTemplate,
    controller: DayTypeController,
    bindings: {
	type: '='
    }
});
