# -*- coding: utf-8 -*-
#Notes: must be in a folder with Thomas' files to function properly
#or just change everthing from local file paths to absolute file paths

#Imports required   
import bookparse as parser
import progbar as progbar
import termrelate as termrelate

import re
from HTMLParser import HTMLParser

#parser.parse_book_file('biology_raw.xhtml', 'organism')

"""
Makes a .txt file that contains only the sentences related to the input term

Input: book--the title of xhtml book in string formatting
	   term--the glossary term you are searching for (string format)

Output: None

Generates: a .txt file called output_file.txt
"""
def makeFile(book, term, terms, tree):
	#genereates a list of all glossary terms
	#terms = parser.find_book_terms(book)
	#takes the xhtml tree and simplifies it into a more readible tree
	#tree = parser.parse_into_tree(book)
	#finds all sentences where the term appears in the sentnece
	appearances = []
	for node in tree:
		if node.cargo is None:
			continue
		elif term in node.cargo.lower():
			appearances.append(node)

	#takes each element from the related_terms list and print to file
	output_file = open('output_file.txt', 'w')
	for item in appearances:
		output_file.write("%s\n" % item)

	return


"""
Checks for the word cargo. cargo= always preceeds the actual sentence.
"""
def containsCargo(word):
    cur = ""
    for elem in word:
        cur += elem
        if cur == "cargo":
            return True
    return False

"""
Provides the index of the final puncutuation in a sentence. Will be used 
to remove  a set of \\ or \\n or > that follow the actual puncutuation.

Input: a single word as a string. Provides the index of the puncutuation

Output: the index of the final puncutuation mark or -1 if None
"""
def dropEndings(word):
    for l in word[::-1]:
                if l == '.' or l == '?' or l == '!':
                    return word.index(l)
    return -1
    
"""
Modifies the input list to remove everything before and including cargo=

Input: a list representing a parsed sentence.

Output: a modified list with extra non text information removed 
		from the head of the list
"""
def removeBeginnings(mylist):
    while containsCargo(mylist[0]) == False and len(mylist) > 2:
        mylist.pop(0)

    if containsCargo(mylist[0]) and len(mylist[0]) > 6:
        cur = mylist[0]
        mylist[0] = cur[6:]
        return mylist
    mylist.pop(0)
    return mylist


"""
Generates a list of sentences from a file. Removes extra crap at the 
beginnning and end that was originally present because of the tree 
parsing method used.

Input: the file path as a string to the file to be read

Output: a list of all sentences. Each sentence is parsed by spaces 
		into its own list.
"""
def genSentences(filepath):
    fileList = list()

    with open(filepath) as f:
        #reads all lines of the file
        for line in f:
            #breaks by spaces
            mylist = line.split(" ")
            #Some lines are just formatting information and are of length 0
            if len(mylist) > 3:
                #remove extranious items at the beginning of a sentence
                mylist = removeBeginnings(mylist)
                #remove extranious endings at the end of the sentence
                word = mylist[-1]
                idx = dropEndings(mylist[-1])
                mylist[-1] = word[:idx + 1]
                #add the line to the parsed list
                fileList.append(mylist)
    return fileList

"""
Takes a list of lists (type str) and converts to a list of strings
"""
def listToString(fileList):
    result = []
    for sentence in fileList:
        string = " ".join(sentence)
        result.append(string)
    return result
           
 

#genereates a list of all glossary terms
#terms = parser.find_book_terms(book)
#takes the xhtml tree and simplifies it into a more readible tree
#tree = parser.parse_into_tree(book)

#makeFile('biology_raw.xhtml', 'microbiology')   
#fileList = genSentences('output_file.txt')            
#print(fileList)   
#print("\n\n\n")           

#sentences = listToString(fileList)
#print(sentences)










