import re
from functools import partial
from collections import Counter
import nltk
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer

def removeUnicode(text):
	#Removes unicode strings like "\u002c" and "x96"
	text = re.sub(r'(\\u[0-9A-Fa-f]+)',r'', text)       
	text = re.sub(r'[^\x00-\x7f]',r'',text)
	return text

def replaceURL(text):
	#Replaces url address with "url" 
	text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','<url>',text)
	text = re.sub(r'#([^\s]+)', r'\1', text)
	return text

def replaceAtUser(text):
	#Replaces "@user" with "atUser"
	text = re.sub('@[^\s]+','<atUser>',text)
	return text

def removeHashtag(text):
	#Removes hastag in front of a word
	text = re.sub(r'#([^\s]+)', r'\1', text)
	return text

def removeNumbers(text):
	#Removes integers
	text = ''.join([i for i in text if not i.isdigit()])         
	return text

def replaceMulExcl(text):
	#Replaces repetitions of exlamation marks
	text = re.sub(r"(\!)\1+", '!', text)
	return text

def replaceMulQues(text):
	#Replaces repetitions of question marks
	text = re.sub(r"(\?)\1+", '?', text)
	return text

def replaceMulStop(text):
	#Replaces repetitions of stop marks
	text = re.sub(r"(\.)\1+", '.', text)
	return text

def countMulExcl(text):
	#count repetitions of exlamation marks
	return len(re.findall(r"(\!)\1+", text))

def countMulQues(text):
	#Count repetitions of question marks
	return len(re.findall(r"(\?)\1+", text))

def countMulStop(text):
	#Count repetitions of stop marks
	return len(re.findall(r"(\.)\1+", text))

def countElongated(text):
	#count of how many words are elongated
	regex = re.compile(r"(.)\1{2}")
	return len([word for word in text.split() if regex.search(word)])

def countAllCaps(text):
	#count of how many words are all caps
	return len(re.findall("[A-Z0-9]{3,}", text))

#Creates a dictionary with slangs and their equivalents and replaces them
with open('slang.txt') as file:
	slang_map = dict(map(str.strip, line.partition('\t')[::2])
	for line in file if line.strip())

slang_words = sorted(slang_map, key=len, reverse=True)
regex = re.compile(r"\b({})\b".format("|".join(map(re.escape, slang_words))))
replaceSlang = partial(regex.sub, lambda m: slang_map[m.group(1)])

#punctuation list for replacing

puncts = [',', '.', '"', ':', ')', '(', '-', '|', ';', "'", '$', '&', '/', '[', ']', '%', '=', '*', '+', '\\', '•',  '~', '£', 
 '·', '_', '{', '}', '©', '^', '®', '`', '→', '°', '€', '™', '›',  '♥', '←', '×', '§', '″', '′', 'Â', '█', '½', 'à', '…', 
 '“', '★', '”', '–', '●', 'â', '►', '−', '¢', '²', '¬', '░', '¶', '↑', '±', '¿', '▾', '═', '¦', '║', '―', '¥', '▓', '—', '‹', '─', 
 '▒', '：', '¼', '⊕', '▼', '▪', '†', '■', '’', '▀', '¨', '▄', '♫', '☆', 'é', '¯', '♦', '¤', '▲', 'è', '¸', '¾', 'Ã', '⋅', '‘', '∞', 
 '∙', '）', '↓', '、', '│', '（', '»', '，', '♪', '╩', '╚', '³', '・', '╦', '╣', '╔', '╗', '▬', '❤', 'ï', 'Ø', '¹', '≤', '‡', '√', ]

def removePuncts(x):
	x = str(x)
	for punct in puncts:
		if punct in x:
			x = x.replace(punct, f' ')
	return x



def countSlang(text):
	# counts how many slang words and a list of found slangs
	slangCounter = 0
	slangsFound = []
	tokens = nltk.word_tokenize(text)
	for word in tokens:
		if word in slang_words:
			slangsFound.append(word)
			slangCounter += 1
	return slangCounter, slangsFound

#Replaces contractions from a string to their equivalents
contraction_patterns = [ (r'I\'m', 'I am'),(r'won\'t', 'will not'), (r'can\'t', 'cannot'), (r'i\'m', 'i am'), (r'ain\'t', 'is not'), (r'(\w+)\'ll', '\g<1> will'), (r'(\w+)n\'t', '\g<1> not'),
						 (r'(\w+)\'ve', '\g<1> have'), (r'(\w+)\'s', '\g<1> is'), (r'(\w+)\'re', '\g<1> are'), (r'(\w+)\'d', '\g<1> would'), (r'&', 'and'), (r'dammit', 'damn it'), (r'dont', 'do not'), (r'wont', 'will not') ]
def replaceContraction(text):
	patterns = [(re.compile(regex), repl) for (regex, repl) in contraction_patterns]
	for (pattern, repl) in patterns:
		(text, count) = re.subn(pattern, repl, text)
	return text

def replaceElongated(word):
	#Replaces an elongated word with its basic form

	repeat_regexp = re.compile(r'(\w*)(\w)\2(\w*)')
	repl = r'\1\2\3'
	if wordnet.synsets(word):
		return word
	repl_word = repeat_regexp.sub(repl, word)
	if repl_word != word:      
		return replaceElongated(repl_word)
	else:       
		return repl_word

def removeEmoticons(text):
	#Removes emoticons from text 
	text = re.sub(':\)|;\)|:-\)|\(-:|:-D|=D|:P|xD|X-p|\^\^|:-*|\^\.\^|\^\-\^|\^\_\^|\,-\)|\)-:|:\'\(|:\(|:-\(|:\S|T\.T|\.\_\.|:<|:-\S|:-<|\*\-\*|:O|=O|=\-O|O\.o|XO|O\_O|:-\@|=/|:/|X\-\(|>\.<|>=\(|D:', '', text)
	return text

def countEmoticons(text):
	#Input: a text, Output: how many emoticons
	return len(re.findall(':\)|;\)|:-\)|\(-:|:-D|=D|:P|xD|X-p|\^\^|:-*|\^\.\^|\^\-\^|\^\_\^|\,-\)|\)-:|:\'\(|:\(|:-\(|:\S|T\.T|\.\_\.|:<|:-\S|:-<|\*\-\*|:O|=O|=\-O|O\.o|XO|O\_O|:-\@|=/|:/|X\-\(|>\.<|>=\(|D:', text))


### Spell Correction begin ###
def words(text): return re.findall(r'\w+', text.lower())

WORDS = Counter(words(open('spell_correction.txt').read()))

def P(word, N=sum(WORDS.values())): 
	#P robability of `word`.
	return WORDS[word] / N

def spellCorrection(word): 
	#Most probable spelling correction for word.
	return max(candidates(word), key=P)

def candidates(word): 
	#Generate possible spelling corrections for word.
	return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

def known(words): 
	#The subset of `words` that appear in the dictionary of WORDS.
	return set(w for w in words if w in WORDS)

def edits1(word):
	#All edits that are one edit away from `word`.
	letters    = 'abcdefghijklmnopqrstuvwxyz'
	splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
	deletes    = [L + R[1:]               for L, R in splits if R]
	transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
	replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
	inserts    = [L + c + R               for L, R in splits for c in letters]
	return set(deletes + transposes + replaces + inserts)

def edits2(word): 
	#All edits that are two edits away from `word`.
	return (e2 for e1 in edits1(word) for e2 in edits1(e1))

### Spell Correction End ###
