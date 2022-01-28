import re
import sys
from bs4 import BeautifulSoup
import requests


    



def tokenize(texts):
    tokens = []
    pattern = re.compile("(?:[a-zA-Z0-9]{2,}(?:-?'?[a-zA-Z0-9]+)*)|[aiAI]")
    for token in pattern.findall(texts):
        tokens.append(token.lower())
    return tokens

def tokenizeForWordFrq(texts):
    tokens = []
    pattern = re.compile("[a-zA-Z]{3,}(?:-?'?[a-zA-Z0-9]+)*")
    for token in pattern.findall(texts):
        tokens.append(token.lower())
    return tokens



def computeWordFrequencies(texts):
    stopwords = {}
    with open('stopwords.txt', 'r') as f:
        for line in f.readlines():
            stopwords[line.strip()] = 1

    tokenList = tokenizeForWordFrq(texts)
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

if __name__ == '__main__':


    url = requests.get('https://www.ics.uci.edu/grad/admissions/Prospective_ApplicationProcess.php')
    soup = BeautifulSoup(url.text, 'html.parser')
    content = soup.get_text()

    tokens = tokenize(content)
    #tokens = tokenize("Hashiri Nio Testing's Mother-In-Law")

    for token in tokens:
        print(token)

    wordCount = len(tokens)

    print("Word Count: " + str(wordCount))

   
    #texts = soup.get_text()
    #print(texts)
    #printWordFreq(computeWordFrequencies(texts.strip()))

