remote_graylog = True # Should we log test results to greylog?

#########################################################################
## XXX ### The giant wall of importation devices.                      ##
#########################################################################
from behave import *                                                    # =>  Behave makes sure the API's behave, man.
import requests                                                         # =>  HTTP ez bro.
from urlparse import urljoin                                            # =>  Allows url manip.
import logging; logging.basicConfig(level=logging.CRITICAL)             # =>  Only make CRIT filtered out,
import json                                                             # =>  I presume a json api unittest will use this funct.
#########################################################################

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
    __doc__ = """Inexpensive ansi color insertion hack."""
    HEADER = '\033[95m';  OKBLUE = '\033[94m'; OKGREEN = '\033[92m'
    WARNING = '\033[93m'; FAIL   = '\033[91m' ;ENDC    = '\033[0m'

def get_status_code(status):
    try:
        return int(status)
    except TypeError:
        # Trick to accept status strings like 'not_found', as well.
        return getattr(requests.codes, status)


#############################################
from socket import *
import zlib
class Client():
        def log(self, message, server='localhost', port=12201, maxChunkSize=8154):
                graylog2_server = server
                graylog2_port = port
                maxChunkSize = maxChunkSize

                UDPSock = socket(AF_INET,SOCK_DGRAM)
                zmessage = zlib.compress(message)
                UDPSock.sendto(zmessage,(graylog2_server,graylog2_port))
                UDPSock.close()


def assertionthing(**kwargs):
    """ Assertion thing that rolls up the whole process good or bad.
    
    It's typically hooked by greylog for ops level inputs.
    """

    if kwargs.get('graylog',False) == True:
        _greylog = True
    if kwargs.get('success',False) == True:
        _success = True # If successful, we change greylogs err level
    else:
        _success = False
    verb            = kwargs.get('verb',None)               # VeRB USED
    requesturl      = kwargs.get('requesturl',None)         # REQUEST URL
    requesthead     = kwargs.get('requesthead',None)        # REQUEST HEADERS
    request         = kwargs.get('request',None)            # REQUEST 
    responsehead    = kwargs.get('responsehead',None)       # RESPONSE HEADERS
    response        = kwargs.get('response',None)           # HTTP RAW RESPONSE
    reason          = kwargs.get('reason',None)             # The reason we failed humanly aka RCA
    logic           = kwargs.get('logic',None)              # The logic why we failed 'parse error'

    # Logs some useful debugging data to stdout.
    print('HTTP.DEBUG....HTTP.DEBUG....HTTP.DEBUG....HTTP.DEBUG....HTTP.DEBUG')
    print('>>>> Request Head for (' + verb + " " + requesturl + ') <<<<')
    print(requesthead)
    print('>>>> Request Data <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
    print(request)
    print('>>>> Response Head <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
    print(responsehead)
    print('>>>> Response <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
    print(response)
    print('END.HTTP.DEBUG....END.HTTP.DEBUG....END.HTTP.DEBUG....END.HTTP.DEB')

    # This does the graylog magic out.
    if remote_graylog:
        print('pew pew pew pew pew pew pew pew pew pew pew pew pew pew pew pew pew pew pew pew ')
        print('  pew pew pew pew pew pew pew pew pew pew pew pew pew pew pew pew pew pew pew pew ')
        message = {}
        message['version']      = '1.0'
        # Level:            DEC .............. Syslog level (0=emerg, 1=alert, 2=crit, 3=err, 4=warning, 5=notice, 6=info, 7=debug)
        if _success:
            message['level']    = '6'
        else:
            message['level']    = '3'
        message['facility']     = 'GELF'
        message['host']         = 'example.com'
        message['short_message'] = str(reason)
        message['full_message'] = str(logic)
        message['_httpverb']    = str(verb)
        message['_requesturl'] = str(requesturl)
        message['_responseheaders'] = str(responsehead)
        message['_responsedata'] = str(response)
        print('::: Graylog message sent as ' + str(message))
        gelfy = Client()
        gelfy.log(json.dumps(message),'')
    
    # Raise typical unit testing exception.
    raise AssertionError(ansi.OKBLUE + "\nRESOURCE .......: " + ansi.FAIL + str(requesturl)   + 
                         ansi.OKBLUE + "\nRCA ............: " + ansi.FAIL + str(reason) +
                         ansi.OKBLUE + "\nUNDERLYING_LOGIC: " + ansi.FAIL + str(logic)  + ansi.ENDC)

# Intro banner.
if not remote_graylog:
    logging.critical(ansi.OKBLUE + "=========================================================" + ansi.ENDC)# THX STYLE INTRO
    logging.critical(ansi.OKBLUE + "testvapi :: \n                          Test {value} api\n                          Tests the values of your beloved API.\n                          " + ansi.OKGREEN + "See github for more information.\n                          https://github.com/jonkelleyatrackspace/testvapi\n                          " + ansi.FAIL + "Author: Jon_K <jon.kelley@rackspace.com>" + ansi.ENDC)# THX STYLE INTRO
    logging.critical(ansi.OKBLUE + "=========================================================" + ansi.ENDC)# THX STYLE INTRO
    

# Givens
@given('my request has the auth token "{token}"')                       #feature-complee
def step(context, token):
    """ shunt style Add x-auth-header for token automagically """
    context.execute_steps(unicode("Given my request has the header \"x-auth-token\" with the value \"{token}\"".format(token=token)))

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
@when('I get "{path}" failure means "{reason}"')                                                 #feature-complee
def step(context, path, reason):
    """ GET request within path context of server.
        You know, think: 
                        I get "cloud_account/9363835"
    """
    context.requestpath = path
    url = urljoin(context.request_endpoint, path)
    try: # There's got to be a better way to set None if missing/attributerror
        timeout = context.request_timeout
    except AttributeError:
        timeout = None

    context.response = requests.get(url, timeout=timeout,headers=context.request_headers) # Makes full response.
    try:    _requestheaders     = str(context.request_headers)
    except: _requestheaders     = None
    try:    _request            = str(payload)
    except: _request            = None
    try:    _responseheaders    = str(context.response.headers)
    except: _responseheaders    = None
    try:    _response            = str(context.response.text)
    except: _response            = "Not applicable (No data?)" 
    context.httpstate = { 'requesturi'      : url ,
                          'verb'            : 'GET' ,
                          'requestheaders'  : _requestheaders ,
                          'request'         : _request ,
                          'responseheaders' : _responseheaders ,
                          'response'        : _response ,
                        }

@when('I delete "{path}" failure means "{reason}"')                                              # TODO untested XXX
def step(context, path, reason):# XXX UNTESTED XXX
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
    try:    _requestheaders     = str(context.request_headers)
    except: _requestheaders     = None
    try:    _request            = str(payload)
    except: _request            = None
    try:    _responseheaders    = str(context.response.headers)
    except: _responseheaders    = None
    try:    _response            = str(context.response.text)
    except: _response            = "Not applicable (No data?)" 
    
    context.httpstate = { 'requesturi'      : url ,
                          'verb'            : 'DELETE' ,
                          'requestheaders'  : _requestheaders ,
                          'request'         : _request ,
                          'responseheaders' : _responseheaders ,
                          'response'        : _response ,
                        }
#TODO @when('I post "{path}" payload file "{payload}"')    
@when('I post "{path}" with payload "{payload}" failure means "{reason}"')                        # feature-complete
def step(context, path,payload, reason):
    url = urljoin(context.request_endpoint, path)
    try: # There's got to be a better way to set None if missing/attributerror
        timeout = context.request_timeout
    except AttributeError:
        timeout = None

    context.response = requests.post(url, data=payload,timeout=timeout,headers=context.request_headers) # Makes full response.
    try:    _requestheaders     = str(context.request_headers)
    except: _requestheaders     = None
    try:    _request            = str(payload)
    except: _request            = None
    try:    _responseheaders    = str(context.response.headers)
    except: _responseheaders    = None
    try:    _response            = str(context.response.text)
    except: _response            = "Not applicable (No data?)" 

    context.httpstate = { 'requesturi'      : url ,
                          'verb'            : 'POST' ,
                          'requestheaders'  : _requestheaders ,
                          'request'         : _request ,
                          'responseheaders' : _responseheaders ,
                          'response'        : _response ,
                        }
    
#TODO @when('I put "{path}" payload file "{payload}"')  
@when('I put "{path}" with payload "{payload}" failure means "{reason}"')                        # TODO untested XXX
def step(context, path,payload, reason):
    """ Entirely and completely untested """
    url = urljoin(context.request_endpoint, path)
    try: # There's got to be a better way to set None if missing/attributerror
        timeout = context.request_timeout
    except AttributeError:
        timeout = None

    context.response = requests.put(url, data=payload,timeout=timeout,headers=context.request_headers) # Makes full response.
    try:    _requestheaders     = str(context.request_headers)
    except: _requestheaders     = None
    try:    _request            = str(payload)
    except: _request            = None
    try:    _responseheaders    = str(context.response.headers)
    except: _responseheaders    = None
    try:    _response            = str(context.response.text)
    except: _response            = "Not applicable (No data?)" 

    context.httpstate = { 'requesturi'      : url ,
                          'verb'            : 'PUT' ,
                          'requestheaders'  : _requestheaders ,
                          'request'         : _request ,
                          'responseheaders' : _responseheaders ,
                          'response'        : _response ,
                        }

# TODO @when('I post "{path}" with multipart payload "{payload}"')      TODO 

##################################
# Thens
@then('the response will contain string "{text}" failure means "{reason}"')                      # feature-complete
def step(context, text, reason):
    failure_logic   = 'Did not find expected text `{text}` in response: {response}'.format(text=text,response=str( context.response.text ))
    if text not in context.response.text:
        assertionthing(verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason=reason,
                   logic=failure_logic)

@then('the response will not contain string "{text}" failure means "{reason}"')                  # feature-complete
def step(context, text, reason):
    if text in context.response.text:
        failure_logic = 'Found string `{text}` in response: {response}'.format(text=text,response=str( context.response.text ))
        assertionthing(verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason=reason,
                   logic=failure_logic)
@then('the response will have the header "{header}" with the value "{value}" failure means "{reason}"') # feature-complete
def step(context, header, value, reason):
    if context.response.headers[header] != value:
        failure_logic = 'HTTP header `{header}` => `{value}` missing in response.'.format(header=header,value=value)
        assertionthing(verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason=reason,
                   logic=failure_logic)

@then('the response will have the header "{header}" failure means "{reason}"')                   # feature-complete
def step(context, header, reason):
    if header not in context.response.headers.keys():
#        logging.debug("I saw these headers though...")
#        for k, v in context.response.headers.iteritems():
#            logging.debug("header: " + k + " => " + v)
        failure_logic = 'Missing header `{header}` in response.'.format(header=header) 
        assertionthing(verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason=reason,
                   logic=failure_logic)

@then('the response will not have the header "{header}" with the value "{value}" failure means "{reason}"')# feature-complete
def step(context, header, value, reason):
    if context.response.headers[header] == value:
        failure_logic = 'HTTP header `{header}` => `{value}` found in response.'.format(header=header,value=value)
        assertionthing(verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason=reason,
                   logic=failure_logic)

@then('the response will not have the header "{header}" failure means "{reason}"')               # feature-complete
def step(context, header,reason):
    if context.response.headers[header]:
        failure_logic = 'HTTP header `{header}` => `{value} found in response.'.format(header=header,value=context.response.headers[header] )
        assertionthing(verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason=reason,
                   logic=failure_logic)

@then('the response json will have path "{path}" with value "{value}" as "{valuetype}" failure means "{reason}"') # feature-complete
def step(context, path, value, valuetype, reason):
    # Check path exists 
    if not context.jsonsearch.pathexists(context.response.json(),path):
        """ Verify if path exists first of all... else raise() """
        failure_logic = 'Response does not have path {path}'.format(path=path)
        assertionthing(verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    reason=reason,
                    logic=failure_logic)

    # Effing unicode strings need hacks to determine their type.
    if valuetype == "int":
        value = int(value)
    elif valuetype == "str":
        value = str(value)
    elif valuetype == "unicode":
        value = unicode(value)
    elif valuetype == "bool" or valuetype == "boolean":
        if value == "true" or value == "True":
            value = True
        else:
            value=False
    # Check if value is there as desired.
    if not value in context.jsonsearch.returnpath(context.response.json(),path):
        """ Verify if value within returned list of results for that path.. else raise() """
        logging.error(ansi.OKBLUE +  "Gherkin input was " + str(type(value)) + " with value \"" + str(value) + "\" ... remote side contained a list with " + str(context.jsonsearch.returnpath(context.response.json(),path)) + "\n"+ansi.ENDC )
        failure_logic = 'Response json path {path} has no value matching {value}'.format(path=path,value=value)
        assertionthing(verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    reason=reason,
                    logic=failure_logic)

@then('the response json will not have path "{path}" with value "{value}" as "{valuetype}" failure means "{reason}"') # feature-complete
def step(context, path, value, valuetype, reason):
    # If path even exists..
    if context.jsonsearch.pathexists(context.response.json(),path):
        # Effing unicode strings need hacks to determine their type.
        if valuetype == "int":
            value = int(value)
        elif valuetype == "str":
            value = str(value)
        elif valuetype == "unicode":
            value = unicode(value)
        elif valuetype == "bool" or valuetype == "boolean":
            if value == "true" or value == "True":
                value = True
            else:
                value=False

        if value in context.jsonsearch.returnpath(context.response.json(),path):
            """ Verify if string is within path, if so raise() """
            logging.error(ansi.OKBLUE +  "Gherkin input was " + str(type(value)) + " with value \"" + str(value) + "\" ... remote side contained a list with " + str(context.jsonsearch.returnpath(context.response.json(),path)) + "\n"+ansi.ENDC )
            failure_logic = 'Response json path {path} has value matching {value}'.format(path=path,value=value)
            assertionthing(verb=context.httpstate['verb'],
                       requesturl=context.httpstate['requesturi'],
                       requesthead=context.httpstate['requestheaders'],
                       request=context.httpstate['request'],
                       responsehead=context.httpstate['responseheaders'],
                       response=context.httpstate['response'],
                       reason=reason,
                       logic=failure_logic)

@then('the response json will have path "{path}" failure means "{reason}"')                      # feature-complete
def step(context, path, reason):
    #raise Exception(context.response.json())
    if not context.jsonsearch.pathexists(context.response.json(),path):
        """ Verify if path exists first of all """
        failure_logic = 'Response does not have path {path}'.format(path=path)
        assertionthing(verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    reason=reason,
                    logic=failure_logic)

@then('the response json will not have path "{path}" failure means "{reason}"')                  # feature-complete
def step(context, path, reason):
    if context.jsonsearch.pathexists(context.response.json(),path):
        """ Verify if path exists , then fail """
        failure_logic = 'Response json has path {path}'.format(path=path)
        assertionthing(verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    reason=reason,
                    logic=failure_logic)


@then('the response will have status {status} failure means "{reason}"')
def step(context, status, reason):
    status = get_status_code(status)
    if context.response.status_code != status:
        failure_logic = 'Response status is {response.status_code}, not {status}'.format(response=context.response, status=status)
        assertionthing(verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason=reason,
                   logic=failure_logic)

@then('the response will not have status {status} failure means "{reason}"')
def step(context, status, reason):
    status = get_status_code(status)
    if context.response.status_code == status:
        failure_logic = 'Response status is {status}'.format(status=status)
        assertionthing(verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason=reason,
                   logic=failure_logic)

