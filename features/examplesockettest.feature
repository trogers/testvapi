Feature: Maybe testing sockets is important to you.

  Scenario: Test socket addressfailure
    Given I send a socket to test.aol.com
    When I connect on port 666 it must respond within 1 second
    
  Scenario: Test socket timeout
    Given I send a socket to aol.com
    When I connect on port 666 it must respond within 1 second

  Scenario: Test socket error
    Given I send a socket to aol.com
    When I connect on port 65536 it must respond within 1 second

  Scenario: The only working one
    Given I send a socket to google.com
    When I connect on port 80 it must respond within 11 seconds
