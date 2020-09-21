import json
import sys

for filename in sys.argv[1:]:
    out = open(filename + ".txt", 'w')
    for line in open(filename):
        data = json.loads(line)
        text = data['text']
        start = 0
        for i, char in enumerate(text):
            if char == '\n':
                start = i
                break
        lines = text[start:].split("\n")
        for line in lines:
            if len(line.strip()) > 0:
                print("".join(line.split("()")), file=out)
        print("[ARTICLE BOUNDARY]", file=out)
