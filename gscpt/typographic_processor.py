import os
import re

SRC = os.path.dirname(os.path.abspath(__file__))
DST = '/Volumes/FURY 2TB/Fury Downloads'
SKIP = {'temp.txt'}
EXTS = {'.txt', '.md'}

# -----------------------------------------------------------------------
# TARGET: straight " and ' only (Unicode U+0022 and U+0027)
# IGNORE: typographic equivalents already in text (U+201C/D, U+2018/9)
# Replace placeholders below with actual typographic characters in VS Code:
#   OPEN_DOUBLE  -> [open"]   = U+201C
#   CLOSE_DOUBLE -> [close"]  = U+201D
#   OPEN_SINGLE  -> [open']   = U+2018
#   CLOSE_SINGLE -> [close']  = U+2019  (also used for apostrophe)
# -----------------------------------------------------------------------
OPEN_DOUBLE  = '“'   # [open"]
CLOSE_DOUBLE = '”'   # [close"]
OPEN_SINGLE  = '‘'   # [open']
CLOSE_SINGLE = '’'   # [close'] / [ap]


def convert(text):
    count = 0
    result = []
    chars = list(text)
    n = len(chars)
    i = 0
    double_open = True  # next " encountered will be OPEN_DOUBLE

    while i < n:
        c = chars[i]

        # --- straight double quote U+0022 ---
        if c == '\u0022':
            if double_open:
                result.append(OPEN_DOUBLE)
            else:
                result.append(CLOSE_DOUBLE)
            double_open = not double_open
            count += 1

        # --- straight single quote / apostrophe U+0027 ---
        elif c == '\u0027':
            left_word = i > 0 and bool(re.match(r'\w', chars[i - 1]))
            if left_word:
                # apostrophe (it's, Test's) or closing single quote
                result.append(CLOSE_SINGLE)
            else:
                prev = chars[i - 1] if i > 0 else ' '
                if i == 0 or prev in ' \t\n\r([{':
                    result.append(OPEN_SINGLE)
                else:
                    result.append(CLOSE_SINGLE)
            count += 1

        else:
            result.append(c)

        i += 1

    return ''.join(result), count


def main():
    os.makedirs(DST, exist_ok=True)

    files = [
        f for f in os.listdir(SRC)
        if f not in SKIP and os.path.splitext(f)[1].lower() in EXTS
    ]
    multi = len(files) > 1

    total = 0
    for fname in files:
        src_path = os.path.join(SRC, fname)
        dst_path = os.path.join(DST, fname)

        with open(src_path, 'r', encoding='utf-8') as f:
            text = f.read()

        converted, n = convert(text)

        if os.path.exists(dst_path):
            prefix = f'[{fname}] ' if multi else ''
            print(f'{prefix}⛔STOPPED: "{fname}" already exists in output folder. Remove it and rerun.')
            continue

        with open(dst_path, 'w', encoding='utf-8') as f:
            f.write(converted)

        if multi:
            print(f'[{fname}] Done. {n} instances converted.')
        else:
            total += n

    if not multi:
        print(f'Done. {total} instances converted.')


if __name__ == '__main__':
    main()