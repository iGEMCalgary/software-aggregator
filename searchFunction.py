from nltk import word_tokenize
from nltk import FreqDist
from nltk.corpus import stopwords
import nltk
import re
import string
from PyDictionary import PyDictionary
from operator import itemgetter

class Search:
	STOP_WORDS = nltk.corpus.stopwords.words('English')

	def __init__(self):
		self.STOP_WORDS.extend(['i','we', 'name', 'software'])
		
	def runSearch(self, software, query):
		scores = []
		searchKeys = self.getSearchKeys(query)
		for i in range(len(software)):
			score = self.getScore(searchKeys, software[i][2], software[i][0], software[i][1])
			scores.append([i, score])
		results = [[index, score] for [index, score] in scores if score not 0]
		results = sorted(scores, key=itemgetter(1))
		return results
			
	##	getSearchKeys
	#		Tokenizes search query and removes stop words
	#		Returns list of query keys
	##
	def getSearchKeys(self, query):
		searchWords = nltk.word_tokenize(query)
		searchKeys = [key.lower() for key in searchWords if key not in self.STOP_WORDS]
		return searchKeys
		
	## RAINER - This will need to be rewritten so that it takes the words occurences column
	
	def getScore(self, searchKeys, text, year, team):
		# words = [word.lower() for word in text.split()]  # Replace this with every other entry in wordOccurences
		score = 0
		
		for key in searchKeys:
			keyS = key + 's'			# For plurals ending in s
			keyAS = key + '\'s'		# For plurals ending in 's
			if key in words or (keyS in words or (keyAS in words or (key[:-1] in words or key[:-2] in words))):
				score += # word score here
			if key in year or key in team.lower():
				score += 1
				
		return score
	
