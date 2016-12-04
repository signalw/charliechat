import re
import requests

import settings

#take params from user
#origin = input ("enter an origin between paren\n")
#destination = input("enter a destination between paren \n")
def getPath():
	origin = "45Hawthornestsomerville"
	destination = "Downtowncrossing"

	#put parameters in URL path
	url = "https://maps.googleapis.com/maps/api/directions/json"
	params = {'origin':origin,
	'destination':destination,
	'key':settings.GOOGLE_API_KEY,
	'mode':'transit',
	}

	response = requests.get(url,params=params)
	r = response.json() # gets us a dictionary

	txt = r['routes'][0]
	arrivaltime = txt['legs'][0]['arrival_time']['text']
	departtime = txt['legs'][0]['departure_time']['text']
	steps = txt['legs'][0]['steps']

	directionsraw = str(r).split('html_instructions')[1:]
	directions_cleaner = ""
	for item in directionsraw:
		path = item[:item.find("'distance'")][4:-3].split("',")[0] + "\n"
		directions_cleaner = directions_cleaner + path


	directions_cleaner = re.sub(r'(\<.*?\>)','',directions_cleaner)

	print(directions_cleaner)
	print('\nleave at', departtime)
	print('\narrive by', arrivaltime)

	return directions_cleaner + '\nLeave at ' + departtime + '\nArrive by ' + departtime
