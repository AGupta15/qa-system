import os
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


def findWordRanges(wordList):


    return []


makeWordList(89)