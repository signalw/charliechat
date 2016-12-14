import apiai, json
from CharlieChat import settings

RESTAURANT_NUMS = ['one','two','three','four','five','first','second','third','fourth','fifth',1,2,3,4,5,6,'six','sixth']
DISAMBIGUATE_MASS = {'brandeis':'waltham','brandeis university':'waltham','harvard':'cambridge','mit':'cambridge','arlington':'massachusetts','south station':'boston','north station':'boston','chinatown':'boston','northeastern':'university huntington ave','logan':'airport','dorcester':'boston','fanueil hall':'boston','burlington':'massachusetts','watertown':'massachusetts'}

def apiai_request(query):
    """Send raw query text to apiai agent, return a json response"""
    ai = apiai.ApiAI(settings.APIAI_DEVELOPER_TOKEN)
    request = ai.text_request()
    # request.session_id = "<SESSION ID, UNIQUE FOR EACH USER>"
    request.query = query #"How can I get to the airport from here?"
    response = request.getresponse()
    return json.loads(response.read().decode())

def get_addresses_from_response(response):
    """get address params from API.AI"""
    params = response["result"]["parameters"]
    return params["address1"], params["address2"]

def get_info_for_locations(response):
    """get required information to filter with yelp's API"""
    params = response["result"]["parameters"]
    return params["loc"],params["type"]

def validate(address):
    curr = ["here", "current location", "current place", "where i am", "my current location", "me", "my location", "my current spot"]
    there = ["there", "that area", "yonder", "those parts"]
    if not address or address.lower() in curr:
        # return the user's current location
        return "current_loc"
    elif address.lower() in there:
        return "there"
    elif address.lower() in DISAMBIGUATE_MASS:
        return "{} {}".format(address,DISAMBIGUATE_MASS[address])
    return address

def get_intent_from_response(response):
    """get intent from API.AI"""
    return response["result"]["metadata"].get('intentName')
