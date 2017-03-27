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
	
	for key,v in tags_count.iteritems():
		for k,value in tagtag_count.iteritems():
			for k1,v1 in value.iteritems():
				prob_tagtag[key][k1]=(tagtag_count[key][k1]+1)/(tags_count[key]+len(tags_count))
			
	for key,value in wordtags_count.iteritems():
		for k1,v1 in value.iteritems():
			prob_wordtag[key][k1]=wordtags_count[key][k1]/tags_count[k1]
			
	print "Completed building the Model"
	model=[prob_wordtag,prob_tagtag,tags_count,words,wordtags_count,wordcount]
	return model
			
def predict_tags(sentences, model):
	## YOU CODE GOES HERE: use the model to predict tags for sentences
	prob_wordtag=model[0]
	prob_tagtag=model[1]
	tags_count=model[2]
	words=model[3]
	wordtags_count=model[4]
	wordcount=model[5]
	tags_list=[]
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
				x1=x1+1.0
	for sentence in sentences:
		Viterbi =[{}]
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
			Viterbi[0][ke]={"prob": prob_tagtag['<s>'][ke]*prob_wordtag[sentence[1].word][ke], "prev": None}
		for t in range(2,len(sentence)-1):
			Viterbi.append({})
			for ke in tags_list:
				max_value = []
				for prev_st1 in tags_list:
					max_value.append(Viterbi[t-2][prev_st1]["prob"]*prob_tagtag[prev_st1][ke])
				maxVit = argmax(max_value)
				prev = None
				max_prob = 0
				for prev_st in tags_list:
					if Viterbi[t-2][prev_st]["prob"]*prob_tagtag[prev_st][ke] == max_value[maxVit]:
						max_prob = max_value[maxVit] * prob_wordtag[sentence[t].word][ke]
						prev = prev_st
						break
				Viterbi[t-1][ke]={"prob":max_prob, "prev": prev}
		backtrack=[]
		max_prob = max(value["prob"] for value in Viterbi[-1].values())
		previous = None
		for k, data in Viterbi[-1].items():
			if data["prob"] == max_prob:
				backtrack.append(k)
				previous=k
				break
		for t in range(len(Viterbi) - 2, -1, -1):
			backtrack.insert(0, Viterbi[t + 1][previous]["prev"])
			previous = Viterbi[t + 1][previous]["prev"]
		for i in range(1,len(sentence)-1):
			sentence[i].tag=backtrack[i-1]
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
