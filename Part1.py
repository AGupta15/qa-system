import os
from sets import Set
import unirest

ANSWER_TYPE = {
    "who" : "PERSON",
    "where" : "GPE",
    "when" : "DATE"
}

QUESTION_FILE="question.txt"
COMMONLY_USED_WORDS=set(["the", "be", "to", "of", "and", "a", "in", "that","have",
"I","it","for","not","","with","he","as","you","is","do","at","this", "but","his",
"by","from","they","we","say","her","she","or","an","will","my","one","all",
"would","there","their","what","so","up","out","if","about","who","get","which",
"go","me","when","make","can","like","time","no","just","him""know","take",
"people","into","year","your","good","some","could","them","see","other","than",
"then","now","look","only","come","its","over","think","also","back","after",
"use","two","how","our","work","first","well","way","even","new","want",
"because","any","these","give","day","most","us"])

path = "/Users/abhigupta/cs4740/qa-system/doc_dev"

# string of format "questionnumber questionidentifier keyword1 keyword2... keywordn"
# takes a string and filters the commonly used words out, returns a tuple of
# the question_number, question_identifier, and keywords
def filter_input_Question(question_string,bad_words):
  keywords=filter(lambda x: not x in bad_words, question_string.split())
  question_number=keywords.pop(0)
  question_identifier=keywords.pop(0)
  return (question_number,question_identifier,keywords)

# takes a file location which is the file of raw questions
# parses all the questions and for each one, calls filterInputQuestion
def parseAllQuestions(question_location):
  question_file=open(question_location)
  raw_data=question_file.read()
  questions=raw_data.replace("<top>\r\n\r\n<num> Number: ",'') \
    .replace('\r\n\r\n<desc> Description:\r\n',' ').replace('?\r\n\r\n<','') \
    .replace('top>\r\n\r\n\r\n','').split('/')
  for question_string in questions[:-1]:
    print filterInputQuestion(question_string,COMMONLY_USED_WORDS)
  return 0
# starts calling all questions
parseAllQuestions(QUESTION_FILE)

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


