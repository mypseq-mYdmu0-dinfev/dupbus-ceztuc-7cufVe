#!/usr/bin/env python3
"""
dlint.py —— deterministic DELIVERABLE linter (CC-only; lives in /cscpt/).

=== NON-CCSIM —— start of all you need to RUN it ===
WHAT: the deterministic prose linter for `universal/writing.md`.

    python3 cscpt/dlint.py [--quick] <path>...
    python3 cscpt/dlint.py [--quick] --text "…"

* `--quick` must come FIRST (before any path or `--text`).
* FULL REWRITES THE FILE IN PLACE (quotes only) + deliverable rules; `--text`
  prints instead. `--quick` does neither, so it is safe over comms.
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
  phrases, weak words (want/something/big), plus either in-quote punctuation
  class once one file carries more than `HART_RED_MAX` of THAT class.
* NEITHER `."` NOR `,"` HAS AN EXEMPTION —— see `_hart`. Both are RED even when
  the mark is original to the quoted sentence, because the rule exists for the
  reader's comfort rather than for grammatical truth. The ONLY relief is the
  per-file count threshold, it demotes rather than silences, and the two
  classes count INDEPENDENTLY so neither can soften the other.
* `--quick` keeps ONLY the register-independent rules —— Americanisms, Hart's
  quotation, `-ize`, hyphen/#numbered, `hi` greeting —— and never rewrites,
  because comms and code may hold intentional straight quotes. It ALSO adds one
  quick-only advisory, the `read`/`#r` tense check, which FULL must never carry
  (house shorthand has no place in a deliverable). That advisory has NO
  suppression switch and no per-session memory —— a `--rt-quiet` flag existed
  and was removed, because a reminder withheld on the grounds that CC was told
  once is a detected instance turned into a hidden one, and the owner's
  standing ruling is that a false positive costs ~10 tokens whilst a false
  negative "could be highly misleading". Do not reintroduce it.
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
#
# AN EXPLICIT WORD LIST, NEVER AN ENDING PATTERN. The tempting repair after a
# miss is a rule on the ENDING (`-or` -> suggest `-our`). It cannot work, because
# the same ending is FOUR different things and only a lexicon separates them:
#   1. the American form of a British `-our` word —— rigor, vigor, valor, candor;
#   2. a Latin AGENT suffix identical in both —— separator, elevator, translator;
#   3. a Latin comparative identical in both —— junior, senior, superior;
#   4. words Johnson once spelled `-our` and nobody has since —— error, horror,
#      mirror, terror, tremor, pallor, doctor, senator, metaphor, anchor, major,
#      minor, donor, motor.
# An `-or` rule fires on every word in 2/3/4, i.e. on ordinary correct English,
# and a RED that cries wolf is switched off in a day. It would ALSO fire on the
# British derivatives that legitimately DROP the u —— rigorous, vigorous,
# humorous, laborious, honorary, glamorous —— though word-boundary matching
# already spares those here (`\brigor\b` cannot match `rigorous`).
#
# SOURCE. The `-our`/`-or`, `-re`/`-er` and doubled-`l` sets below were taken
# from Wikipedia's "American and British English spelling differences" (which
# cites Webster's Third p.24a, the OED, and Peters, "The Cambridge Guide to
# English Usage"), then each individual word was checked against its own
# Wiktionary entry for an explicit American/US-spelling label. Anything the
# check did not confirm was left OUT rather than guessed —— see the KNOWN GAPS
# note under AMERICANISM_OK_HERE.
AMERICANISMS = {
    "learned": "learnt", "while": "whilst", "amid": "amidst",
    "toward": "towards", "among": "amongst",
    # -our / -or
    "ardor": "ardour",
    "armor": "armour", "armors": "armours", "armored": "armoured",
    "armory": "armoury", "armories": "armouries",
    "behavior": "behaviour", "behaviors": "behaviours",
    "behavioral": "behavioural", "behaviorally": "behaviourally",
    "candor": "candour",
    "clamor": "clamour", "clamors": "clamours", "clamored": "clamoured",
    "clamoring": "clamouring",
    "color": "colour", "colors": "colours", "colored": "coloured",
    "coloring": "colouring", "colorful": "colourful",
    "colorless": "colourless",
    "demeanor": "demeanour",
    "dishonor": "dishonour", "dishonored": "dishonoured",
    "enamor": "enamour", "enamored": "enamoured",
    "endeavor": "endeavour", "endeavors": "endeavours",
    "endeavored": "endeavoured", "endeavoring": "endeavouring",
    "favor": "favour", "favors": "favours", "favored": "favoured",
    "favoring": "favouring", "favorable": "favourable",
    "favorably": "favourably", "unfavorable": "unfavourable",
    "favorite": "favourite", "favorites": "favourites",
    "fervor": "fervour",
    "flavor": "flavour", "flavors": "flavours", "flavored": "flavoured",
    "flavoring": "flavouring", "flavorful": "flavourful",
    "glamor": "glamour",
    "harbor": "harbour", "harbors": "harbours", "harbored": "harboured",
    "harboring": "harbouring",
    "honor": "honour", "honors": "honours", "honored": "honoured",
    "honoring": "honouring", "honorable": "honourable",
    "honorably": "honourably",
    "humor": "humour", "humors": "humours", "humored": "humoured",
    "humorless": "humourless",
    "labor": "labour", "labors": "labours", "labored": "laboured",
    "laboring": "labouring", "laborer": "labourer", "laborers": "labourers",
    "misdemeanor": "misdemeanour", "misdemeanors": "misdemeanours",
    "neighbor": "neighbour", "neighbors": "neighbours",
    "neighborhood": "neighbourhood", "neighborhoods": "neighbourhoods",
    "odor": "odour", "odors": "odours",
    "rancor": "rancour",
    "rigor": "rigour", "rigors": "rigours",
    "rumor": "rumour", "rumors": "rumours", "rumored": "rumoured",
    "savior": "saviour", "saviors": "saviours",
    "savor": "savour", "savors": "savours", "savored": "savoured",
    "savoring": "savouring", "savory": "savoury",
    "splendor": "splendour",
    "succor": "succour",
    "tumor": "tumour", "tumors": "tumours",
    "valor": "valour",
    "vapor": "vapour", "vapors": "vapours",
    "vigor": "vigour",
    # -re / -er
    "center": "centre", "centers": "centres", "centered": "centred",
    "centering": "centring",
    "theater": "theatre", "theaters": "theatres",
    "meter": "metre", "meters": "metres",
    "liter": "litre", "liters": "litres",
    "fiber": "fibre", "fibers": "fibres",
    "luster": "lustre", "maneuver": "manoeuvre", "maneuvers": "manoeuvres",
    "maneuvered": "manoeuvred", "maneuvering": "manoeuvring",
    "ocher": "ochre", "saber": "sabre", "sabers": "sabres",
    "scepter": "sceptre", "somber": "sombre",
    "specter": "spectre", "specters": "spectres",
    # -ce / -se
    "defense": "defence", "defenses": "defences",
    "offense": "offence", "offenses": "offences",
    "pretense": "pretence", "pretenses": "pretences",
    "practiced": "practised", "practicing": "practising",
    # -yse / -yze (NOT reachable by the -ize rule: the stem is `analys-`, so
    # Oxford `-ize` never licensed `analyze`)
    "analyze": "analyse", "analyzes": "analyses", "analyzed": "analysed",
    "analyzing": "analysing",
    # doubled `l`: British doubles a final unstressed -l before a suffix
    "canceled": "cancelled", "canceling": "cancelling",
    "counselor": "counsellor", "counselors": "counsellors",
    "counseled": "counselled", "counseling": "counselling",
    "cruelest": "cruellest",
    "dialed": "dialled", "dialing": "dialling",
    "equaling": "equalling", "initialed": "initialled",
    "fueled": "fuelled", "fueling": "fuelling",
    "labeled": "labelled", "labeling": "labelling",
    "leveled": "levelled", "leveling": "levelling",
    "libelous": "libellous",
    "marveled": "marvelled", "marveling": "marvelling",
    "marvelous": "marvellous", "marvelously": "marvellously",
    "modeled": "modelled", "modeling": "modelling",
    "quarreled": "quarrelled", "quarreling": "quarrelling",
    "rivaled": "rivalled",
    "signaled": "signalled", "signaling": "signalling",
    "totaled": "totalled", "totaling": "totalling",
    "traveled": "travelled", "traveling": "travelling",
    "traveler": "traveller", "travelers": "travellers",
    "woolen": "woollen",
    # single `l` where American doubles it. `distill` is deliberately ABSENT:
    # `universal/shrink.md` documents `#distil`/`#distill` as interchangeable
    # TRIGGER names, so a hard block would fire on a house command rather than
    # on a spelling error.
    "appall": "appal", "enroll": "enrol",
    "enrollment": "enrolment", "enthrall": "enthral",
    "fulfill": "fulfil", "fulfillment": "fulfilment",
    "installment": "instalment", "installments": "instalments",
    "instill": "instil", "skillful": "skilful", "skillfully": "skilfully",
    "willful": "wilful", "willfully": "wilfully",
    # miscellaneous, each Wiktionary-confirmed as the American form
    "aluminum": "aluminium", "archeology": "archaeology",
    "catalog": "catalogue", "dialog": "dialogue",
    "esthetic": "aesthetic", "esthetics": "aesthetics",
    "gray": "grey", "jewelry": "jewellery",
    "mold": "mould", "molds": "moulds", "molded": "moulded",
    "molding": "moulding",
    "mustache": "moustache", "pajamas": "pyjamas",
    "plow": "plough", "plowed": "ploughed",
    "skeptic": "sceptic", "skeptics": "sceptics",
    "skeptical": "sceptical", "skepticism": "scepticism",
    "smolder": "smoulder",
}

# THE SHORT LIST OF PLACES A LISTED WORD IS ACTUALLY CORRECT. Each entry is a
# regex over the LOWERCASED line whose `hit` group must cover the flagged word;
# a match at that exact offset suppresses that one hit and nothing else, so the
# same word elsewhere on the same line still fires.
#
# Kept deliberately tiny. Every entry is named by the source above as genuinely
# correct British usage, NOT as a judgement call:
#   * `rigor mortis` is Latin and carries no `u` in any variety.
#   * `Labor` is the registered spelling of the Australian Labor Party (adopted
#     1912) —— a Sydney-based author writes it constantly and a RED there would
#     be simply wrong.
#   * proper-noun harbours keep their native spelling (Pearl Harbor, and the
#     South Australian Victor/Franklin/Outer Harbor).
#   * British distinguishes a `meter` (a device that measures) from a `metre`
#     (the unit), so a parking meter is correct as spelled.
AMERICANISM_OK_HERE = {
    "rigor": [re.compile(r"\b(?P<hit>rigor)\s+mortis\b")],
    "labor": [re.compile(r"\b(?P<hit>labor)\s+(?:party|mp|mps|government|"
                         r"caucus|leader|senator|premier|voter|voters)\b"),
              re.compile(r"\baustralian\s+(?P<hit>labor)\b")],
    "harbor": [re.compile(r"\b(?:pearl|victor|franklin|outer|coffs|darling|"
                          r"bar)\s+(?P<hit>harbor)\b")],
    "meter": [re.compile(r"\b(?:parking|gas|water|electric|electricity|smart|"
                         r"power|utility|taxi|postage|light)\s+(?P<hit>meter)\b"),
              re.compile(r"\b(?P<hit>meter)\s+(?:reading|readings|box|maid|"
                         r"maids)\b")],
    "meters": [re.compile(r"\b(?:parking|gas|water|electric|electricity|smart|"
                          r"power|utility|taxi|postage|light)\s+"
                          r"(?P<hit>meters)\b")],
}

_AMERICANISM_KEYS = frozenset(AMERICANISMS)

# KNOWN GAPS, so nobody reads this list as exhaustive:
#   * `paralyze`/`catalyze` are left OUT —— unambiguously `-yse` in British, but
#     the per-word check returned no explicit American label, and the rule here
#     is confirmed-or-omitted rather than confirmed-or-guessed.
#   * `parlor`, `caliber` and `arbor` are out for the same reason; `pallor` is
#     out because it is `-or` in British too.
#   * The list flags a SPELLING, so a proper noun spelled the American way
#     (`Honor Oak`, a US place or company name) still fires. That is the same
#     precision trade-off `hi` already carries; judgement governs the edge case.
#   * `savory` is listed for the adjective; the HERB savory is spelled thus
#     everywhere, so that one genuine sense mis-fires.

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

# TOKENISE-THEN-LOOK-UP, not one regex per listed word per line. The naive loop
# is O(lines x words), and growing the list from 36 words to ~200 took a
# `--quick` pass over the repo's largest `.md` (322 KB) from `~`350 ms to
# `~`1,555 ms —— past the 1 s per-event ceiling `cp/ccsim/hook_guide.md` §12.4
# sets for PostToolUse, on a hook that fires on every write. One `\w+` findall
# per line plus a set intersection is the same verdict at a fraction of the
# cost, and leaves headroom for the list to keep growing.
#
# `\w+` over the LOWERCASED line reproduces `\b<word>\b` exactly: `color's`
# yields `color`, matching `\bcolor\b`, whilst `color2` and `colorful` yield a
# single token that does not, matching `\b` refusing those too.
_WORD_RE = re.compile(r"\w+", re.UNICODE)


def _americanisms(lines, orig, red):
    """Flag each listed American spelling, once per (line, word).

    Word-boundary semantics throughout, so `rigorous` can never be caught by
    `rigor` nor `thermometer` by `meter`. A hit is dropped only when an
    AMERICANISM_OK_HERE pattern covers that exact offset —— the handful of
    contexts where the listed spelling is the correct one. The offset work runs
    ONLY for the few words that carry an exemption."""
    for ln, line in enumerate(lines, 1):
        low = line.lower()
        for w in sorted(set(_WORD_RE.findall(low)) & _AMERICANISM_KEYS):
            pats = AMERICANISM_OK_HERE.get(w)
            if pats:
                hits = [m.start()
                        for m in re.finditer(rf"\b{re.escape(w)}\b", low)]
                ok = set()
                for pat in pats:
                    for m in pat.finditer(low):
                        ok.add(m.start("hit"))
                if not [i for i in hits if i not in ok]:
                    continue
            red.append((ln, f"Americanism `{w}` -> use `{AMERICANISMS[w]}`: "
                            f"{_snip(orig[ln - 1])}"))


def _vs(lines, orig, red):
    """`vs.` (with trailing period) is banned —— only the bare `vs` is accepted.
    Matches case-insensitively on a word-boundaried `vs` immediately followed by
    a period (e.g. `A vs. B`); the bare `vs` never fires."""
    for ln, line in enumerate(lines, 1):
        if re.search(r"\bvs\.", line, re.IGNORECASE):
            red.append((ln, f"`vs.` with period —— use bare `vs`: {_snip(orig[ln - 1])}"))


# Above this many hits of ONE punctuation class inside a closing quote in ONE
# file, that class demotes from RED to YELLOW for that file. RATIONALE, baked in
# so nobody "restores consistency" later: the owner wants `."` and `,"` gone
# unconditionally for READING COMFORT, not because either is always wrong, and
# at a handful of hits the fix is a couple of clicks. Past this count it stops
# being a couple of clicks, and a hard block on a long quotation-heavy document
# would buy tidiness at the price of wedging real work —— so the flag stays
# visible and the judgement returns to the author.
HART_RED_MAX = 5


def _hart(lines, orig, red, yellow):
    """Hart's logical quotation (root §2.1.4): punctuation belongs inside a quote
    only if original to it. Flag ONLY the char IMMEDIATELY before a closing
    quote, and treat the two classes IDENTICALLY:
      - a comma           `,"` -> RED, no exemption, up to HART_RED_MAX hits
      - a LONE period     `."` -> RED, no exemption, up to HART_RED_MAX hits
    Past that count the OFFENDING CLASS (only) demotes to YELLOW for that file.

    NO "it might be original to the quote" exemption exists for either. The
    owner's rule is `".`/`",` no matter what, INCLUDING when the punctuation
    genuinely belongs to the quoted sentence —— it is a reading-comfort rule,
    and moving the mark outside costs two clicks. Anything reading this as a
    mis-fire is mistaken; do not reinstate a conditional.

    An ellipsis (`..`/`...`) immediately before the quote is NOT a full stop and
    stays exempt, e.g. `test..."` and `test, still..."` are both fine.

    THE COUNTERS ARE INDEPENDENT, one per class, and that is a decision rather
    than an accident. The threshold expresses "how many clicks does clearing
    this cost", and clearing a comma is not clearing a period —— so a file with
    six commas and one period owes one click for the period, which is squarely
    inside the reason RED exists. Sharing a counter would let a comma-heavy file
    soften the period rule (and the reverse), i.e. relax a class nobody named,
    on evidence drawn from a different class."""
    buckets = {",": [], ".": []}
    for ln, line in enumerate(lines, 1):
        for i, ch in enumerate(line):
            if ch not in CLOSING_QUOTES or i == 0:
                continue
            prev = line[i - 1]
            if prev == ",":
                buckets[","].append((ln, ch))
            elif prev == "." and not (i >= 2 and line[i - 2] == "."):   # exempt `..`/`...`
                buckets["."].append((ln, ch))

    for mark, hits in buckets.items():
        if not hits:
            continue
        name = "comma" if mark == "," else "period"
        if len(hits) <= HART_RED_MAX:
            for ln, ch in hits:
                red.append((ln, f"{name} inside closing quote `{mark}{ch}` —— ALWAYS move it OUTSIDE, even if the mark is original to the quote: {_snip(orig[ln - 1])}"))
        else:
            for ln, ch in hits:
                yellow.append((ln, f"{name} inside closing quote `{mark}{ch}` —— {len(hits)} in this file (over {HART_RED_MAX}), so demoted from RED; does the mark truly belong INSIDE the quote? Move it out unless quoting verbatim: {_snip(orig[ln - 1])}"))


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


# QUICK-ONLY —— the `#r` tense check. `glossary.md` reserves `#r` for the
# past/perfect tense of "read", so that "I #r A and will read B" stays
# unambiguous. A bare "read" is correct for present/future and WRONG for past,
# and only a human (or CC re-reading its own sentence) can tell which is which
# —— so this advises, never asserts.
#
# QUICK ONLY, and that exclusion is load-bearing: `#r` is house shorthand.
# FULL mode lints DELIVERABLES, which go to third parties who have never seen
# this glossary, so a deliverable must spell "read" out in full. Firing there
# would push house abbreviations into outgoing work —— the opposite of the rule.
#
# WHY THE MATCHER IS NOT JUST `\b[Rr]ead\b`, measured rather than assumed. That
# bare pattern fires on 63% of this repo's 494 `response_` files, 974 hits in
# all, and most of those are not tense errors at all. Only TWO classes are
# excluded, and the test for inclusion is severe: an exclusion is allowed ONLY
# where `#r` could not be the right word under ANY reading, because the owner's
# standing ruling is that a false positive costs ~10 wasted tokens whilst a
# false negative "could be highly misleading". So:
#   1. HYPHENATED COMPOUNDS —— `re-read`, `read-only`, `conditional-read`,
#      `must-read`, `over-read`. A hyphen IS a word boundary, so the bare
#      pattern matched all of them. `#r` cannot substitute inside a compound;
#      there is no `re-#r`, and `glossary.md` defines `#r` for the WORD "read".
#   2. THE TOOL NAME —— "the Read tool", "Read/Write". A proper noun, and
#      abbreviating a tool's name would be simply wrong.
#
# BOTH WERE RE-EXAMINED AGAINST THAT RULING AND DELIBERATELY KEPT, on a census
# of the corpus rather than on the assertion above —— "there is no `re-#r`" is
# the WEAK form of the argument and covers only one form. The strong form is
# that most of what they exclude is not a verb at all:
#   * Class 1 = 222 occurrences, 52 distinct forms. 122 are TENSELESS ——
#     `read-only` (41), `run-not-read`, `live-read`, `delta-read`,
#     `conditional-read`, `auto-read`, `machine-read`, `read-path`: compound
#     adjectives and noun modifiers with no tense for anyone to judge. The
#     other 100 are the `re-read` family —— a real verb with a real past
#     tense, and no available substitution.
#   * Class 2 = 13 occurrences, all 13 the tool's proper noun. Zero verbs.
# So the owner's trade-off does not REACH either class. It prices a false
# positive against a false negative, and here there is no false negative to
# buy: nothing excluded is a bare past-tense "read" that `#r` would fix. A
# flag on `read-only` is not a ten-token false positive with a fix attached ——
# it is a demand to judge the tense of a word that has none, forever.
# The cost of dropping both anyway was measured, since the decision turns on
# it: 581 hits / 257 files (52%) now, against 791 / 283 (57%) —— +210 hits,
# every one unactionable. That is NOT the 974 above, which additionally needs
# the noun and bare-stem filters dropped; conflating the two overstates the
# price of this particular choice by roughly twofold.
#
# EVERYTHING ELSE FIRES, including cases a tense-aware reader would call
# correct. That is the point: the flag asks CC to JUDGE, and a judgement baked
# into the matcher is a judgement CC never gets to make.
#
# WHAT WAS REMOVED AND WHY, so it is not helpfully restored:
#   * THE `be`-PASSIVE ("that file is read only at `#close`", "is not yet
#     read"). This was excluded as "present passive, cannot be past" —— but a
#     passive `read` is the PARTICIPLE, pronounced /rɛd/, which is exactly the
#     form `#r` exists to disambiguate. It was the real miss that prompted this
#     narrowing being narrowed back: a live `response_` shipped "that file is
#     read only at" and the advisory never mentioned it.
#   * A DETERMINER A WORD OR TWO BACK PLUS A CLAUSE BREAK ("a missing read.").
#     It swallowed "the file you read." —— a plain past tense —— because `the`
#     sat within three tokens. It bought silence on a noun and paid for it with
#     a genuine miss.
#   * DISTRIBUTIVE AND DEMONSTRATIVE DETERMINERS (`this that these those each
#     every another one no`). Every one of them doubles as a PRONOUN that can
#     head a past clause: "That read as an oversight", "Each read the brief".
# The residual is REAL and stated in the flag, not hidden —— see `_read_tense`.
_READ_RE = re.compile(r"[A-Za-z0-9_#-]*\b([Rr]ead)\b[A-Za-z0-9_-]*")

# An article or possessive IMMEDIATELY before "read" makes it a noun ("a read
# via Bash", "discharge the read"). Only forms that cannot themselves be the
# SUBJECT of a past-tense clause survive here —— see WHAT WAS REMOVED above.
_READ_NOUN_BEFORE = frozenset("""
a an the its his her their your my our first second last single extra further
failed missed
""".split())

# Words that cannot be followed by a PAST "read": modals and infinitive `to`
# force the bare stem. The `be` forms are deliberately ABSENT —— "is read" is a
# passive participle, i.e. `#r` territory.
_READ_NONPAST_BEFORE = frozenset("""
to will can cannot could may might must shall should would do does let please
ll wont dont doesnt cant couldnt shouldnt wouldnt
""".split())

# Adverbs allowed to sit between the governor and the verb ("is only read",
# "is not yet read"). `already` is deliberately ABSENT —— "already read" is a
# perfect, i.e. exactly the case this check exists to catch.
_READ_ADVERBS = frozenset("""
not yet only also just still never always often usually rarely generally
typically normally merely simply then again freely fully partly carefully
silently actually directly ever
""".split())

_READ_TOKEN_RE = re.compile(r"[A-Za-z']+")


def _read_tense(lines, orig, yellow):
    """ONE yellow per file, never one per occurrence —— but EVERY line number in
    it, never a truncated list.

    Reporting per occurrence is what made this feel like noise: the same
    reminder repeated twenty times says nothing the first one did not, and a
    flag nobody finishes reading is a flag nobody acts on. One entry carrying
    every candidate's line number is the same information at a twentieth of the
    volume, and it still lets CC jump straight to each instance.

    THE LINE LIST IS NOT CAPPED, and that is the one thing here that is not a
    presentation choice. It used to show the first eight and elide the rest,
    which meant a genuine past tense on line nine was DETECTED and then hidden
    —— a false negative manufactured by the report rather than by the matcher,
    which is the failure mode the owner ranks worst. A long list is ~1 token
    per entry; a hidden instance is a wrong sentence shipped."""
    hits = []
    for ln, line in enumerate(lines, 1):
        for m in _READ_RE.finditer(line):
            if m.group(0) != m.group(1):
                continue                      # class 1: hyphenated compound
            before = line[:m.start(1)]
            after = line[m.end(1):]
            if m.group(1) == "Read" and (
                    re.match(r"\s*(?:tool|/|\bor\b|,\s*Write)", after)
                    or before.endswith("/")):
                continue                      # class 2: the Read tool
            prev = _READ_TOKEN_RE.findall(before)
            skip = False
            for tok in reversed(prev[-3:]):
                low = tok.lower().replace("'", "")
                if low in _READ_ADVERBS:
                    continue                  # step over an adverb and re-test
                if low in _READ_NOUN_BEFORE or low in _READ_NONPAST_BEFORE:
                    skip = True               # a noun, or a bare-stem governor
                break
            if skip:
                continue
            words = line.split()
            pos = len(before.split())
            hits.append((ln, " ".join(words[max(0, pos - 5):pos + 6])))

    if not hits:
        return
    shown = ", ".join("L%d" % ln for ln, _ in hits)
    yellow.append((hits[0][0],
                   f'{len(hits)} bare "read" left to judge ({shown}); first is '
                   f'"{hits[0][1]}". Past/perfect (incl. a passive "is read") '
                   f'-> `#r` (per `glossary.md`); present/future/imperative is '
                   f"already correct. **Silently** fix, no explanation to "
                   f"user."))


def run_checks(text, quick=False):
    """Return (red, yellow). Fenced code blocks AND inline `code` spans are masked
    first so prose rules never fire inside code (embedded deliverables are linted
    separately via FULL `--text`); detection runs on the masked text, snippets are
    shown from the original.

    There is no per-caller suppression parameter. `--rt-quiet` used to let
    `dlint_quick.py` silence the `read`/`#r` advisory once a (session, file) had
    seen it; it was removed because a withheld reminder is a detected instance
    made invisible, and the whole point of the advisory is that only a reader
    can settle the tense."""
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

    if quick:
        # QUICK ONLY —— house shorthand must never be pushed into a deliverable
        _read_tense(lines, orig, yellow)

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
    # `--rt-quiet` is still SWALLOWED, never honoured: the flag is gone but a
    # stale caller (an old shim, a copied command line) must not be handed a
    # usage error and silently stop linting. Accepting and ignoring it is the
    # fail-safe direction —— the lint still runs, in its stricter form.
    while args and args[0] in ("--quick", "--rt-quiet"):
        if args[0] == "--quick":
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
