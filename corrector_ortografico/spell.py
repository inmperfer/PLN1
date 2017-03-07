import re
import requests
from collections import Counter
from os import walk


def export_csv():
    with open('WORDS_es.csv', 'w') as f:
        [f.write('{0},{1}\n'.format(key, value)) for key, value in WORDS.items()]


        
def exist_word_in_dict(w):
    result=False
    url ="https://glosbe.com/gapi/translate?from=spa&dest=spa&format=json&phrase={0}".format(w)
    print(url)
    resp = requests.get(url).json()
    if('result' in resp):
        if(resp['result'] == 'ok'):
            if('tuc' in resp):
                result=True            
    return result
    
    
def words(text): 
	return re.findall(r'\w+', text.lower(), re.UNICODE)

# Inicio WORDS con las palabras de los diccionarios
# En este método no se aumentará la frecuencia de la palabra, si ya existe no se actualiza el numero de ocurrencias
def init_WORDS(dictionary_path):
    c_result = Counter()
    for (path, dirs, files) in walk(dictionary_path):
        for f in files:
            print('reading file {0} ...'.format(path + '/' + f))
            c_result = c_result | Counter(words(open(path + '/' + f, encoding="utf-8").read()))
    return c_result
    


def train_WORDS(train_path):
    c_result = Counter()
    for (path, dirs, files) in walk(train_path):
        for f in files:
            print('reading file {0} ...'.format(path + '/' + f))
            ws = words(open(path + '/' + f, encoding="utf-8").read())
            c_result = c_result + Counter(ws)
    return c_result
 
    
WORDS=dict()
WORDS=init_WORDS('dictionary/es')
print('size of WORDS={0}'.format(len(WORDS)))

WORDS_train=train_WORDS('train/es')
print('size of WORDS_train={0}'.format(len(WORDS_train)))

# remove = [w for w in WORDS_train if exist_word_in_dict(w)==False]
# for r in remove: del WORDS_train[r]

WORDS=WORDS+WORDS_train
print('size of WORDS after training={0}'.format(len(WORDS)))

export_csv()


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
