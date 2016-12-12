from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .queryGoogleForDirectionsv5 import return_travel_info
from .apiai import *
import json, re

from random import randint

FIRST_TIME_MSG = "Welcome to CharlieChat! Are you new to the area?"
INTENT_CLARIFICATION = ["That doesn't quite make sense, could you word that differently?",\
                        "I'm not sure what you mean. Could you say that again?"]

def msg(msg_type,message):
    return {'author':msg_type,'msg':message}

def charliechat_msg(message):
    return msg('charliechat',message)

def user_msg(message):
    return msg('user',message)

def assemble_instructions_map(segments):
    code = ""

    for segment in segments:
        step = segment['html_instructions']
        print(step)
        print(segment)
        print("*****")
        if segment['travel_mode'] == 'WALKING':
            code += "<p>{} (about <span class='traveltime'>{}</span>)</p>".format(step,segment['duration']['text'])
        else:
            transit = segment['transit_details']
            depart = transit['departure_stop']['name']

            if 'color' in transit['line']:
                color = transit['line']['color']
                code += "<p><span style='background-color:{}'>&nbsp;</span>&nbsp;".format(color)
            else:
                code += "<p>"


            mode = transit['line']['vehicle']['type'].lower()

            if mode == 'bus':
                number = transit['line']['short_name']
                code += "{} {} from {} for {} stops".format(number,step,depart,transit['num_stops'])
            elif mode == 'heavy_rail':
                line = transit['line']['name']
                code += "Take the {} from {} towards {} for {} stops".format(line,depart,transit['headsign'],transit['num_stops'])
            elif mode == 'subway':
                line_name = transit['line']['name']
                code += "Take the {} from {} towards {} for {} stops".format(line_name,depart,transit['headsign'],transit['num_stops'])
            elif mode == 'tram':
                train_letter = transit['line']['short_name']
                code += "Take green line {} train from {} towards {} for {} stops".format(train_letter,depart,transit['headsign'],transit['num_stops'])
            else:
                code += step

            code += " (<span class='traveltime'>{}</span>)</p>".format(segment['duration']['text'])

    return code

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
            info_dict = return_travel_info(address1,address2)

            if info_dict['MBTA directions'] == 'Directions not found':
                request.session['_messages'].append(msg('charliechat','I don\'t seem to be working right now! Try something else, or try again later.'))
            else:
                request.session['_messages'].append({'author':'charliechat', \
                    'msg':"Arrival time is {} if you leave at {}.".format(info_dict['MBTA arrival time'],info_dict['MBTA depart time'])})
                request.session['_messages'].append(msg('charliechat',assemble_instructions_map(info_dict['Route segments'])))
        
            request.session['_historyQueries'].append(info_dict)
        
        return HttpResponseRedirect(reverse('index'))
    # get the cost
    elif intent == "getCost":
        # if the previous request was a navigation, assume we're getting that cost
        if request.session['_historyIntents'][-1] == "direction":
            print(request.session['_historyQueries'][-1]['MBTA price'])
    # unknown intent
    else:
        r = response["result"]["fulfillment"]["speech"]
        if r is not "" and r is not None:
            request.session['_messages'].append({'author':'charliechat','msg':r})
        else:
            request.session['_messages'].append({'author':'charliechat', \
                        'msg':INTENT_CLARIFICATION[randint(0,len(INTENT_CLARIFICATION) - 1 )]})
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
    # returning user
    else:
        decide_intent(intent,response,request,query,geo_loc)
