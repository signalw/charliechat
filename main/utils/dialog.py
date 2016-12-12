from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .queryGoogleForDirectionsv5 import return_travel_info
from .apiai import *
import json

FIRST_TIME_MSG = "Welcome to CharlieChat! Are you new to the area?"

def msg(msg_type,message):
    return {'author':msg_type,'msg':message}

def charliechat_msg(message):
    return msg('charliechat',message)

def user_msg(message):
    return msg('user',message)

def decide_intent(intent,response,request,query,geo_loc):
    # intent is to navigate
    if intent == "direction":
        address1, address2 = get_addresses_from_response(response)
        if not address2:
            request.session['_messages'].append(msg('charliechat',response["result"] \
                                            ["fulfillment"]["speech"]))
        else:
            if (validate(address1) == "current_loc"):
                address1 = geo_loc
            request.session['_messages'].append({'author':'charliechat', \
                        'msg':str(return_travel_info(address1, address2))})
        return HttpResponseRedirect(reverse('index'))
    # unknown intent
    else:
        
        request.session['_messages'].append({'author':'charliechat','msg':response["result"]["fulfillment"] \
                                                ["speech"]})
        return HttpResponseRedirect(reverse('index'))


def dialog_flow(request,query,geo_loc):
    response = apiai_request(query)
    intent = get_intent_from_response(response)
    print(intent)

    # logic for first time use
    if len(request.session['_messages']) == 2 and request.session['_messages'][0] == msg('charliechat',FIRST_TIME_MSG):
        if intent == 'agree':
            request.session['_messages'].append(msg('charliechat','Awesome, welcome! What do you want to do?'))
        elif intent == 'disagree':
            request.session['_messages'].append(msg('charliechat','Well hi! What can I do for you?'))
        else:
            request.session['_messages'].append(msg('charliechat','I\'ll get on that.'))
            decide_intent(intent,response,request,query,geo_loc)
        return HttpResponseRedirect(reverse('index'))
    # returning
    else:
        decide_intent(intent,response,request,query,geo_loc)
