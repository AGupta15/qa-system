import os
from sets import Set
import sys
import re

path = "/Users/abhigupta/cs4740/qa-system/doc_dev"

def makeWordList(directory):
    wordList = []
    dirPath = path +"/"+ str(directory)+"/"
    for file in os.listdir(dirPath):
        filePath = dirPath+file
        with open(filePath) as f:
            fileList = []
            for line in f:
                values = line.rstrip().split("\t")
                values = " ".join(values).split(" ")
                for value in values:
                    if(len(value) > 0):
                        fileList.append(value)
            wordList.append(fileList)
    return wordList


def findWordRanges(wordList, directory):

    dirWordList = makeWordList(directory)
    print dirWordList

    wordSet = Set()
    for word in wordList:
        wordSet.add(word)

    rangeArray = []
    for i in range(0, len(dirWordList)):
        fileWordList = dirWordList[i]
        fileRanges = []
        for j in range(0, len(fileWordList)):
            if (fileWordList[j] in wordSet):
                fileRanges.append(j)
        rangeArray.append(fileRanges)

    print rangeArray
    return rangeArray



fileWordList = makeWordList(89)
wordArray = ["the", "hello", "hi"]
findWordRanges(wordArray, 89)
