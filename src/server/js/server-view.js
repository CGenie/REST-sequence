(function(app) {
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

                }
            };
        }
    ]);
}(app));