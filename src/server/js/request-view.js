(function(app) {
    app.directive('requestView', [
        function(
            ) {
            return {
                scope: {
                    ngModel: '='
                },
                templateUrl: '/static/js/request-view.html',
                restrict: 'A',
                link: function(scope, element, attrs) {

                }
            };
        }
    ]);
}(app));
