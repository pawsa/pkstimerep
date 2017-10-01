/** @file provides basic routing etc. */
var app = angular.module('PtsAdmin', ['ngRoute']);

app.config(['$routeProvider', function ($routeProvider) {
    $routeProvider
        .when('/', {
            template: '<user-list></user-list>',
        })
        .when('/holidays', {
            template: '<holidays></holidays>',
        })
        .otherwise({ redirectTo: '/' });
}]);


/** User List component */
function UserListController($http) {
    var ctrl = this;
    function loadUsers () {
	$http.get('user').then(function (response) {
	    ctrl.users = response.data.users;
	}).catch(function (err) {
	    console.log('show notify', err);
	});
    };
    
    ctrl.onAdd = function () {
	loadUsers();
    };
    ctrl.users = [];
    loadUsers();
};

angular.module('PtsAdmin').component('userList', {
    templateUrl: 'components/userList.html',
    controller: UserListController,
    bindings: {
    }
});

/** User add component */
function UserAddController($http) {
    var ctrl = this;

    ctrl.showAdd = function() {
	ctrl.inputsShown = true;
    };

    ctrl.add = function () {
	$http.post('user', {email: ctrl.email, name: ctrl.name,
			    password: ctrl.password,
			    status: 'active'}).then(
	    function (response) {	
		ctrl.inputsShown = false;
		ctrl.email = ctrl.name = ctrl.password = '';
		ctrl.onAdd();
	    }).catch(function (err) {
		console.log('error', err);
	    });
    };	
};

var UserAddTemplate = "<button class='btn btn-default' ng-click='$ctrl.showAdd()' ng-if='!$ctrl.inputsShown'>Add</button>"+
    "<div ng-if='$ctrl.inputsShown'><input ng-model='$ctrl.email' placeholder='Email'>" +
    "<input ng-model='$ctrl.name' placeholder='Real Name'>" +
    "<input ng-model='$ctrl.password' placeholder='Password' type='password'>" +
    "<button class='btn btn-default' ng-click='$ctrl.add()'>Add</button></div>";

angular.module('PtsAdmin').component('userAdd', {
    template: UserAddTemplate,
    controller: UserAddController,
    bindings: {
	onAdd: '&'
    }
});



/** Holidays component */
function HolidayController ($http) {
    var ctrl = this;
    function loadHolidays () {
	$http.get('holiday', {params: {year: ctrl.year}}).then(function (response) {
	    ctrl.holidays = response.data.rdl;
	}).catch(function (err) {
	    console.log('holiday load err', err);
	});
    };

    ctrl.onYearChange = function () {
	loadHolidays();
    };
    ctrl.holidays = [];
    loadHolidays();
};

angular.module('PtsAdmin').component('holidays', {
    templateUrl: 'components/holidays.html',
    controller: HolidayController
});

