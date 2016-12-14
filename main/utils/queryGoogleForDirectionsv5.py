import requests
from CharlieChat import settings
import datetime
import re
#ticket price variables. assumes no charlie-card
#most prices pertain to charlie card zones.  '1A' is the price to go between two '1A' stops only
#the whole numbers are prices to go between a 1A stop to the listed zone, the keys that end
#in .5 are inter-zone prices. So if going from zone 7 to zone 5, the price will be the value that matches
#|7-5\+.5 = 2.5
price_dict = {'tram':2.75,'subway':2.75,'bus':1.70,'inner_express':4,'outer_express':5.25,'1A':2.25,1:6.25,1.5:2.75,2:6.75,2.5:3.25,3:7.50,3.5:3.50,4:8.25,4.5:4.00,5:9.25,5.5:4.50,6:10.00,6.5:5.00,7:10.50,7.5:5.50,8:11.50,8.5:6.00,9:12.00,9.5:6.50,10:12.50,10.5:6.50}
inner_express = [170, 325, 326, 351, 424, 426,428, 434, 448, 449, 450, 459, 501, 502, 504, 553, 554,556,558]
outer_express = [352,354,505]
#to help with pricing
zone_dict ={"South Station":"1A","JFK/UMass":"1A","Quincy Center":1,\
    "Weymouth Landing/East Braintree":2,"East Weymouth":2,"West Hingham":3,\
    "Nantasket Junction":4,"Cohasset":4,"North Scituate":5,"Greenbush":6,\
    "Braintree":2,"Holbrook/Randolph":3,"Montello":4,"Brockton":4,\
    "Campello":5,"Bridgewater":6,"Middleborough/Lakeville":8,"South Weymouth":3,\
    "Abington":4,"Whitman":5,"Hanson":6,"Halifax":7,"Kingston/Route":3,"Plymouth":8,\
    "Newmarket":"1A","Uphams Corner":"1A","Four Corners/Geneva Ave":"1A","Talbot Ave":"1A",\
    "Morton Street":"1A","Fairmount":"1A","Readville":2,"Back Bay":"1A","Ruggles":"1A",\
    "Hyde Park":1,"Route 128":2,"Canton Junction":3,"Canton Center":3,"Stoughton":4,"Sharon":4,\
    "Mansfield":6,"Attleboro":7,"South Attleboro":7,"Providence":8,"T.F. Green Airport":9,\
    "Wickford Junction":10,"Endicott":2,"Dedham Corporate Center":2,"Islington":3,\
    "Norwood Depot":3,"Norwood Central":3,"Windsor Gardens":4,"Plimptonville":4,"Walpole":4,\
    "Norfolk":5,"Franklin/Dean College":6,"Forge Park/495":6,"Forest Hills":"1A",\
    "Roslindale Village":1,"Bellevue":1,"Highland":1,"West Roxbury":1,"Hersey":2,\
    "Needham Junction":2,"Needham Center":2,"Needham Heights":2,"Yawkey":"1A",\
    "Newtonville":1,"West Newton":2,"Auburndale":2,"Wellesley Farms":3,"Wellesley Hills":3,\
    "Wellesley Square":3,"Natick Center":4,"West Natick":4,"Framingham":5,"Ashland":6,\
    "Southborough":6,"Westborough":7,"Grafton":8,"Worcester":8,"North Station":"1A","Porter":"1A",\
    "Belmont Center":1,"Waverley":1,"Waltham":2,"Brandeis/Roberts":2,"Kendal Green":3,"Hastings":3,"Silver Hill":3,\
    "Lincoln":4,"Concord":5,"West Concord":5,"South Acton":6,"Littleton/Route 495":7,"Ayer":8,"Shirley":8,"North Leominster":8,\
    "Fitchburg":8,"Wachusett":8,"West Medford":"1A","Wedgemere":1,"Winchester Center":1,"Mishawum":2,"Anderson RTC":2,"Wilmington":3,\
    "North Billerica":5,"Lowell":6,"Malden Center":"1A","Wyoming Hill":1,"Melrose/Cedar Park":1,"Melrose Highlands":1,"Greenwood":2,\
    "Wakefield":2,"Reading":2,"North Wilmington":3,"Ballardvale":4,"Andover":5,"Lawrence":6,"Bradford":7,"Haverhill":7,\
    "Chelsea":"1A","River Works":2,"Lynn":2,"Swampscott":3,"Salem":3,"Beverly Depot":4,"North Beverly":5,"Hamilton/Wenham":5,\
    "Ipswich":6,"Rowley":7,"Newburyport":8,"Montserrat":4,"Prides Crossing":5,"Beverly Farms":5,"Manchester":6,\
    "West Gloucester":7,"Gloucester":7,"Rockport":8,"Boston North Station":"1A"}

#necessary dictinaries for alerting API
alertnames = {'Chiswick Road': 'place-chswk', 'North Quincy': 'place-nqncy', 'Boston College': 'place-lake',\
     'Babcock Street': 'place-babck', 'Riverway': 'place-rvrwy', 'Reservoir': 'place-rsmnl',\
     'Green Street': 'place-grnst', 'Coolidge Corner': 'place-cool', \
     'Warren Street': 'place-wrnst', 'Back of the Hill': 'place-bckhl', \
     'Airport': 'place-aport', 'Museum of Fine Arts': 'place-mfa', 'South Street': 'place-sougr',\
     'Copley': 'place-coecl', 'Mattapan': 'place-matt', 'Central': 'place-cntsq', \
     'Waban': 'place-waban', 'Capen Street': 'place-capst', 'Kent Street': 'place-kntst', \
     'Back Bay': 'place-bbsta', 'Andrew': 'place-andrw', 'Newton Highlands': 'place-newtn', \
     'Alewife': 'place-alfcl', 'Ashmont': 'place-asmnl', 'Hawes Street': 'place-hwsst', 'Fenway': 'place-fenwy',\
     'Prudential': 'place-prmnl', 'State Street': 'place-state', 'Ruggles': 'place-rugg', \
     'Symphony': 'place-symcl', 'Fairbanks Street': 'place-fbkst', \
     'Tappan Street': 'place-tapst', 'Boston Univ. East': 'place-buest', 'Assembly': \
     'place-astao', 'World Trade Center': 'place-wtcst', 'Shawmut': 'place-smmnl',\
     'Newton Centre': 'place-newto', 'Charles/MGH': 'place-chmnl', 'Central Ave.': \
     'place-cenav', 'Riverside': 'place-river', 'Davis': 'place-davis', 'Chestnut Hill': \
     'place-chhil', 'Science Park': 'place-spmnl', 'Butler': 'place-butlr', 'Savin Hill': 'place-shmnl', \
     'Quincy Adams': 'place-qamnl', 'Quincy Center': 'place-qnctr', \
     'Tufts Medical Center': 'place-tumnl', 'Saint Mary Street': 'place-smary', \
     'Chestnut Hill Ave.': 'place-chill', 'Wonderland': 'place-wondl', 'Aquarium': \
     'place-aqucl', 'Beachmont': 'place-bmmnl', 'Milton': 'place-miltt', 'Harvard':\
     'place-harsq', 'Brookline Village': 'place-bvmnl', 'Longwood Medical Area': \
     'place-lngmd', 'Downtown Crossing': 'place-dwnxg', 'Maverick': 'place-mvbcl', \
     'Sullivan Square': 'place-sull', 'Boston Univ. Central': 'place-bucen', 'Suffolk Downs': 'place-sdmnl',\
     'Mission Park': 'place-mispk', 'Brigham Circle': 'place-brmnl', 'Bowdoin': 'place-bomnl',\
     'Pleasant Street': 'place-plsgr', 'Wood Island': 'place-wimnl', \
     'Kendall/MIT': 'place-knncl','Kendall': 'place-knncl', 'Heath Street': 'place-hsmnl', 'Brookline Hills': 'place-brkhl', \
     'Summit Ave.': 'place-sumav', 'Dean Road': 'place-denrd',\
     'Hynes Convention Center': 'place-hymnl', 'Braintree': 'place-brntn', 'Kenmore': \
     'place-kencl', 'Wellington': 'place-welln', 'Sutherland Road': 'place-sthld', \
     'Brandon Hall': 'place-bndhl', 'Boston Univ. West': 'place-buwst', 'Porter': 'place-portr', \
     'Stony Brook': 'place-sbmnl', 'JFK/Umass': 'place-jfk', 'Packards Corner': 'place-brico',\
     'Chinatown': 'place-chncl', 'Saint Paul Street': 'place-stpul', 'Orient Heights': 'place-orhte', \
     'Lechmere': 'place-lech', 'Malden Center': 'place-mlmnl', 'Haymarket': 'place-haecl', \
     'Northeastern University': 'place-nuniv', 'Courthouse': 'place-crtst', \
     'Englewood Ave.': 'place-engav', 'Fenwood Road': 'place-fenwd', 'Broadway': 'place-brdwy',\
     'Allston Street': 'place-alsgr', 'Eliot': 'place-eliot', 'Revere Beach': 'place-rbmnl', \
     'Jackson Square': 'place-jaksn', 'Beaconsfield': 'place-bcnfd', 'Park Street': 'place-pktrm', \
     'Massachusetts Ave.': 'place-masta', 'Washington Street': 'place-wascm', 'Longwood': 'place-longw', \
     'Blandford Street': 'place-bland', 'North Station': 'place-north', \
     'Oak Grove': 'place-ogmnl', 'Cedar Grove': 'place-cedgr', 'Woodland': 'place-woodl', \
     'Fields Corner': 'place-fldcr', 'Griggs Street': 'place-grigg', 'Boylston': 'place-boyls', \
     'Washington Square': 'place-bcnwa', 'Wollaston': 'place-wlsta', 'Cleveland Circle': 'place-clmnl',\
     'Harvard Ave.': 'place-harvd', 'Valley Road': 'place-valrd', 'Government Center': 'place-gover', \
     'South Station': 'place-sstat', 'Arlington': 'place-armnl', 'Forest Hills': 'place-forhl',\
     'Roxbury Crossing': 'place-rcmnl', 'Community College': 'place-ccmnl'}
routeorders = {'Green Line B': ['Lechmere', 'Science Park', 'North Station', 'Haymarket', \
    'Park Street', 'Boylston', 'Arlington', 'Copley', 'Hynes Convention Center', 'Kenmore', \
    'Blanford Street', 'Boston Univ. East', 'Boston Univ. Central', 'Boston Univ. West', \
    'Saint Paul Street', 'Pleasant Street', 'Babcock Street', 'Packards Corner', \
    'Harvard Avenue', 'Griggs Street', 'Allston Street', 'Warren Street', 'Washington Street', \
    'Sutherland Road', 'Chiswick Road', 'Chestnut Hill Ave', ' South Street', 'Boston College'], \
    'Blue Line': ['Wonderland', 'Revere Beach', 'Beachmont', 'Suffolk Downs', 'Orient Heights', 'Wood Island', \
    'Airport', 'Maverick', 'Aquarium', 'State', 'Government', 'Bowdoin'], \
    'Orange Line': ['Oak Grove', 'Malden Center', 'Wellington', 'Assembly', 'Sullivan Square', \
    'Community College', 'North Station', 'Haymarket', 'State', 'Downtown Crossing', 'Chinatown', \
    'Tufts', 'Back Bay', 'Massachusetts Ave.', 'Ruggles', 'Roxbury Crossing', 'Jackson Square',\
    'Stony Brook', 'Greet Street', 'Forest Hills'], 'Green Line': ['Lechmere', 'Science Park', 'North Station',\
    'Haymarket', 'Park Street', 'Boylston', 'Arlington', 'Copley', 'Hynes Convention Center', \
    'Kenmore'], 'Green Line E': ['Lechmere', 'Science Park', 'North Station', 'Haymarket', \
    'Park Street', 'Boylston', 'Arlington', 'Copley', 'Hynes Convention Center', 'Kenmore', \
    'Prudential', 'Symphony', 'Northeastern', 'Longwood', 'Brigham Circle', 'Fenwood Road', \
    'Mission Park', 'Riverway', 'Back of the Hill', 'Heath Street'], 'Red Ashmont': ['Alewife', \
    'Davis', 'Porter', 'Harvard', 'Central', 'Kendall', 'Charles/MGH', 'Park Street', \
    'Downtown Crossing', 'South Station', 'Broadway', 'Andrew', 'Savin Hill', 'Fields Corner',\
    'Shawmut', 'Ashmont'], 'Green Line D': ['Lechmere', 'Science Park', 'North Station', \
    'Haymarket', 'Park Street', 'Boylston', 'Arlington', 'Copley', 'Hynes Convention Center',\
    'Kenmore', 'Fenway', 'Longwood', 'Brookline Village', 'Brookline Hills', 'Beaconsfiled',\
    'Reservoir', 'Chestnut Hill', 'Newton Centre', 'Newton Highlands', 'Elliot', 'Waban', \
    'Woodland', 'Riverside'], 'Green Line C': ['Lechmere', 'Science Park', 'North Station', \
    'Haymarket', 'Park Street', 'Boylston', 'Arlington', 'Copley', 'Hynes Convention Center',\
    'Kenmore', 'Saint Marys Street', 'Hawes Street', 'Kent Street', 'Saint Paul Street', \
    'Coolidge Corner', 'Summit Ave.', 'Brandon hall', 'Fairbanks', 'Washington Square', \
    'Tappan Street', 'Dean Road', 'Englewood Avenue', 'Cleaveland Circle'], 'Red Braintree':\
    ['Alewife', 'Davis', 'Porter', 'Harvard', 'Central', 'Kendall', 'Charles/MGH',\
    'Park Street', 'Downtown Crossing', 'South Station', 'Broadway', 'Andrew', 'JFK/Umass', \
    'North Quincy', 'Wollaston', 'Quincy Center', 'Quincy Adams', 'Braintree']}

#put parameters in URL path
def buildGoogleMapsURL(origin, destination, mode ='transit'):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        'origin':origin.replace(' ','+'),
        'destination':destination.replace(' ','+'),
        'key':settings.GOOGLE_API_KEY,
        'mode':mode,
        'region':'us'
	}

    response = requests.get(url, params=params)
    r = response.json()
    return r

def buildAlertsURL(stop):
    url = "http://realtime.mbta.com/developer/api/v2/alertsbystop"
    params = {'stop':stop,
    'include_access_alerts':'false',
    'api_key':'xk7jp6dSYEeidJi0P8sBcQ',
    'format':'json',
    'include_service_alerts':'true',
    }
    response = requests.get(url,params=params)
    r = response.json()
    return r

def getUberPriceTime(start_lat, start_long, end_lat, end_long):
    url='https://api.uber.com/v1/estimates/price'
    url2 = 'https://api.uber.com/v1/estimates/time'
    params = {'start_latitude':start_lat,
	'start_longitude':start_long,
     'end_latitude':start_lat,
     'end_longitude':start_long,
     'Accept-Language': 'en_US',
	'server_token':'bEcr6qr2ggY-fVYXr0uump4AdxMLNZmCFvyJwJ-i',
	'Content-Type': 'application/json',
	}
    price = requests.get(url,params=params)
    p = price.json()
    time = requests.get(url2,params=params)
    t = time.json()
    return p,t




def process_directions(origin,destination):
    output_dict = {}
    MBTA_trip_price = 0
    txt2 = buildGoogleMapsURL(origin, destination)

    if txt2['routes'] == []:
        output_dict['MBTA directions'] = 'Directions not found'
        output_dict['MBTA depart time']= 'Directions not found'
        output_dict['MBTA arrival time'] ='Directions not found'
        output_dict['MBTA duration']= 'Directions not found'
        output_dict['MBTA alerts']= 'Directions not found'
        output_dict['MBTA price'] = 'Directions not found'
        output_dict['Uber price'] = 'Directions not found'
        output_dict['Uber driver arrival (sec)'] = 'Directions not found'
        output_dict['Uber duration'] = 'Directions not found'
        output_dict['Route segments'] = 'Directions not found'
    #parse apart directions info
    else:
        txt = txt2['routes'][0]
        start_lat = txt['legs'][0]['start_location']['lat']
        start_lng = txt['legs'][0]['start_location']['lng']

        end_lat = txt['legs'][0]['end_location']['lat']
        end_lng = txt['legs'][0]['end_location']['lng']

        #price and time for uberx. change index to get different uber prices
        p,t = getUberPriceTime(start_lat, start_lng,end_lat,end_lng)
        drive_duration,uber_price,uber_time = ('','','')
        if 'prices' not in p and len(p['prices']) > 1:
            uber_price = p['prices'][0]['estimate']  
            uber_time = t['times'][0]['estimate']
            #used for uber duration
            drive_duration = buildGoogleMapsURL(origin, destination, mode = 'driving')['routes'][0]['legs'][0]['duration']['text']
        
        uber_price = p['prices'][1]['estimate']
        uber_time = t['times'][1]['estimate']
        #used for uber duration
        drive_duration = buildGoogleMapsURL(origin, destination, mode = 'driving')['routes'][0]['legs'][0]['duration']['text']
        
        duration = txt['legs'][0]['duration']['text']

        # if arrival time given
        if 'arrival_time' in txt['legs'][0]:
            arrivaltime = txt['legs'][0]['arrival_time']['text']
            departtime = txt['legs'][0]['departure_time']['text']
        # compute it
        else:
            formatting = '%I:%M %p'
            
            current_time = datetime.datetime.now()
            d = (duration.split(' ')[0]) 
            departtime = current_time.strftime(formatting)

            arrival_date = current_time + datetime.timedelta(minutes=int(d))
            arrivaltime = arrival_date.strftime(formatting)
            

        directionsraw = str(txt2).split('html_instructions')[1:]

        # directions_cleaner = ""
        # for item in directionsraw:
        #     if len(re.findall(r'Subway toward',item)) !=0 or len(re.findall(r'Light rail towards',item)) !=0 \
        #         or len(re.findall(r'Train towards',item)) !=0 or len(re.findall(r'Bus towards',item)) !=0:

        #         lineList = []
        #   #      print(item)
        #         subwayToward = item[:item.find('distance')][4:-3]
        #         subwayDetails = item.split("'name'")
        #         getOnAt= subwayDetails[1].split("'")[1]
        #         getOffAt = subwayDetails[2].split("'")[1]
        #         if len(re.findall(r'Subway toward',item)) !=0:
        #             MBTA_trip_price = MBTA_trip_price + price_dict['subway']

        #             line = subwayDetails[5].split("'")[1]
        #             if item == 'Red Line Subway towards Ashmont':
        #                 lineList = routeorders['Red Ashmont']
        #             elif line =='Red Line':
        #                 lineList= routeorders['Red Braintree']
        #             else:
        #                 lineList = routeorders[line]
        #         elif len(re.findall(r'Light rail towards',item)) !=0:
        #             line = subwayDetails[3].split("'")[1]
        #             lineList = routeorders[line]
        #             MBTA_trip_price = MBTA_trip_price + price_dict['subway']
        #         elif len(re.findall(r'Bus towards',item)) !=0:
        #             MBTA_trip_price = MBTA_trip_price + price_dict['bus']
        #             line= subwayDetails[4].split("'")[1]

        segments = []
        text_directions = []
        MBTA_trip_price = 0.0
        for leg in txt['legs'][0]['steps']:
            segments.append(leg)
            text_directions.append(re.sub(r'(\<.*?\>)','',leg['html_instructions']))

            if leg['travel_mode'] == 'TRANSIT':
                mode = leg['transit_details']['line']['vehicle']['type'].lower()
                if mode == 'heavy_rail':
                    getOffAt = leg['transit_details']['arrival_stop']['name']
                    getOnAt = leg['transit_details']['departure_stop']['name']

                    if getOnAt in zone_dict:
                        onZone = zone_dict[getOnAt]
                    #this guessing method could be improved
                    else:
                        onZone = "1A"
                    
                    if getOffAt in zone_dict:
                        offZone = zone_dict[getOffAt]
                    else:
                        #this guessing method could be improved
                        offZone = "1A"
                    
                    if onZone=="1A" and offZone =="1A":
                        MBTA_trip_price = MBTA_trip_price + price_dict['1A']
                    elif onZone=="1A" or offZone =="1A":
                        if onZone != "1A":
                            MBTA_trip_price = MBTA_trip_price + price_dict[onZone]
                        else:
                            MBTA_trip_price = MBTA_trip_price + price_dict[offZone]
                    else:
                        MBTA_trip_price = MBTA_trip_price + price_dict[abs(onZone-offZone)+.5]
                else:
                    #TODO: handle transfers
                    
                    if 'short_name' in leg['transit_details']['line']:
                        short_name = leg['transit_details']['line']['short_name']
                        if 'SL' in short_name:
                            MBTA_trip_price += 0 # silver line is free
                        elif short_name in inner_express:
                            MBTA_trip_price += price_dict[inner_express]
                        elif short_name in outer_express:
                            MBTA_trip_price += price_dict[outer_express]
                        else:
                            MBTA_trip_price += price_dict[mode]
                    else:
                        MBTA_trip_price += price_dict[mode]
   

        directions_cleaner = ""

        # for item in directionsraw:
        #     print(item)
        #     if len(re.findall(r'Subway toward',item)) !=0 or len(re.findall(r'Light rail towards',item)) !=0 \
        #         or len(re.findall(r'Train towards',item)) !=0 or len(re.findall(r'Bus towards',item)) !=0:
                 
        #         lineList = []            
        #         #print(item)
        #         subwayToward = item[:item.find('distance')][4:-3]
        #         subwayDetails = item.split("'name'")  
        #         #print(subwayDetails)
        #         if len(subwayDetails) > 1:
        #             getOnAt= subwayDetails[1].split("'")[1]
        #             getOffAt = subwayDetails[2].split("'")[1]
        #         else:
        #             getOnAt = "didn't parse"
        #             getOffAt = "didn't parse"
        #             break
        #         if len(re.findall(r'Subway toward',item)) !=0:
        #             MBTA_trip_price = MBTA_trip_price + price_dict['subway'] 
        #             line = subwayDetails[5].split("'")[1]
        #             if item == 'Red Line Subway towards Ashmont':
        #                 lineList = routeorders['Red Ashmont']
        #             elif line =='Red Line':
        #                 lineList= routeorders['Red Braintree']
        #             else:
        #                 print(subwayDetails)
        #                 lineList = routeorders[line]
        #         elif len(re.findall(r'Light rail towards',item)) !=0:
        #             line = subwayDetails[3].split("'")[1]
        #             lineList = routeorders[line]
        #             MBTA_trip_price = MBTA_trip_price + price_dict['subway']
        #         elif len(re.findall(r'Bus towards',item)) !=0:
        #             MBTA_trip_price = MBTA_trip_price + price_dict['bus']
        #             line= subwayDetails[4].split("'")[1]
        #         #this one is commuter rail and does not include alerts
        #         else:
        #             line= subwayDetails[5].split("'")[1]
        #             if getOnAt in zone_dict:
        #                 onZone = zone_dict[getOnAt]
        #             #this guessing method could be improved
        #             else:
        #                 onZone = "1A"
        #             if getOffAt in zone_dict:
        #                 offZone = zone_dict[getOffAt]
        #             else:
        #                 #this guessing method could be improved
        #                 offZone = "1A"
        #             if onZone=="1A" and offZone =="1A":
        #                 MBTA_trip_price = MBTA_trip_price + price_dict['1A']
        #             elif onZone=="1A" or offZone =="1A":
        #                 if onZone != "1A":
        #                     MBTA_trip_price = MBTA_trip_price + price_dict[onZone]
        #                 else:
        #                     MBTA_trip_price = MBTA_trip_price + price_dict[offZone]
        #             else:
        #                 MBTA_trip_price = MBTA_trip_price + price_dict[abs(onZone-offZone)+.5]
                
        #         warning = ''
        #         alertdict ={}
        #         look = False
        #         for i in range(len(lineList)):
        #             if lineList[i] == getOnAt:
        #                 if look == True:
        #                     if lineList[i] in alertdict:
        #                         alertdict[lineList[i]] = alertnames[lineList[i]]
        #                     look = False
        #                 else:
        #                     look = True
        #                     if lineList[i] in alertdict:
        #                         alertdict[lineList[i]] =alertnames[lineList[i]]
        #             elif lineList[i]==getOffAt:
        #                 if look ==True:
        #                     if lineList[i] in alertdict:
        #                         alertdict[lineList[i]] = alertnames[lineList[i]]
        #                     look = False
        #                 else:
        #                     if lineList[i] in alertdict:
        #                         alertdict[lineList[i]] = alertnames[lineList[i]]
        #             else:
        #                 if look ==True:
        #                     if lineList[i] in alertdict:
        #                         alertdict[lineList[i]] = alertnames[lineList[i]]
                            
        #         for stop in alertdict:

        #              alert2 = buildAlertsURL(alertnames[stop])
                     
        #              if alert2['alerts'] ==[]:
        #                  pass
        #              else:
        #                  warning = warning+'\nAlert at '+stop+': '+str(alert2['alerts'][0]['short_header_text'])
        #         directions_cleaner = directions_cleaner+'go to '\
        #             +getOnAt+'\ntake '+line+' '+subwayToward+'\nget off at '+getOffAt+'\n'
        #     else:
                
        #         directions_cleaner = directions_cleaner + item[:item.find('distance')][4:-3] + "\n"
        
        # directions_cleaner = re.sub(r'(\<.*?\>)','',directions_cleaner)

            #     warning = ''
            #     alertdict ={}
            #     look = False
            #     for i in range(len(lineList)):
            #         if lineList[i] == getOnAt:
            #             if look == True:
            #                 if lineList[i] in alertdict:
            #                     alertdict[lineList[i]] = alertnames[lineList[i]]
            #                 look = False
            #             else:
            #                 look = True
            #                 if lineList[i] in alertdict:
            #                     alertdict[lineList[i]] =alertnames[lineList[i]]
            #         elif lineList[i]==getOffAt:
            #             if look ==True:
            #                 if lineList[i] in alertdict:
            #                     alertdict[lineList[i]] = alertnames[lineList[i]]
            #                 look = False
            #             else:
            #                 if lineList[i] in alertdict:
            #                     alertdict[lineList[i]] = alertnames[lineList[i]]
            #         else:
            #             if look ==True:
            #                 if lineList[i] in alertdict:
            #                     alertdict[lineList[i]] = alertnames[lineList[i]]

            #     for stop in alertdict:

            #          alert2 = buildAlertsURL(alertnames[stop])

            #          if alert2['alerts'] ==[]:
            #              pass
            #          else:
            #              warning = warning+'\nAlert at '+stop+': '+str(alert2['alerts'][0]['short_header_text'])
            #     directions_cleaner = directions_cleaner+'go to '\
            #         +getOnAt+'\ntake '+line+' '+subwayToward+'\nget off at '+getOffAt+'\n'
            # else:

            #     directions_cleaner = directions_cleaner + item[:item.find('distance')][4:-3] + "\n"

        #directions_cleaner = re.sub(r'(\<.*?\>)','',directions_cleaner)

        warning = ' '
        output_dict['MBTA directions'] = text_directions
        output_dict['MBTA depart time']= departtime
        output_dict['MBTA arrival time'] =arrivaltime
        output_dict['MBTA duration']= duration
        output_dict['MBTA alerts']= warning
        output_dict['MBTA price']= MBTA_trip_price
        output_dict['Uber price'] = uber_price
        output_dict['Uber driver arrival (sec)'] = uber_time
        output_dict['Uber duration']=drive_duration
        output_dict['Route segments']=segments
    return output_dict

def return_travel_info(origin, destination):
    print(origin)
    print(destination)
    printdict = process_directions(origin,destination)
    return printdict
#return_travel_info("BrandeisBoston","Fitchberg")
