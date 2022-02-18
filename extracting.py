from textblob import TextBlob
import re
import nltk

usless = ['a', 'an', 'the', 'da']

abbreviations = {
    "ai": "be",
    "n't" : "not",
    "'ll" : "will",
    "'re" : "be",
    "'s" : "be",    
    "'m" : "be",
    "'ve" : "have",
    "'d" : "would",
    "ya" : "you",
    "cuz" : "because",
    "bc" : "because",
    "u" : "you",
    "ur" : "your",
    "r" : "be",
    "c" : "see",
    "wanna" : "want",
    "gonna" : "go",
    "gotta": "have got",
    "lets": "let us"
}

def remove_short_verbs(s):
    while match := re.search("in'( |$)", s):
        s_l = list(s)
        idx = match.span()[0]
        s_l[idx:idx + 3] = 'ing'
        s = ''.join(s_l)
    return s

def remove_alpha_exceptions(s):
    while match := re.search("s'( |$)", s):
        s_l = list(s)
        idx = match.span()[0]
        s_l[idx:idx + 2] = "s's"
        s = ''.join(s_l)
    return s
    
def extract(s):
    s = remove_short_verbs(s)
    s = remove_alpha_exceptions(s)
    s = s.replace('’', "'")
    
    blob = TextBlob(s.lower())
    tags = blob.tags
    extracted = []
    
    for word, tag in tags:
        if word in usless:
            continue
        elif word == "'s" and tag == 'POS' and len(extracted) > 0:
            if extracted[-1] == 'let':
                word = 'us'
            else:
                word = '<alpha>'
        elif word in abbreviations:
            abbr = abbreviations[word]
            extracted += abbr.split()
            continue
        
        if tag == 'JJR':
            to_add = [
                'more', word.lemmatize('a')
            ]
        elif tag == 'JJS':
            to_add = [
                'most', word.lemmatize('a')
            ]
        elif tag[:2] == 'NN' and tag[-1] == 'S':
            to_add = [
                word.lemmatize()
            ]
        elif tag in ['VBP', 'VBZ', 'VBG']:
            to_add = [
                word.lemmatize('v')
            ]
        elif tag in ['VBD']:
            to_add = [
                'did', word.lemmatize('v')
            ]
        else:
            to_add = [str(word)]
        
        extracted += to_add
    
    return extracted
                                                                       
def apply_alpha(words):
    while '<alpha>' in words:
        idx = words.index('<alpha>')  
        del words[idx]
        if idx == 0:
            continue
        prev_word = words[idx - 1]
        tag = nltk.pos_tag([prev_word])[0][1]
        if tag[:2] != 'NN':
            continue
        suffix = "'s" if prev_word[-1] != 's' else "'"
        words[idx - 1] += suffix
    return words

def extract_daily_dialogs(lb, rb):
    with open('daily_dialogs/text.txt', 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
        
    dialogs = []
    
    if rb == -1:
        rb = len(lines)
    
    lines = lines[lb:rb]
    #print(lines)
    
    for line in lines:
        dialog = line.replace(' ’ ', "'").split('__eou__')
        del dialog[-1]
        dialogs.append(dialog)
        
    return dialogs
        
def extract_movie_dialogs(lb, rb):
    with open('movie_dialogs/lines.txt', 'r') as f:
        lines_raw = f.read().splitlines()
        
    lines = {}
    
    for line_raw in lines_raw:
        splitted = line_raw.split(' +++$+++ ')
        key, line = splitted[0], splitted[-1]
        lines[key] = line
    
    with open('movie_dialogs/conversations.txt', 'r') as f:
        dialog_lines = f.read().splitlines()
        
    dialogs = []
    
    if rb == -1:
        rb = len(dialog_lines)
    
    dialog_lines = dialog_lines[lb:rb]
        
    for dialog_line in dialog_lines:
        keys = eval(dialog_line.split(' +++$+++ ')[-1])
        dialog = [
            lines[key] for key in keys
        ]
        dialogs.append(dialog)
        
    return dialogs