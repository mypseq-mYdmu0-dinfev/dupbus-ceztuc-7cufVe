#!/usr/bin/env python3
"""padv.py —— `#replace #adv` helper (RUN, don't read). Extracts a verbatim span
from a `<name>.pages.md` mirror and splits it into break-free blocks ready to
paste into a Pages find-and-replace.

=== NON-CCSIM —— start of all you need to RUN it ===
WHAT: `#replace #adv` helper —— extracts a verbatim span from a `.pages.md`
mirror, split into break-free blocks Pages' find-and-replace can match.

CLI:  python3 cscpt/padv.py <mirror.pages.md> "<start_anchor>" ["<end_anchor>"]
      -> prints the U+2028 count + paste-ready Replace block(s).
      Omit <end_anchor> for the start_anchor text alone.
Lib:  import sys; sys.path.insert(0, 'cscpt'); from padv import grab, split_for_pages
      span   = grab(open(mirror).read(), start, end)   # U+2028 intact
      blocks = split_for_pages(span)                   # 1, 2 or 3 break-free blocks

* ANCHORS must themselves be break-free (no U+2028 inside); the span between
  them may hold any number of breaks.
* A missing anchor raises ValueError naming which one.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
FAIL-LOUD, NOT PARTIAL: a missing anchor raises before anything is printed, so a
half-formed Replace block can never reach the clipboard and be pasted over live
Pages content.

WHY THE SPLIT EXISTS: Pages' ⌘F cannot match a string containing a U+2028 layout
line-break, so a `Replace:` target spanning breaks must be quoted as break-free
blocks (max 3): 0 breaks -> the span; 1 -> [before, after]; 2+ -> [before_first,
middle with its internal breaks cancelled, after_last].
Each non-final mirror segment ends with the space that preceded its U+2028, so
joining the middle with '' restores single spaces —— never insert a separator
there, nor strip the segments individually before joining.
"""
import sys

LSEP = ' '  # Unicode LINE SEPARATOR == Pages soft-return (Shift-Return / wrap)


def grab(text, start, end=None):
    """Verbatim substring from `start` through `end` (inclusive), U+2028 preserved."""
    i = text.find(start)
    if i < 0:
        raise ValueError(f"start anchor not found: {start!r}")
    if end is None:
        return text[i:i + len(start)]
    j = text.find(end, i + len(start))
    if j < 0:
        raise ValueError(f"end anchor not found after start: {end!r}")
    return text[i:j + len(end)]


def split_for_pages(span):
    """Break-free blocks per the #adv fallback:
       0 breaks -> [span]; 1 -> [before, after];
       >=2 -> [before_first, middle_with_internal_breaks_cancelled, after_last].
    Each non-final mirror segment ends with the space that preceded its U+2028,
    so joining the middle by '' restores single spaces."""
    parts = span.split(LSEP)
    n = len(parts) - 1
    if n == 0:
        return [span.strip()]
    if n == 1:
        return [parts[0].strip(), parts[1].strip()]
    return [parts[0].strip(), ''.join(parts[1:-1]).strip(), parts[-1].strip()]


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit('usage: python3 cscpt/padv.py <mirror.pages.md> "<start_anchor>" ["<end_anchor>"]')
    mirror = open(sys.argv[1], encoding='utf-8').read()
    span = grab(mirror, sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    blocks = split_for_pages(span)
    print(f"# {span.count(LSEP)} U+2028 break(s) -> {len(blocks)} block(s)")
    for b in blocks:
        print('```')
        print(b)
        print('```')
