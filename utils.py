# -*- coding: utf-8 -*-


import re
import math


# Naïve Bayes class
class NaiveBayes(object):
    def __init__(self):
        self.data = None
        self.train = None
        self.cross_validate = None        
        self.PM = None
        self.PF = None
        self.vocab = []
        self.vocab_male = []
        self.vocab_female = []
        self.corpus = None
        self.corpus_m = None        
        self.corpus_f = None        
        self.tokens = None
        self.tokens_m = None
        self.tokens_f = None
        self.vocab_size = None
        self.male_words = None
        self.female_words = None
        
        
    def trainModel(self, data):
        self.data = data
        self.splitData()

        # Total docs
        total_docs = len(self.train)
        #print "total # of docs: %d" % total_docs

        # Male docs
        male_docs = len([i for i in self.train if int(i[1])==0])
        #print "# of male docs: %d" % male_docs

        # Female docs
        female_docs = len([i for i in self.train if int(i[1])==1])
        #print "# of female docs: %d" % female_docs

        # prior
        self.PM = float(male_docs)/float(total_docs)
        self.PF = 1. - self.PM
        #print "Prior: male - %f\tfemale - %f" % (self.PM, self.PF, )

        # corpus text
        self.loadCorpus() 

        # tokenize text
        self.tok()

        # Vocabulary
        self.vocab = self.makeDictionary(self.tokens)
        self.vocab_m = self.makeDictionary(self.tokens_m)
        self.vocab_f = self.makeDictionary(self.tokens_f)
        self.vocab_size = len(self.vocab)
        
        #print ("%d vocabulary words, %d male words, %d female words") % (self.vocab_size, self.male_words, self.male_words)

        for word in self.vocab.keys():
            self.vocab[word] = (float(self.vocab_m.get(word, 0)+1)/float(self.male_words+self.vocab_size),
                                float(self.vocab_f.get(word, 0)+1)/float(self.female_words+self.vocab_size))
        #for key, value in self.vocab.items(): print "%s, (%f, %f)" % (key, self.vocab[key][0], self.vocab[key][1])
        
        # Accuracy
        self.calcAccuracy()
        
    
    def classify(self, data):
        res = []
        for text in data:
            words = self.tokenize(text)
            p = []
            for i, word in enumerate(words):
                if word not in self.vocab:
                    p.append((float(1)/float(self.male_words+self.vocab_size), 
                              float(1)/float(self.female_words+self.vocab_size),))
                else: p.append(self.vocab[word])
                #print word, p[i]

            male, female = .0, .0
            for i in p:
                male+= math.log(i[0])
                female+= math.log(i[1])
                
            res.append((text, "male" if male+math.log(self.PM)>female+math.log(self.PF) else "female",))
            #print "Male: %.12f, female: %12f" % (male+math.log(self.PM), female+math.log(self.PF))
        return res


    # Split data to 
    # Train 80%
    # Cross Validation 20%
    def splitData(self, frac=.8):
        end = int(len(self.data)*frac)
        self.train = self.data[:end]

        start = end
        self.cross_validation = self.data[start:]

        
    # Accuracy
    def calcAccuracy(self):
        data = [entry[0] for entry in self.cross_validation]
        c = [int(entry[1]) for entry in self.cross_validation]
        res = self.classify(data)
        hit = 0
        for i, val in enumerate(c):
            #print "class: %s, predict: %s" % (val, res[i][1])
            if (val==0 and res[i][1]=="male") or (val==1 and res[i][1]=="female"): hit += 1

        self.accuracy = (float(hit)/float(len(self.cross_validation)))
        print "Accuracy: %f" % self.accuracy

        
    # Load corpus
    def loadCorpus(self):
        male, female, corpus = [], [], []
        for entry in self.train:
            text = entry[0]
            corpus.append(text)
            if int(entry[1]): female.append(text)
            else: male.append(text)
        
        self.corpus = " ".join(corpus)
        self.corpus_m = " ".join(male)
        self.corpus_f = " ".join(female)

        
    # Tokenize text
    def tok(self):
        self.tokens = self.tokenize(self.corpus)
        self.tokens_m = self.tokenize(self.corpus_m)
        self.tokens_f = self.tokenize(self.corpus_f)    
        self.male_words = len(self.tokens_m)
        self.female_words = len(self.tokens_f)


    # Tokenize text
    def tokenize(self, text):
        return self.removeDelimiters(self.removeDigits(text)).lower().split()


    # Remove any digits from corpus
    def removeDigits(self, text):
        return re.sub("[0-9]", " ", text)


    # Remove delimiters
    # like .!,:@), etc.
    def removeDelimiters(self, text):
        delims = [u"-", u"\.", u"!", u"_", u"\)", u"\(", u":", u"\+", u"\*", u";", u">", u"\?", u"@", u"=", "\.", "!", "\+"]
        for delim in delims:
            text = re.sub(delim, " ", text)
        return text

    # Dictionary
    # key: word
    # value: frequence
    def makeDictionary(self, text):
        D = {}
        for word in text: D[word] = D.get(word, 0) + 1
        return D


def readCSV(file_name):
    import codecs
    data = []
    with codecs.open(file_name, encoding="utf-8") as f:
        data = [line.split(",") for line in f.readlines()]
    return data
