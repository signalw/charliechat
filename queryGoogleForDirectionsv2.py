import urllib2
import urlparse
from urllib import urlencode
import json
import re

#take params from user
#origin = input ("enter an origin between paren\n")
#destination = input("enter a destination between paren \n")
origin = "DavisSquare"
destination = "BrandeisUniversityWaltham"

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
    'Blue': ['Wonderland', 'Revere Beach', 'Beachmont', 'Suffolk Downs', 'Orient Heights', 'Wood Island', \
    'Airport', 'Maverick', 'Aquarium', 'State', 'Government', 'Bowdoin'], \
    'Orange': ['Oak Grove', 'Malden Center', 'Wellington', 'Assembly', 'Sullivan Square', \
    'Community College', 'North Station', 'Haymarket', 'State', 'Downtown Crossing', 'Chinatown', \
    'Tufts', 'Back Bay', 'Massachusetts Ave.', 'Ruggles', 'Roxbury Crossing', 'Jackson Square',\
    'Stony Brook', 'Greet Street', 'Forest Hills'], 'Green': ['Lechmere', 'Science Park', 'North Station',\
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
def buildGoogleMapsURL(destination):
	url = "https://maps.googleapis.com/maps/api/directions/json"
	params = {'origin':origin,
	'destination':destination,
	'key':'AIzaSyDoIcIWHO6WZ9XZhIEU7VOQNA4ZcIIVDbw',
	'mode':'transit',
	}

	url_parts = list(urlparse.urlparse(url))
	query = dict(urlparse.parse_qsl(url_parts[4]))
	query.update(params)

	url_parts[4] = urlencode(query)

	return urlparse.urlunparse(url_parts)

def buildAlertsURL(stop):
	url = "http://realtime.mbta.com/developer/api/v2/alertsbystop"
	params = {'stop':stop,
	'include_access_alerts':'false',
	'api_key':'xk7jp6dSYEeidJi0P8sBcQ',	
	'format':'json',	
     'include_service_alerts':'true',
	}

	url_parts = list(urlparse.urlparse(url))
	query = dict(urlparse.parse_qsl(url_parts[4]))
	query.update(params)

	url_parts[4] = urlencode(query)

	return urlparse.urlunparse(url_parts)


def process_directions(destination):
    output_dict = {}  
    mapsURL = buildGoogleMapsURL(destination)
#    print mapsURL
    request = urllib2.Request(mapsURL)
    response = urllib2.urlopen(request)
    txt2 = json.loads(response.read())
    
    if txt2['routes'] == []:
        output_dict['directions'] = 'Directions not found'
        output_dict['depart time']= 'Directions not found'
        output_dict['arrival time'] ='Directions not found'
        output_dict['duration']= 'Directions not found'
        output_dict['alerts']= 'Directions not found'
    #parse apart directions info
    else:
        txt = txt2['routes'][0]
        arrivaltime2 = txt['legs'][0]['arrival_time']['text']
        departtime2 = txt['legs'][0]['departure_time']['text']
        duration2 = txt['legs'][0]['duration']['text']
        steps =txt['legs'][0]['steps']
        directionsraw = str(txt2).split('html_instructions')[1:]
        directions_cleaner = ""
        for item in directionsraw:
            if len(re.findall(r'Subway toward',item)) !=0 or len(re.findall(r'Light rail towards',item)) !=0 or len(re.findall(r'Train towards',item)) !=0:
                lineList = []            
                subwayToward = item[:item.find("u'distance'")][5:-3]
                subwayDetails = item.split("u'name': u'")   
                getOnAt= subwayDetails[1].split("'")[0]
                getOffAt = subwayDetails[2].split("'")[0]
                if len(re.findall(r'Subway toward',item)) !=0:
                    line = subwayDetails[5].split("'")[0]
                    if item == 'Red Line Subway towards Ashmont':
                        lineList = routeorders['Red Ashmont']
                    elif line =='Red Line':
                        lineList= routeorders['Red Braintree']
                    else:
                        lineList = routeorders[line.split()[0]]
                elif len(re.findall(r'Light rail towards',item)) !=0:
                    line = subwayDetails[3].split("'")[0]
                    lineList = routeorders[line]
                #this one is actually commuter rail and does not include alerts
                else:
                    line = subwayDetails[5].split("'")[0]
                
                warning = ''
                alertdict ={}
                look = False
                for i in range(len(lineList)):
                    if lineList[i] == getOnAt:
                        if look == True:
                            alertdict[lineList[i]] = alertnames[lineList[i]]
                            look = False
                        else:
                            look = True
                            alertdict[lineList[i]] =alertnames[lineList[i]]
                    elif lineList[i]==getOffAt:
                        if look ==True:
                            alertdict[lineList[i]] = alertnames[lineList[i]]
                            look = False
                        else:
                            alertdict[lineList[i]] = alertnames[lineList[i]]
                    else:
                        if look ==True:
                            alertdict[lineList[i]] = alertnames[lineList[i]]
                            
                for stop in alertdict:
                     alertURL = buildAlertsURL(alertnames[stop])
                     req = urllib2.Request(alertURL)
                     res = urllib2.urlopen(req)
                     alert2 = json.loads(res.read())
                     if alert2['alerts'] ==[]:
                         pass
                     else:
                         warning = warning+'\nAlert at '+stop+': '+str(alert2['alerts'][0]['short_header_text'])
                directions_cleaner = directions_cleaner+'go to '\
                    +getOnAt+'\ntake '+line+' '+subwayToward+'\nget off at '+getOffAt+'\n'
            else:
                directions_cleaner = directions_cleaner + item[:item.find("u'distance'")][5:-3] + "\n"
        
        directions_cleaner = re.sub(r'(\<.*?\>)','',directions_cleaner)
    
        
        output_dict['directions'] = directions_cleaner
        output_dict['depart time']= '\nleave at', departtime2
        output_dict['arrival time'] ='\narrive by ', arrivaltime2
        output_dict['duration']= '\ntotal duration ',duration2
        output_dict['alerts']= 'warning, the following alerts exist"\n',warning
    return output_dict
    
printdict = process_directions(destination)
print printdict