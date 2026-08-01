#!/usr/bin/env python3
"""
dlint.py —— deterministic DELIVERABLE linter (CC-only; lives in /cscpt/).

=== NON-CCSIM —— start of all you need to RUN it ===
WHAT: the deterministic prose linter for `universal/writing.md`.

    python3 cscpt/dlint.py [--quick] <path>...
    python3 cscpt/dlint.py [--quick] --text "…"

* `--quick` must come FIRST.
* FULL mode REWRITES THE FILE IN PLACE (quote conversion only) and applies the
  deliverable-only rules; `--text` prints instead. `--quick` does neither, so it
  is safe over comms.
* 🔴 RED = hard breach, ZERO TOLERANCE, loop until 0. 🟡 YELLOW = conditional;
  judge each, justify any you accept. Flags print, never auto-apply.
* EXIT: 0 = no RED | 1 = RED | 2 = usage error.
* WORKFLOW (run-and-loop): `universal/writing.md` § Deliverable Lint.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
* WHAT EACH TIER HOLDS (moved out of NON-CCSIM —— a caller reads the terminal
  output, which names the rule that fired, so the enumeration only serves an
  editor). RED: exact Americanisms, `vs.` with period, em dash, mid-sentence
  colon, a comma OR a period as the last char inside a closing quote, `hi` as a
  greeting. YELLOW: en dash, bare `+`, hyphen used as a dash/non-#numbered
  bullet, `-ize`/`-isation`, sentence-initial `Where`, GenAI/cliche words and
  phrases, weak words (want/something/big), plus the period-in-quote class once
  one file carries more than `HART_PERIOD_RED_MAX` of them.
* `."` HAS NO EXEMPTION —— see `_hart`. It is RED even when the full stop is
  original to the quoted sentence, because the rule exists for the reader's
  comfort rather than for grammatical truth. The ONLY relief is the per-file
  count threshold, and that demotes rather than silences.
* `--quick` keeps ONLY the register-independent rules —— Americanisms, Hart's
  quotation, `-ize`, hyphen/#numbered, `hi` greeting —— and never rewrites,
  because comms and code may hold intentional straight quotes.
* AUTO-FIX (full mode only) converts straight quotes/apostrophes to typographic,
  chosen by context, and is idempotent —— already-typographic quotes are left
  alone.
* The run-and-loop workflow lives in `universal/writing.md`, not here: that file
  is open at deliverable time whilst this one is not.
* The real rules ARE the check fns below; this header is a map, not a spec ——
  keep it so, rather than duplicating the lists into prose that drifts.
* RED fires ONLY on a genuine breach, so it never needs "conditional
  acceptance". Anything register-dependent belongs in YELLOW: generalised
  `-ize`/`-isation` sits there because exact rules must be unconditional and
  `-ize` has Oxford-acceptable exceptions.
* Suggested British forms are never auto-applied —— the rewrite stays the
  author's, so a flag is judged rather than obeyed.
* The double-quote open/close toggle can DESYNC on unbalanced quotes —— eyeball
  the result if a deliverable has stray quotes (see `convert_quotes`).
* POLISH NOTE: the word/spelling lists are seeded from `writing.md` + root
  `CLAUDE.md` and are NOT exhaustive —— on each polish, briefly web_search the
  latest GenAI/cliche terms (per `writing.md`) and extend GENAI_WORDS / PHRASES.
* RECEIPTS: every FULL-mode FILE lint appends one line to
  `cscpt/.dlint_receipts.jsonl` —— realpath, SHA-256 of the text as it stands
  on disk AFTER the quote auto-fix, and the RED count. `cscpt/dlint_quick.py` reads
  it to decide whether a deliverable has actually been linted, so a deliverable
  drafted on Monday and delivered on Friday stays covered, and an edit AFTER a
  clean lint correctly lapses the receipt because the hash moves. `--quick` and
  `--text` write NOTHING, which is what makes a receipt's mere existence proof
  that FULL mode ran. This file is the SOLE writer of that ledger (the hook
  only reads it), so no lock is needed; appends are line-atomic and pruning happens
  here alone. It is best-effort throughout —— it can never raise, never change
  an exit code, and never alter printed output.
"""

import os
import re
import sys
import json
import time
import hashlib
from pathlib import Path

# Receipt ledger —— anchored on THIS file's own location, never on cwd, so it
# resolves identically from `dlint_quick.py` (which computes the same expression
# from its own `__file__` in the same folder) and survives a repo move.
RECEIPTS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        ".dlint_receipts.jsonl")
RECEIPT_MAX_LINES = 4000        # past this, the oldest half is dropped

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

# RED —— "hi" as a greeting is impolite in the user's culture (writing.md §
# General); "Hello" or any other salutation is fine. Register-independent (also
# checked by --quick) since this is a firm ban, not a register-dependent style
# choice. Simple word-boundary match, same precision tradeoff as AMERICANISMS —
# judgement still governs genuine edge cases (e.g. "hi-vis", "hi-fi").
GREETING_HI = re.compile(r"\bhi\b", re.IGNORECASE)

# YELLOW —— "weak"/unsophisticated words (writing.md § General): actively avoid,
# NOT banned —— CC may still insist through a mis-flag when context calls for it
# (e.g. Casual Writing, or a deliberate human touch). Deliverable-only (FULL mode
# only, like GENAI_WORDS) since ordinary language between user and CC in
# response_/comms should not be nagged. Kept short and hard-coded on purpose —
# writing.md states the PRINCIPLE (prefer precise/stronger words, e.g. "believe"
# over "feel"/"want"), this list is just the 3 concrete always-avoid words.
WEAK_WORDS = {
    "want": r"\bwants?\b|\bwanted\b|\bwanting\b",
    "something": r"\bsomething\b",
    "big": r"\bbig(?:ger|gest)?\b",
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


def _mask_code(text):
    """Mask BOTH fenced code blocks AND inline `code` spans (replace with spaces;
    length & newline count preserved) so prose checks NEVER fire inside code.
    A deliverable EMBEDDED in a fenced block is NOT meant to be caught here —— it
    is linted separately by extracting it and running FULL `--text` on it (per
    writing.md § Deliverable Lint). So masking code lets `--quick` over a whole
    `response_` check the prose only, without false-flagging real code snippets."""
    out = []
    in_fence = False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(" " * len(line))          # blank the fence line itself too
            continue
        if in_fence:
            out.append(" " * len(line))
            continue
        out.append(re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), line))
    return "\n".join(out)


# Each check scans the MASKED lines/text for matches, but shows the ORIGINAL
# line in its message (via orig[ln-1]) so flags stay readable.

def _americanisms(lines, orig, red):
    for ln, line in enumerate(lines, 1):
        low = line.lower()
        for w, brit in AMERICANISMS.items():
            if re.search(rf"\b{re.escape(w)}\b", low):
                red.append((ln, f"Americanism `{w}` -> use `{brit}`: {_snip(orig[ln - 1])}"))


def _vs(lines, orig, red):
    """`vs.` (with trailing period) is banned —— only the bare `vs` is accepted.
    Matches case-insensitively on a word-boundaried `vs` immediately followed by
    a period (e.g. `A vs. B`); the bare `vs` never fires."""
    for ln, line in enumerate(lines, 1):
        if re.search(r"\bvs\.", line, re.IGNORECASE):
            red.append((ln, f"`vs.` with period —— use bare `vs`: {_snip(orig[ln - 1])}"))


# Above this many lone-period-inside-quote hits in ONE file, the whole class
# demotes from RED to YELLOW for that file. RATIONALE, baked in so nobody
# "restores consistency" later: the owner wants `."` gone unconditionally for
# READING COMFORT, not because it is always wrong, and at a handful of hits the
# fix is a couple of clicks. Past this count it stops being a couple of clicks,
# and a hard block on a long quotation-heavy document would buy tidiness at the
# price of wedging real work —— so the flag stays visible and the judgement
# returns to the author.
HART_PERIOD_RED_MAX = 5


def _hart(lines, orig, red, yellow):
    """Hart's logical quotation (root §2.1.4): punctuation belongs inside a quote
    only if original to it. Flag ONLY the char IMMEDIATELY before a closing quote:
      - a comma             -> RED, always (`test,"`)
      - a LONE period `.`   -> RED, always, up to HART_PERIOD_RED_MAX hits in one
                               file; past that the whole class demotes to YELLOW
                               for that file (see the constant for why)
    NO "it might be original to the quote" exemption exists for the period. The
    owner's rule is `".` no matter what, INCLUDING when the full stop genuinely
    belongs to the quoted sentence —— it is a reading-comfort rule, and moving
    the stop outside costs two clicks. Anything reading this as a mis-fire is
    mistaken; do not reinstate a conditional.

    An ellipsis (`..`/`...`) immediately before the quote is NOT a full stop and
    stays exempt, e.g. `test..."` and `test, still..."` are both fine.

    The two classes are counted SEPARATELY and the threshold applies to the
    PERIOD class alone: the comma rule was never relaxed, so a comma-heavy file
    must not be able to soften the period rule (or the reverse), and the
    owner's arithmetic —— "more than 5 means more than 10 clicks" —— is about
    `."` and nothing else."""
    periods = []
    for ln, line in enumerate(lines, 1):
        for i, ch in enumerate(line):
            if ch not in CLOSING_QUOTES or i == 0:
                continue
            prev = line[i - 1]
            if prev == ",":
                red.append((ln, f"comma immediately inside closing quote `,{ch}` —— Hart: move it OUTSIDE: {_snip(orig[ln - 1])}"))
            elif prev == "." and not (i >= 2 and line[i - 2] == "."):   # exempt `..`/`...`
                periods.append((ln, ch))

    if not periods:
        return
    if len(periods) <= HART_PERIOD_RED_MAX:
        for ln, ch in periods:
            red.append((ln, f"period inside closing quote `.{ch}` —— ALWAYS move it OUTSIDE, even if the stop is original to the quote: {_snip(orig[ln - 1])}"))
    else:
        for ln, ch in periods:
            yellow.append((ln, f"period inside closing quote `.{ch}` —— {len(periods)} in this file (over {HART_PERIOD_RED_MAX}), so demoted from RED; does the stop truly belong INSIDE the quote? Move it out unless quoting verbatim: {_snip(orig[ln - 1])}"))


def _em_dash(lines, orig, red):
    for ln, line in enumerate(lines, 1):
        if "\u2014" in line:
            red.append((ln, f"em dash `\u2014` —— RESTRUCTURE the sentence (NOT a comma/colon swap): {_snip(orig[ln - 1])}"))


def _en_dash(lines, orig, yellow):
    """en dash is OK ONLY for a range (1\u20132, Jan\u2013Mar). YELLOW (not RED) so a
    legitimate range never blocks; restructure if it substitutes an em dash."""
    for ln, line in enumerate(lines, 1):
        for m in re.finditer(r"\u2013", line):
            i = m.start()
            left = line[i - 1] if i > 0 else ""
            right = line[i + 1] if i + 1 < len(line) else ""
            if left.isdigit() and right.isdigit():        # `1\u20132` numeric range -> silent OK
                continue
            yellow.append((ln, f"en dash `\u2013` —— keep ONLY if a genuine range (e.g. Jan\u2013Mar); if it substitutes an em dash, RESTRUCTURE: {_snip(orig[ln - 1])}"))
            break


def _colon(lines, orig, red):
    for ln, line in enumerate(lines, 1):
        for m in re.finditer(r":", line):
            i = m.start()
            if line[i:i + 3] == "://":                    # URL -> skip
                continue
            l = line[i - 1] if i > 0 else ""
            r = line[i + 1] if i + 1 < len(line) else ""
            if l.isdigit() and r.isdigit():               # 9:00, 3:1 -> skip
                continue
            if line[i + 1:].strip() != "":                # text follows -> not a list lead-in
                red.append((ln, f"mid-sentence colon `:` (only allowed before a list/line break): {_snip(orig[ln - 1])}"))
                break


def _plus(lines, orig, yellow):
    for ln, line in enumerate(lines, 1):
        if "+" in line:
            yellow.append((ln, f"bare `+` —— OK only for addition/a name (else use `\u207a`): {_snip(orig[ln - 1])}"))


def _hyphen_bullet(lines, orig, yellow):
    """YELLOW a hyphen followed by a space then a NON-digit. Catches BOTH a dash
    substitute (`word - word`) AND a non-#numbered bullet (`- text`, `  - text`)
    —— every deliverable/output must be #numbered. EXEMPT:
      - intra-word hyphen, no space after (`re-use`, `cutting-edge`)
      - a number follows (`- 1.`, `- 1.2.` = valid #numbered sub-item)
      - hyphen glued to a preceding word (`say- text`) —— a typo, not a bullet/dash."""
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
            yellow.append((ln, f"`-` + space + non-number —— use #numbered (`- 1.1.`) for a list, or restructure if it is a dash: {_snip(orig[ln - 1])}"))
            break


def _ize(lines, orig, yellow):
    for ln, line in enumerate(lines, 1):
        for m in IZE_PATTERN.finditer(line.lower()):
            if m.group(0) not in IZE_EXCEPTIONS:
                yellow.append((ln, f"`-ize/-isation` spelling `{m.group(0)}` —— Oxford `-ize` is acceptable, else use `-ise` (judge; `size`/`prize` etc. are fine): {_snip(orig[ln - 1])}"))


def _greeting_hi(lines, orig, red):
    for ln, line in enumerate(lines, 1):
        if GREETING_HI.search(line):
            red.append((ln, f"`hi` as a greeting is banned —— use `Hello` or another salutation: {_snip(orig[ln - 1])}"))


def _weak_words(lines, orig, yellow):
    for ln, line in enumerate(lines, 1):
        low = line.lower()
        for w, pat in WEAK_WORDS.items():
            if re.search(pat, low):
                yellow.append((ln, f"weak/unsophisticated word `{w}` —— avoid where a stronger, more precise word fits (e.g. `believe` > `feel`/`want`): {_snip(orig[ln - 1])}"))


def _genai_words(lines, orig, yellow):
    for ln, line in enumerate(lines, 1):
        low = line.lower()
        for w in GENAI_WORDS:
            if re.search(rf"\b{re.escape(w)}\b", low):
                yellow.append((ln, f"GenAI/cliche word `{w}` (OK if a name/trademark or literal sense): {_snip(orig[ln - 1])}"))


def _where(masked_text, yellow):
    for m in re.finditer(r"(?:^|[.!?]\s+|\n\s*)(Where)\b", masked_text):
        ln = masked_text.count("\n", 0, m.start(1)) + 1
        yellow.append((ln, "sentence-initial `Where` —— prefer whilst/since/as, or restructure (OK if a genuine question)"))


def _genai_phrases(masked_text, yellow):
    low = masked_text.lower()
    for ph in GENAI_PHRASES:
        idx = low.find(ph)
        if idx != -1:
            ln = masked_text.count("\n", 0, idx) + 1
            yellow.append((ln, f"GenAI/cliche phrase `{ph}`"))


def run_checks(text, quick=False):
    """Return (red, yellow). Fenced code blocks AND inline `code` spans are masked
    first so prose rules never fire inside code (embedded deliverables are linted
    separately via FULL `--text`); detection runs on the masked text, snippets are
    shown from the original."""
    orig = text.splitlines()
    masked_text = _mask_code(text)
    lines = masked_text.splitlines()
    red, yellow = [], []

    # register-independent rules —— wrong in ANY output; the ones --quick keeps
    _americanisms(lines, orig, red)
    _vs(lines, orig, red)
    _hart(lines, orig, red, yellow)
    _ize(lines, orig, yellow)
    _hyphen_bullet(lines, orig, yellow)       # dash substitute + #numbered compliance
    _greeting_hi(lines, orig, red)            # `hi` banned everywhere, incl. --quick

    if not quick:
        # deliverable-only rules (em dash / colons are fine in internal comms)
        _em_dash(lines, orig, red)
        _colon(lines, orig, red)
        _en_dash(lines, orig, yellow)
        _plus(lines, orig, yellow)
        _genai_words(lines, orig, yellow)
        _weak_words(lines, orig, yellow)
        _where(masked_text, yellow)
        _genai_phrases(masked_text, yellow)

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


def _write_receipt(path, text, red_count):
    """Record that FULL mode linted EXACTLY this content, and with what
    result. Read by `cscpt/dlint_quick.py`, whose gate enforces root CLAUDE.md
    §3.7.3 on deliverables no other check covers (rationale: RECEIPTS in the
    CCSIM header).

    Best-effort by contract: every failure is swallowed, because a linter that
    dies over its own bookkeeping is worse than one with a gap in it. The RED
    count is stored rather than a pass/fail flag so a lint that ENDED with RED
    flags can never be mistaken for a clean one."""
    try:
        line = json.dumps({
            "p": os.path.realpath(str(path)),
            "h": hashlib.sha256(text.encode("utf-8", "replace")).hexdigest(),
            "r": int(red_count),
            "t": int(time.time()),
        }, ensure_ascii=True)
        with open(RECEIPTS, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        _prune_receipts()
    except Exception:                                           # noqa: BLE001
        pass


def _prune_receipts():
    """Keep the ledger bounded. Safe without a lock because this module is its
    ONLY writer; the rewrite is atomic via `os.replace`, so a concurrent
    READER (the hook) sees either the old file or the new one, never a partial."""
    try:
        with open(RECEIPTS, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
        if len(lines) <= RECEIPT_MAX_LINES:
            return
        tmp = RECEIPTS + ".tmp%d" % os.getpid()
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.writelines(lines[-(RECEIPT_MAX_LINES // 2):])
        os.replace(tmp, RECEIPTS)
    except Exception:                                           # noqa: BLE001
        pass


def lint_file(path: Path, quick=False):
    try:
        original = path.read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        print(f"❌ {path}: unreadable ({e})")
        return None
    if quick:
        # --quick NEVER rewrites: comms/code may contain intentional straight
        # quotes (variable names, JSON), so leave the file byte-for-byte intact.
        text = original
        qnote = "Quotes: untouched (--quick does not rewrite; safe on comms/code)."
    else:
        text, qn = convert_quotes(original)
        if text != original:
            path.write_text(text, encoding="utf-8")
        qnote = f"Quotes: {qn} straight quote(s) converted in place." if qn else "Quotes: none to convert."
    red, yellow = run_checks(text, quick)
    n_red = report(path.name, red, yellow, qnote)
    if not quick:
        # FULL mode only —— a receipt's existence is the gate's proof that FULL
        # mode ran, so --quick must never leave one. `text` is what is on disk
        # (the auto-fix already wrote it if it differed), so the hash matches
        # what the gate will compute.
        _write_receipt(path, text, n_red)
    return n_red


def lint_text(text, quick=False):
    if quick:
        qnote = "Quotes: untouched (--quick)."
        checked = text
    else:
        checked, qn = convert_quotes(text)
        if qn:
            print("\n--- QUOTE-FIXED TEXT (copy this back) ---")
            print(checked)
            print("--- end ---")
            qnote = f"Quotes: {qn} straight quote(s) converted (see fixed text above)."
        else:
            qnote = "Quotes: none to convert."
    red, yellow = run_checks(checked, quick)
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
