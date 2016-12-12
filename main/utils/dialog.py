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
TROUBLE = ["I seem to be having trouble, could you try again later?", "Uh oh, I'm having difficulties. Try again later.", \
        "I can't seem to connect, try again some time later."]

def msg(msg_type,message):
    return {'author':msg_type,'msg':message}

def cc_msg(message):
    return msg('charliechat',message)

def user_msg(message):
    return msg('user',message)

def appendToDestHistory(request,dest):
    request.session['_historyDestinations'].append(dest)

def random_choice(responses):
    return responses[randint(0,len(responses) - 1 )]

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
            request.session['_messages'].append(cc_msg(response["result"] \
                                            ["fulfillment"]["speech"]))
        else:
            if (validate(address1) == "current_loc"):
                address1 = geo_loc

            appendToDestHistory(request,address2)
            info_dict = return_travel_info(address1,address2)

            if info_dict['MBTA directions'] == 'Directions not found':
                request.session['_messages'].append(cc_msg('I don\'t seem to be working right now! Try something else, or try again later.'))
            else:
                request.session['_messages'].append({'author':'charliechat', \
                    'msg':"Arrival time is {} if you leave at {}.".format(info_dict['MBTA arrival time'],info_dict['MBTA depart time'])})
                request.session['_messages'].append(cc_msg(assemble_instructions_map(info_dict['Route segments'])))
        
            request.session['_historyQueries'].append(info_dict)
        
        return HttpResponseRedirect(reverse('index'))
    # get the cost
    elif intent == "getCost":       
        # if asking for fare to a place
        if response['result']['parameters']['address2'] != '':
            address1, address2 = get_addresses_from_response(response)
            price = return_travel_info(address1,address2)['MBTA price']
            if price == 'Directions not found':
                request.session['_messages'].append(cc_msg(random_choice(TROUBLE)))
            else:
                if (validate(address1) == "current_loc"):
                    address1 = "your current location"
                request.session['_messages'].append(cc_msg('It\'ll cost you ${0:.2f} to go from {1} to {2}.'.format(price,address1,address2)))
        # if the previous request or the one before was a navigation, assume we're getting that cost
        elif request.session['_historyIntents'][-2] == "direction" or request.session['_historyIntents'][-3] == "direction":
            price = request.session['_historyQueries'][-1]['MBTA price']
            destination = request.session['_historyDestinations'][-1]
            request.session['_messages'].append(cc_msg('Your trip to {0} is going to cost ${1:.2f} with an adult CharlieCard.'.format(destination,price)))
        # if it was a while back, ask if that's the one
        elif 'direction' in request.session['_historyIntents']:
            request.session['_messages'].append(cc_msg('It was back a bit, but do you mean the cost of your trip to {}?'.format(request.session['_historyDestinations'][-1])))
            # remember unfinished so agree intent is handled properly later
            request.session['_unfinished']['getCost'] = 'farBack'

        return HttpResponseRedirect(reverse('index'))
    # unknown intent
    else:
        r = response["result"]["fulfillment"]["speech"]
        if r is not "" and r is not None:
            request.session['_messages'].append({'author':'charliechat','msg':r})
        else:
            request.session['_messages'].append({'author':'charliechat', \
                        'msg':random_choice(INTENT_CLARIFICATION)})
        return HttpResponseRedirect(reverse('index'))


def dialog_flow(request,query,geo_loc):
    response = apiai_request(query)
    intent = get_intent_from_response(response)
    request.session['_historyIntents'].append(intent)
    print(intent)

    # logic for first time use
    if len(request.session['_messages']) == 2 and request.session['_messages'][0] == cc_msg(FIRST_TIME_MSG):
        if intent == 'agree':
            request.session['_messages'].append(cc_msg('Awesome, welcome! Are you interesting in getting any recommendations?'))
        elif intent == 'disagree':
            request.session['_messages'].append(cc_msg('Well hi! What can I do for you?'))
        else:
            request.session['_messages'].append(cc_msg('I\'ll get on that.'))
            decide_intent(intent,response,request,query,geo_loc)
        return HttpResponseRedirect(reverse('index'))
    # returning user
    else:
        if intent == "agree":
            if len(request.session['_unfinished']) == 0:
                request.session['_messages'].append(cc_msg('Yes to you too!'))
            else:
                if len(request.session['_unfinished']) == 1:
                    unfinished_request = list(request.session['_unfinished'].keys())[0]
                    if unfinished_request == 'getCost':
                        if request.session['_unfinished'][unfinished_request] == 'farBack':
                            request.session['_messages'].append(cc_msg('Got it!'))
                            request.session['_unfinished'] = {}
                            price = request.session['_historyQueries'][-1]['MBTA price']
                            request.session['_messages'].append(cc_msg("The price was ${}.".format(price)))
                            request.session['_historyIntents'].append('getCost')


                # somehow, a bunch of unfinished queries
                else:
                    pass

        elif intent == "disagree":
            if len(request.session['_unfinished']) == 0:
                request.session['_messages'].append(cc_msg('Boo to you too.'))
            else:
                pass
        else:
            decide_intent(intent,response,request,query,geo_loc)
