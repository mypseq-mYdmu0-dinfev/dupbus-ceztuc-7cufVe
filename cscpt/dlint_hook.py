#!/usr/bin/env python3
"""PostToolUse hook —— after a CC-authored comms file (`response_`/`close_`/`wrap_`
`*.md`, incl. CP prefixes) is written/edited, run `dlint.py --quick` on it and
BLOCK (exit 2) while any 🔴 RED flag remains, feeding the flags back so CC fixes
them; the loop repeats until RED = 0.

YELLOW flags do NOT block —— CC surfaces & justifies them via its own --quick run
(per root CLAUDE.md §3.5.5), placing the justification as the LAST content of the
same file.

Scope guard —— it acts ONLY on `response_`/`close_`/`wrap_` `.md` files (NOT
`query_` = user's words, NOT `artefact_` = non-CC), so it can NEVER misfire on
code scripts, deliverables, automations (`/seek/`), or anything else. FAIL-SAFE
—— on ANY error or non-match it exits 0; it will never block on its own failure.
(Run, not read —— see README.)"""

import sys
import os
import json
import subprocess


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0

    fp = (data.get("tool_input") or {}).get("file_path") or ""
    base = os.path.basename(fp)

    # ONLY CC-authored comms files (incl. CP-prefixed e.g. career_response_*.md):
    # response_ / close_ / wrap_. NOT query_ (user's words) or artefact_ (non-CC).
    if not base.endswith(".md") or not any(
        k in base for k in ("response_", "close_", "wrap_")
    ):
        return 0
    if "/seek/" in fp:            # AJAP automation —— never touch
        return 0
    if not os.path.isfile(fp):
        return 0

    dlint = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dlint.py")
    if not os.path.isfile(dlint):
        return 0

    try:
        r = subprocess.run(
            [sys.executable, dlint, "--quick", fp],
            capture_output=True, text=True, timeout=30,
        )
    except Exception:
        return 0

    # dlint exit: 0 = no RED, 1 = RED present, 2 = usage/error.
    if r.returncode == 1:
        sys.stderr.write(
            "dlint --quick found RED flag(s) in this comms file —— fix them "
            "(British spelling / Hart's quotation / #numbered), they then clear:\n"
            + r.stdout
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
