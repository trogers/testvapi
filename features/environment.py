#!/usr/bin/env python

# This file puts things within a sort of global scope within behave.

import jsonpath
class jsonxpath(object):
    """ <jon.kelley> May 1 2013
        This is a helper class to the jsonpath module, making it easiest for our purposes
        or use in the gherkin syntax. Also allows easier refactor if a newer module becomes available.
        
        I actually tried several x-path style JSON libraries for python;
        including jmespath and others. jsonpath seems like the best. The rest sorta suck.
        
        Method features.
        - Search for patterns and if they exist within a json path. 
        - Search if a json path exists.
        - Return the contents of a json path.

        A inline usage example:
            #{
            #	"id": "0001",
            #	"topping":
            #		[
            #			{ "id": "5001", "type": "None" },
            #			{ "id": "5002", "type": "Glazed" },
            #			{ "id": "5005", "type": "Sugar" },
            #			{ "id": "5007", "type": "Powdered Sugar" },
            #			{ "id": "5006", "type": "Chocolate with Sprinkles" },
            #			{ "id": "5003", "type": "Chocolate" },
            #			{ "id": "5004", "type": "Maple" }
            #		]
            #}
            #jxp = jsonxpath()
            #print jxp.returnpath(data, 'topping[*].type')  # Returns data structure
            #print jxp.pathexists(data, 'topping[*].type','Sugar') # True or false if path exists with type 'sugar'
            #print jxp.pathexists(data, 'toppieng[*].type',None) # True or false if path exists.

        """
    def returnpath(self,json,query):
        """ returnpath('topping[*].type')
            Returns data structure from json, else false """
        try:
            return jsonpath.jsonpath(json,query)
        except TypeError:  # Return is path is missing.
            return None

    def pathexists(self,json,path,value=None):
        """ Checks if JSON path exists with an explicit value.
            Returns true or false.

            If arguement 'value' == None; just returns True if path exists.
            """
        if value == None: # If not searching for value, your verifying truth of a path... so
            try:
                results = jsonpath.jsonpath(json,path)
                if results:
                    return True # Path exists! Results exist.
                else:
                    return False
            except TypeError: # False if the path is nonexistant.
                return False
        else: # You must have a value == so we will see if the value matches a value in the list.
            try:
                results = jsonpath.jsonpath(json,path)
                if value in results: # If value is contained within LIST of results; it exists
                    return True
                else: # It's not in the list, so its 
                    return False
            except TypeError: #  False if the path is nonexistant.
                return False

def before_all(context):
    context.request_headers = {} # Define this dictionary context for use in step functions.
    context.jsonsearch = jsonxpath() # Define this context so we can use it in there.

    if not context.config.log_capture:
        import logging
        logging.basicConfig(level=logging.DEBUG)
