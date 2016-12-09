import apiai, json
from CharlieChat import settings

def apiai_request(query):
    """Send raw query text to apiai agent, return a json response"""
    ai = apiai.ApiAI(settings.APIAI_DEVELOPER_TOKEN)
    request = ai.text_request()
    # request.session_id = "<SESSION ID, UNIQUE FOR EACH USER>"
    request.query = query #"How can I get to the South Station from here?"
    response = request.getresponse()
    return json.loads(response.read().decode())
