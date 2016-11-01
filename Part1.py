import os
from sets import Set
import unirest

ANSWER_TYPE = {
    "who" : "PERSON",
    "where" : "GPE",
    "when" : "DATE"
}

path = "/Users/abhigupta/cs4740/qa-system/doc_dev"

# determine the answer from a single range of words with specific answer_type
def parse_answer_from_single_range(answer_type, range_tuple, words):
    text = ' '.join(words[range_tuple[0]:range_tuple[1]])
    response = unirest.post("https://textanalysis.p.mashape.com/spacy-named-entity-recognition-ner",
                        headers={"X-Mashape-Key": "<key>", "Content-Type": "application/x-www-form-urlencoded",
                                 "Accept": "application/json"}, params={"text": text})
    for result in response.body["result"]:
        if ANSWER_TYPE[answer_type] in result:
            return result.rsplit('/')[0]

# return a list of results for each of the given range tuples in range_tuples list
# Example print parse_answer_from_ranges("who", [(1,12), (2,10), (6,16)], ["test", "My", "name", "is", "Evan", "and", "I", "can", "not", "live", "in", "California", "his", "name", "is", "Bob"])
def parse_answer_from_ranges(answer_type, range_tuples, words):
    result = []
    for ranges in range_tuples:
        current = parse_answer_from_single_range(answer_type, ranges, words)
        if current not in result:
            result.append(current)
        if len(result) == 5:
            break
    return result


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


