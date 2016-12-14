# -*- coding: utf-8 -*-
"""
Yelp Fusion API query tool

Sample usage of the program:
`python sample.py --term="bars" --location="San Francisco, CA"`
"""
from __future__ import print_function

import argparse
import json
import pprint
import requests
import sys
import urllib
import itertools
from CharlieChat import settings

# This client code can run on Python 2.x or 3.x.  Your imports can be
# simpler if you only need one of those.
try:
	# For Python 3.0 and later
	from urllib.error import HTTPError
	from urllib.parse import quote
	from urllib.parse import urlencode
except ImportError:
	# Fall back to Python 2's urllib2 and urllib
	from urllib2 import HTTPError
	from urllib import quote
	from urllib import urlencode


# OAuth credential placeholders that must be filled in by users.
# You can find them on
# https://www.yelp.com/developers/v3/manage_app
CLIENT_ID = settings.YELP_CLIENT_ID
CLIENT_SECRET = settings.YELP_CLIENT_SECRET


# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
TOKEN_PATH = '/oauth2/token'
GRANT_TYPE = 'client_credentials'


# Defaults for our simple example.
DEFAULT_TERM = 'cafe'
DEFAULT_LOCATION = 'Boston, MA'
SEARCH_LIMIT = 20  # number of businesses returned in response


def obtain_bearer_token(host, path):
	"""Given a bearer token, send a GET request to the API.

	Args:
		host (str): The domain host of the API.
		path (str): The path of the API after the domain.
		url_params (dict): An optional set of query parameters in the request.

	Returns:
		str: OAuth bearer token, obtained using client_id and client_secret.

	Raises:
		HTTPError: An error occurs from the HTTP request.
	"""
	url = '{0}{1}'.format(host, quote(path.encode('utf8')))
	assert CLIENT_ID, "Please supply your client_id."
	assert CLIENT_SECRET, "Please supply your client_secret."
	data = urlencode({
		'client_id': CLIENT_ID,
		'client_secret': CLIENT_SECRET,
		'grant_type': GRANT_TYPE,
	})
	headers = {
		'content-type': 'application/x-www-form-urlencoded',
	}
	response = requests.request('POST', url, data=data, headers=headers)
	bearer_token = response.json()['access_token']
	return bearer_token


def request(host, path, bearer_token, url_params=None):
	"""Given a bearer token, send a GET request to the API.

	Args:
		host (str): The domain host of the API.
		path (str): The path of the API after the domain.
		bearer_token (str): OAuth bearer token, obtained using client_id and client_secret.
		url_params (dict): An optional set of query parameters in the request.

	Returns:
		dict: The JSON response from the request.

	Raises:
		HTTPError: An error occurs from the HTTP request.
	"""
	url_params = url_params or {}
	url = '{0}{1}'.format(host, quote(path.encode('utf8')))
	headers = {
		'Authorization': 'Bearer %s' % bearer_token,
	}

	print(u'Querying {0} ...'.format(url))

	response = requests.request('GET', url, headers=headers, params=url_params)

	return response.json()


def search(bearer_token, term, location):
	"""Query the Search API by a search term and location.

	Args:
		term (str): The search term passed to the API.
		location (str): The search location passed to the API.

	Returns:
		dict: The JSON response from the request.
	"""

	url_params = {
		'term': term.replace(' ', '+'),

		# "address, neighborhood, city, state or zip, optional country"
		'location': location.replace(' ', '+'),
		'limit': SEARCH_LIMIT,
		'open_now': "1",
		'radius': '4000',
	}
	return request(API_HOST, SEARCH_PATH, bearer_token, url_params=url_params)


def get_business(bearer_token, business_id):
	"""Query the Business API by a business ID.

	Args:
		business_id (str): The ID of the business to query.

	Returns:
		dict: The JSON response from the request.
	"""
	business_path = BUSINESS_PATH + business_id

	r = request(API_HOST, business_path, bearer_token)
	print(r)
	return r


def query_api(term, location, searchLim):
	"""Queries the API by the input values from the user.

	Args:
		term (str): The search term to query.
		location (str): The location of the business to query.
		searchLim (int): number of results from response to return
	"""

	searchLim = int(searchLim)  # number of businesses to print

	bearer_token = obtain_bearer_token(API_HOST, TOKEN_PATH)

	response = search(bearer_token, term, location)

	businesses = response.get('businesses')

	if not businesses:
		print(u'No businesses for {0} in {1} found.'.format(term, location))
		return

	responseList = []
	print("displaying info for top " + str(searchLim) + " results")
	for x in range(0, searchLim):
		business_id = businesses[x]['id']

		response = get_business(bearer_token, business_id)

		business_distance = businesses[x]['distance']
		# append distance to the response for later
		response['distance'] = business_distance
		business_price = businesses[x].get('price', '$')
		response['price'] = business_price

		responseList.append(response)
		# pprint.pprint(response, indent=2)
	return responseList

	# Original Yelp code sample:
	# business_id = businesses[0]['id']

	# print(u'{0} businesses found, querying business info ' \
	#     'for the top result "{1}" ...'.format(
	#         len(businesses), business_id))
	# response = get_business(bearer_token, business_id)

	# print(u'Result for business "{0}" found:'.format(business_id))
	# pprint.pprint(response, indent=2)


def query_multiterm(termList, location, searchLim):
	allResponses = {}
	for term in termList:
		termResponses = []
		query = query_api(term, location, searchLim)
		if query is not None:
			for r in query:
				termResponses.append(r)
			allResponses[term] = termResponses

	return allResponses


def main():
	# CLI Interface, dont really need
	parser = argparse.ArgumentParser()

	parser.add_argument('-q', '--term', dest='term', default=DEFAULT_TERM,
						type=str, help='Search term (default: %(default)s)')
	parser.add_argument('-l', '--location', dest='location',
						default=DEFAULT_LOCATION, type=str,
						help='Search location (default: %(default)s)')
	parser.add_argument('-sl', '--searchLim', dest='searchLim',
						default=1, type=str,
						help='Number of results (default: %(default)s)')
	input_values = parser.parse_args()

	try:

		query_api(input_values.term, input_values.location,
				  input_values.searchLim)

	except HTTPError as error:
		sys.exit(
			'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
				error.code,
				error.url,
				error.read(),
			)
		)

# if __name__ == '__main__':
#     main()
# def formatResponses(responseList):
# 	"""Given a list of JSON responses, return their Python object form

#     Args:
#        responseList: list of http responses, i.e. given by query_api

#     Returns:
#     	parsedResponseList: list after JSON decoding

# 	"""
# 	formattedResponseList = []
# 	for response in responseList:
# 		data = json.loads(response)
# 		formattedResponseList.append(data)
# 	return formattedResponseList


def parseResponses(termToResponseList):
	"""
	Args:
		dict: {term:responsesForTermList}
	Returns:
		dict: {term: businessInfoList}
				businessInfoList: {businessName: businessInfo}

		 e.g. dict[terms][businessNames][businessInfo]
	"""
	# for response in termToResponseList:
	# 	print(type(response))
	
	termToBusinessDict = {}
	for term in termToResponseList:
		businessInfoList = {}
		for response in termToResponseList[term]:
			infoDict = {}
			infoDict['name'] = response['name']
			infoDict['rating'] = response['rating']
			infoDict['price'] = response['price']
			infoDict['distance'] = response['distance']
			infoDict['url'] = response['url']
			infoDict['location'] = "{} {} {}".format(response['location']['address1'],response['location']['city'],response['location']['state']) 
			businessInfoList[response['name']] = infoDict
		termToBusinessDict[term] = businessInfoList
	return termToBusinessDict

def getUserType(userType):
	"""
	Args:
		userType (str): type of user
	Returns:
		list of search terms for the designated user
	"""

	def student():
		terms = ['coffee', 'cafe', 'thrift', 'active life',
				'arts and entertainment']
		return terms
	def tourist():
		terms = ['points of interest', 'museum', 'restaurants', 'shopping',
				'arts and entertainment', 'local flavor']
		return terms
	def worker():
		terms = ['coffee', 'cafe', 'nightlife']
		return terms

	options = {
		'student': student,
		'tourist': tourist,
		'worker': worker,
	}
	terms = []


	return options[userType]()

# searchTermList = getUserType('student')
# businesses = query_multiterm(["food"], '42.3754247,-71.2220716', '3')
# parsed = parseResponses(businesses)
# print([name for term in parsed for name in parsed[term]])
# for term in parsed:
# 	print(term)
# 	for businessName in parsed[term]:
# 		print(businessName)
# 	print('\n')
