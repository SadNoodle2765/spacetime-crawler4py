import re
import sys
from bs4 import BeautifulSoup
import requests

stopwords = {}
with open('stopwords.txt', 'r') as f:
    for line in f.readlines():
        stopwords[line.strip()] = 1
    

# url = requests.get('https://www.ics.uci.edu/~pattis/ICS-33/lectures/iterators.txt')
# soup = BeautifulSoup(url.text, 'html.parser')
# texts = soup.get_text()
# print(type(texts))


def tokenize(texts):
    tokens = []
    pattern = re.compile("[a-zA-Z0-9]+[-?'?[a-zA-Z0-9]{2,}")
    for token in pattern.findall(texts):
        tokens.append(token.lower())
    return tokens


def computeWordFrequencies(texts):
    tokenList = tokenize(texts)
    freqencyDict = {}
    for token in tokenList:
        if token not in stopwords:
            if freqencyDict.get(token) is None:
                freqencyDict[token] = 1
            else:
                freqencyDict[token] += 1
    return freqencyDict


def printWordFreq(frequencies):
    for token, freq in sorted(frequencies.items(), key = (lambda k: (-k[1],k[0]))):
        print("{} - {}".format(token,freq))


# printWordFreq(computeWordFrequencies(texts.strip()))