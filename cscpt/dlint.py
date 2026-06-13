#!/usr/bin/env python3
"""
dlint.py —— deterministic DELIVERABLE linter (Claude-only; lives in /cscript/).

Run AFTER drafting ANY deliverable, on the deliverable TEXT ONLY. NEVER point it
at a `response_`/comms file —— those legitimately use ` —— `, colons, etc.
  - Long deliverable (separate file): pass that file path directly.
  - Short deliverable embedded in a `response_`: extract it to a temp file beside
    the `response_`, lint that temp, paste back when clean, then VOID the temp.

TWO JOBS
--------
1. AUTO-FIX (in place): straight quotes/apostrophes (U+0022 / U+0027) ->
   typographic, chosen by context. Inherited from gscpt/quote_fix.py; idempotent
   (already-typographic quotes are left alone). This is the ONLY thing it rewrites.

2. FLAG (print only, never rewrites prose) two tiers of breaches drawn from
   `universal/writing.md` AND root `CLAUDE.md`:

     RED  —— hard, deterministic breaches: em dash `—`, en dash `–` used as
             punctuation (range `1–2` excepted), banned Americanisms (root
             §2.1.1), mid-sentence colons. You CANNOT proceed until RED = 0;
             fix and rerun, looping until clean.
     YELLOW — conditional breaches that may be legitimate in context: bare `+`,
             spaced hyphen, sentence-initial `Where`, GenAI/cliche words &
             phrases. You MAY proceed with yellows remaining ONLY IF you
             concisely justify EACH in the `response_` (e.g. `+` is part of
             `iCloud+`; `Where are you?` is a genuine question).

USAGE
-----
    python3 cscript/dlint.py <deliverable_path> [<more_paths> ...]

EXIT CODE
---------
    0 = no RED flags (yellows may remain -> justify in response_)
    1 = at least one RED flag (fix and rerun)
    2 = usage / file error

NOTE: the word/spelling lists below are seeded from `writing.md` + root
`CLAUDE.md` and are NOT exhaustive —— extend as conventions evolve.
(`cc_writing.md` is being retired and is deliberately NOT referenced.)
"""

import re
import sys
from pathlib import Path

# =========================================================
# QUOTE CONVERSION (inherited from gscpt/quote_fix.py)
# =========================================================

OPEN_DOUBLE  = "“"   # “
CLOSE_DOUBLE = "”"   # ”
OPEN_SINGLE  = "‘"   # ‘
CLOSE_SINGLE = "’"   # ’ (also the apostrophe)


def convert_quotes(text):
    """Straight " and ' -> typographic, picking open/close by context.
    Returns (converted_text, count). Idempotent on already-typographic quotes.
    NOTE: the double-quote open/close toggle can desync on UNBALANCED quotes
    —— eyeball the result if a deliverable has stray quotes."""
    count = 0
    result = []
    chars = list(text)
    n = len(chars)
    i = 0
    double_open = True  # next " encountered will be OPEN_DOUBLE

    while i < n:
        c = chars[i]

        if c == '\u0022':  # straight double quote
            result.append(OPEN_DOUBLE if double_open else CLOSE_DOUBLE)
            double_open = not double_open
            count += 1

        elif c == '\u0027':  # straight single quote / apostrophe
            left_word = i > 0 and bool(re.match(r"\w", chars[i - 1]))
            if left_word:
                result.append(CLOSE_SINGLE)            # it's / Test's / closing
            else:
                prev = chars[i - 1] if i > 0 else " "
                result.append(OPEN_SINGLE if (i == 0 or prev in " \t\n\r([{") else CLOSE_SINGLE)
            count += 1

        else:
            result.append(c)

        i += 1

    return "".join(result), count


# =========================================================
# RULE DATA
# =========================================================

# RED —— banned American spellings (root §2.1.1). word(lower) -> British form.
# Curated to UNAMBIGUOUS cases only (these BLOCK); -ize/-isation are Oxford-
# acceptable so deliberately excluded to avoid false reds.
AMERICANISMS = {
    "learned": "learnt", "while": "whilst", "amid": "amidst",
    "toward": "towards", "towards": None,  # placeholder removed below
    "among": "amongst",
    "color": "colour", "colors": "colours", "colored": "coloured",
    "favorite": "favourite", "favorites": "favourites",
    "behavior": "behaviour", "behaviors": "behaviours",
    "neighbor": "neighbour", "neighbors": "neighbours",
    "honor": "honour", "honors": "honours",
    "labor": "labour", "favor": "favour", "flavor": "flavour",
    "center": "centre", "centers": "centres",
    "theater": "theatre", "meter": "metre", "liter": "litre",
    "defense": "defence", "offense": "offence",
    "traveled": "travelled", "traveling": "travelling",
    "canceled": "cancelled", "modeling": "modelling", "labeled": "labelled",
    "fulfill": "fulfil", "catalog": "catalogue", "dialog": "dialogue",
    "gray": "grey", "fiber": "fibre", "practiced": "practised",
}
AMERICANISMS.pop("towards", None)  # keep map clean (no self-map)

# YELLOW —— GenAI / cliche single words (writing.md §Professional Copywriting).
# `amidst` is intentionally absent (root §2.1.1 mandates it as correct British).
GENAI_WORDS = {
    "elevate", "captivate", "captivating", "tapestry", "delve", "leverage",
    "resonate", "resonates", "embark", "unleash", "plethora", "myriad",
    "utilise", "utilize", "paradigm", "landscape", "evolving", "evolve",
    "nuanced", "comprehensive", "supercharge", "dynamic", "elucidate",
    "holistic", "synergy", "pivotal", "robust", "aid", "beacon", "bolster",
    "breeze", "churn", "command", "crack", "crucial", "employ", "enable",
    "encourage", "ensure", "evoke", "enhance", "entices", "essential", "gaze",
    "facilitate", "forge", "fortify", "inundated", "ignite", "imperative",
    "instrument", "instills", "navigate", "irresistible", "master", "material",
    "materially", "paramount", "promptly", "realm", "soar", "revolutionize",
    "revolutionise", "safeguard", "substantive", "persuasive", "sparks",
    "streamline", "uncover", "vast", "journey", "seamless", "seamlessly",
    "adhere", "beyond", "bustling", "enigma", "triangulate", "triangulation",
    "enumerate", "enumeration", "significant", "demonstrate", "perspective",
}

# YELLOW —— GenAI cliche PHRASES (case-insensitive substring).
GENAI_PHRASES = [
    "it is important to note", "master the art of", "in summary",
    "in conclusion", "a testament to", "in the dynamic world of",
    "a tapestry of", "delve into", "embark on a journey", "a treasure trove of",
    "an ongoing voyage", "as we conclude", "captivating narrative",
    "ever-evolving", "game-changer", "golden ticket", "in a sea of",
    "let it shine through", "on the ascent to", "reaching new heights",
    "seize the", "to furnish", "to thrive", "uncharted waters", "well-crafted",
]


# =========================================================
# CHECKS  (each returns list of (line_no, message))
# =========================================================

def _snip(line, limit=90):
    s = line.strip()
    return s if len(s) <= limit else s[:limit] + "…"


def check_red(lines):
    red = []
    for ln, line in enumerate(lines, 1):

        # em dash —— always banned in deliverables (root §2.4)
        if "—" in line:
            red.append((ln, f"em dash `—` —— RESTRUCTURE the sentence (NOT a comma/colon swap): {_snip(line)}"))

        # en dash used as punctuation (range `5–10` is OK per §2.5)
        for m in re.finditer(r"–", line):
            i = m.start()
            left = line[i - 1] if i > 0 else ""
            right = line[i + 1] if i + 1 < len(line) else ""
            if not (left.isdigit() and right.isdigit()):
                red.append((ln, f"en dash `–` as punctuation (only OK for a range like `1–2`) —— RESTRUCTURE the sentence: {_snip(line)}"))
                break

        # banned Americanisms (root §2.1.1)
        low = line.lower()
        for w, brit in AMERICANISMS.items():
            if re.search(rf"\b{re.escape(w)}\b", low):
                red.append((ln, f"Americanism `{w}` -> use `{brit}`: {_snip(line)}"))

        # mid-sentence colon (writing.md: only OK immediately before a list, i.e.
        # nothing but whitespace after it on the line). Excludes `://` and times.
        for m in re.finditer(r":", line):
            i = m.start()
            if line[i:i + 3] == "://":
                continue
            l = line[i - 1] if i > 0 else ""
            r = line[i + 1] if i + 1 < len(line) else ""
            if l.isdigit() and r.isdigit():       # 9:00, 3:1
                continue
            if line[i + 1:].strip() != "":        # text follows -> not a list lead-in
                red.append((ln, f"mid-sentence colon `:` (only allowed before a list/line break): {_snip(line)}"))
                break

    return red


def check_yellow(lines, text):
    yellow = []

    for ln, line in enumerate(lines, 1):

        # bare `+` (root §2.3: only for addition or a name like iCloud+)
        if "+" in line:
            yellow.append((ln, f"bare `+` —— OK only for addition/a name (else use `⁺`): {_snip(line)}"))

        # spaced hyphen that reads as a dash substitute ( word - word ); intra-
        # word compounds and line-start bullets ('- item') are left alone
        if re.search(r"\S +-{1,3} +\S", line):
            yellow.append((ln, f"spaced hyphen reads as a dash —— if so, RESTRUCTURE (ignore if a deliberate compound/range): {_snip(line)}"))

        # GenAI / cliche single words
        low = line.lower()
        hits = [w for w in GENAI_WORDS if re.search(rf"\b{re.escape(w)}\b", low)]
        for w in hits:
            yellow.append((ln, f"GenAI/cliche word `{w}` (OK if a name/trademark or literal sense): {_snip(line)}"))

    # sentence-initial "Where" (writing.md: avoid as clause opener; capital W)
    for m in re.finditer(r"(?:^|[.!?]\s+|\n\s*)(Where)\b", text):
        ln = text.count("\n", 0, m.start(1)) + 1
        yellow.append((ln, f"sentence-initial `Where` —— prefer whilst/since/as, or restructure (OK if a genuine question)"))

    # GenAI cliche phrases
    low_text = text.lower()
    for ph in GENAI_PHRASES:
        idx = low_text.find(ph)
        if idx != -1:
            ln = text.count("\n", 0, idx) + 1
            yellow.append((ln, f"GenAI/cliche phrase `{ph}`"))

    return yellow


# =========================================================
# MAIN
# =========================================================

def lint_file(path: Path):
    try:
        original = path.read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        print(f"❌ {path}: unreadable ({e})")
        return None

    # 1) auto-fix quotes in place
    converted, qn = convert_quotes(original)
    if converted != original:
        path.write_text(converted, encoding="utf-8")

    lines = converted.splitlines()

    red = check_red(lines)
    yellow = check_yellow(lines, converted)

    print(f"\n=== dlint: {path.name} ===")
    print(f"Quotes: {qn} straight quote(s) converted in place." if qn else "Quotes: none to convert.")

    if red:
        print(f"\n🔴 RED FLAGS ({len(red)}) —— CANNOT proceed until 0; fix & rerun:")
        for ln, msg in sorted(red):
            print(f"   L{ln}: {msg}")
        print("   ↳ For any dash flag: REWRITE the sentence; never just swap in a comma/colon.")
    else:
        print("\n🔴 RED FLAGS: 0 ✅")

    if yellow:
        print(f"\n🟡 YELLOW FLAGS ({len(yellow)}) —— may remain, but JUSTIFY EACH concisely in response_:")
        for ln, msg in sorted(yellow):
            print(f"   L{ln}: {msg}")
    else:
        print("\n🟡 YELLOW FLAGS: 0 ✅")

    return len(red)


def main(argv):
    if len(argv) < 2:
        print("usage: python3 cscript/dlint.py <deliverable_path> [<more_paths> ...]")
        return 2

    any_error = False
    any_red = False
    for arg in argv[1:]:
        p = Path(arg)
        if not p.is_file():
            print(f"❌ {arg}: file not found")
            any_error = True
            continue
        r = lint_file(p)
        if r is None:
            any_error = True
        elif r > 0:
            any_red = True

    print("")
    if any_error:
        return 2
    if any_red:
        print("RESULT: 🔴 BLOCKED —— rectify RED flags and rerun until 0.")
        return 1
    print("RESULT: ✅ PASS (RED=0). Justify any YELLOW flags in response_.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
