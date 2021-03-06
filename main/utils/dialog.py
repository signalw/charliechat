from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser, User
from .queryGoogleForDirectionsv5 import return_travel_info
from .apiai import *
from .yelpfusionapi import *
from .recommend import *
import json, re

from random import randint

FIRST_TIME_MSG = "Welcome to CharlieChat! Are you new to the area?"
INTENT_CLARIFICATION = ["That doesn't quite make sense, could you word that differently?",\
                        "I'm not sure what you mean. Could you say that again?"]
TROUBLE = ["I seem to be having trouble, could you try again later?", "Uh oh, I'm having difficulties. Try again later.", \
        "I can't seem to connect, try again some time later.", "Oh no, something's wrong on my end. Could you try again later?", \
        'I don\'t seem to be working right now! Try something else, or try again later.', "I can't get that information right now."]
RESTAURANTS = ["I can't seem to find anything matching that.","My restaurants finding tool is broken at the moment!"]

def msg(msg_type,message):
    return {'author':msg_type,'msg':message}

def cc_msg(message):
    return msg('charliechat',message)

def user_msg(message):
    return msg('user',message)

def appendToDestHistory(request,start,dest):
    request.session['_historyDestinations'].append((start,dest))

def random_choice(responses):
    return responses[randint(0,len(responses) - 1 )]

def validate_addresses(a1,a2,geo_loc):
    address1 = validate(a1)
    address2 = validate(a2)
    if address1 == "current_loc":
        address1 = geo_loc
    if address2 == "current_loc":
        address2 = geo_loc
    return address1,address2

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
                if 'short_name' in transit['line']:
                    number = transit['line']['short_name']
                    code += "{} {} from {} for {} stops".format(number,step,depart,transit['num_stops'])
                else:
                    code += "{} from {} for {} stops".format(step,depart,transit['num_stops'])
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



def display_help(request):
    request.session['_messages'].append(cc_msg("I can do a lot of things."))
    request.session['_messages'].append(cc_msg("Ask me how to get somewhere, how to get from point A to point B, how much that costs, how long that'll take, or how an Uber trip might compare. I might also serve up recommendations at certain points to make your life easier!"))

def direction(response,request,query,geo_loc):
    address1, address2 = get_addresses_from_response(response)
    if not address2:
        # if you've already asked things, assume the previous
        lastQuery = request.session['_historyQueries'][-1]
        if lastQuery['MBTA directions'] == 'Directions not found':
            request.session['_messages'].append(cc_msg(random_choice(TROUBLE)))
        else:
            request.session['_messages'].append({'author':'charliechat', \
                'msg':"Arrival time is {} if you leave at {}.".format(lastQuery['MBTA arrival time'],lastQuery['MBTA depart time'])})
            request.session['_messages'].append(cc_msg(assemble_instructions_map(lastQuery['Route segments'])))
    else:
        address1, address2 = validate_addresses(address1,address2,geo_loc)
        
        # if context calls for navigating to a restaurant
        if len(request.session['_historyIntents']) > 1 and request.session['_historyIntents'][-2] == 'restaurant':
            yelpQuery = request.session['_historyYelp'][-1]
            if address2 in RESTAURANT_NUMS:
                address2 = yelpQuery[words2num(address2) - 1]['location']
            if address1 in RESTAURANT_NUMS:
                address1 = yelpQuery[words2num(address1) - 1]['location']
        # handle agree/disagree in between
        elif len(request.session['_historyIntents']) > 2 and request.session['_historyIntents'][-3] == 'restaurant':
            yelpQuery = request.session['_historyYelp'][-1]
            if address2 in RESTAURANT_NUMS:
                address2 = yelpQuery[words2num(address2) - 1]['location']
            if address1 in RESTAURANT_NUMS:
                address1 = yelpQuery[words2num(address1) - 1]['location']

        # get navigation info, validate first address
        info_dict = return_travel_info(address1,address2)
        if address1 == geo_loc:
            address1 = "current_loc" # make it easier to check historyDestinations later on
        if address2 == geo_loc:
            address2 = "current_loc"
        appendToDestHistory(request,address1,address2)
        if info_dict['MBTA directions'] == 'Directions not found':
            request.session['_messages'].append(cc_msg(random_choice(TROUBLE)))
        else:
            request.session['_messages'].append({'author':'charliechat', \
                'msg':"Arrival time is {} if you leave at {}.".format(info_dict['MBTA arrival time'],info_dict['MBTA depart time'])})
            request.session['_messages'].append(cc_msg(assemble_instructions_map(info_dict['Route segments'])))
        
        request.session['_historyQueries'].append(info_dict)

        # recommend an uber, maybe
        rec_uber = recommend_uber(info_dict)
        if rec_uber[0]:
            request.session['_messages'].append(cc_msg("It might be a better idea to take an Uber instead.".format()))
            for rec in rec_uber[1:]:
                if rec:
                    request.session['_messages'].append(cc_msg(rec))
            request.session['_messages'].append(cc_msg("The cost would be {}.".format(info_dict['Uber price'])))


        # if they asked for the price previously, also give the price
        if 'getCost' in request.session['_unfinished']:
            price = info_dict['MBTA price']
            if price != 'Directions not found':
                request.session['_messages'].append(cc_msg('And the total cost of this trip is ${0:.2f}.'.format(price)))
            else:
                request.session['_messages'].append(cc_msg('I can\'t seem to find any prices at the moment.'))
            del request.session['_unfinished']['getCost']
        elif 'lengthTime' in request.session['_unfinished']:
            duration = info_dict['MBTA duration']
            if duration != 'Directions not found':
                request.session['_messages'].append(cc_msg('And the total duration of this trip would be {0}.'.format(duration)))
            else:
                request.session['_messages'].append(cc_msg('I can\'t seem to calculate the time right now.'))
            del request.session['_unfinished']['lengthTime']

def getCost(response,request,query,geo_loc):
    # if asking for fare to a place
    if response['result']['parameters']['address2'] != '':
        address1, address2 = get_addresses_from_response(response)
        appendToDestHistory(request,address1,address2)

        address1, address2 = validate_addresses(address1,address2,geo_loc)

        info_dict = return_travel_info(address1,address2)
        request.session['_historyQueries'].append(info_dict)
        price = info_dict['MBTA price']
        if price == 'Directions not found':
            request.session['_messages'].append(cc_msg(random_choice(TROUBLE)))
        else:
            if (validate(address1) == geo_loc):
                address1 = "your current location"
            if validate(address2) == geo_loc:
                address2 = "your current location"
            request.session['_messages'].append(cc_msg('It\'ll cost you ${0:.2f} to go from {1} to {2}.'.format(price,address1,address2)))
    # if the previous request or the one before was a navigation, assume we're getting that cost
    elif request.session['_historyIntents'][-2] == "direction" or request.session['_historyIntents'][-3] == "direction":
        price = request.session['_historyQueries'][-1]['MBTA price']
        if price != 'Directions not found':
            destination = request.session['_historyDestinations'][-1][1]
            request.session['_messages'].append(cc_msg('Your trip to {0} is going to cost ${1:.2f} with an adult CharlieCard.'.format(destination,(price))))
        else:
            request.session['_messages'].append(cc_msg(random_choice(TROUBLE)))
    # if it was a while back, ask if that's the one
    elif 'direction' in request.session['_historyIntents'] or 'lengthTime' in request.session['_historyIntents']:
        request.session['_messages'].append(cc_msg('Do you mean the cost of your trip to {}?'.format(request.session['_historyDestinations'][-1][1])))
        # remember unfinished so agree intent is handled properly later
        print(request.session['_unfinished'])
        request.session['_unfinished']['getCost'] = 'farBack'
    else:
        request.session['_messages'].append(cc_msg('From where to where?'))
        request.session['_unfinished']['getCost'] = 'needTrip'

def lengthTime(response,request,query,geo_loc):
    # if they want duration to a specified place
    if response['result']['parameters']['address2'] != '':
        address1, address2 = get_addresses_from_response(response)
        appendToDestHistory(request,address1,address2)
        if (validate(address1) == "current_loc"):
            address1 = geo_loc
        if validate(address2) == "current_loc":
            address2 = geo_loc
        info_dict = return_travel_info(address1,address2)
        duration = info_dict['MBTA duration']
        request.session['_historyQueries'].append(info_dict)
        if duration == 'Directions not found':
            request.session['_messages'].append(cc_msg(random_choice(TROUBLE)))
        else:
            if (validate(address1) == geo_loc):
                address1 = "where you currently are"
            if validate(address2) == geo_loc:
                address2 = "your current spot"
            request.session['_messages'].append(cc_msg('It\'ll take you {0} to go from {1} to {2}.'.format(duration,address1,address2)))
    # ask if they're referencing the last mentioned
    elif 'direction' in request.session['_historyIntents'] or 'getCost' in request.session['_historyIntents']:
        lastQuery = request.session['_historyDestinations'][-1]
        a1 = lastQuery[0]
        a2 = lastQuery[1]
        if (validate(a1) == "current_loc"):
            a1 = "where you are now"
        if validate(a2) == "current_loc":
            a2 = "your current location"
        request.session['_messages'].append(cc_msg('Do you mean between {} and {}?'.format(a1,a2)))
        request.session['_unfinished']['lengthTime'] = 'farBack'
    else:
        request.session['_messages'].append(cc_msg('From where to where?'))
        request.session['_unfinished']['lengthTime'] = 'needTrip'

def restaurant(response,request,query,geo_loc):
    # determine parameters
    loc,type_food = get_info_for_locations(response)
    loc = validate(loc)

    # user wants food near them
    if not loc or loc == "current_loc":
        businesses = query_multiterm(["food"], geo_loc, '5')
        location_phrase = "near you"
    # user wants food near a destination they specify
    elif loc != "there":
        businesses = query_multiterm(["food"],loc,'5')
        appendToDestHistory(request,geo_loc,loc)
        location_phrase = "around {}".format(loc)
    # user wants food near the previously mentioned destination
    else:
        if len(request.session['_historyDestinations']) > 0:
            loc = request.session['_historyDestinations'][-1][1]
            businesses = query_multiterm(["food"],loc,'5')
            location_phrase = "near {}".format(loc)
        else:
            parsed = {}

    parsed = parseResponses(businesses)
    if len(parsed) > 0:
        candidates = [parsed[term][name] for term in parsed for name in parsed[term]]
        candidates_text = [restaurant_listing(candidate) for candidate in candidates]
        request.session['_messages'].append(cc_msg("Here's what I found {0} that's open now: <ol>".format(location_phrase)+" ".join(candidates_text)+"</ol>"))
        request.session['_historyYelp'].append(candidates)
    else:
        request.session['_messages'].append(cc_msg(random_choice(RESTAURANTS)))

def uber(response,request,query,geo_loc):
    prevIntent = request.session['_historyIntents'][-2]

    if prevIntent == "direction" or prevIntent == "getCost" or prevIntent == "lengthTime" or prevIntent == "agree" or prevIntent == "lengthTrip":
        prevQuery = request.session['_historyQueries'][-1]
        if prevQuery['Uber price'] != 'Directions not found':
            price = prevQuery['Uber price']
            duration = prevQuery['Uber duration']
            arrival = prevQuery['Uber driver arrival (sec)']

            prevTrip = request.session['_historyDestinations'][-1]
            if prevTrip[0] == "current_loc" or prevTrip[0] == geo_loc:
                a1 = "your current location"
            else:
                a1 = prevTrip[0]

            request.session['_messages'].append(cc_msg("By Uber from {0} to {1}, it would cost around {2} for a {3} trip. A driver could be at {0} in about {4} minutes.".format(a1, prevTrip[1], price, duration, arrival % 60 + 2)))
        else:
            request.session['_messages'].append(cc_msg(random_choice(TROUBLE)))
    else:
        pass

def decide_intent(intent,response,request,query,geo_loc):
    if intent == "help":
        display_help(request)
    # intent is to navigate
    elif intent == "direction":
        direction(response,request,query,geo_loc)
    # get the cost
    elif intent == "getCost":
        getCost(response,request,query,geo_loc)
    # asked how long it takes to get somewhere
    elif intent == "lengthTime":
        lengthTime(response,request,query,geo_loc)
    # user wants food
    elif intent == "restaurant":
        restaurant(response,request,query,geo_loc)
    # ask about uber
    elif intent == "uber":
        uber(response,request,query,geo_loc)
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
    if (len(request.session['_messages']) == 2 and request.session['_messages'][0] == cc_msg(FIRST_TIME_MSG)) \
        or (request.session['_messages'][-2] == cc_msg(FIRST_TIME_MSG)):
        user = User.objects.get(username="admin") if isinstance(request.user, AnonymousUser) else request.user
        # they're a tourist'
        if intent == 'agree':
            user.profile.group = 1
            user.save()
            request.session['_messages'].append(cc_msg("That's great, welcome!"))
            display_help(request)
            request.session['_messages'].append(cc_msg('What do you want to know?'))
        # either worker or student, need further clarification
        elif intent == 'disagree':
            request.session['_messages'].append(cc_msg("Cool. Are you a student?"))
            request.session['_unfinished']['userType'] = 'clarification'
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
                    if unfinished_request == 'userType': # are a student
                        user = User.objects.get(username="admin") if isinstance(request.user, AnonymousUser) else request.user
                        user.profile.group = 3
                        user.save()
                        
                        request.session['_messages'].append(cc_msg("I hope you've been enjoying your studies!"))
                        display_help(request)
                        request.session['_messages'].append(cc_msg("What can I do for you?"))
                    elif unfinished_request == 'getCost':
                        if request.session['_unfinished'][unfinished_request] == 'farBack':
                            request.session['_messages'].append(cc_msg('Got it!'))
                            price = request.session['_historyQueries'][-1]['MBTA price']
                            if price != 'Directions not found':
                                request.session['_messages'].append(cc_msg("The price was ${0:.2f}.".format(price)))
                            else:
                                request.session['_messages'].append(cc_msg(random_choice(TROUBLE)))
                            request.session['_historyIntents'].append('getCost')
                    elif unfinished_request == 'lengthTime':
                        if request.session['_unfinished'][unfinished_request] == 'farBack':
                            request.session['_messages'].append(cc_msg('On it!'))
                            duration = request.session['_historyQueries'][-1]['MBTA duration']
                            if duration != 'Directions not found':
                                request.session['_messages'].append(cc_msg("The trip will take {}.".format(duration)))
                            else:
                                request.session['_messages'].append(cc_msg(random_choice(TROUBLE)))
                            request.session['_historyIntents'].append('lengthTrip')

                    request.session['_unfinished'] = {}

                # somehow, a bunch of unfinished queries
                else:
                    pass

        elif intent == "disagree":
            if len(request.session['_unfinished']) == 0:
                request.session['_messages'].append(cc_msg('Boo to you too.'))
            else:
                if len(request.session['_unfinished']) == 1:
                    unfinished_request = list(request.session['_unfinished'].keys())[0]
                    if unfinished_request == 'userType': # are a worker
                        user = User.objects.get(username="admin") if isinstance(request.user, AnonymousUser) else request.user
                        user.profile.group = 2
                        user.save()
                        
                        request.session['_messages'].append(cc_msg("Awesome."))
                        display_help(request)
                        request.session['_messages'].append(cc_msg("What can I help you with?"))
                    elif unfinished_request == 'lengthTime':
                        # not the last trip mentioned
                        if request.session['_unfinished'][unfinished_request] == 'farBack':
                            request.session['_messages'].append(cc_msg('Okay. What trip do you mean?'))
                    elif unfinished_request == 'getCost':
                        # not the last trip mentioned
                        if request.session['_unfinished'][unfinished_request] == 'farBack':
                            request.session['_messages'].append(cc_msg('Okay. The cost from where to where?'))
        else:
            # maybe they didn't answer the student question
            # just assume they're a worker and move on
            if 'userType' in request.session['_unfinished']:
                request.session['_unfinished'] = {}
                request.session['_messages'].append(cc_msg("All right. Just remember you can always change your user type in settings if you login."))
            
            decide_intent(intent,response,request,query,geo_loc)


def words2num(word):
    d = {'one':1,'two':2,'three':3,'four':4,'five':5,'first':1,'second':2,'third':3,'fourth':4,'fifth':5,1:1,2:2,3:3,4:4,5:5,6:6,'six':6,'sixth':6}
    return d[word]
