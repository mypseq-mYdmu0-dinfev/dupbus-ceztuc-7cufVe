#!/usr/bin/env python3
"""PostToolUse hook —— after a `response_*.md` is written/edited, run
`dlint.py --quick` on it and BLOCK (exit 2) while any 🔴 RED flag remains,
feeding the flags back so CC fixes them; the loop repeats until RED = 0.

YELLOW flags do NOT block —— CC surfaces & justifies them via its own --quick run
(per root CLAUDE.md §3.5.5), placing the justification as the LAST content of the
same `response_`.

Scope guard —— it acts ONLY on `response_*.md` comms files, so it can NEVER
misfire on code scripts, deliverables, automations (`/seek/`), or anything else.
FAIL-SAFE —— on ANY error or non-match it exits 0; it will never block on its own
failure. (Run, not read —— see README.)"""

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

    # ONLY response_ comms files (incl. CP-prefixed e.g. career_response_*.md)
    if "response_" not in base or not base.endswith(".md"):
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
            "dlint --quick found RED flag(s) in this response_ file —— fix them "
            "(British spelling / Hart's quotation / #numbered), they then clear:\n"
            + r.stdout
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
