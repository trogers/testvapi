graylog_server = False  # If this was a string 
                        # to a graylog server all your messages 
                        # would magically go there.

graylog_facility = 'valkyrietest.GELF' # A graylog setting.

###########################################################################
# Author: Jon Kelley <jon.kelley@rackspace>                               #
# Date: May 23 2013                                                       #
# Title:  Testvapi. TestvalueAPI. It tests the values and stuff.          #
# Purpose:                                                                #
#        This nifty program lets you unittest any API using restful       #
#        Gherkin style language syntax. It has optional hooks for greylog.#
#        It's the ultimate ops/QE testing tool ever for restful API's.    #
#                                                                         #
#        Find examples, source, instructions on github.                   #
#             https://github.com/jonkelleyatrackspace/testvapi            #
# Python Version: 2.7.3 ###################################################
#  Dependecies:         # 
#    behave  1.2.2      #
#    requests 1.2.0     #
#    jsonpath 0.54      #
#########################

#########################################################################
# Giant wall of importation devices.                                    #
#########################################################################
from behave import *                                                    # =>  Behave makes sure the API's behave, man.
import requests                                                         # =>  <3
from urlparse import urljoin                                            # =>  Allows url manipulation.
from urlparse import urlparse                                           # =>  For greylog gethostname byurl
import logging; logging.basicConfig(level=logging.CRITICAL)             # =>  Only make CRIT filtered to stdout
import json                                                             # =>  We use this.
import traceback                                                        # =>  traceback.format_exc()!
import time                                                             # =>  For request time benchmarking.
from socket import *; import zlib                                       # =>  For the graylogclient class.
#########################################################################
# TODO Unhook reason='null' from giant exceptor class. Its redundant.

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

if not graylog_server:
    logging.critical(ansi.OKBLUE + "=========================================================" + ansi.ENDC)# THX STYLE INTRO
    logging.critical(ansi.OKBLUE + "testvapi :: Testing the values of all your apis          " + ansi.ENDC)# THX STYLE INTRO
    logging.critical(ansi.OKBLUE + "testvapi ::    while you relax                           " + ansi.ENDC)# THX STYLE INTRO
    logging.critical(ansi.OKBLUE + "testvapi ::       on the top some mountains              " + ansi.ENDC)# THX STYLE INTRO
    logging.critical(ansi.OKBLUE + "testvapi ::    with a bottle of scotch                   " + ansi.ENDC)# THX STYLE INTRO
    logging.critical(ansi.OKBLUE + "testvapi ::          and laserbeams and greylog          " + ansi.ENDC)# THX STYLE INTRO
    logging.critical(ansi.OKBLUE + "testvapi :: on your android phone and stuff.             " + ansi.ENDC)# THX STYLE INTRO
    logging.critical(ansi.OKBLUE + "testvapi ::                well                          " + ansi.ENDC)# THX STYLE INTRO
    logging.critical(ansi.OKBLUE + "testvapi ::                      almost anyway.          " + ansi.ENDC)# THX STYLE INTRO
    logging.critical(ansi.OKBLUE + "AUTHOR   :: Jon.Kelley@rackspace                         " + ansi.ENDC)# THX STYLE INTRO
    logging.critical(ansi.OKBLUE + "=========================================================" + ansi.ENDC)# THX STYLE INTRO

def get_status_code(status):
    try:
        return int(status)
    except TypeError:
        # Trick to accept status strings like 'not_found', as well.
        return getattr(requests.codes, status)

class graylogclient():
    """ from socket import *; import zlib
        Hi there, this is the little graylog client. Connects to ports and stuff
        based on funct args. """
    def log(self, message, server='localhost', port=12201, maxChunkSize=8154):
            graylog2_server = server
            graylog2_port = port
            maxChunkSize = maxChunkSize

            UDPSock = socket(AF_INET,SOCK_DGRAM)
            zmessage = zlib.compress(message)
            UDPSock.sendto(zmessage,(graylog2_server,graylog2_port))
            UDPSock.close()

def assertionthing(**kwargs):
    """ This is a giant event processor thing.
        I'll clean it up and break it out later I promise.
        
        Any event it basically evaluates based on if it's FAIL or not, and then
        aggregates and collects the data from the entire unit test from kwargs.
        
        If run from the TTY it's also what throws the assertion failures that you
        see on your console.
        
        It also hooks greylog in this area to funnel all your datas to the internets
        in the event you have an IP configured instead of false.
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

    # Logs some useful debugging data to stdout for QE
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

    # Logs the magical and wonderful outputs to graylog for OPS.
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
        try:
            gelfinstance = graylogclient()
            gelfinstance.log(json.dumps(message),graylog_server) # writeout 
        except:
            print("Graylog send request error. I don't know why!!!!")

    # Raise typical unit testing exception.
    if not _success:
        raise AssertionError(ansi.OKBLUE + "\nRESOURCE .......: " + ansi.FAIL + str(requesturl)   + 
                             ansi.OKBLUE + "\nRCA ............: " + ansi.FAIL + str(reason) +
                             ansi.OKBLUE + "\nUNDERLYING_LOGIC: " + ansi.FAIL + str(logic)  + ansi.ENDC)


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
@when('I get "{path}"')                                                 #feature-complee
def step(context, path):
    """ GET request within path context of server.
        You know, think: 
                        I get "cloud_account/9363835"
    """
    stepsyntax = "I get {path}".format(path=path)

    context.requestpath = path
    url = urljoin(context.request_endpoint, path)
    try: # There's got to be a better way to set None if missing/attributerror
        timeout = context.request_timeout
    except AttributeError:
        timeout = None

    try:
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
        
        # Nifty idea. Sends out equiv curlcommand for you to replicate.
        curlcmd =  'curl -v '
        curlcmd += ' -XGET '
        curlcmd += ' --connect-timeout ' + str(int(timeout)) + ' '
        for (header,value) in context.request_headers.items():
           print header,value
           if header == 'x-auth-token': value = '***CENSORED***'
           curlcmd += "-H " + "\'" + header + ": " + value + "\' "
        curlcmd += "\'"+url+"\'"

        print curlcmd

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
                    reason='null', gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@when('I delete "{path}"')                                              # TODO untested XXX
def step(context, path):# XXX UNTESTED XXX
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
@when('I post "{path}" with payload "{payload}"')                        # feature-complete
def step(context, path,payload):
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
@when('I put "{path}" with payload "{payload}"')                        # TODO untested XXX
def step(context, path,payload):
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
@then('the response will contain string "{text}"')                      # feature-complete
def step(context, text):
    stepsyntax = "the response will contain string {text}".format(text=text)
    failure_logic   = 'Did not find expected text `{text}` in response.'.format(text=text )
    if text not in context.response.text:
        assertionthing(success=False,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason='null', gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    else:
        failure_logic = 'OK'
        assertionthing(success=True,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason='null', gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)

@then('the response will not contain string "{text}"')                  # feature-complete
def step(context, text):
    stepsyntax = "the response will not contain string {text}".format(text=text)
    if text in context.response.text:
        failure_logic = 'Found string `{text}` in response.'.format(text=text)
        assertionthing(success=False,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason='null', gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    else:
        failure_logic = 'OK'
        assertionthing(success=True,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason='null', gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response will have the header "{header}" with the value "{value}"') # feature-complete
def step(context, header, value):
    stepsyntax = "the response will have the header {header} with the value {value}".format(header=header,value=value)
    if context.response.headers[header] != value:
        failure_logic = 'HTTP header `{header}` => `{value}` missing in response.'.format(header=header,value=value)
        assertionthing(success=False,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason='null', gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    else:
        failure_logic = 'OK'
        assertionthing(success=True,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason='null', gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response will have the header "{header}"')                   # feature-complete
def step(context, header):
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
                   reason='null', gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    else:
        failure_logic = 'OK'
        assertionthing(success=True,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason='null', gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response will not have the header "{header}" with the value "{value}"')# feature-complete
def step(context, header, value):
    stepsyntax = "the response will not have the header {header} with the value {value}".format(header=header,value=value)
    if context.response.headers[header] == value:
        failure_logic = 'HTTP header `{header}` => `{value}` found in response.'.format(header=header,value=value)
        assertionthing(success=False,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason='null', gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    else:
        failure_logic = 'OK'
        assertionthing(success=True,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason='null', gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response will not have the header "{header}"')               # feature-complete
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
                   reason='null', gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    else:
        failure_logic = 'OK'
        assertionthing(success=True,verb=context.httpstate['verb'],
                   requesturl=context.httpstate['requesturi'],
                   requesthead=context.httpstate['requestheaders'],
                   request=context.httpstate['request'],
                   responsehead=context.httpstate['responseheaders'],
                   response=context.httpstate['response'],
                   reason='null', gherkinstep=stepsyntax,
                   logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response json will have path "{path}" with value "{value}" as "{valuetype}"') # feature-complete
def step(context, path, value, valuetype):
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
                        reason='null', gherkinstep=stepsyntax,
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
                        reason='null', gherkinstep=stepsyntax,
                        logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
        else:
            failure_logic = 'OK'
            assertionthing(success=True,verb=context.httpstate['verb'],
                       requesturl=context.httpstate['requesturi'],
                       requesthead=context.httpstate['requestheaders'],
                       request=context.httpstate['request'],
                       responsehead=context.httpstate['responseheaders'],
                       response=context.httpstate['response'],
                       reason='null', gherkinstep=stepsyntax,
                       logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    except:
        failure_logic = traceback.format_exc()
        assertionthing(success=False,verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    reason='null', gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response json will not have path "{path}" with value "{value}" as "{valuetype}"') # feature-complete
def step(context, path, value, valuetype):
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
                           reason='null', gherkinstep=stepsyntax,
                           logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
            else:
                failure_logic = 'OK'
                assertionthing(success=True,verb=context.httpstate['verb'],
                           requesturl=context.httpstate['requesturi'],
                           requesthead=context.httpstate['requestheaders'],
                           request=context.httpstate['request'],
                           responsehead=context.httpstate['responseheaders'],
                           response=context.httpstate['response'],
                           reason='null', gherkinstep=stepsyntax,
                           logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    except:
        failure_logic = traceback.format_exc()
        assertionthing(success=False,verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    reason='null', gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response json will have path "{path}"')                      # feature-complete
def step(context, path):
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
                        reason='null', gherkinstep=stepsyntax,
                        logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
        else:
            failure_logic = 'OK'
            assertionthing(success=True,verb=context.httpstate['verb'],
                       requesturl=context.httpstate['requesturi'],
                       requesthead=context.httpstate['requestheaders'],
                       request=context.httpstate['request'],
                       responsehead=context.httpstate['responseheaders'],
                       response=context.httpstate['response'],
                       reason='null', gherkinstep=stepsyntax,
                       logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    except:
        failure_logic = traceback.format_exc()
        assertionthing(success=False,verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    reason='null', gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response json will not have path "{path}"')                  # feature-complete
def step(context, path):
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
                        reason='null', gherkinstep=stepsyntax,
                        logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
        else:
            failure_logic = 'OK'
            assertionthing(success=True,verb=context.httpstate['verb'],
                       requesturl=context.httpstate['requesturi'],
                       requesthead=context.httpstate['requestheaders'],
                       request=context.httpstate['request'],
                       responsehead=context.httpstate['responseheaders'],
                       response=context.httpstate['response'],
                       reason='null', gherkinstep=stepsyntax,
                       logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    except:
        failure_logic = traceback.format_exc()
        assertionthing(success=False,verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    reason='null', gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response will have status {status}')
def step(context, status):
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
                       reason='null', gherkinstep=stepsyntax,
                       logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    except:
        failure_logic = traceback.format_exc()
        assertionthing(success=False,verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    reason='null', gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
@then('the response will not have status {status}')
def step(context, status):
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
                       reason='null', gherkinstep=stepsyntax,
                       logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
    except:
        failure_logic = traceback.format_exc()
        assertionthing(success=False,verb=context.httpstate['verb'],
                    requesturl=context.httpstate['requesturi'],
                    requesthead=context.httpstate['requestheaders'],
                    request=context.httpstate['request'],
                    responsehead=context.httpstate['responseheaders'],
                    response=context.httpstate['response'],
                    reason='null', gherkinstep=stepsyntax,
                    logic=failure_logic,statuscode=context.httpstate['statuscode'],latency=context.httpstate['latency'],)
