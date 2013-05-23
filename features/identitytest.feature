Feature: An example how your ops/qe process can revolutionize with BDD rest tests
  See it test our identity root page. See it roar.

  Scenario Outline: Make sure root page of identity json api functioning properly.
    Given my request endpoint is "<myendpoints>"
    Given my request has a timeout of 4 seconds
    When I get "/v2.0" failure means "Identity network failure!"
    Then the response will contain string "docs.rackspacecloud.com" failure means "Documentation links missing."
    Then the response json will have path "$.version." failure means "Auth json missing?"
    Then the response json will have path "$.version.links[*].href." with value "https://identity.api.rackspacecloud.com/v2.0" as "str" failure means "Missing auth endpoint in json"
    Then the response json will have path "$.version.links[*].href." with value "http://docs.rackspacecloud.com/auth/api/v2.0/auth-client-devguide-latest.pdf" as "str" failure means "Missing documentation link in json"
    Then the response json will have path "$.version.links[*].href." with value "http://docs.rackspacecloud.com/auth/api/v2.0/auth.wadl" as "str" failure means "Missing WADL contract in json description"
    Then the response will have status 201 failure means "badHttpCode"
  Examples:
  | myendpoints |
  | https://identity.api.rackspacecloud.com |
