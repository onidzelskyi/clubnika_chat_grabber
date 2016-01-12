# -*- coding: utf-8 -*-


import re
import math


# Naïve Bayes class
class NaiveBayes(object):
    def __init__(self):
        self.data = None
        self.frac = None
        self.train = None
        self.cross_validate = None       
        self.classes = {}
        self.corpus = {}
        #self.PM = None
        #self.PF = None
        self.vocab = {}
        #self.vocab_male = []
        #self.vocab_female = []
        #self.corpus = None
        #self.corpus_m = None        
        #self.corpus_f = None        
        self.tokens = {}
        #self.tokens_m = None
        #self.tokens_f = None
        #self.vocab_size = None
        #self.male_words = None
        #self.female_words = None
        
        
    def trainModel(self, data, frac = .8):
        self.data = data
        self.frac = frac
        self.splitData()

        # Total docs
        total_docs = len(self.train)
        #print "total # of docs: %d" % total_docs
        
        # Classes
        for entry in self.train:
            text = entry[0]
            category = entry[1]
            self.classes[category] = self.classes.get(category, 0) + 1
            
        # Priors
        for key in self.classes.keys(): self.classes[key] /= float(total_docs)

        # Male docs
        #male_docs = len([i for i in self.train if int(i[1])==0])
        #print "# of male docs: %d" % male_docs

        # Female docs
        #female_docs = len([i for i in self.train if int(i[1])==1])
        #print "# of female docs: %d" % female_docs

        # prior
        #self.PM = float(male_docs)/float(total_docs)
        #self.PF = 1. - self.PM
        #print "Prior: male - %f\tfemale - %f" % (self.PM, self.PF, )

        # corpus text
        self.loadCorpus() 

        # tokenize text
        self.tok()

        # Vocabulary
        for key,value in self.tokens.items(): self.vocab[key] = self.makeDictionary(value)

        #self.vocab = self.makeDictionary(self.tokens)
        #self.vocab_m = self.makeDictionary(self.tokens_m)
        #self.vocab_f = self.makeDictionary(self.tokens_f)
        #self.vocab_size = len(self.vocab)
        
        #print ("%d vocabulary words, %d male words, %d female words") % (self.vocab_size, self.male_words, self.male_words)

        for word in self.vocab["corpus"].keys():
            freq = {}
            for cat in self.classes.keys():
                freq[cat] = (float(self.vocab[cat].get(word, 0)+1)/float(len(self.tokens[cat])+len(self.vocab["corpus"])))
            self.vocab["corpus"][word] = freq
            #self.vocab["corpus"][word] = (float(self.vocab_m.get(word, 0)+1)/float(self.male_words+self.vocab_size),
            #                    float(self.vocab_f.get(word, 0)+1)/float(self.female_words+self.vocab_size))
        #for key, value in self.vocab.items(): print "%s, (%f, %f)" % (key, self.vocab[key][0], self.vocab[key][1])
        #print self.vocab        
        # Accuracy
        self.calcAccuracy()
        
    
    def classify(self, data, test=False):
        res = []
        for text in data:
            words = self.tokenize(text)
            p = []
            for i, word in enumerate(words):
                if word not in self.vocab["corpus"]:
                    freq = {}
                    for cat in self.classes.keys():
                        freq[cat] = (float(1)/float(len(self.tokens[cat])+len(self.tokens["corpus"])))
                    p.append(freq)
                    #p.append((float(1)/float(self.male_words+self.vocab_size), 
                    #          float(1)/float(self.female_words+self.vocab_size),))
                else: p.append(self.vocab["corpus"][word])
                #print word, p[i]

            #male, female = .0, .0
            predicted = {}
            for i in p:
                for cat in self.classes.keys():
                    predicted[cat] = predicted.get(cat, 1.) + math.log(i[cat])
                #male+= math.log(i[0])
                #female+= math.log(i[1])
                
            for key in predicted.keys(): predicted[key] += math.log(self.classes[key])
            estim = sorted(predicted, key=predicted.get, reverse=True)
            if test: print predicted
            res.append((text, estim[0][0],))
            #res.append((text, "male" if male+math.log(self.PM)>female+math.log(self.PF) else "female",))
            #print "Male: %.12f, female: %12f" % (male+math.log(self.PM), female+math.log(self.PF))
        return res


    # Split data to 
    # Train 80%
    # Cross Validation 20%
    def splitData(self):
        end = int(len(self.data)*self.frac)
        self.train = self.data[:end]

        start = end
        self.cross_validation = self.data[start:]

        
    # Accuracy
    def calcAccuracy(self):
        data = [entry[0] for entry in self.cross_validation]
        c = [entry[1] for entry in self.cross_validation]
        res = self.classify(data)
        hit = 0
        for i, val in enumerate(c):
            if (val.strip()==res[i][1].strip()): hit += 1

        self.accuracy = (float(hit)/float(len(self.cross_validation))) if len(self.cross_validation) else .0
        print "Accuracy: %f" % self.accuracy

        
    # Load corpus
    def loadCorpus(self):
        #male, female, corpus = [], [], []
        for text, cat in self.train:
            if "corpus" not in self.corpus: self.corpus["corpus"] = []
            self.corpus["corpus"].append(text)
            if cat not in self.corpus: self.corpus[cat] = []
            self.corpus[cat].append(text)
            #corpus.append(text)
            #if int(entry[1]): female.append(text)
            #else: male.append(text)
        
        for key in self.corpus.keys(): self.corpus[key] = " ".join(self.corpus[key])
        #self.corpus = " ".join(corpus)
        #self.corpus_m = " ".join(male)
        #self.corpus_f = " ".join(female)

        
    # Tokenize text
    def tok(self):
        #self.tokens["tokens"] = self.tokenize(self.corpus)
        for key,value in self.corpus.items():
            self.tokens[key] = self.tokenize(value)
        #self.tokens = self.tokenize(self.corpus)
        #self.tokens_m = self.tokenize(self.corpus_m)
        #self.tokens_f = self.tokenize(self.corpus_f)    
        #self.male_words = len(self.tokens_m)
        #self.female_words = len(self.tokens_f)


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
