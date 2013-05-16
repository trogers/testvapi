# Puts things within global scope.


import jsonpath
class jsonxpath(object):
    """ This class allows you to:
        - Search for patterns and if they exist within a json path. 
        - Search if a json path exists.
        - Return the contents of a json path.
        TODO REWRITE THESE DOCS--------------------------------------
        Usage: Given this data:
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
            #jxp = jsonxpath(data)
            #print jxp.returnpath('topping[*].type')  # Returns data structure
            #print jxp.pathexists('topping[*].type','Sugar') # True or false if path exists with type 'sugar'
            #print jxp.pathexists('toppieng[*].type',None) # True or false if path exists.
            
        Based on https://github.com/boto/jmespath
        """
    def returnpath(self,json,query):
        """ returnpath('topping[*].type')
            Returns data structure from json, else false """
        try:
            return jsonpath.jsonpath(json,query)
        except TypeError:
            return None

    def pathexists(self,json,path,value=None):
        """ Checks if JSON path exists with an explicit value.
            Returns true or false.

            If arguement 'value' == None; just returns True if path exists.
            """
        if value == None:
            try:
                results = jsonpath.jsonpath(json,path)
                if results:
                    return True
                else:
                    return False
            except TypeError:
                return False
        else:
            try:
                results = jsonpath.jsonpath(json,path)
                if value in results: # If value in results; in event it is list.
                    return True
                else:
                    return False
            except TypeError:
                return False

def before_all(context):
    context.request_headers = {} # Define this dictionary context for use in step functions.
    context.jsonsearch = jsonxpath()

    if not context.config.log_capture:
        import logging
        logging.basicConfig(level=logging.DEBUG)
