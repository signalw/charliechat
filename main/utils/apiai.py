import apiai, json
from CharlieChat import settings

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

def validate(address):
    curr = ["here", "current location", "current place"]
    if not address or address.lower() in curr:
        return "45Hawthornestsomerville"
    return address
