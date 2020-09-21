import re
import sys
import string

def apply_re(expression, done, todo, current, label=''):
    if len(current) == 0:
        return current
    else:
        # Split
        parts = []
        for v in re.split(expression, current):
            if v is not None and len(v) > 0:
                parts.append(label + v)

        # Push all but the start back on todo
        if len(parts) > 1:
            for part in parts[:0:-1]:
                if len(part) > 0:
                    todo.insert(0, part)

        return parts[0]

# Names two letters or less that occur more than 500 times in the data
common_short_names = {"ng", "_2", "x_", "rq", "\\9", "ww", "nn", "bc", "te",
"io", "v7", "dm", "m0", "d1", "mr", "x3", "nm", "nu", "jc", "wy", "pa", "mn",
"a_", "xz", "qr", "s1", "jo", "sw", "em", "jn", "cj", "j_"}

def tokenise(line, users):
    tokens = []

    parts = line.strip().split()
    # Handle timestamp and username
    if re.match(".*\[[0-9][0-9][:][0-9][0-9]\]$", parts[0]) is None:
        timestamp = parts.pop(0)
    else:
        timestamp = parts.pop(0)
        user = parts.pop(0)
        while user[-1] != '>' and len(parts) > 0:
            user += parts.pop(0)
        if user[0] == '<':
            user = user[1:]
        if user[-1] == '>':
            user = user[:-1]
        user = user.strip()
        tokens.append(get_user(users, user))

    # Handle message
    while len(parts) > 0:
        current = parts.pop(0)
        current = current.lower()

        # Handle username mentions
        user = None
        if current in users and len(current) > 2:
            user = current
        else:
            core = [char for char in current]
            while len(core) > 0 and core[-1] in string.punctuation:
                core.pop()
                nword = ''.join(core)
                if nword in users and (len(core) > 2 or nword in common_short_names):
                    user = nword
                    break
            if user is None:
                while len(core) > 0 and core[0] in string.punctuation:
                    core.pop(0)
                    nword = ''.join(core)
                    if nword in users and (len(core) > 2 or nword in common_short_names):
                        user = nword
                        break
        if user is not None:
            subparts = current.split(user)
            if len(subparts[0]) > 0:
                tokens.append(subparts[0])
            tokens.append(get_user(users, user))
            if len(subparts[-1]) > 0:
                tokens.append(subparts[-1])
            current = ''
            continue

###        #  - email (...@...) or prompt (...@...:...) make word shape (...@...) and split on ':'
###        if "@" in current and (not current.startswith("@")) and (not current.endswith('@')):
###            if len(current.split("@")) == 2:
###                tokens.append("ADDRESS_" + current.split("@")[0])
###                tokens.append("ADDRESS_@" + current.split("@")[1])
###                current = ''
###                continue

###        #  - Permissions (only rwxd-), split into groups of three characters
###        if len(current) == 10 and re.fullmatch("[-rwxd]+", current) is not None:
###            tokens.append('PERMISSIONS_'+ current[:1])
###            tokens.append('PERMISSIONS_'+ current[1:4])
###            tokens.append('PERMISSIONS_'+ current[4:7])
###            tokens.append('PERMISSIONS_'+ current[7:])
###            current = ''
###            continue

###        #  - URLs (start with http, sftp, telnet) split on '/' and add it (http://) (...) (/.../) (/.../) ...
###        if re.match("^((http)|(sftp)|(telnet)).*\/", current) is not None:
###            chunks = [c for c in current.split("/") if len(c) != 0]
###            tokens.append("URL/"+ chunks[0] +"/")
###            if len(chunks) > 1:
###                tokens.append("URL/"+ chunks[1] +"/")
###                if len(chunks) > 2:
###                    tokens.append("URL/"+ '/'.join(chunks[2:]) +"/")
###            current = ''
###            continue
###        if current.startswith("www."):
###            current = "URL/"+ current

        #  - ...[:;*,.?!)] and group repeats (... or ... or !?!!??!?!)
        current = apply_re("""([":;?!.,)}\]]+$)""", tokens, parts, current)

###        #  - Directories (start with / or ~) split into pieces (/.../) (/.../)
###        if re.match("^[~/]", current) is not None:
###            chunks = current.split("/")
###            for chunk in chunks:
###                if len(chunk) > 0:
###                    tokens.append("DIR/"+ chunk +"/")
###            current = ''
###            continue

        #  - [!({[]...
        current = apply_re("""(^["!({[]+)""", tokens, parts, current)

        #  - ...'s  ...n't  ...'ll  ...'m ...'ve (and in all cases allow ' or ")
        current = apply_re("""(['"]s)$""", tokens, parts, current)
        current = apply_re("""(n['"]t)$""", tokens, parts, current)
        current = apply_re("""(['"]ll)$""", tokens, parts, current)
        current = apply_re("""(['"]m)$""", tokens, parts, current)
        current = apply_re("""(['"]ve)$""", tokens, parts, current)

        #  - mid-word ellipses (e.g. know...But)
        current = apply_re("""([.][.]+)""", tokens, parts, current)

        #  - Instructions like "System->Admin->Shared" split on "[-]?>"
        current = apply_re("""([-]?[>])""", tokens, parts, current)

###        #  - "s/.../..." to "substitution / ... / ... /"
###        if re.match("s/.*/", current) is not None:
###            for chunk in current.split("/"):
###                if len(chunk) > 0:
###                    tokens.append("SUB/"+ chunk +"/")
###            current = ''
###            continue

        #  - Numbers (do not convert all numbers to 0, as 32 != 64)
        # versions, etc, so not worth collapsing

        if len(current) > 0:
            tokens.append(current)

    return tokens

def get_user(users, user):
    while isinstance(user, str):
        user = users[user]
    return "participant_{}".format(user)

def update_user(users, user, key):
    all_digit = True
    for char in user:
        if char not in string.digits:
            all_digit = False
    if all_digit:
        return

    if user not in users:
        if key is None:
            users[user] = len(users)
        else:
            users[user] = key

def update_users(line, users):
    if len(line.split()) < 2:
        return
    parts = line.strip().split()
    parts.pop(0)
    user = parts.pop(0)
    while user[-1] != '>' and len(parts) > 0:
        user += parts.pop(0)
    if user in ["Topic", "Signoff", "Signon", "Total", "#ubuntu",
            "Window", "Server:", "Screen:", "Geometry", "CO,",
            "Current", "Query", "Prompt:", "Second", "Split",
            "Logging", "Logfile", "Notification", "Hold", "Window",
            "Lastlog", "Notify", 'netjoined:']:
        # Ignore as these are channel commands
        pass
    else:
        if line.split()[0].endswith("==="):
            parts = line.split("is now known as")
            if len(parts) == 2 and line.split()[-1] == parts[-1].strip():
                user = line.split()[-1]
        elif line.split()[0][-1] == ']':
            if user[0] == '<':
                user = user[1:]
            if user[-1] == '>':
                user = user[:-1]

        user = user.lower()
        update_user(users, user, len([_ for _, v in users.items() if isinstance(v, int)]))
        # This is for cases like a user named |blah| who is
        # refered to as simply blah
        core = [char for char in user]
        while len(core) > 0 and core[0] in string.punctuation:
            core.pop(0)
        while len(core) > 0 and core[-1] in string.punctuation:
            core.pop()
        core = ''.join(core)
        update_user(users, core, user)

cur = []
for line in sys.stdin:
    line = line.strip()
    if len(line) == 0:
        if len(cur) > 0:
            users = {}
            for line in cur:
                update_users(line.strip(), users)

            final = []
            for line in cur:
                line = line.strip()
                tokens = tokenise(line.strip(), users)
                final.append(' '.join(tokens))
            print(" NEXT_MSG ".join(final))

            cur = []
    else:
        cur.append(line.lower())
