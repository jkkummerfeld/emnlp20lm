import stanza
import sys

nlp = stanza.Pipeline(lang='en', processors='tokenize')

article = []
for line in sys.stdin:
    line = line.strip()
    if line == '':
        continue
    if line == "[ARTICLE BOUNDARY]":
        print(' '.join(article))
        article = []
        continue

    doc = nlp(line)
    for i, sentence in enumerate(doc.sentences):
        article.append(' '.join([token.text for token in sentence.tokens]))
