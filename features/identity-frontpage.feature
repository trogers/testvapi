Feature: Test the exterior entryway of the Rackspace Public Cloud for general availability
  This is suppose to give you an idea for writing your own templates to check your own API's.
  Good luck!

  Scenario Outline: Ensure major references exist on identity frontpage.
    Given my request has the header "x-auth-token" with the value "XXXXapikeyXXXX"
    Given my request endpoint is "<myendpoints>"
    Given my request has a timeout of 10 seconds
    When I get "/" failure means "Valkyrie outage?"
    Then the response json will not have path "$.regression." with value "xxxxx" as "int" failure means "Regression bug"
    Then the response json will not have path "$.regressionx." failure means "Regression bug"
    Then the response json will have path "$.vesrsions.version[*].status." with value "CURRENT" as "str" failure means "Catalog failure"
    Then the response will have status 200 failure means "Request not processed properly."
  Examples:
  | myendpoints |
  | https://identity.api.rackspacecloud.com:443 |


