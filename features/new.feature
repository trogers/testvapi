Feature: Ensure auth API meets some basic checks without authorization.
  As the ops / qe person
  I want to make sure identity API works publically at a basic level.
  Else throw some awesome alerts to why.

  Scenario: Test GET on cloud identity root namespace
    #Given my request has the auth token "12345"
    Given my request has the header "x-who-am-i" with the value "testvalueapi (qe+ops checks) (https://github.com/jonkelleyatrackspace/testvapi)"
    And my request endpoint is "https://identity.api.rackspacecloud.com"
    And my request has a timeout of 1 seconds
     When I get "/" failure means "critical http failure"
     Then the response will contain string "dossc" failure means "Missing documentation URI"
     And the response will NOT contain string "FAILURE_CODE" failure means "errorcode in body"
     And the response will have the header "Content-Type" with the value "application/json" failure means "Unexpected content-type!!!"
     And the response will NOT have the header "transfer-encoding" with the value "regression-bug" failure means "make sure regression D-39393 gone"
     And the response will NOT have the header "x-horrible-regression-bug" failure means "make sure regression D-39393 gone"
     And the response json will have path "versions.version[*].status" failure means "JSON catalog is broken"
     And the response json will have path "versions.version[*].stsatus" with value "DEPRECATED" failure means "JSON catalog is broken"
     And the response json will NOT have path "versions.version[*].statuss" failure means "JSON catalog is broken"
     And the response json will NOT have path "versions.version[*].status" with value "DEPRECATEsD" failure means "JSON catalog is broken"
     And the response will NOT have status 999 failure means "critical error"
     And the response will have status 200 failure means "status not ok"


  Scenario: Test GET on cloud identity root namespace
    #Given my request has the auth token "12345"
    Given my request has the header "x-who-am-i" with the value "testvalueapi (qe+ops checks) (https://github.com/jonkelleyatrackspace/testvapi)"
    And my request endpoint is "https://identity.api.rackspacecloud.com"
    And my request has a timeout of 1 seconds
     When I get "//" failure means "critical http failure"
     Then the response will contain string "doc" failure means "Missing documentation URI"
     And the response will NOT contain string "FAILURE_CODE" failure means "errorcode in body"
     And the response will have the header "Content-Type" with the value "application/json" failure means "Unexpected content-type!!!"
     And the response will NOT have the header "transfer-encoding" with the value "regression-bug" failure means "make sure regression D-39393 gone"
     And the response will NOT have the header "x-horrible-regression-bug" failure means "make sure regression D-39393 gone"
     And the response json will have path "versions.version[*].status" failure means "JSON catalog is broken"
     And the response json will have path "versions.version[*].status" with value "DEPRECATED" failure means "JSON catalog is broken"
     And the response json will NOT have path "versions.version[*].status" failure means "JSON catalog is broken"
     And the response json will NOT have path "versions.version[*].status" with value "DEPRECATEsD" failure means "JSON catalog is broken"
     And the response will NOT have status 999 failure means "critical error"
     And the response will have status 200 failure means "status not ok"


