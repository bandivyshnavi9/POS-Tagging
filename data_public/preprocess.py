#!/usr/bin/env python

from optparse import OptionParser
import os, logging, re

class Token:
    def __init__(self, word, tag):
        self.word = word
        self.tag = tag

    def __str__(self):
        return "%s/%s" % (self.word, self.tag)

def read_tokens(file):
	f = open(file, "r")
	if file == "hw3_train":
		fw = open("prehw3_train", "w")
	else:
		fw = open("prehw3_heldout", "w")
	sentences = []
	for l in f.readlines():
		tokens = l.split()
		sentence = []
		for token in tokens:
			## split only one time, e.g. pianist|bassoonist\/composer/NN
			word = ""
			tag = ""
			try:
				word, tag = token.rsplit('/', 1)
			except:
				## no tag info (test), assign tag UNK
				word, tag = token, "UNK"
			if(re.match(r'^N(.*)$', tag) != None):
				tag = "NOUN"
			elif(re.match(r'^V(.*)$', tag) != None):
				tag = "VERB"
			elif(re.match(r'^IN$', tag) != None or re.match(r'^TO$', tag) != None):
				tag = "PREP"
			else:
				tag = "OTHER"
			
			sentence.append(Token(word, tag))
			st = word + "/" + tag + " "
			fw.write(st)
		sentences.append(sentence)
		fw.write("\n")
	fw.close();


if __name__ == "__main__":
    usage = "usage: %prog [options] GOLD SYSTEM"
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--debug", action="store_true",
                      help="turn on debug mode")

    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Please provide required arguments")

    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.CRITICAL)

    gold = read_tokens(args[0])
