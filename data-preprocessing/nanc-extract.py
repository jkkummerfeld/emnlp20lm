import sys

in_headline = False
in_text = False
print_part = False
print_article = False
part = []
article = []
for line in sys.stdin:
    line = line.strip()

    if '. .' in line:
        words = []
        for word in line.split():
            if word.startswith('.'):
                words.append('.')
                words.append(word[1:])
            elif word.endswith('.'):
                words.append(word[:-1])
                words.append('.')
            else:
                words.append(word)
        nwords = []
        for word in words:
            if len(word) == 0:
                continue
            if word == '.' and len(nwords) > 0 and nwords[-1].endswith('.'):
                nwords[-1] += '.'
            else:
                nwords.append(word)

        line = ' '.join(nwords)
    
    if line == "<p>":
        print_part = True
    elif line.strip() == "</TEXT>":
        print_part = True
        print_article = True
        in_text = False
    else:
        if line.startswith("<HL>"):
            in_headline = True
            line = line.lstrip("<HL>").strip()
        elif line.startswith("<TEXT>"):
            in_text = True
            line = line.lstrip("<TEXT>").strip()

        if line.endswith("</HL>"):
            in_headline = False
            line = line.rstrip("</HL>").strip()
###            part.append(line)
            print_part = True

###        if in_headline or in_text:
        if in_text and len(line) > 0:
            if len(article) == 0 and len(part) == 0 and '--' in line:
                line = '--'.join(line.split('--')[1:])
            part.append(line)

    if print_part:
        if len(part) > 0:
            if not any(p.startswith("|") for p in part):
                if ''.join(part).strip() == '---':
                    print_article = True
                else:
                    article.append(" ".join(part))
            part = []
        print_part = False
        if print_article:
            if len(article) > 0:
                print("\n\n".join(article))
                print("[ARTICLE BOUNDARY]")
            print_article = False
            article = []

