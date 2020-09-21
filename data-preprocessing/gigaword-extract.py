import sys

in_text = False
print_part = False
print_article = False
part = []
article = []

filenum = 0
out = open('gigaword{}.txt'.format(filenum), 'w')
todo = 100000
for line in sys.stdin:
    line = line.strip()
    
    if line.lower() in ["<p>", "</p>"] or len(line) == 0:
        print_part = True
    elif line.strip() == "</TEXT>":
        print_part = True
        print_article = True
        in_text = False
    elif line.startswith("<TEXT>"):
        in_text = True
    elif in_text:
        part.append(line)

    if print_part:
        if len(part) > 0:
            article.append(" ".join(part))
            part = []
        print_part = False

    if print_article:
        if len(article) > 0:
            print("\n\n".join(article), file=out)
            print("[ARTICLE BOUNDARY]", file=out)
            todo -= 1
            if todo == 0:
                out.close()
                filenum += 1
                out = open('gigaword{}.txt'.format(filenum), 'w')
                todo = 100000
        print_article = False
        article = []

