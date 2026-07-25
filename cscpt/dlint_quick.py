#!/usr/bin/env python3
"""`dlint.py --quick` runner for the PostToolUse chain —— after a CC-authored comms
file is written/edited, it runs the quick lint on that file and BLOCKS whilst
any 🔴 RED flag remains, feeding the flags back so CC fixes them.

=== NON-CCSIM —— all you need to RUN it ===
* Run by the harness via `dlint_hook.sh` (the registered bash fast-path), never
  by hand: shim -> this file -> `dlint.py --quick <file>`. Registered PostToolUse
  (Edit|Write|MultiEdit) in the USER-level `~/.claude/settings.json` (the Claude
  Desktop app executes user-level hooks and silently ignores project-level
  ones), and it self-scopes: outside THIS repo it exits 0.
* SCOPE: `response_`/`close_`/`wrap_` `.md` files only (incl. CP prefixes). NOT
  `query_` (the user's words), NOT `artefact_` (non-CC), and never code or
  deliverables —— so it cannot misfire on them.
* IN: PostToolUse JSON on stdin. EXIT 2 whilst RED remains, with the flag list
  on STDERR for CC to act on; the write-fix-rewrite loop repeats until RED = 0.
  EXIT 0 otherwise.
* YELLOW never blocks —— CC surfaces and justifies YELLOW flags from its own
  `dlint.py --quick` run (root CLAUDE.md §3.5.5), placed as the LAST content of
  the same file.
* FAIL-SAFE: any error, missing field, non-match, or a missing/slow `dlint.py`
  (30 s timeout) -> exit 0. It never blocks on its own failure.
(Run, not read —— see README.)

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
NAMED `_quick`, NOT `_hook`: the registered hook is `dlint_hook.sh`. Across
`cscpt/` every `.sh` carries `_hook` and no `.py` does, so the filename tells the
truth about which file the harness actually launches. This is not a generic hook
body —— it does exactly one thing.

SCOPE IS LOAD-BEARING HERE because this is the one lint in the chain that BLOCKS:
under user-level registration it would otherwise exit 2 on any project's file
merely NAMED `response_`/`close_`/`wrap_`, judged against a style guide that has
nothing to do with it. Hence `_in_scope` runs BEFORE the `dlint.py` subprocess is
spawned (signals: see the guard's own block comment). It FAILS OPEN on an
unscopeable payload —— that is not evidence of a different project, and a lint
going dark on ambiguity is the failure this whole wiring exists to fix.

NO PATH-BASED EXEMPTIONS: role and extension alone decide scope. An earlier
per-folder carve-out was removed rather than repointed once its target retired ——
resist adding another; a filename rule true everywhere beats a path rule that
rots.
"""

import sys
import os
import re
import json
import subprocess

# ---------------------------------------------------------------------------
# REPO-SCOPE GUARD —— user-level registration fires in EVERY project on this
# Mac, so self-scope to THIS repo and exit silently elsewhere. Signals, in
# order: the payload's `cwd`, else the `~/.claude/projects/<slug>/` transcript
# slug —— both compared against values derived from this file's OWN location,
# never a hard-coded path. FAILS OPEN when neither is usable. Full rationale
# (why user-level, why fail-open, why THIS lint in particular must not roam)
# is in the CCSIM section of the module docstring above.
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
    # No path-based exemptions: role + extension alone decide scope (see CCSIM).
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
