import scispacy
import spacy
import sys
import json

nlp = spacy.load("en_core_sci_lg")
nlp.max_length = 10000000

for line in sys.stdin:
    data = json.load(open(line.strip()))
    text = []
    for para in data['body_text']:
        text.append(' '.join(para['text'].split()))
    doc = nlp(' '.join(text), disable=["tagger", "parser", "ner"])
    for tok in doc:
        print(str(tok).lower(), end=' ')
    print()
