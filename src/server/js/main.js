var Tools = {
    clearObject: function(obj) {
        'use strict';

        var prop;

        for (prop in obj) {
            if (obj.hasOwnProperty(prop)) {
                delete obj[prop];
            }
        }
    },
    extend: function(obj, src) {
        'use strict';

        var prop;

        for (prop in src) {
            if (src.hasOwnProperty(prop)) {
                obj[prop] = src[prop];
            }
        }
    }
};

var app = angular.module('RESTApp', ['ngResource', 'ngPrettyJson']),
    urls = {
        make_request: '/requests/:request/:server/make/',
        request: '/requests/:request/',
        requests: '/requests/',
        server: '/servers/:server/',
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
app.directive('prettyjsonEditable', [
    '$q',
    function(
        $q
    ) {
        'use strict';

        return {
            scope: {
                ngModel: '=',
                ngSave: '='
            },
            restrict: 'A',
            templateUrl: '/static/js/prettyjson-editable.html',
            link: function(scope, element, attrs) {
                var computeStringModel = function() {
                    scope.stringModel = JSON.stringify(scope.ngModel, null, 4);
                };
                var computeModel = function() {
                    Tools.clearObject(scope.ngModel);
                    Tools.extend(scope.ngModel, JSON.parse(scope.stringModel));
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

                    $q.when(scope.ngSave()).then(function() {
                        scope.control.view = 'json';
                    });
                };
            }  // link
        };  // return
    }  // function
]);  // app.directive('prettyjsonEditable'


app.directive('requestView', [
    '$rootScope',
    '$resource',
    function(
        $rootScope,
        $resource
    ) {
        'use strict';

        return {
            scope: {
                ngModel: '=',
                ngServer: '='
            },
            templateUrl: '/static/js/request-view.html',
            restrict: 'A',
            link: function(scope, element, attrs) {
                var makeRequestResource = $resource(urls.make_request),
                    requestResource = $resource(urls.request),
                    oldName = scope.ngModel.name;

                scope.requestResult = null;

                scope.control = {
                    expand: false
                };

                scope.make_request = function() {
                    makeRequestResource.query({
                        request: scope.ngModel.name,
                        server: scope.ngServer.name
                    }).$promise.then(function(data) {
                        scope.requestResult = data;
                    });
                };

                scope.clearRequestResult = function() {
                    scope.requestResult = null;
                };

                scope.clone = function() {
                    var name = scope.ngModel.name,
                        idx = name.indexOf('.json');

                    if(idx === -1) {
                        name = name + '~';
                    } else {
                       name = name.slice(0, idx) + '~.json';
                    }

                    requestResource.save(
                        {request: name},
                        scope.ngModel
                    ).$promise.then(function() {
                        $rootScope.$broadcast('fetch-requests');
                    });
                };

                scope.delete = function() {
                    if(confirm('Delete' + scope.ngModel.name + '. Are you sure?')) {
                        requestResource.delete(
                            {request: scope.ngModel.name}
                        ).$promise.then(function() {
                                $rootScope.$broadcast('fetch-requests');
                            });
                    }
                };

                scope.save_request = function() {
                    requestResource.save(
                        {request: scope.ngModel.name},
                        scope.ngModel
                    ).$promise.then(function() {
                        if(oldName !== scope.ngModel.name) {
                            requestResource.delete(
                                {request: oldName}
                            ).$promise.then(function() {
                                oldName = scope.ngModel.name;

                                $rootScope.$broadcast('fetch-requests');
                            });
                        }
                    });
                };

                scope.expand_toggle = function() {
                    // If expanded view is present, save model under new name
                    if(scope.control.expand) {
                        scope.save_request();
                    }

                    scope.control.expand = !scope.control.expand;
                };
            }  // link
        };  // return
    }  // function
]);  // app.directive('requestView'


app.directive('serverView', [
    '$rootScope',
    '$resource',
    function(
        $rootScope,
        $resource
    ) {
        'use strict';

        return {
            scope: {
                ngModel: '='
            },
            templateUrl: '/static/js/server-view.html',
            restrict: 'A',
            link: function(scope, element, attrs) {
                var serverResource = $resource(urls.server),
                    oldName = scope.ngModel.name;

                scope.control = {
                    expand: false
                };

                scope.clone = function() {
                    var name = scope.ngModel.name,
                        idx = name.indexOf('.json');

                    if(idx === -1) {
                        name = name + '~';
                    } else {
                        name = name.slice(0, idx) + '~.json';
                    }

                    serverResource.save(
                        {server: name},
                        scope.ngModel
                    ).$promise.then(function() {
                        $rootScope.$broadcast('fetch-servers');
                    });
                };

                scope.delete = function() {
                    if(confirm('Delete ' + scope.ngModel.name + '. Are you sure?')) {
                        serverResource.delete(
                            {server: scope.ngModel.name}
                        ).$promise.then(function () {
                            $rootScope.$broadcast('fetch-servers');
                        });
                    }
                };

                scope.save_server = function() {
                    serverResource.save(
                        {server: scope.ngModel.name},
                        scope.ngModel
                    ).$promise.then(function() {
                        if(oldName !== scope.ngModel.name) {
                            serverResource.delete(
                                {server: oldName}
                            ).$promise.then(function() {
                                oldName = scope.ngModel.name;

                                $rootScope.$broadcast('fetch-servers');
                            });
                        }
                    });
                };

                scope.expand_toggle = function() {
                    // If expanded view is present, save model under new name
                    if(scope.control.expand) {
                        scope.save_server();
                    }

                    scope.control.expand = !scope.control.expand;
                };
            }  // link
        };  // return
    }  // function
]);  // app.directive('serverView'


var MainController = [
    '$scope',
    '$rootScope',
    '$resource',
    function(
        $scope,
        $rootScope,
        $resource
    ) {
        'use strict';

        var requestsResource = $resource(urls.requests),
            serversResource = $resource(urls.servers);

        $scope.control = {
            view: 'servers',
            searchText: ''
        };

        $scope.server = null;

        $rootScope.$on('fetch-requests', function() {
            $scope.requests = requestsResource.query();
        });
        $rootScope.$broadcast('fetch-requests');

        $rootScope.$on('fetch-servers', function() {
            $scope.servers = serversResource.query();
        });
        $rootScope.$broadcast('fetch-servers');

        $scope.servers.$promise.then(function(data) {
            $scope.server = data[0];
        });
    }
];
