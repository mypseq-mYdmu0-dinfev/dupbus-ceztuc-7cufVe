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
code scripts, deliverables, or anything else. FAIL-SAFE —— on ANY error or
non-match it exits 0; it will never block on its own failure.
(Run, not read —— see README.)"""

import sys
import os
import re
import json
import subprocess

# ---------------------------------------------------------------------------
# REPO-SCOPE GUARD.
#
# WHY: this hook is registered in the USER-level ~/.claude/settings.json, not
# a project settings.json —— proven live this session that Claude Desktop
# NEVER runs project-level hooks, only user-level ones. A user-level
# registration fires for EVERY project open on this Mac, not just this repo.
# Unscoped, that is actively harmful here: this hook BLOCKS (exit 2) on
# THIS repo's own `dlint.py` prose/style rules and would start blocking
# unrelated projects' `response_`/`close_`/`wrap_`-named files against a
# style guide that has nothing to do with them. So before doing anything
# else (incl. before spawning the `dlint.py` subprocess below), self-scope
# to this repo and exit silently everywhere else.
#
# HOW: prefer the payload's `cwd` (an absolute path, confirmed present on
# every real PostToolUse payload captured live this session —— exactly the
# event type this hook receives). If `cwd` is ever absent, fall back to
# `transcript_path`'s Claude-Code project slug: transcripts live at
# `~/.claude/projects/<slug>/<uuid>.jsonl`, where `<slug>` is the project
# directory with every `/` and ` ` replaced by `-` (confirmed live).
# Compare either signal against THIS repo's own root/slug, derived from
# this script's OWN location (never a hard-coded path, so the repo stays
# portable/relocatable) —— resolving symlinks via `os.path.realpath` and
# treating a sub-path of the repo as in-scope too.
#
# FAIL-OPEN: if NEITHER field is present/parseable, run exactly as if this
# guard did not exist. An unscopeable payload is not evidence of a
# different project —— it is just a shape we cannot read —— and a lint
# that goes silently dark on ambiguity is precisely the failure this whole
# hook-migration effort exists to fix.
# ---------------------------------------------------------------------------
_REPO_ROOT_REAL = os.path.realpath(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_REPO_SLUG = re.sub(r"[/ ]", "-", _REPO_ROOT_REAL.rstrip("/"))


def _in_scope(data):
    """True if this invocation's project is THIS repo (or a sub-path of
    it), or if scope genuinely cannot be determined (FAIL-OPEN, see block
    comment above). Never raises: any unexpected error here must default to
    "run the lint", exactly like every other fail-safe path in this file."""
    try:
        if not isinstance(data, dict):
            return True
        cwd = data.get("cwd")
        if isinstance(cwd, str) and cwd:
            real_cwd = os.path.realpath(cwd)
            return (real_cwd == _REPO_ROOT_REAL
                    or real_cwd.startswith(_REPO_ROOT_REAL + os.sep))
        tp = data.get("transcript_path")
        if isinstance(tp, str) and tp:
            m = re.search(r"/projects/([^/]+)/", tp)
            if m:
                slug = m.group(1)
                return (slug == _REPO_SLUG
                        or slug.startswith(_REPO_SLUG + "-"))
            # transcript_path present but not the recognised
            # .../projects/<slug>/... shape -> unparseable -> fall through.
        return True  # neither field usable -> FAIL-OPEN
    except Exception:
        return True  # never let a scope-check error silence the lint


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0

    if not _in_scope(data):
        return 0

    fp = (data.get("tool_input") or {}).get("file_path") or ""
    base = os.path.basename(fp)

    # ONLY CC-authored comms files (incl. CP-prefixed e.g. career_response_*.md):
    # response_ / close_ / wrap_. NOT query_ (user's words) or artefact_ (non-CC).
    if not base.endswith(".md") or not any(
        k in base for k in ("response_", "close_", "wrap_")
    ):
        return 0
    # (why: seek/ retired 202607181152; this hook is wired only via this
    # dupbus repo's own .claude/settings.json, so the old /seek/ exemption
    # had no live target left — removed rather than repointed)
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
