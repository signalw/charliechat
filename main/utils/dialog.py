from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .queryGoogleForDirectionsv5 import return_travel_info
from .apiai import *
import json

FIRST_TIME_MSG = "Welcome to CharlieChat! Are you new to the area?"

def msg(msg_type,message):
    return json.dumps({'author':msg_type,'msg':message})

def charliechat_msg(message):
    return msg('charliechat',message)

def user_msg(message):
    return msg('user',message)

def dialog_flow(request,query,geo_loc):
    response = apiai_request(query)
    intent = get_intent_from_response(response)
    print(intent)

    # logic for first time use
    if request.session['_messages'][-1] is FIRST_TIME_MSG:
        if intent is 'agree':
            request.session['_messages'].append({'author':'charliechat','msg':'Awesome, welcome! What do you want to do?'})
        elif intent is 'disagree':
            request.session['_messages'].append({'author':'charliechat','msg':'Well hi! What can I do for you?'})
        else:
            request.session['_messages'].append({'author':'charliechat','msg':intent})

    if intent == "direction":
        # if intent is direction
        address1, address2 = get_addresses_from_response(response)
        if not address2:
            request.session['_messages'].append({'author':'charliechat','msg':response["result"] \
                                            ["fulfillment"]["speech"]})
        else:
            if (validate(address1) is "current_loc"):
                address1 = geo_loc
            request.session['_messages'].append({'author':'charliechat', \
                        'msg':str(return_travel_info(address1, address2))})
        return HttpResponseRedirect(reverse('index'))
    else:
        # if intent is not direction
        request.session['_messages'].append({'author':'charliechat','msg':response["result"]["fulfillment"] \
                                                ["speech"]})
        return HttpResponseRedirect(reverse('index'))
