#!/usr/bin/env python

from optparse import OptionParser
import os, logging,math
import utils,re
import collections,operator
from numpy import argmax
def create_model(sentences):
	model = None
	## YOUR CODE GOES HERE: create a model
	tags_count= collections.defaultdict(float)
	prob_tagtag=collections.defaultdict(lambda:collections.defaultdict(float))
	prob_wordtag=collections.defaultdict(lambda:collections.defaultdict(float))
	wordtags_count=collections.defaultdict(lambda:collections.defaultdict(float))
	tagtag_count=collections.defaultdict(lambda:collections.defaultdict(float))
	tags3_count = collections.defaultdict(lambda:collections.defaultdict(lambda:collections.defaultdict(float)))
	prob_tags3 = collections.defaultdict(lambda:collections.defaultdict(lambda:collections.defaultdict(float)))
	words=set()
	wordcount=0.0
	for sentence in sentences:
		for i in range(len(sentence)-1):
			if sentence[i].word !='<s>':
				wordcount=wordcount+1
			words.add(sentence[i].word)
			wordtags_count[sentence[i].word][sentence[i].tag] +=1
			tags_count[sentence[i].tag] +=1		
	for sentence in sentences:
		for i in range(len(sentence)-1):
			if i < len(sentence)-2:
				tagtag_count[sentence[i].tag][sentence[i+1].tag] +=1
	
	for sentence in sentences:
		for i in range(len(sentence)-1):
			if i < len(sentence)-2:
				tags3_count[sentence[i].tag][sentence[i+1].tag][sentence[i+2].tag] +=1
	
	
	for key,v in tags3_count.iteritems():
		for k,value in v.iteritems():
			for k1,v1 in v.iteritems():
				prob_tags3[key][k][k1]=(tags3_count[key][k][k1]+1)/(tagtag_count[key][k]+len(tags_count))
		
	for key,value in wordtags_count.iteritems():
		for k1,v1 in value.iteritems():
			prob_wordtag[key][k1]=wordtags_count[key][k1]/tags_count[k1]
	print "Completed building the Model"
	model=[prob_wordtag, tags_count,words,wordtags_count,wordcount,tags3_count,prob_tags3]
	return model			
	
def predict_tags(sentences, model):
	## YOU CODE GOES HERE: use the model to predict tags for sentences
	prob_wordtag=model[0]
	tags_count=model[1]
	words=model[2]
	wordtags_count=model[3]
	wordcount=model[4]
	tags3 = model[5]
	tags3pb = model[6]
	tags_list=[]
	sentenceLen = 14
	x1=0.0
	for k,v in tags_count.iteritems():
		if k!='<s>' and k!='<\\s>':
			tags_list.append(k)
	pattern ="(.*)?[0-9]+(.*)?"
	p="^[A-Z].+$"
	p1="[a-z]+ing$"
	p2="[a-z]+ed\b"
	p3="\'s$"
	for k,v in wordtags_count.iteritems():
		for k1,v1 in v.iteritems():
			if wordtags_count[k][k1]==1.0:
				x1=x1+1.0 # x1 counts the combination of word-tag that occurs one in the training set
	for sentence in sentences:
		Viterbi =[{}]
		sentence = sentence[:sentenceLen]
		for i in range(1,len(sentence)-1):
			if not sentence[i].word in words:
				if re.match(p1,sentence[i].word)!= None or re.match(p2,sentence[i].word)!= None:# or re.match(p3,sentence[i].word)!= None:
					prob_wordtag[sentence[i].word]['VERB']=1.0*x1/wordcount
				elif re.match(p,sentence[i].word)!= None:
					prob_wordtag[sentence[i].word]['NOUN']=1.0*x1/wordcount
				elif re.match(pattern,sentence[i].word)!= None:
					prob_wordtag[sentence[i].word]['OTHER']=1.0*x1/wordcount
				else:
					prob_wordtag[sentence[i].word]['OTHER']=1.0*x1/wordcount
		for ke in tags_list:
			Viterbi[0][ke]={"prob": tags3pb['<s>']['<s>'][ke]*prob_wordtag[sentence[2].word][ke], "prev": None} #first word in the sentence
		#print Viterbi[0]
		Viterbi.append({})
		for ke in tags_list:
			max_value = []
			for prev_st1 in tags_list:
				max_value.append(Viterbi[0][prev_st1]["prob"] * tags3pb['<s>'][prev_st1][ke]) # to find the best tag from the tags assigned to first word
			maxVit = max(max_value)
			#print maxVit
			prev = None
			max_prob = 0
			for prev_st in tags_list:
				if Viterbi[0][prev_st]["prob"]*tags3pb['<s>'][prev_st][ke] == maxVit:
					max_prob = maxVit * prob_wordtag[sentence[3].word][ke]
					prev = prev_st
					break
			Viterbi[1][ke]={"prob":max_prob, "prev": prev}
			#Viterbi[1][ke] = {"prob": tags3pb['<s>']['<s>'][ke]*prob_wordtag[sentence[3].word][ke], "prev": None}
		for t in range(4,len(sentence)-2):
			#print sentence[t].word
			Viterbi.append({})
			for ke in tags_list:
				max_value = []
				for prev_st1 in tags_list:
					for prev_st2 in tags_list:
						max_value.append(Viterbi[t-4][prev_st1]["prob"] * Viterbi[t-3][prev_st2]["prob"] * tags3pb[prev_st1][prev_st2][ke])
				maxVit = max(max_value)
				prev = None
				max_prob = 0
				for prev_st1 in tags_list:
					for prev_st2 in tags_list:
						if Viterbi[t-4][prev_st1]["prob"] * Viterbi[t-3][prev_st2]["prob"] * tags3pb[prev_st1][prev_st2][ke] == maxVit:
							max_prob = maxVit * prob_wordtag[sentence[t].word][ke]
							prev = prev_st2
							break
				Viterbi[t-2][ke]={"prob":max_prob, "prev": prev}
			#print t-2, Viterbi[t-2]
		backtrack=[]
		max_prob = max(value["prob"] for value in Viterbi[-1].values())
		previous = None
		for k, data in Viterbi[-1].items():
			if data["prob"] == max_prob:
				#print k
				backtrack.append(k)
				previous=k
				break
		for t in range(len(Viterbi) - 2, -1, -1):
			#print Viterbi[t + 1][previous]["prev"]
			backtrack.insert(0, Viterbi[t + 1][previous]["prev"])
			previous = Viterbi[t + 1][previous]["prev"]
		#print backtrack
		for i in range(2,len(sentence)-3):
			sentence[i].tag=backtrack[i-2]
			
		#for i in range(len(sentence)):
		#	print sentence[i].word, sentence[i].tag
	return sentences

if __name__ == "__main__":
    usage = "usage: %prog [options] GOLD TEST"
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--debug", action="store_true",
                      help="turn on debug mode")

    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("Please provide required arguments")

    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.CRITICAL)

    training_file = args[0]
    training_sents = utils.read_tokens(training_file)
    test_file = args[1]
    test_sents = utils.read_tokens(test_file)

    model = create_model(training_sents)

    ## read sentences again because predict_tags(...) rewrites the tags
    sents = utils.read_tokens(training_file)
    predictions = predict_tags(sents, model)
    accuracy = utils.calc_accuracy(training_sents, predictions)
    print "Accuracy in training [%s sentences]: %s" % (len(sents), accuracy)

    ## read sentences again because predict_tags(...) rewrites the tags
    sents = utils.read_tokens(test_file)
    predictions = predict_tags(sents, model)
    accuracy = utils.calc_accuracy(test_sents, predictions)
    print "Accuracy in training [%s sentences]: %s" % (len(sents), accuracy)
