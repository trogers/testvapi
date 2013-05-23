
graylog_server = False # False value means turn greylogging off.
graylog_facility = 'valkyrietest.GELF'

#########################################################################
## XXX ### The giant wall of importation devices.                      ##
#########################################################################
from behave import *                                                    # =>  Behave makes sure the API's behave, man.
import requests                                                         # =>  HTTP ez bro.
from urlparse import urljoin                                            # =>  Allows url manip.
from urlparse import urlparse                                           # =>  For greylog gethostname byurl
import logging; logging.basicConfig(level=logging.CRITICAL)             # =>  Only make CRIT filtered out,
import json                                                             # =>  I presume a json api unittest will use this funct.
import traceback                                                        # =>  traceback.format_exc()!
import time                                                             # =>  Benchmarking.
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
    statuscode     = kwargs.get('statuscode',None)
    latency     = kwargs.get('latency',None)
    latency     = "%.*f" % ( 3, latency ) # Strip off all but 3 char
    gherkinstep     = kwargs.get('gherkinstep',None)
    if kwargs.get('success',False) == True:
        _success = True # If successful, we change greylogs err level
    else:
        _success = False
    verb            = kwargs.get('verb',None)               # VeRB USED
    requesturl      = kwargs.get('requesturl',None)         # REQUEST URL
    requestpath     = urlparse(requesturl).path
    host            = urlparse(requesturl).netloc.split(":")[0] # Gets just hostname
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
    if graylog_server:
        message = {}
        message['version']      = '1.0'
        # Level:            DEC .............. Syslog level (0=emerg, 1=alert, 2=crit, 3=err, 4=warning, 5=notice, 6=info, 7=debug)
        if _success:    message['level']            = '6'
        else:           message['level']            = '3'
        message['facility']                         = graylog_facility
        message['host']                             = str(host)
        if _success:    message['short_message']    = 'OK: ' + str(requestpath) + " - " + str(gherkinstep)
        else:           message['short_message']    = 'FAIL: ' + str(requestpath) + " - " + str(gherkinstep)

        message['full_message'] = '=======Request=======\n' + str(request) + '\n\n\n=======Response=======\n' + 'Headers:\n' + str(responsehead) + '\n\nBody:\n' + str(response)
        message['_testrequirements']      = str(gherkinstep)
        message['_testoutcome']      = str(logic)
        message['_http_verb']                    = str(verb)
        message['_http_status']                  = str(statuscode)
        message['_http_latency']                 = str(latency)
        message['_url']                     = str(requesturl)
        message['_path']                     = str(requestpath)
        print('::: Graylog message sent as ' + str(message))
        gelfy = Client()
        gelfy.log(json.dumps(message),graylog_server) # writeout 


    # Raise typical unit testing exception.
    if not _success:
        raise AssertionError(ansi.OKBLUE + "\nRESOURCE .......: " + ansi.FAIL + str(requesturl)   + 
                             ansi.OKBLUE + "\nRCA ............: " + ansi.FAIL + str(reason) +
                             ansi.OKBLUE + "\nUNDERLYING_LOGIC: " + ansi.FAIL + str(logic)  + ansi.ENDC)

# Intro banner.
if not graylog_server:
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
    stepsyntax = "I get {path}".format(path=path)
    try:
        context.requestpath = path
        url = urljoin(context.request_endpoint, path)
        try: # There's got to be a better way to set None if missing/attributerror
            timeout = context.request_timeout
        except AttributeError:
            timeout = None

        timebench_before = time.time()
        context.response = requests.get(url, timeout=timeout,headers=context.request_headers) # Makes full response.
        timebench_after = time.time()
        
        _latency = timebench_after - timebench_before
        try:    _statuscode         = str(context.response.status_code)
        except: _statuscode         = '-1'
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
                              'latency'         : _latency,
                              'statuscode'      : _statuscode
                            }
    except:
        failure_logic = traceback.format_exc()
        assertionthing(success=False,verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    reason=reason, gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@when('I delete "{path}" failure means "{reason}"')                                              # TODO untested XXX
def step(context, path, reason):# XXX UNTESTED XXX
    """ Entirely untested.
        DELETE request within path context of server.
        You know, think: 
                        I delete "server/entity/id/9363835"
    """
    stepsyntax = "I delete {path}".format(path=path)
    url = urljoin(context.request_endpoint, path)
    try: # There's got to be a better way to set None if missing/attributerror
        timeout = context.request_timeout
    except AttributeError:
        timeout = None
    timebench_before = time.time()
    context.response = requests.delete(url,timeout=timeout,headers=context.request_headers) # Makes full response.
    timebench_after = time.time()
    
    _latency = timebench_after - timebench_before
    try:    _statuscode         = str(context.response.status_code)
    except: _statuscode         = '-1'
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
                            'latency'         : _latency,
                            'statuscode'      : _statuscode
                        }
#TODO @when('I post "{path}" payload file "{payload}"')    
@when('I post "{path}" with payload "{payload}" failure means "{reason}"')                        # feature-complete
def step(context, path,payload, reason):
    stepsyntax = "I post {path}".format(path=path)
    url = urljoin(context.request_endpoint, path)
    try: # There's got to be a better way to set None if missing/attributerror
        timeout = context.request_timeout
    except AttributeError:
        timeout = None

    timebench_before = time.time()
    context.response = requests.post(url, data=payload,timeout=timeout,headers=context.request_headers) # Makes full response.
    timebench_after = time.time()
    
    _latency = timebench_after - timebench_before
    try:    _statuscode         = str(context.response.status_code)
    except: _statuscode         = '-1'
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
                            'latency'         : _latency,
                            'statuscode'      : _statuscode
                        }
    
#TODO @when('I put "{path}" payload file "{payload}"')  
@when('I put "{path}" with payload "{payload}" failure means "{reason}"')                        # TODO untested XXX
def step(context, path,payload, reason):
    """ Entirely and completely untested """
    stepsyntax = "I put {path}".format(path=path)
    url = urljoin(context.request_endpoint, path)
    try: # There's got to be a better way to set None if missing/attributerror
        timeout = context.request_timeout
    except AttributeError:
        timeout = None
    timebench_before = time.time()
    context.response = requests.put(url, data=payload,timeout=timeout,headers=context.request_headers) # Makes full response.
    timebench_after = time.time()
    
    _latency = timebench_after - timebench_before
    try:    _statuscode         = str(context.response.status_code)
    except: _statuscode         = '-1'
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
                            'latency'         : _latency,
                            'statuscode'      : _statuscode
                        }

# TODO @when('I post "{path}" with multipart payload "{payload}"')      TODO 

##################################
# Thens
@then('the response will contain string "{text}" failure means "{reason}"')                      # feature-complete
def step(context, text, reason):
    stepsyntax = "the response will contain string {text}".format(text=text)
    failure_logic   = 'Did not find expected text `{text}` in response.'.format(text=text )
    if text not in context.response.text:
        assertionthing(success=False,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason=reason, gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    else:
        failure_logic = 'OK'
        assertionthing(success=True,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason=reason, gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)

@then('the response will not contain string "{text}" failure means "{reason}"')                  # feature-complete
def step(context, text, reason):
    stepsyntax = "the response will not contain string {text}".format(text=text)
    if text in context.response.text:
        failure_logic = 'Found string `{text}` in response.'.format(text=text)
        assertionthing(success=False,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason=reason, gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    else:
        failure_logic = 'OK'
        assertionthing(success=True,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason=reason, gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response will have the header "{header}" with the value "{value}" failure means "{reason}"') # feature-complete
def step(context, header, value, reason):
    stepsyntax = "the response will have the header {header} with the value {value}".format(header=header,value=value)
    if context.response.headers[header] != value:
        failure_logic = 'HTTP header `{header}` => `{value}` missing in response.'.format(header=header,value=value)
        assertionthing(success=False,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason=reason, gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    else:
        failure_logic = 'OK'
        assertionthing(success=True,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason=reason, gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response will have the header "{header}" failure means "{reason}"')                   # feature-complete
def step(context, header, reason):
    stepsyntax = "the response will have the header {header}".format(header=header)
    if header not in context.response.headers.keys():
#        logging.debug("I saw these headers though...")
#        for k, v in context.response.headers.iteritems():
#            logging.debug("header: " + k + " => " + v)
        failure_logic = 'Missing header `{header}` in response.'.format(header=header) 
        assertionthing(success=False,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason=reason, gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    else:
        failure_logic = 'OK'
        assertionthing(success=True,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason=reason, gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response will not have the header "{header}" with the value "{value}" failure means "{reason}"')# feature-complete
def step(context, header, value, reason):
    stepsyntax = "the response will not have the header {header} with the value {value}".format(header=header,value=value)
    if context.response.headers[header] == value:
        failure_logic = 'HTTP header `{header}` => `{value}` found in response.'.format(header=header,value=value)
        assertionthing(success=False,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason=reason, gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    else:
        failure_logic = 'OK'
        assertionthing(success=True,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason=reason, gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response will not have the header "{header}" failure means "{reason}"')               # feature-complete
def step(context, header,reason):
    stepsyntax = "the response will not have the header {header}".format(header=header)
    if context.response.headers[header]:
        failure_logic = 'HTTP header `{header}` => `{value} found in response.'.format(header=header,value=context.response.headers[header] )
        assertionthing(success=False,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason=reason, gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    else:
        failure_logic = 'OK'
        assertionthing(success=True,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason=reason, gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response json will have path "{path}" with value "{value}" as "{valuetype}" failure means "{reason}"') # feature-complete
def step(context, path, value, valuetype, reason):
    stepsyntax = "the response json will have the path {path} with value {value} as {valuetype}".format(path=path,value=value,valuetype=valuetype)
    # Check path exists 
    try:
        if not context.jsonsearch.pathexists(context.response.json(),path):
            """ Verify if path exists first of all... else raise() """
            failure_logic = 'Response does not have path {path}'.format(path=path)
            assertionthing(success=False,verb=context.httpstate['verb'],
                        requesturl=context.httpstate['requesturi'],
                        requesthead=context.httpstate['requestheaders'],
                        request=context.httpstate['request'],
                        responsehead=context.httpstate['responseheaders'],
                        response=context.httpstate['response'],
                        reason=reason, gherkinstep=stepsyntax,
                        logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)

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
            assertionthing(success=False,verb=context.httpstate['verb'],
                        requesturl=context.httpstate['requesturi'],
                        requesthead=context.httpstate['requestheaders'],
                        request=context.httpstate['request'],
                        responsehead=context.httpstate['responseheaders'],
                        response=context.httpstate['response'],
                        reason=reason, gherkinstep=stepsyntax,
                        logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
        else:
            failure_logic = 'OK'
            assertionthing(success=True,verb=context.httpstate['verb'],
                       requesturl=context.httpstate['requesturi'],
                       requesthead=context.httpstate['requestheaders'],
                       request=context.httpstate['request'],
                       responsehead=context.httpstate['responseheaders'],
                       response=context.httpstate['response'],
                       reason=reason, gherkinstep=stepsyntax,
                       logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    except:
        failure_logic = traceback.format_exc()
        assertionthing(success=False,verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    reason=reason, gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response json will not have path "{path}" with value "{value}" as "{valuetype}" failure means "{reason}"') # feature-complete
def step(context, path, value, valuetype, reason):
    stepsyntax = "the response json will not have the path {path} with value {value} as {valuetype}".format(path=path,value=value,valuetype=valuetype)
    # If path even exists..
    try:
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
                assertionthing(success=False,verb=context.httpstate['verb'],
                           requesturl=context.httpstate['requesturi'],
                           requesthead=context.httpstate['requestheaders'],
                           request=context.httpstate['request'],
                           responsehead=context.httpstate['responseheaders'],
                           response=context.httpstate['response'],
                           reason=reason, gherkinstep=stepsyntax,
                           logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
            else:
                failure_logic = 'OK'
                assertionthing(success=True,verb=context.httpstate['verb'],
                           requesturl=context.httpstate['requesturi'],
                           requesthead=context.httpstate['requestheaders'],
                           request=context.httpstate['request'],
                           responsehead=context.httpstate['responseheaders'],
                           response=context.httpstate['response'],
                           reason=reason, gherkinstep=stepsyntax,
                           logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    except:
        failure_logic = traceback.format_exc()
        assertionthing(success=False,verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    reason=reason, gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response json will have path "{path}" failure means "{reason}"')                      # feature-complete
def step(context, path, reason):
    stepsyntax = "the response json will have path {path}".format(path=path)
    #raise Exception(context.response.json())
    try:
        if not context.jsonsearch.pathexists(context.response.json(),path):
            """ Verify if path exists first of all """
            failure_logic = 'Response does not have path {path}'.format(path=path)
            assertionthing(success=False,verb=context.httpstate['verb'],
                        requesturl=context.httpstate['requesturi'],
                        requesthead=context.httpstate['requestheaders'],
                        request=context.httpstate['request'],
                        responsehead=context.httpstate['responseheaders'],
                        response=context.httpstate['response'],
                        reason=reason, gherkinstep=stepsyntax,
                        logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
        else:
            failure_logic = 'OK'
            assertionthing(success=True,verb=context.httpstate['verb'],
                       requesturl=context.httpstate['requesturi'],
                       requesthead=context.httpstate['requestheaders'],
                       request=context.httpstate['request'],
                       responsehead=context.httpstate['responseheaders'],
                       response=context.httpstate['response'],
                       reason=reason, gherkinstep=stepsyntax,
                       logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    except:
        failure_logic = traceback.format_exc()
        assertionthing(success=False,verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    reason=reason, gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response json will not have path "{path}" failure means "{reason}"')                  # feature-complete
def step(context, path, reason):
    stepsyntax = "the response json will not have path {path}".format(path=path)
    try:
        if context.jsonsearch.pathexists(context.response.json(),path):
            """ Verify if path exists , then fail """
            failure_logic = 'Response json has path {path}'.format(path=path)
            assertionthing(success=False,verb=context.httpstate['verb'],
                        requesturl=context.httpstate['requesturi'],
                        requesthead=context.httpstate['requestheaders'],
                        request=context.httpstate['request'],
                        responsehead=context.httpstate['responseheaders'],
                        response=context.httpstate['response'],
                        reason=reason, gherkinstep=stepsyntax,
                        logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
        else:
            failure_logic = 'OK'
            assertionthing(success=True,verb=context.httpstate['verb'],
                       requesturl=context.httpstate['requesturi'],
                       requesthead=context.httpstate['requestheaders'],
                       request=context.httpstate['request'],
                       responsehead=context.httpstate['responseheaders'],
                       response=context.httpstate['response'],
                       reason=reason, gherkinstep=stepsyntax,
                       logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    except:
        failure_logic = traceback.format_exc()
        assertionthing(success=False,verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    reason=reason, gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response will have status {status} failure means "{reason}"')
def step(context, status, reason):
    stepsyntax = "the response will have status {status}".format(status=status)
    try:
        status = get_status_code(status)
        if context.response.status_code != status:
            failure_logic = 'Response status is {response.status_code}, not {status}'.format(response=context.response, status=status)
            assertionthing(sucess=False,verb=context.httpstate['verb'],
                       requesturl=context.httpstate['requesturi'],
                       requesthead=context.httpstate['requestheaders'],
                       request=context.httpstate['request'],
                       responsehead=context.httpstate['responseheaders'],
                       response=context.httpstate['response'],
                       reason=reason, gherkinstep=stepsyntax,
                       logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    except:
        failure_logic = traceback.format_exc()
        assertionthing(success=False,verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    reason=reason, gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response will not have status {status} failure means "{reason}"')
def step(context, status, reason):
    stepsyntax = "the response will not have status {status}".format(status=status)
    try:
        status = get_status_code(status)
        if context.response.status_code == status:
            failure_logic = 'Response status is {status}'.format(status=status)
            assertionthing(success=False,verb=context.httpstate['verb'],
                       requesturl=context.httpstate['requesturi'],
                       requesthead=context.httpstate['requestheaders'],
                       request=context.httpstate['request'],
                       responsehead=context.httpstate['responseheaders'],
                       response=context.httpstate['response'],
                       reason=reason, gherkinstep=stepsyntax,
                       logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    except:
        failure_logic = traceback.format_exc()
        assertionthing(success=False,verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    reason=reason, gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
