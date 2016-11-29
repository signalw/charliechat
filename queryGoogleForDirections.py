#Heather Lourie CS136A PA1
import urllib2
import urlparse
from urllib import urlencode
import json

#import sclite

#take params from user
#origin = input ("enter an origin between paren\n")
#destination = input("enter a destination between paren \n")
origin = "BrandeisUniversityWaltham"
destination = "SouthStationBoston"

#put parameters in URL path
def buildURL(destination):
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

finalURL = buildURL(destination)

request = urllib2.Request(finalURL)
response = urllib2.urlopen(request)
txt = json.loads(response.read())['routes'][0]

#['legs'][0]['steps'][0]
directionsraw = str(txt).split('html_instructions')[1:]
directions_cleaner = ""
for item in directionsraw:
    directions_cleaner = directions_cleaner + item[:item.find("u'distance'")][5:-3] + "\n"
arrivaltime = str(txt).split("arrival_time': {u'text': u'")[1][:7]
print directions_cleaner
print '\narrive by ', arrivaltime