#!/usr/bin/env python3
"""
cl_check.py —— deterministic Cover-Letter (CL) compliance linter for ONE or more
AJAP Application Records (ARs).

Purpose (per investigation query_202606091942 §7.2): give SA1, SA3 and MA a COLD,
non-LLM gate for CL format rules, so a compromised CL cannot pass on agent
"judgement" alone. The violation logic is extracted/adapted from
`gscpt/ajap_logs.py` (scan_applied_violations) and extended with the
colon-pillar finding from `audit_202606040352` and the `16⁺`-once rule.

USAGE
-----
    python3 cl_check.py <AR_path> [<AR_path> ...]

  - SA1: run on the single applying AR right before declaring "Applying".
  - SA3 (or MA): run before approving Submit.
  - MA half-hourly cold audit: pass every applied AR created since last audit.

EXIT CODE
---------
    0  = all files clean
    1  = at least one violation found (details printed per file)
    2  = usage / file error

SCOPE & LIMITS
--------------
  - Checks the COVER LETTER only (text from the `## N. Cover Letter` marker to EOF).
  - This is FORMAT linting, NOT truth-checking. It cannot catch false claims,
    wrong salary/notice answers, or wrong resume variant —— those still require
    SA1/SA3 reasoning. Keep both gates.
  - BANNED_WORDS is seeded with known offenders; extend from gcl.md / mini_writing.md.
"""

import re
import sys
from pathlib import Path

# --- Rules (verbatim from ajap_logs.py where applicable) -----------------------

# Dash/plus symbols that must NEVER appear in a CL (bare `+` must be `⁺`; em/en
# dashes are banned in deliverables).
RULE_VIOLATION_SYMBOLS = ["—", "–", "+"]

# Every applied CL must END with EXACTLY this line (no text after it).
PS_REQUIRED_TAIL = (
    "P.S. I hold full work rights until 2031 and would never require visa sponsorship."
)

# Marker that opens the CL section; the digit is captured to enforce "== 6".
CL_MARKER = re.compile(r"##\s+(\d+)\.\s+Cover Letter")

# "16⁺ years" (or bare "16⁺") may appear AT MOST once in the CL.
SIXTEEN_PLUS = re.compile(r"16⁺")

# Colon-pillar header pattern (audit_202606040352 §9.1): a paragraph that opens
# with a short Capitalised label terminated by a colon, e.g.
# "Strategic Transformation:" or "**Data-Driven Growth:**". Strengths must be
# inline, never colon-headed. Salutation lines ("Dear ...,") use a comma, not a
# colon, so they are not matched. Times like "9:00" are not at line start as a
# label, so they are excluded by requiring letters-only before the colon.
COLON_PILLAR = re.compile(r"^\s*\**[A-Z][A-Za-z][A-Za-z &/-]{2,40}:\s*\S", re.MULTILINE)

# Seed list —— EXTEND from gcl.md / mini_writing.md banned-words.
BANNED_WORDS = [
    "seamlessly",
    "seamless",
    "resonates",
    "resonate",
    "delve",
    "leverage",
    "synergy",
    "tapestry",
]


def check_one(path: Path):
    """Return (hard_violations, soft_warnings) for a single AR file.

    HARD = deterministic, no-judgement-needed breaches → fail (exit 1).
    SOFT = heuristic flags that CAN false-positive (e.g. a company literally
    named "Synergy") → printed for the agent to judge, do NOT fail the run.
    """
    hard, soft = [], []
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        return ([f"UNREADABLE: {e}"], [])

    m = CL_MARKER.search(content)
    if not m:
        return (["NO `## N. Cover Letter` marker (skip/pending AR? else a violation)"], [])

    section_no = m.group(1)
    if section_no != "6":
        hard.append(f"CL section heading is `## {section_no}.` (must be `## 6.`)")

    cl = content[m.start():]

    # HARD: dash/plus symbols
    for sym in RULE_VIOLATION_SYMBOLS:
        n = cl.count(sym)
        if n:
            hard.append(f"banned symbol `{sym}` x{n} in CL (use `⁺` for plus; no dashes)")

    # HARD: 16⁺ at most once
    n16 = len(SIXTEEN_PLUS.findall(cl))
    if n16 > 1:
        hard.append(f"`16⁺` appears x{n16} (allowed once)")

    # HARD: P.S. tail must be the exact final line
    stripped = content.rstrip()
    last_line = stripped.splitlines()[-1] if stripped else ""
    if last_line != PS_REQUIRED_TAIL:
        hard.append("file does NOT end with the exact required P.S. line")

    # SOFT: colon-pillar headers (audit_202606040352 §9.1)
    pillars = COLON_PILLAR.findall(cl)
    if pillars:
        soft.append(
            f"possible colon-pillar header(s) x{len(pillars)} "
            f"(strengths must be inline, not `Label:`) —— verify"
        )

    # SOFT: banned/AI-slop words (may match a company name → judge)
    low = cl.lower()
    for w in BANNED_WORDS:
        if re.search(rf"\b{re.escape(w)}\b", low):
            soft.append(f"possible banned word `{w}` (ignore if part of a company/person name)")

    return (hard, soft)


def main(argv):
    if len(argv) < 2:
        print("usage: python3 cl_check.py <AR_path> [<AR_path> ...]")
        return 2

    any_violation = False
    any_error = False
    for arg in argv[1:]:
        p = Path(arg)
        if not p.is_file():
            print(f"❌ {arg}: file not found")
            any_error = True
            continue
        hard, soft = check_one(p)
        if hard:
            any_violation = True
            print(f"❌ {p.name} —— HARD VIOLATION(S):")
            for v in hard:
                print(f"   - {v}")
        else:
            print(f"✅ {p.name}: no hard violation")
        for w in soft:
            print(f"   ⚠️  {w}")

    if any_error:
        return 2
    return 1 if any_violation else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
