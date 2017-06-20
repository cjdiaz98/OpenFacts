# -*- coding: utf-8 -*-
#Aaron Shaw June 12, 2017--OpenStax, OpenFacts project

#imports
#import other project parts
from collections import defaultdict
import nltk
import TreetoList as listGen
import bookparse as parser
import random


"""
Finds all the useful sentences in a dictionary where the keys are the full sentences and values are parsed info
about the sentences.

Input--DF: dictionary w/ keys = sentences and values = parsed info about that sentence
	   key: glossary term

Output--result: list of relevant sentences
"""
def findDefSentences(df, key):
	sentences = df
	tagged_sentences = nltk.pos_tag_sents(nltk.word_tokenize(sent) for sent in sentences)

	#checks if the key has multiple words
	if len(key.split(' ')) > 1:
		result = set()
		#iterates through each word of the key to find sentences related to it
		for w in key.split(' '):
			tagged = iterTaggedSentences(w, tagged_sentences, sentences)

	else:
		tagged = iterTaggedSentences(key, tagged_sentences, sentences)
	return tagged
	


def iterTaggedSentences(w, tagged_sentences, sentences):
	result = []
	backup = []
	if len(tagged_sentences) < 7:
		return (sentences, backup)

	#Find relevant sentences
	for s in tagged_sentences:
		#Finds index of verb and key
		vIdx = findVIndex(s)
		nIdx = findNIndex(s, w)
		sIdx = tagged_sentences.index(s)

		'''
		if nIdx != -1 and vIdx != -1 or len(s) < 6:
			result.append(sentences[sIdx])
		elif nIdx != -1 or len(sentences) < 6:
		elif nIdx != -1 or len(s) < 6:
			backup.append(sentences[sIdx])
		print(len(s), len(tagged_sentences), len(sentences))
		'''

		if nIdx != -1: 
			result.append(sentences[sIdx])
	
	return (result, backup)
			
"""
Gives a parsed sentence, finds the index of the first verb that appears in the sentence.

Input--sentence: a list of (word, tag) tuples

Output--index: the index of the verb if present (-1 if not present)
"""
def findVIndex(sentence):
	
	#find the first VB word in the sentence
	for word in sentence:
		tag = word[1]
		if tag == "VB" or tag == "VBD" or tag == "VBG" or tag == "VBN" or tag == "VBP" or tag == "VBZ":

			return sentence.index(word)

	return -1
	
"""
Gives a parsed sentence, finds the index of the first key that appears in the sentence.

Input--sentence: a list of (word, tag) tuples
	   key: the term we are trying to find in the sentence

Output--index: the index of the verb if present (-1 if not present)
"""
def findNIndex(sentence,  key):
	
	#find the first key word in the sentence
	for word in sentence:
		tag = word[0].lower()
		if tag == key:
			return sentence.index(word)
	return -1    
	
	
"""
Runs the entire program. Generates lists of relevant sentences for a given
term and outouts those sentences and term to a .txt file. 

Can easily adjust which set of terms to examine. Simply adjust the range
of the "for term in terms" for loop.
"""	
def runTest():
	book = 'biology_raw.xhtml'
	#genereates a list of all glossary terms
	terms = parser.find_book_terms(book)
	#takes the xhtml tree and simplifies it into a more readible tree
	tree = parser.parse_into_tree(book)
	
	useful = 0
	notuseful = 0

	termDict = defaultdict(list)
	for term in terms[-10:-1]:

		listGen.makeFile(book, term, terms, tree)
		fileList = listGen.genSentences('output_file.txt')   
		sentences = listGen.listToString(fileList)
		importantSentences = findDefSentences(sentences, term)

		useful += len(importantSentences[0]) #extra info, can remove
		notuseful += len(fileList) #extra info, can remove
		termDict[term] += importantSentences[0]
		print(len(importantSentences[0]), len(sentences)) #extra info, can remove
		
		#WARNING CHANGED IMPORTANTSENTENCES TO A TUPLE, ORIGINIALLY A LIST
		if terms.index(term) % 100 == 0:
			print ("Completed " + str(terms.index(term)) + " of " + str(len(terms)) + " terms")
	
	
	f = open("useful_output.txt", 'w')
	for KV in termDict.keys():
		f.write(KV) 
		f.write("\n")
		value = termDict[KV]
		for v in value:
			f.write(v)
			f.write(" ")
		f.write("\n\n")
	print(useful, notuseful) #extra info, can remove


"""
Finds all relevant sentences to a given list of terms. Can be used
if you want to pick and choose what terms to search
"""
def genForTermsList(terms):

	termDict = defaultdict(list)
	book = 'biology_raw.xhtml'
	tree = parser.parse_into_tree(book)

	for term in terms:
		listGen.makeFile(book, term, terms, tree)
		fileList = listGen.genSentences('output_file.txt')   
		sentences = listGen.listToString(fileList)
		importantSentences = findDefSentences(sentences, term)

		termDict[term] += importantSentences[0]
		
		#WARNING CHANGED IMPORTANTSENTENCES TO A TUPLE, ORIGINIALLY A LIST
	
	f = open("useful_output.txt", 'w')
	for KV in termDict.keys():
		f.write(KV) 
		f.write("\n")
		value = termDict[KV]
		for v in value:
			f.write(v)
			f.write(" ")
		f.write("\n\n")



#runTest()

termsList = ['anaerobic', 
			'renal capsule',
			 'diabetes insipidus', 
			 'Apoda', 
			 'transitional epithelia',
			 'follicle stimulating hormone (FSH)',
			 'septa',
			 'loam', 
			 'lipid', 
			 'capillary', 
			 'progesterone', 
			 'testes', 
			 'hypothyroidism', 
			 'beta cell', 
			 'compliance']

genForTermsList(termsList)





				
				
