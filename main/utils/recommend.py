from django.contrib.auth.models import AnonymousUser, User

import datetime
from .yelpfusionapi import *
from random import randint

MEALS = {
    'breakfast':(datetime.time(6,30,0),datetime.time(8,0,0)),
    'brunch':(datetime.time(9,30,0),datetime.time(11,0,0)),
    'lunch':(datetime.time(11,30,0),datetime.time(13,0,0)),
    'dinner':(datetime.time(18,30,0),datetime.time(20,30,0)),
    'a midnight snack':(datetime.time(23,30,0),datetime.time(1,30,0))
}

def recommend_uber(info_dict):
    recommend = [False,None,None]
    formatting = '%I:%M%p'

    if info_dict['Uber price'] != 'Directions not found':
        uber_time = info_dict['Uber duration'].split(" ")[0]
        uber_arrival = info_dict['Uber driver arrival (sec)']
        uber_departure = (datetime.datetime.now() + datetime.timedelta(seconds=int(uber_arrival)))

        mbta_time = info_dict['MBTA duration']
        t_depart = info_dict['MBTA depart time']
        t_departure = datetime.datetime.strptime(t_depart, '%I:%M%p')

        # if you have to wait more than 30 minutes for the T, rec an uber
        if ((uber_departure + datetime.timedelta(minutes=30)).time() < t_departure.time()):
            recommend[0] = True
            arrival = (uber_departure).time()
            recommend[1] = "The Uber would arrive at {}, a much shorter wait time than for the T.".format(arrival.strftime(formatting).lower())
        # if the uber gets there before the T even leaves
        if ((uber_departure + datetime.timedelta(minutes=int(uber_time))).time() <= t_departure.time()):
            recommend[0] = True
            arrival = (uber_departure + datetime.timedelta(minutes=int(uber_time))).time()
            recommend[2] = "The Uber would get to your destination at {}, which is before your designated departure time!".format(arrival.strftime(formatting).lower())

    print(recommend)
    return recommend

def time_in_range(r):
    current_time = datetime.datetime.now().time()
    start = r[0]
    end = r[1]

    if start <= end:
        return start <= current_time <= end
    else:
        return start <= current_time or current_time <= end

def restaurant_listing(candidate):
    """assemble code to display a restaurant"""
    return "<li>{}, {} stars, <span class='restaurantprice'>{}</span><br><small>{}</small></li>".format(candidate['name'],candidate['rating'],candidate['price'],candidate['location'])

def recommend_meal(request,geo_loc):
    user = User.objects.get(username="admin") if isinstance(request.user, AnonymousUser) else request.user
    userGroup = user.profile.group

    if userGroup != 0 and geo_loc is not None and geo_loc != '': # never used the app before at all
        # check if it's time for a MEAL
        meal_time = False
        current_meal = ''
        for meal in MEALS.keys():
            if time_in_range(MEALS[meal]):
                meal_time = True
                current_meal = meal  

        if not meal_time:
            request.session['_suggestedMeal'] = False

        if meal_time and not request.session['_suggestedMeal']:
            userTypeMapping = {1:'tourist',2:'worker',3:'student'}
            userType = userTypeMapping[userGroup]
            terms = getUserType(userType)
            category = terms[randint(0,len(terms) - 1 )]
            
            rec = query_multiterm(["food"], geo_loc, '3')
            parsed = parseResponses(rec)
            if len(parsed) > 0:
                candidates = [parsed[term][name] for term in parsed for name in parsed[term]]
                candidates_text = [restaurant_listing(candidate) for candidate in candidates]

                request.session['_messages'].append({'author':'charliechat','msg':"Hey, it's time for {}!".format(current_meal)})
                request.session['_messages'].append({'author':'charliechat','msg':"Here's what I found that's open now near you: <ol>"+" ".join(candidates_text)+"</ol>"})

                request.session['_historyYelp'].append(candidates)
                request.session['_historyIntents'].append('restaurant')
                request.session['_suggestedMeal'] = True