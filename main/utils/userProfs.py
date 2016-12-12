
import json 
import requests
import yelpfusionapi as yelp



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

searchTermList = getUserType('student')
businesses = yelp.query_multiterm(searchTermList, 'Boston', '3')
parsed = parseResponses(businesses)

for term in parsed:
	print(term)
	for businessName in parsed[term]:
		print(businessName)
	print('\n')