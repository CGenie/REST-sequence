var app = angular.module('RESTApp', ['ngResource', 'ngPrettyJson']),
    urls = {
        make_request: '/requests/:request/:server/make/',
        requests: '/requests/',
        servers: '/servers/'
    };

app.config([
    '$interpolateProvider',
    function(
        $interpolateProvider
    ) {
        'use strict';

        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
    }
]);


// directives
app.directive('requestView', [
    '$resource',
    function(
        $resource
    ) {
        return {
            scope: {
                ngModel: '=',
                ngServers: '=',
                ngFilter: '=?'
            },
            templateUrl: '/static/js/request-view.html',
            restrict: 'A',
            link: function(scope, element, attrs) {
                var makeRequestResource = $resource(urls.make_request);

                scope.requestResult = null;
                scope.server = scope.ngServers[0];

                scope.control = {
                    expand: false
                };

                scope.make_request = function() {
                    var requestResult = makeRequestResource.query({
                        request: scope.ngModel.name,
                        server: scope.server.name
                    }).$promise.then(function(data) {
                        scope.requestResult = data;
                    });
                };

                scope.clearRequestResult = function() {
                    scope.requestResult = null;
                };
            }  // link
        };  // return
    }  // function
]);  // app.directive('requestView'


app.directive('serverView', [
    function(
    ) {
        return {
            scope: {
                ngModel: '='
            },
            templateUrl: '/static/js/server-view.html',
            restrict: 'A',
            link: function(scope, element, attrs) {
                scope.control = {
                    expand: false
                };
            }  // link
        };  // return
    }  // function
]);  // app.directive('serverView'


app.directive('prettyjsonEditable', [
    function(
    ) {
        return {
            scope: {
                ngModel: '='
            },
            restrict: 'A',
            templateUrl: '/static/js/prettyjson-editable.html',
            link: function(scope, element, attrs) {
                var computeStringModel = function() {
                    scope.stringModel = JSON.stringify(scope.ngModel, null, 4);
                };
                var computeModel = function() {
                    scope.ngModel = JSON.parse(scope.stringModel);
                };
                computeStringModel();

                scope.control = {
                    view: 'json'  // 'json' or 'text'
                };

                scope.text_view = function() {
                    computeStringModel();

                    scope.control.view = 'text';
                };

                scope.json_view = function() {
                    computeModel();

                    scope.control.view = 'json';
                };
            }  // link
        };  // return
    }  // function
]);  // app.directive('prettyjsonEditable'


var MainController = [
    '$scope',
    '$resource',
    function(
        $scope,
        $resource
    ) {
        'use strict';

        var requestsResource = $resource(urls.requests),
            serversResource = $resource(urls.servers);

        $scope.control = {
            view: 'servers',
            searchText: ''
        };

        $scope.requests = requestsResource.query();
        $scope.servers = serversResource.query();
    }
];
