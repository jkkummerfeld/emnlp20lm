import sys
import string

for line in sys.stdin:
    words = line.strip().split()
    for i, word in enumerate(words):
        has_char = False
        has_num = False
        for char in word:
            if char in string.ascii_letters:
                has_char = True
            elif char in string.digits:
                has_num = True
        if has_num and (not has_char):
            words[i] = 'N'
    print(' '.join(words))
