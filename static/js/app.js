var formApp = angular.module('formApp', [])

    .controller('formController', function($scope, $http) {
        $scope.formData = {};
        
        $scope.submitForm = function () {
            var requestContent = {}

            requestContent['userid'] = "Test"
            requestContent['ranktype'] = "test"
            requestContent['answerchecked'] = 1

            $http({
                method: 'POST',
                url: '/meiva/api/rankfiler/new',
                data: requestContent,
                header: {
                    "Content-Type": "application/json"
                }
            }).then(
            function (success) {
                $scope.result = success.data
            },
            function (error) {
                $scope.error = error.data.message
            })
        }
    });