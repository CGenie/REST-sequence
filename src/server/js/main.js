var app = angular.module('RESTApp', ['ngResource', 'ngPrettyJson']);

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

var MainController = [
    '$scope',
    '$resource',
    function(
        $scope,
        $resource
    ) {
        'use strict';

        var urls = {
            requests: '/requests/',
            servers: '/servers/'
        },
            requestsResource = $resource(urls.requests),
            serversResource = $resource(urls.servers);

        $scope.control = {
            view: 'servers'
        };

        $scope.requests = requestsResource.query();
        $scope.servers = serversResource.query();
    }
];
