from nltk.corpus import wordnet
from itertools import product


list1 = ['murdered', "ball", "sack", "fuck"]
list2 = ['kill', "jim", "bob", "fish"]
allsyns1 = set(ss for word in list1 for ss in wordnet.synsets(word))
allsyns2 = set(ss for word in list2 for ss in wordnet.synsets(word))
best = max((wordnet.wup_similarity(s1, s2) or 0, s1, s2) for s1, s2 in
        product(allsyns1, allsyns2))
print(best)