#!/usr/bin/env python3
"""
dlint.py —— deterministic DELIVERABLE linter (CC-only; lives in /cscpt/).

DESIGNED TO BE RUN, NOT READ —— normal use invokes it via the shell and reads
ONLY its terminal output. This docstring & the comments below are for the NEXT CC
that POLISHES this script, not for routine callers. USAGE, MODES (file / --text /
--quick) and the run-and-loop workflow live in `universal/writing.md`
§ Deliverable Lint —— kept there because THAT file is read at deliverable time
whilst THIS one is not.

WHAT IT DOES
------------
1. AUTO-FIX: straight quotes/apostrophes (U+0022 / U+0027) -> typographic, by
   context. File mode rewrites IN PLACE; --text mode prints the fixed text.
   Idempotent (already-typographic quotes are left alone).

2. FLAG (print only) two tiers (the real rules ARE the check fns below):
     🔴 RED  —— hard breaches, ZERO TOLERANCE (must reach 0): exact Americanisms,
                em dash, mid-sentence colon, a comma as the last char inside a
                closing quote. Fires ONLY on a genuine breach, so a RED never
                needs "conditional acceptance".
     🟡 YELLOW — conditional, may be legitimate: en dash, bare `+`, hyphen used as
                a dash/non-#numbered bullet, `-ize`/`-isation` spellings,
                sentence-initial `Where`, a lone period inside a closing quote,
                GenAI/cliche words & phrases.
   --quick keeps ONLY the register-independent rules (Americanisms, Hart's
   quotation, `-ize`, hyphen/#numbered) so it is safe to run over comms too.

EXIT CODE: 0 = no RED (yellows may remain) | 1 = RED present | 2 = usage/error

POLISH NOTE: the word/spelling lists are seeded from `writing.md` + root
`CLAUDE.md` and are NOT exhaustive —— on each polish, briefly web_search the
latest GenAI/cliche terms (per `writing.md`) and extend GENAI_WORDS / PHRASES.
`cc_writing.md` is retiring and is deliberately NOT referenced.
"""

import re
import sys
from pathlib import Path

# =========================================================
# QUOTE CONVERSION (inherited from gscpt/quote_fix.py)
# =========================================================

OPEN_DOUBLE  = "“"
CLOSE_DOUBLE = "”"
OPEN_SINGLE  = "‘"
CLOSE_SINGLE = "’"   # also the apostrophe
CLOSING_QUOTES = (CLOSE_DOUBLE, CLOSE_SINGLE, '\u0022', '\u0027')


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
    double_open = True  # the next straight " becomes an OPEN_DOUBLE, then toggles

    while i < n:
        c = chars[i]

        if c == '\u0022':  # straight double quote U+0022
            # alternate open/close on each " seen (can desync if quotes unbalanced)
            result.append(OPEN_DOUBLE if double_open else CLOSE_DOUBLE)
            double_open = not double_open
            count += 1

        elif c == '\u0027':  # straight single quote / apostrophe U+0027
            # a quote right after a word char is an apostrophe / closing single
            left_word = i > 0 and bool(re.match(r"\w", chars[i - 1]))
            if left_word:
                result.append(CLOSE_SINGLE)            # it's / Test's / closing single
            else:
                prev = chars[i - 1] if i > 0 else " "
                # opener only after a space or an opening bracket, else a closer
                result.append(OPEN_SINGLE if (i == 0 or prev in " \t\n\r([{") else CLOSE_SINGLE)
            count += 1

        else:
            result.append(c)  # not a straight quote -> copy through unchanged

        i += 1

    return "".join(result), count


# =========================================================
# RULE DATA
# =========================================================

# RED —— banned American spellings (root §2.1.1). EXACT words only (these BLOCK).
# A suggested British form is shown in the flag for convenience —— it is NEVER
# auto-applied (dlint flags, you rewrite). Generalised `-ize`/`-isation` lives in
# YELLOW instead, because exact rules must be unconditional and `-ize` has Oxford-
# acceptable exceptions.
AMERICANISMS = {
    "learned": "learnt", "while": "whilst", "amid": "amidst",
    "toward": "towards", "among": "amongst",
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

# YELLOW —— `-ize`/`-ise` family. Words matching the pattern but in this set are
# legitimate (the `iz` is part of the root), so they are NOT flagged.
IZE_EXCEPTIONS = {
    "prize", "prizes", "prized", "prizing",
    "seize", "seizes", "seized", "seizing",
    "maize", "capsize", "capsizes", "capsized", "capsizing",
    "resize", "resizes", "resized", "resizing",
    "downsize", "downsizes", "downsized", "downsizing",
    "upsize", "oversize", "oversized", "midsize", "assize", "assizes", "baize",
}
IZE_PATTERN = re.compile(r"\b[a-z]{2,}iz(?:e|es|ed|ing|ation|ations)\b")

# YELLOW —— GenAI / cliche single words (writing.md §Professional Copywriting).
# `amidst` intentionally absent (root §2.1.1 mandates it as correct British).
# POLISH: this list ages —— web_search the latest GenAI/cliche terms and extend
# it (and GENAI_PHRASES) on each polish, per writing.md.
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
# CHECKS  (each appends (line_no, message) tuples)
# =========================================================

def _snip(line, limit=90):
    s = line.strip()
    return s if len(s) <= limit else s[:limit] + "…"


def _americanisms(lines, red):
    for ln, line in enumerate(lines, 1):
        low = line.lower()
        for w, brit in AMERICANISMS.items():
            if re.search(rf"\b{re.escape(w)}\b", low):
                red.append((ln, f"Americanism `{w}` -> use `{brit}`: {_snip(line)}"))


def _hart(lines, red, yellow):
    """Hart's logical quotation (root §2.1.4): punctuation belongs inside a quote
    only if original to it. Flag ONLY the char that sits IMMEDIATELY before a
    closing quote:
      - a comma             -> RED    (essentially never original; e.g. `test,"`)
      - a LONE period `.`   -> YELLOW (might end a fully-quoted sentence; `test."`)
    An ellipsis (`..` / `...`) immediately before the quote is EXEMPT —— it is not
    a lone dot (e.g. `test..."` and `test, still..."` are both fine)."""
    for ln, line in enumerate(lines, 1):
        for i, ch in enumerate(line):
            if ch not in CLOSING_QUOTES or i == 0:
                continue
            prev = line[i - 1]
            if prev == ",":
                red.append((ln, f"comma immediately inside closing quote `,{ch}` —— Hart: move it OUTSIDE: {_snip(line)}"))
            elif prev == "." and not (i >= 2 and line[i - 2] == "."):   # exempt `..`/`...`
                yellow.append((ln, f"lone period inside closing quote `.{ch}` —— OK only if it ends the quoted sentence, else move it out: {_snip(line)}"))


def _em_dash(lines, red):
    for ln, line in enumerate(lines, 1):
        if "—" in line:
            red.append((ln, f"em dash `—` —— RESTRUCTURE the sentence (NOT a comma/colon swap): {_snip(line)}"))


def _en_dash(lines, yellow):
    """en dash is OK ONLY for a range (1–2, Jan–Mar). Flagged YELLOW (not RED) so
    a legitimate range never blocks; if it is an em-dash substitute, restructure."""
    for ln, line in enumerate(lines, 1):
        for m in re.finditer(r"–", line):
            i = m.start()
            left = line[i - 1] if i > 0 else ""
            right = line[i + 1] if i + 1 < len(line) else ""
            if left.isdigit() and right.isdigit():   # `1–2` numeric range -> silent OK
                continue
            yellow.append((ln, f"en dash `–` —— keep ONLY if a genuine range (e.g. Jan–Mar); if it substitutes an em dash, RESTRUCTURE: {_snip(line)}"))
            break


def _colon(lines, red):
    for ln, line in enumerate(lines, 1):
        for m in re.finditer(r":", line):
            i = m.start()
            if line[i:i + 3] == "://":
                continue
            l = line[i - 1] if i > 0 else ""
            r = line[i + 1] if i + 1 < len(line) else ""
            if l.isdigit() and r.isdigit():          # 9:00, 3:1
                continue
            if line[i + 1:].strip() != "":           # text follows -> not a list lead-in
                red.append((ln, f"mid-sentence colon `:` (only allowed before a list/line break): {_snip(line)}"))
                break


def _plus(lines, yellow):
    for ln, line in enumerate(lines, 1):
        if "+" in line:
            yellow.append((ln, f"bare `+` —— OK only for addition/a name (else use `⁺`): {_snip(line)}"))


def _hyphen_bullet(lines, yellow):
    """YELLOW a hyphen that is followed by a space then a NON-digit. This catches
    BOTH a dash substitute (`word - word`) AND a non-#numbered bullet (`- text`,
    `  - text`) —— every deliverable/output must be #numbered. EXEMPT:
      - intra-word hyphen with no space after (`re-use`, `cutting-edge`)
      - the token after the hyphen is a number (`- 1.`, `- 1.2.` = valid #numbered)
      - a hyphen glued to a preceding word with no space (`say- text`) —— a typo,
        not a bullet/dash, so left alone to avoid false positives."""
    for ln, line in enumerate(lines, 1):
        for m in re.finditer(r"-", line):
            i = m.start()
            after = line[i + 1:]
            if not after.startswith(" "):                 # intra-word hyphen -> skip
                continue
            before = line[:i]
            if before.strip() != "" and not before.endswith(" "):   # glued to a word -> skip
                continue
            rest = after.lstrip(" ")
            if rest[:1].isdigit():                        # `- 1.` numbered list -> OK
                continue
            yellow.append((ln, f"`-` + space + non-number —— use #numbered (`- 1.1.`) for a list, or restructure if it is a dash: {_snip(line)}"))
            break


def _ize(lines, yellow):
    for ln, line in enumerate(lines, 1):
        for m in IZE_PATTERN.finditer(line.lower()):
            if m.group(0) not in IZE_EXCEPTIONS:
                yellow.append((ln, f"`-ize/-isation` spelling `{m.group(0)}` —— Oxford `-ize` is acceptable, else use `-ise` (judge; `size`/`prize` etc. are fine): {_snip(line)}"))


def _genai_words(lines, yellow):
    for ln, line in enumerate(lines, 1):
        low = line.lower()
        for w in GENAI_WORDS:
            if re.search(rf"\b{re.escape(w)}\b", low):
                yellow.append((ln, f"GenAI/cliche word `{w}` (OK if a name/trademark or literal sense): {_snip(line)}"))


def _where(text, yellow):
    for m in re.finditer(r"(?:^|[.!?]\s+|\n\s*)(Where)\b", text):
        ln = text.count("\n", 0, m.start(1)) + 1
        yellow.append((ln, "sentence-initial `Where` —— prefer whilst/since/as, or restructure (OK if a genuine question)"))


def _genai_phrases(text, yellow):
    low_text = text.lower()
    for ph in GENAI_PHRASES:
        idx = low_text.find(ph)
        if idx != -1:
            ln = text.count("\n", 0, idx) + 1
            yellow.append((ln, f"GenAI/cliche phrase `{ph}`"))


def run_checks(text, quick=False):
    """Return (red, yellow) flag lists for already-quote-converted text."""
    lines = text.splitlines()
    red, yellow = [], []

    # register-independent rules —— wrong in ANY output; the ones --quick keeps
    _americanisms(lines, red)
    _hart(lines, red, yellow)
    _ize(lines, yellow)
    _hyphen_bullet(lines, yellow)     # dash substitute + #numbered-bullet compliance

    if not quick:
        # deliverable-only rules (em dash / colons are fine in internal comms)
        _em_dash(lines, red)
        _colon(lines, red)
        _en_dash(lines, yellow)
        _plus(lines, yellow)
        _genai_words(lines, yellow)
        _where(text, yellow)
        _genai_phrases(text, yellow)

    return red, yellow


# =========================================================
# REPORT / MAIN
# =========================================================

def report(label, red, yellow, qnote):
    print(f"\n=== dlint: {label} ===")
    print(qnote)
    if red:
        print(f"\n🔴 RED FLAGS ({len(red)}) —— CANNOT proceed until 0; fix & rerun:")
        for ln, msg in sorted(red):
            print(f"   L{ln}: {msg}")
        if any("dash" in m for _, m in red):
            print("   ↳ Any dash flag: REWRITE the sentence; never just swap in a comma/colon.")
    else:
        print("\n🔴 RED FLAGS: 0 ✅")
    if yellow:
        print(f"\n🟡 YELLOW FLAGS ({len(yellow)}) —— may remain, but JUSTIFY EACH concisely in response_:")
        for ln, msg in sorted(yellow):
            print(f"   L{ln}: {msg}")
    else:
        print("\n🟡 YELLOW FLAGS: 0 ✅")
    return len(red)


def lint_file(path: Path, quick=False):
    try:
        original = path.read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        print(f"❌ {path}: unreadable ({e})")
        return None
    converted, qn = convert_quotes(original)
    if converted != original:
        path.write_text(converted, encoding="utf-8")
    qnote = f"Quotes: {qn} straight quote(s) converted in place." if qn else "Quotes: none to convert."
    red, yellow = run_checks(converted, quick)
    return report(path.name, red, yellow, qnote)


def lint_text(text, quick=False):
    converted, qn = convert_quotes(text)
    if qn:
        print("\n--- QUOTE-FIXED TEXT (copy this back) ---")
        print(converted)
        print("--- end ---")
        qnote = f"Quotes: {qn} straight quote(s) converted (see fixed text above)."
    else:
        qnote = "Quotes: none to convert."
    red, yellow = run_checks(converted, quick)
    return report("--text", red, yellow, qnote)


def main(argv):
    args = argv[1:]
    quick = False
    if args and args[0] == "--quick":
        quick = True
        args = args[1:]

    if not args:
        print("usage: python3 cscpt/dlint.py [--quick] <path> [<path> ...]")
        print("       python3 cscpt/dlint.py [--quick] --text \"your text\"")
        return 2

    if args[0] == "--text":
        text = args[1] if len(args) > 1 else ""
        r = lint_text(text, quick)
        print("")
        print("RESULT: 🔴 BLOCKED —— rectify RED flags and rerun." if r else
              "RESULT: ✅ PASS (RED=0). Justify any YELLOW flags in response_.")
        return 1 if r else 0

    any_error = any_red = False
    for arg in args:
        p = Path(arg)
        if not p.is_file():
            print(f"❌ {arg}: file not found")
            any_error = True
            continue
        r = lint_file(p, quick)
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
