#! /usr/bin/env python3
# Time-stamp: <2007-05-09 08:22:32 pallier>

import pandas as pd

""" provides 'dico' objects track the frequency of letters, bigrams, trigrams and words from list of words """


def letters(word):
    return list(word)


def bigrams(word, boundaries=False):
    if boundaries:
        lword = '@' + word + '#'
    else:
        lword = word
    bigrams = []
    for i in range(len(lword)-1):
        bigrams.append(lword[i:i+2])
    return bigrams


def openbigrams(word, boundaries=False):
    if boundaries:
        lword = '@' + word + '#'
    else:
        lword = word
    n = len(lword)
    openbig = []
    for i in range(n - 2):
        opbg = lword[i] + lword[i+2]
        openbig.append(opbg)
    return openbig


def trigrams(word, boundaries=False):
    if boundaries:
        lword = '@' + word + '#'
    else:
        lword = word
    trigrams = []
    for i in range(len(lword)-2):
        trigrams.append(lword[i:i+3])
    return trigrams

def quadrigrams(word, boundaries=False):
    if boundaries:
        lword = '@' + word + '#'
    else:
        lword = word
    quadrigrams = []
    for i in range(len(lword)-3):
        quadrigrams.append(lword[i:i+4])
    return quadrigrams


def addtodict(dictio, items, weight=1):
    for item in items:
        if item in dictio:
            dictio[item] += weight
        else:
            dictio[item] = weight


class dico:
    def __init__(self):
        self.hashd = {}  # transformation of the original list into a dictionary for faster access
        self.dico_sub = {}  # dictionnary of substitutions
        self.dico_del = {}  # dictionnary of deletions
        self.letter_distrib = {}
        self.bigram_distrib = {}
        self.openbigram_distrib = {}
        self.trigram_distrib = {}
        self.quadrigram_distrib = {}


    def letter_distribution(self):
        return self.letter_distrib

    def bigram_distribution(self):
        return self.bigram_distrib

    def openbigram_distribution(self):
        return self.openbigram_distrib

    def trigram_distribution(self):
        return self.trigram_distrib

    def quadrigram_distribution(self):
        return self.quadrigram_distrib

    def word_distribution(self):
        return self.hashd

    def add(self, word, weight=1):
        # if (DEBUG): print(f"adding {word} {weight}")
        addtodict(self.hashd, [word], weight)

        # add to letter, bigram and trigram counts
        addtodict(self.letter_distrib, letters(word), weight)
        addtodict(self.bigram_distrib, bigrams(word), weight)
        addtodict(self.openbigram_distrib, openbigrams(word), weight)
        addtodict(self.trigram_distrib, trigrams(word), weight)
        addtodict(self.quadrigram_distrib, quadrigrams(word), weight)

        # create substitution patterns (bonjour -> .onjour, b.njour, bo.jour, ...)
        for i in range(len(word)):
            k = list(word)  # get the list of letters
            k[i:i+1] = '.'  # insert a '.' at position 'i'
            kk = "".join(k)
            if kk in self.dico_sub:
                if not word in self.dico_sub[kk]:
                    self.dico_sub[kk].append(word)
            else:
                self.dico_sub[kk] = [word]

        # create deletion dictionary (bonjour -> bnjour, ...)
        for i in range(len(word)):
            k = list(word)
            del k[i]
            kk = "".join(k)
            if kk in self.dico_del:
                self.dico_del[kk].append(word)
            else:
                self.dico_del[kk] = [word]

    def import_csv(self, filename, sep='\t', header=1):
        a = pd.read_csv(filename, sep=sep, header=header).dropna()
        words = a.iloc[:, 0]
        weights = a.iloc[:, 1]
        for wd, we in zip(words, weights):
            self.add(wd, we)


    def import_textfile(self, filename):
        with open(filename, 'r') as f:
            for line in f:
                for word in line.split():
                    self.add(word)


    def neighboors_substitution(self, word):
        n = []
        for i in range(len(word)):
            k = list(word)
            k[i:i+1] = '.'
            kk = "".join(k)
            if kk in self.dico_sub:
                n.extend([x for x in self.dico_sub[kk] if not x == word if not x in n])
        return n

    def neighboors_deletion(self, word):
        n = []
        for i in range(len(word)):
            k = list(word)
            del k[i]
            kk = "".join(k)
            if kk in self.hashd:
                n.append(kk)
        return n

    def neighboors_addition(self, word): # BUG: FIXME does not work
        if word in self.dico_del:
            return self.dico_del[word]
        else:
            return []

    def neighboors_transposition(self, word):
        n = []
        for i in range(len(word)-1):
            k = list(word)
            k[i], k[i+1] = k[i+1], k[i] # swap letters
            kk = "".join(k)
            if kk !=word and kk in self.hashd:
                n.append(kk)
        return n


def compute_stats(word, dico):
    """ extracts stats from 'dico' for the subcomponents of 'word' """
    letterfreq = [dico.letter_distribution()[l] for l in letters(word)]
    bigramfreq = [dico.bigram_distribution()[l] for l in bigrams(word)]
    openbigramfreq = [dico.openbigram_distribution()[l] for l in openbigrams(word)]
    trigramfreq = [dico.trigram_distribution()[l] for l in trigrams(word)]
    quadrigramfreq = [dico.quadrigram_distribution()[l] for l in quadrigrams(word)]
    return {'letters': letterfreq,
            'bigrams': bigramfreq,
            'openbigrams': openbigramfreq,
            'trigrams': trigramfreq,
            'quadrigrams': quadrigramfreq}



if __name__ == '__main__':
    import pprint as pp
    mydic = dico()
    mydic.import_csv('ortho-freql.txt')

    # two examples:
    print("bonjour : ")
    pp.pprint(compute_stats('bonjour', mydic))
    print()
    print("aliata : ")
    pp.pprint(compute_stats('aliata', mydic))


