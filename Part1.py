import os
from sets import Set
import unirest
import nltk

API_KEY = "y5TSV5GnovmshgN9RBrmSvGlOT7Lp1bSp3xjsnaJQ5nmWCtG0H"

ANSWER_TYPE = {
    "who": ["PERSON"],
    "where": ["GPE", "LOC"],
    "when": ["DATE"]
}

SENTENCE_TERMINALS = ['.', '!', '?', '<', '>', '/']
QUESTION_FILE="question.txt"
SMALL_QUESTION_FILE="smallq.txt"
BELIZE="belize.txt"
COMMONLY_USED_WORDS=set(["the", "be", "to", "of", "and", "a", "in", "that","have",
"I","it","for","not","","with","he","as","you","is","do","at","this", "but","his",
"by","from","they","we","say","her","she","or","an","will","my","one","all",
"would","there","their","what","so","up","out","if","about","get","which",
"go","me","make","can","like","time","no","just","him""know","take",
"people","into","year","your","good","some","could","them","see","other","than",
"then","now","look","only","come","its","over","think","also","back","after",
"use","two","how","our","work","first","well","way","even","new","want",
"because","any","these","give","day","most","us"])

path = "doc_dev"


# string of format "questionnumber questionidentifier keyword1 keyword2... keywordn"
# takes a string and filters the commonly used words out, returns a tuple of
# the question_number, question_identifier, and keywords
def filterInputQuestion(question_string, bad_words):
    keywords = filter(lambda x: not x in bad_words, question_string.split())
    question_number = keywords.pop(0)
    question_identifier = keywords.pop(0)
    if question_identifier == "Where's":
        question_identifier = "Where"
    if question_identifier == "Who's":
        question_identifier = "Who"
    return (question_number, question_identifier, keywords)


# determine the answer from a single range of words with specific answer_type
def parse_answer_from_single_range(answer_type, range_tuple, words, question_keys):
    text = ' '.join(words[range_tuple[0]:range_tuple[1]])
    print "text: {}".format(text)
    response = unirest.post("https://textanalysis.p.mashape.com/spacy-named-entity-recognition-ner",
                            headers={"X-Mashape-Key": API_KEY, "Content-Type": "application/x-www-form-urlencoded",
                                     "Accept": "application/json"}, params={"text": text})
    if response.headers.get('X-RateLimit-requests-Remaining') < 10: raise Exception('Dont waste Alexs Money!!' + str(response.headers))
    answer = []
    for result in response.body["result"]:
        token = result.rsplit('/')
        if token[1] in ANSWER_TYPE[answer_type] and not token[0] in question_keys:
            answer.append(token[0])
    return answer

# return a list of results for each of the given range tuples in range_tuples list
# Example print parse_answer_from_ranges("who", [(1,12), (2,10), (6,16)], ["test", "My", "name", "is", "Evan", "and", "I", "can", "not", "live", "in", "California", "his", "name", "is", "Bob"])
def parse_answer_from_ranges(answer_type, range_tuples, words, question_keys):
    result = []
    for ranges in range_tuples:
        answers = parse_answer_from_single_range(answer_type, ranges, words, question_keys)
        if answers:
            for current in answers:
                if current not in result:
                    result.append(current)
                if len(result) == 5:
                    return result
    return result


# makes a list of words in a directory
def makeWordList(directory):
    wordList = []
    dirPath = path + "/" + str(directory) + "/"
    file_list = os.listdir(dirPath)
    file_list = [f for f in file_list if f[0] != '.']
    file_start_ends = [0]
    counter = 0
    for file_obj in file_list:
        filePath = os.path.join(dirPath, file_obj)
        f = open(filePath)
        for line in f:
          values=nltk.word_tokenize(line)
          for value in values:
            counter+=1
            wordList.append(value)
        file_start_ends.append(counter)

    return wordList, file_start_ends


# finds the ranges that the list of keywords appears in
def findWordRanges(wordList, directory):
    dirWordList = makeWordList(directory)[0]
    # print dirWordList

    wordSet = Set()
    for word in wordList:
        wordSet.add(word.lower())

    rangeArray = []
    for i in range(0, len(dirWordList)):
        if dirWordList[i].lower() in wordSet:
            rangeArray.append(i)
    return rangeArray


# Evan cluster

def evan_cluster(indices_list, word_list, max_gap = 30):
  indices_list.sort()
  groups = [[indices_list[0]]]
  for x in indices_list[1:]:
      if abs(x - groups[-1][-1]) <= max_gap:
          groups[-1].append(x)
      else:
          groups.append([x])
  groups.sort(key=len, reverse=True)

  groups = [group for group in groups if len(group) >= 2]
  # adjust chunks to extend to full sentences on each side of the bound
  for group in groups:
    first = group[0]
    last = group[-1]
    while (first > 0 and not any(terminal in word_list[first] for terminal in SENTENCE_TERMINALS)):
      first -= 1
    while (last <= (len(word_list) - 1) and not any(terminal in word_list[last] for terminal in SENTENCE_TERMINALS)):
      last += 1
    group[0] = first + 1
    group[-1] = last - 1

  print 'START CLUSTER TEST\n\n'
  print len(groups)
  # remove: for testing
  for group in groups:
    print group
    for i in range(group[0]-3, group[0]+3):
      print "(i: {}, word: {}".format(i,word_list[i])
    print '========'
    for i in range(group[-1]-3, group[-1]+3):
      print "(i: {}, word: {}".format(i,word_list[i])
    print '\n'
  print '\n\n'

  return groups


# Joined Alex P and Abhi's parts
def cluster_func(indices_list, window_size=10):
    head = 0
    tail = 0
    counter = 1
    ranked_subsequences = []

    while head < len(indices_list):
        while (indices_list[head] + 1 - indices_list[tail]) > window_size:
            counter -= 1
            tail += 1

        ranked_subsequences.append((tail, head, counter))
        head += 1
        counter += 1

    sorted_ranges = sorted(ranked_subsequences, key=lambda x: x[2], reverse=True)
    return [(x[0] - 5, x[1] + 5) for x in sorted_ranges]


# uses the list of tuples and list of file_starts to find where a density occurs
def find_relevant_doc_id(average, file_start_ends):
    for file_start_index in range(1, len(file_start_ends)):
        if average >= file_start_ends[file_start_index - 1] and average <= file_start_ends[file_start_index]:
            return file_start_index


# takes a file location which is the file of raw questions
# parses all the questions and for each one, calls filterInputQuestion
def parseAllQuestions(question_location):
    question_file = open(question_location)
    raw_data = question_file.read()
    questions = raw_data.replace("<top>\r\n\r\n<num> Number: ", '') \
        .replace('\r\n\r\n<desc> Description:\r\n', ' ').replace('?\r\n\r\n<', '') \
        .replace('top>\r\n\r\n\r\n', '').split('/')
    # print questions

    output_file = open("answer.txt", 'w')
    for question_string in questions[:-1]:
        print question_string
        question_data = filterInputQuestion(question_string, COMMONLY_USED_WORDS)
        question_id = question_data[0]
        # find word ranges for the keywords and corresponding question number
        word_ranges = findWordRanges(question_data[2], question_id)
        # print word_ranges
        word_list_and_ranges = makeWordList(question_id)
        word_list = word_list_and_ranges[0]
        file_start_ends = word_list_and_ranges[1]
        # print file_start_ends
        # range_tuples are indices into the word_ranges array
        range_tuples = evan_cluster(word_ranges, word_list)

        first_five = range_tuples[:5]
        print first_five

        # output answers to the answers.txt file
        list_of_answers = parse_answer_from_ranges(question_data[1].lower(), first_five, word_list, question_data[2])
        # list_of_answers= [("1",2),("2",2),("3",1000),("4",2000),("5",500)]
        counter = 0
        for answer in list_of_answers:
            print answer[0]
            # nothing returned
            if (answer[0] == "None"):
                output_file.write(str(question_id) + ' ' + '1' + ' ' + ' ')
                # answer found
            else:
                doc_id=find_relevant_doc_id(answer[1],file_start_ends)
                print "DOCUMENT ID for average "+str(answer[1])+": "+str(doc_id)
                output_file.write(str(question_id) + ' ' + str(doc_id) + ' ' + str(answer) + '\n')
            counter += 1


# starts calling all questions
parseAllQuestions(SMALL_QUESTION_FILE)
