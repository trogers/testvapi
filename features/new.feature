Feature: Ensure auth API meets some basic checks without authorization.
  As the ops / qe person
  I want to make sure identity API works publically at a basic level.
  Else throw some awesome alerts to why.

  Scenario: Test GET on cloud identity root namespace
    #Given my request has the auth token "12345"
    Given my request has the header "x-who-am-i" with the value "testvalueapi (qe+ops checks) (https://github.com/jonkelleyatrackspace/testvapi)"
    And my request endpoint is "https://identity.api.rackspacecloud.com"
    And my request has a timeout of 1 seconds
     When I get "/"
     Then the response will contain string "doc"
     And the response will NOT contain string "FAILURE_CODE"
     And the response will have the header "Content-Type" with the value "application/json"
     And the response will NOT have the header "transfer-encoding" with the value "regression-bug"
     And the response will NOT have the header "x-horrible-regression-bug"
     And the response json will have path "versions.version[*].status"
     And the response json will have path "versions.version[*].status" with value "DEPRECATED"
     And the response json will NOT have path "versions.version[*].statuss"
     And the response json will NOT have path "versions.version[*].status" with value "DEPRECATEsD"
     #And the response json will have path "unimplement" containing regex "DEPRECIATED"
     #And the response json will NOT have path "uninplement" containing regex "DEPRECIATED"
     And the response will NOT have status 999
     And the response will have status 200


