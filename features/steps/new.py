""" This step test implements RESTful API testing towards any API, 
    but specifically tailored for Rackspace API testing.
    
    This fancy revolutionary thing written by Jon for ops and qe all over the world.

    - Jonathan Kelley, May 12 ; 2013 ->>>- jon.kelley@rackspace.com

    The current gherkin test file syntax conformity is:
        This should go within the features/ directory as: featurename.feature
        /opt/testv/features/testapi.feature:::
        Feature: Ensure auth API meets some basic checks.
        As the ops / qe person
        I want to make sure identity API works.
        If it doesnt, I want this test to fail.
        
        Scenario: Test GET on cloud identity root
            Given my request has the auth token "12345"
            And my request has the header "jon_was_here" with the value "true"
            And my request endpoint is "https://identity.api.rackspacecloud.com"
            And my request has a timeout of 1 seconds
            When I get "/"
            Then the response will contain string "http://docs.rackspacecloud.com/auth/api/v2.0/auth.wadl"
            And the response will NOT contain string "FAILURE_CODE"
            And the response will have the header "Content-Type" with the value "application/json"
            And the response will NOT have the header "transfer-encoding" with the value "regression-bug"
            And the response will NOT have the header "x-horrible-regression-bug"
            And the response json will have path "versions.version[*].status"
            And the response json will have path "versions.version[*].status" with value "sssDEPRECATED"
            And the response json will NOT have path "versions.version[*].statuss"
            And the response json will NOT have path "versions.version[*].status" with value "DEPRECATEsD"
            And the response will NOT have status 999
            And the response will have status 201

    """
class ansi:
    __doc__ = "Just a cheap way to hijack ansi colors into strings. Muahahaha.."
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

#########################################################################
## XXX ### The giant wall of importation devices.                      ##
#########################################################################
from behave import *                                                    # =>  Behave makes sure the API's behave, man.
import requests                                                         # =>  HTTP ez bro.
from urlparse import urljoin                                            # =>  Allows url manip.
import logging; logging.basicConfig(level=logging.CRITICAL)             # =>  Only make CRIT filtered out,
import json                                                             # =>  I presume a json api unittest will use this funct.
#########################################################################
logging.critical(ansi.OKBLUE + "=========================================================" + ansi.ENDC)# THX STYLE INTRO
logging.critical(ansi.OKBLUE + "testvapi :: \n                          Test {value} api\n                          Tests the values of your beloved API.\n                          " + ansi.OKGREEN + "See github for more information.\n                          https://github.com/jonkelleyatrackspace/testvapi\n                          " + ansi.FAIL + "Author: Jon_K <jon.kelley@rackspace.com>" + ansi.ENDC)# THX STYLE INTRO
logging.critical(ansi.OKBLUE + "=========================================================" + ansi.ENDC)# THX STYLE INTRO
# Givens
@given('my request has the auth token "{token}"')                       #feature-complee
def step(context, token):
    context.execute_steps('My request has the HTTP header X-Auth-Token with the value ' + token)

@given('my request has the header "{header}" with the value "{value}"') #feature-complee
def step(context, header, value):
    context.request_headers[header] = value

@given('my request endpoint is "{endpoint}"')                           #feature-complee
def step(context, endpoint):
    """ This is where you want to define what python.requests should connect to.
        You know, think:
                        my request endpoint is "https://myendpoint.local:30000"
                        my request endpoint is "http://127.0.0.1"
    """
    context.request_endpoint = endpoint

@given('my request has a timeout of {seconds} seconds')                 #feature-complee
def step(context, seconds):
    """ This is where you want to define how long is TOO LONG for the server to responde to your requests.
        This should throw a red flag if the API is problematic.
        You know, think:
                        my request endpoint is "https://myendpoint.local:30000"
                        my request endpoint is "http://127.0.0.1"
    """
    context.request_timeout = float(seconds)

##################################
# Whens
@when('I get "{path}"')                                                 #feature-complee
def step(context, path):
    """ GET request within path context of server.
        You know, think: 
                        I get "cloud_account/9363835"
    """
    url = urljoin(context.request_endpoint, path)
    try: # There's got to be a better way to set None if missing/attributerror
        timeout = context.request_timeout
    except AttributeError:
        timeout = None

    context.response = requests.get(url, timeout=timeout,headers=context.request_headers) # Makes full response.
    logging.info("=================== HTTP REQUEST HEADERS   =================== \n" + str(context.request_headers))
    logging.info("=================== HTTP RESPONSE HEADERS  =================== \n" + str(context.response.headers))
    logging.info("=================== HTTP RESPONSE          =================== \n" + json.dumps(context.response.json()))

@when('I delete "{path}"')                                              # TODO untested XXX
def step(context, path):# XXX UNTESTED XXX
    """ Entirely untested.
        DELETE request within path context of server.
        You know, think: 
                        I delete "server/entity/id/9363835"
    """
    url = urljoin(context.request_endpoint, path)
    try: # There's got to be a better way to set None if missing/attributerror
        timeout = context.request_timeout
    except AttributeError:
        timeout = None

    context.response = requests.delete(url,timeout=timeout,headers=context.request_headers) # Makes full response.
    logging.info("=================== HTTP REQUEST HEADERS   =================== \n" + str(context.request_headers))
    logging.info("=================== HTTP RESPONSE HEADERS  =================== \n" + str(context.response.headers))
    logging.info("=================== HTTP RESPONSE          =================== \n" + json.dumps(context.response.json()))

#TODO @when('I post "{path}" payload file "{payload}"')    
@when('I post "{path}" with payload "{payload}"')                        # feature-complete
def step(context, path,payload):
    url = urljoin(context.request_endpoint, path)
    try: # There's got to be a better way to set None if missing/attributerror
        timeout = context.request_timeout
    except AttributeError:
        timeout = None

    context.response = requests.post(url, data=payload,timeout=timeout,headers=context.request_headers) # Makes full response.
    logging.info("=================== HTTP REQUEST HEADERS   =================== \n" + str(context.request_headers))
    logging.info("=================== HTTP REQUEST           =================== \n" + str(payload))
    logging.info("=================== HTTP RESPONSE HEADERS  =================== \n" + str(context.response.headers))
    logging.info("=================== HTTP RESPONSE          =================== \n" + json.dumps(context.response.json()))

#TODO @when('I put "{path}" payload file "{payload}"')  
@when('I put "{path}" with payload "{payload}"')                        # TODO untested XXX
def step(context, path,payload):
    """ Entirely and completely untested """
    url = urljoin(context.request_endpoint, path)
    try: # There's got to be a better way to set None if missing/attributerror
        timeout = context.request_timeout
    except AttributeError:
        timeout = None

    context.response = requests.put(url, data=payload,timeout=timeout,headers=context.request_headers) # Makes full response.
    logging.info("=================== HTTP REQUEST HEADERS   =================== \n" + str(context.request_headers))
    logging.info("=================== HTTP REQUEST           =================== \n" + str(payload))
    logging.info("=================== HTTP RESPONSE HEADERS  =================== \n" + str(context.response.headers))

# TODO @when('I post "{path}" with multipart payload "{payload}"')      TODO 

##################################
# Thens
@then('the response will contain string "{text}"')                      # feature-complete
def step(context, text):
    if text not in context.response.text:
        raise AssertionError('Did not find `{text}` in response: {response}'.format(text=text,response=str( context.response.json() )))
     
@then('the response will not contain string "{text}"')                  # feature-complete
def step(context, text):
    if text in context.response.text:
        raise AssertionError('Found string `{text}` in response: {response}'.format(text=text,response=str( context.response.json() )))

@then('the response will have the header "{header}" with the value "{value}"') # feature-complete
def step(context, header, value):
    if context.response.headers[header] != value:
        raise AssertionError('HTTP header `{header}` => `{value}` missing in response.'.format(header=header,value=value) )

@then('the response will have the header "{header}"')                   # feature-complete
def step(context, header):
    if header not in context.response.headers.keys():
#        logging.debug("I saw these headers though...")
#        for k, v in context.response.headers.iteritems():
#            logging.debug("header: " + k + " => " + v)
        raise AssertionError('Missing header `{header}` in response.'.format(header=header) )

@then('the response will not have the header "{header}" with the value "{value}"')# feature-complete
def step(context, header, value):
    if context.response.headers[header] == value:
        raise AssertionError('HTTP header `{header}` => `{value}` found in response.'.format(header=header,value=value) )

@then('the response will not have the header "{header}"')               # feature-complete
def step(context, header):
    if context.response.headers[header]:
        raise AssertionError('HTTP header `{header}` => `{value} found in response.'.format(header=header,value=context.response.headers[header] ))

@then('the response json will have path "{path}" with value "{value}"') # feature-complete
def step(context, path, value):
    # Check path exists 
    if not context.jsonsearch.pathexists(context.response.json(),path,None):
        raise AssertionError('Response json does not have path {path}'.format(path=path))

    # Check value exists 
    if not value in context.jsonsearch.returnpath(context.response.json(),path):
        raise AssertionError('Response json path {path} has no value matching {value}'.format(path=path,value=value))

@then('the response json will not have path "{path}" with value "{value}"') # feature-complete
def step(context, path, value):
    # Check path exists 
    if context.jsonsearch.pathexists(context.response.json(),path,None):
        # Check value exists 
        if value in context.jsonsearch.returnpath(context.response.json(),path):
            raise AssertionError('Response json path {path} has value matching {value}'.format(path=path,value=value))

@then('the response json will have path "{path}"')                      # feature-complete
def step(context, path):
    #raise Exception(context.response.json())
    if not context.jsonsearch.pathexists(context.response.json(),path,None):
        raise AssertionError('Response json does not have path {path}'.format(path=path))

@then('the response json will not have path "{path}"')                  # feature-complete
def step(context, path):
    #raise Exception(context.response.json())
    if context.jsonsearch.pathexists(context.response.json(),path,None):
        raise AssertionError('Response json does not have path {path}'.format(path=path))

def get_status_code(status):
    try:
        return int(status)
    except TypeError:
        # Trick to accept status strings like 'not_found', as well.
        return getattr(requests.codes, status)

@then('the response will have status {status}')
def step(context, status):
    status = get_status_code(status)
    if context.response.status_code != status:
        raise AssertionError('Response status is {response.status_code}, not {status}'.format(response=context.response, status=status))

@then('the response will not have status {status}')
def step(context, status):
    status = get_status_code(status)
    if context.response.status_code == status:
        raise AssertionError('Response status is {status}'.format(status=status))
