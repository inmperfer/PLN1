import re
from collections import Counter
from os import walk

def words(text): 
	return re.findall(r'\w+', text.lower())

# Inicio WORDS con las palabras de los diccionarios
# En este método no se aumentará la frecuencia de la palabra, si ya existe no se actualiza el numero de ocurrencias
def init_WORDS(dictionary_path):
    c_result = Counter()
    for (path, dirs, files) in walk(dictionary_path):
        for f in files:
            print('reading file {0} ...'.format(path + '/' + f))
            c_result = c_result | Counter(words(open(path + '/' + f, encoding="latin-1").read()))
    return c_result
    


WORDS=init_WORDS('dictionary/es')
print('size of WORDS={0}'.format(len(WORDS)))


def train_WORDS(train_path):
    c_result = Counter()
    for (path, dirs, files) in walk(train_path):
        for f in files:
            print('reading file {0} ...'.format(path + '/' + f))
            c_result = c_result + Counter(words(open(path + '/' + f, encoding="utf-8").read()))
    return c_result
    
WORDS_train=train_WORDS('train/es')
print('size of WORDS train={0}'.format(len(WORDS_train)))


def P(word, N=sum(WORDS.values())): 
    "Probability of `word`."
    return WORDS[word] / N

# Develve una lista de posibles palabras ordenadas por probabilidad
def correction(word): 
    return sorted(candidates(word), key=P)


def candidates(word): 
    "Generate possible spelling corrections for word."
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

def known(words): 
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)

# Añado el caracter ñ	
def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnñopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word): 
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))
	
def edits3(word):
	return