Feature: Test the exterior entryway of the Rackspace Public Cloud for general availability
  This is suppose to give you an idea for writing your own templates to check your own API's.
  Good luck!

  Scenario Outline: Ensure major references exist on identity frontpage.
    Given my request has the header "x-auth-token" with the value "XXXXapikeyXXXX"
    Given my request endpoint is "<myendpoints>"
    Given my request has a timeout of 10 seconds
    When I post "/account/1.0" with docstring """<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetAccountClassesRequest xmlns="http://cloud.rackspace.com/account/1.0">
      <accountId>555446</accountId>
    </GetAccountClassesRequest>
  </soap:Body>
</soap:Envelope>"""
    Then the response will have status 200
  Examples:
  | myendpoints |
  | http://smix-n01.prod.dfw1.us.ci.rackspace.net:8193 |


