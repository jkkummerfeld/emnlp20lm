#!/usr/bin/env python3

import tarfile
import string
import sys
import argparse

parser = argparse.ArgumentParser(description='Get text for language modeling evaluation based on the original Penn Treebank Wall Street Journal data, following the Mikolov style preprocessing. Run with just the treebank file to get a very close match to the Mikolov files (all but 282 words match out of more than a million).')

parser.add_argument('treebank',
        help='treebank_3_LDC99T42.tgz file from the LDC')

parser.add_argument('--prefix', default="penn_text.",
        help='Prefix for output files')
parser.add_argument('--no-unks', action='store_true',
        help='Do not introduce unks')
parser.add_argument('--keep-case', action='store_true',
        help='Do not lowercase all text')
parser.add_argument('--keep-nums', action='store_true',
        help='Do not convert numbers to N')
parser.add_argument('--keep-punc', action='store_true',
        help='Do not remove punctuation')
parser.add_argument('--keep-percent', action='store_true',
        help='Do not remove percentage signs')
args = parser.parse_args()

# Apply edits based on command line arguments
def modify_token(token):
    if not args.keep_case:
        token = token.lower()

    if not args.keep_punc:
        if token in ["''", "``", ',', '.', ':', ';', '--', '(', ')', '...', '-lrb-', '-rrb-', '-lcb-', '-rcb-', '?', '!', '`', '-']:
            return None
        if token.lower() == 'u.s':
            token = 'u.s.'

    if not args.keep_nums:
        has_char = False
        has_num = False
        for char in token:
            if char in string.ascii_letters + "'":
                has_char = True
            elif char in string.digits:
                has_num = True
        if has_num and (not has_char):
            token = "N"

    if not args.keep_percent:
        if token == '%':
            token = 'N'

    if len(token) == 0:
        return None
    return token

# Read data
data = tarfile.open(args.treebank, "r:gz")
text = {}
for member in data.getmembers():
    if member.name.endswith(".mrg") and 'wsj' in member.name:
        name = member.name.split('_')[-1][:2]
        text.setdefault(name, [[]])

        lines = data.extractfile(member).readlines()

        # We are reading the syntactic parses, so track depth to know when we
        # finish a sentence.
        # Note, why the parse files?
        # - Raw, require tokenisation
        # - Tagged, have breaks that make sentence boundaries unclear
        # - Prd, have some formatting issues
        depth = 0
        for line in lines:
            line = line.decode("ascii").strip().split()
            for prev, token in zip([''] + line, line):
                if '(' in token:
                    for char in token:
                        if char == '(':
                            depth += 1
                else:
                    for char in token:
                        if char == ')':
                            depth -= 1
                    if prev == '(-NONE-':
                        continue
                    token = token.rstrip(")")
                    token = modify_token(token)
                    if token is not None:
                        text[name][-1].append(token)

            if depth == 0 and len(text[name][-1]) > 0:
                text[name].append([])

# Prepare output files
train = open(args.prefix +'train.txt', 'w')
valid = open(args.prefix +'valid.txt', 'w')
test = open(args.prefix +'test.txt', 'w')
name2file = {
    "00": train, "01": train, "02": train, "03": train, "04": train,
    "05": train, "06": train, "07": train, "08": train, "09": train,
    "10": train, "11": train, "12": train, "13": train, "14": train,
    "15": train, "16": train, "17": train, "18": train, "19": train,
    "20": train,
    "21": valid, "22": valid,
    "23": test, "24": test,
}

# Insert <unk> tokens
if not args.no_unks:
    # Count words in training and validation data
    counts = {}
    for name in text:
        if name2file[name] == train or name2file[name] == valid:
            for sentence in text[name]:
                for token in sentence:
                    counts[token] = counts.get(token, 0) + 1

    # Keep 10,000 words, keeping the most frequent ones. This cuts off part way
    # through the words with frequency 5.
    #
    # This is where the remaining difference is with Mikolov's data.
    pairs = [(-c, t) for t, c in counts.items()]
    pairs.sort()
    top10k = {t for _, t in pairs[:10000]}

    # Replace rare words with <unk>
    for name in text:
        for sentence in text[name]:
            for j, token in enumerate(sentence):
                if token not in top10k:
                    sentence[j] = '<unk>'
 
# Print data
names = list(text.keys())
names.sort()
for name in names:
    for sentence in text[name]:
        if len(sentence) > 0:
            print(' '.join(sentence), file=name2file[name])

# Close files
train.close()
valid.close()
test.close()
