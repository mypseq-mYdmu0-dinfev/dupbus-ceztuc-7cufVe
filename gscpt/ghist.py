#!/usr/bin/env python3
"""
ghist.py —— Git History, human-readable (macOS)

Renders ONE file's full git history as a single self-contained HTML page,
GitHub-web style: one card per commit (newest first) with the commit message,
date, author, and a WORD-LEVEL inline diff (red = removed, green = added) —
built for prose .md files (word diffs read naturally), works on code too.
Follows renames (`git log --follow`), so a file that was `git mv`-ed any
number of times still shows its whole story.

USAGE (DXMF-style activation)
-----------------------------
1. Place an instruction file with a .txt or .md extension beside this script
   (any name except `temp.txt` and this script's own outputs). Its FIRST
   non-empty line = the target file's path (macOS "copy file path" absolute
   form; a leading/trailing quote pair is tolerated).
2. Run:  python3 ghist.py
3. Output: `ghist_[target-stem]_[YYYYMMDDHHmm].html` beside this script —
   open it in any browser. Nothing else is written; the repo is never touched.

Notes: the target must live inside a git repository (any repo, found
automatically). Large histories are fine — every commit body is a collapsed
<details> block, so an 80-commit file still opens instantly.
"""
from __future__ import annotations

import difflib
import html
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
MAX_RENDER_CHARS = 400_000        # per-commit diff cap (huge blobs truncated)


def die(msg: str) -> None:
    print(f"ghist: {msg}", file=sys.stderr)
    sys.exit(1)


def read_instruction() -> Path:
    for p in sorted(SCRIPT_DIR.iterdir()):
        if p.suffix.lower() not in (".txt", ".md"):
            continue
        if p.name in ("temp.txt",) or p.name.startswith("ghist_"):
            continue
        if p.name == "ajap_runtime_log.md":      # AJAP's analytics log, not ours
            continue
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip().strip("'\"")
            if line and not line.startswith("#"):
                return Path(line).expanduser()
    die("no instruction .txt/.md with a file path found beside the script")


def git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or f"git {' '.join(args)} failed")
    return r.stdout


def repo_root(target: Path) -> Path:
    r = subprocess.run(["git", "-C", str(target.parent), "rev-parse",
                        "--show-toplevel"], capture_output=True, text=True)
    if r.returncode != 0:
        die(f"{target} is not inside a git repository")
    return Path(r.stdout.strip())


def history(repo: Path, rel: str) -> list[dict]:
    """[{hash, author, date, subject, path}], newest first, rename-following."""
    out = git(repo, "log", "--follow", "--name-only",
              "--format=@@@%H%x09%an%x09%ad%x09%s",
              "--date=format:%Y-%m-%d %H:%M", "--", rel)
    commits: list[dict] = []
    cur: dict | None = None
    for line in out.splitlines():
        if line.startswith("@@@"):
            h, an, ad, s = (line[3:].split("\t", 3) + ["", "", ""])[:4]
            cur = {"hash": h, "author": an, "date": ad, "subject": s,
                   "path": rel}
            commits.append(cur)
        elif line.strip() and cur is not None:
            cur["path"] = line.strip()          # the file's name AT that commit
    return commits


def content_at(repo: Path, commit: str, path: str) -> str:
    try:
        return git(repo, "show", f"{commit}:{path}")
    except RuntimeError:
        return ""


_TOKEN = re.compile(r"\n|[ \t]+|[^\s]+")


def word_diff_html(old: str, new: str) -> str:
    """Inline word-level diff, GH-style: <del> red, <ins> green."""
    a, b = _TOKEN.findall(old), _TOKEN.findall(new)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    out: list[str] = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op in ("equal",):
            out.append(html.escape("".join(a[i1:i2])))
        if op in ("delete", "replace") and i2 > i1:
            seg = html.escape("".join(a[i1:i2]))
            if seg.strip():
                out.append(f"<del>{seg}</del>")
            else:
                out.append(seg)
        if op in ("insert", "replace") and j2 > j1:
            seg = html.escape("".join(b[j1:j2]))
            if seg.strip():
                out.append(f"<ins>{seg}</ins>")
            else:
                out.append(seg)
    return "".join(out)


CSS = """
body{font:15px/1.55 -apple-system,'Helvetica Neue',sans-serif;margin:0;
     background:#f6f8fa;color:#1f2328}
header{background:#24292f;color:#fff;padding:14px 22px}
header h1{font-size:17px;margin:0}
header .sub{color:#c9d1d9;font-size:12px;margin-top:3px}
main{max-width:980px;margin:18px auto;padding:0 14px}
.commit{background:#fff;border:1px solid #d0d7de;border-radius:8px;
        margin-bottom:14px;overflow:hidden}
.commit summary{cursor:pointer;padding:10px 14px;display:flex;gap:10px;
        align-items:baseline;flex-wrap:wrap;list-style:none}
.commit summary::-webkit-details-marker{display:none}
.commit summary:hover{background:#f3f4f6}
.hash{font:12px ui-monospace,Menlo,monospace;color:#0969da;
      background:#ddf4ff;border-radius:4px;padding:1px 6px}
.subj{font-weight:600}
.meta{color:#57606a;font-size:12.5px;margin-left:auto;white-space:nowrap}
.rename{font-size:12px;color:#9a6700;background:#fff8c5;border-radius:4px;
        padding:1px 6px}
.body{border-top:1px solid #d0d7de;padding:12px 16px;background:#fff}
pre.diff{white-space:pre-wrap;word-wrap:break-word;
         font:12.8px ui-monospace,Menlo,monospace;margin:0}
del{background:#ffebe9;color:#82071e;text-decoration:line-through}
ins{background:#dafbe1;color:#116329;text-decoration:none}
.note{color:#57606a;font-size:12.5px;margin:0 0 8px}
"""


def main() -> None:
    target = read_instruction()
    if not target.exists():
        die(f"target not found: {target}")
    repo = repo_root(target)
    rel = str(target.resolve().relative_to(repo))
    commits = history(repo, rel)
    if not commits:
        die(f"no git history for {rel}")
    # oldest→newest contents (each vs its predecessor), rendered newest-first
    texts: list[str] = []
    for c in reversed(commits):                  # oldest first
        texts.append(content_at(repo, c["hash"], c["path"]))
    cards: list[str] = []
    n = len(commits)
    for idx, c in enumerate(commits):            # newest first
        new_i = n - 1 - idx
        new_text = texts[new_i]
        old_text = texts[new_i - 1] if new_i > 0 else ""
        renamed = (new_i > 0
                   and commits[idx + 1]["path"] != c["path"])
        if len(old_text) + len(new_text) > MAX_RENDER_CHARS:
            body = ("<p class='note'>diff too large to render word-by-word "
                    f"({len(new_text)} chars) — showing no inline diff.</p>")
        else:
            label = ("file created in this commit"
                     if new_i == 0 else
                     f"vs previous commit ({commits[idx + 1]['hash'][:7]})")
            body = (f"<p class='note'>{html.escape(label)}"
                    + (f" · renamed from <code>{html.escape(commits[idx + 1]['path'])}</code>"
                       if renamed else "")
                    + "</p><pre class='diff'>"
                    + word_diff_html(old_text, new_text) + "</pre>")
        open_attr = " open" if idx == 0 else ""   # newest card pre-expanded
        cards.append(
            f"<details class='commit'{open_attr}><summary>"
            f"<span class='hash'>{c['hash'][:7]}</span>"
            f"<span class='subj'>{html.escape(c['subject'])}</span>"
            + (f"<span class='rename'>renamed</span>" if renamed else "")
            + f"<span class='meta'>{html.escape(c['author'])} · "
            f"{html.escape(c['date'])}</span>"
            f"</summary><div class='body'>{body}</div></details>")
    ts = datetime.now().strftime("%Y%m%d%H%M")
    out = SCRIPT_DIR / f"ghist_{target.stem}_{ts}.html"
    out.write_text(
        "<!doctype html><meta charset='utf-8'>"
        f"<title>ghist — {html.escape(target.name)}</title>"
        f"<style>{CSS}</style>"
        f"<header><h1>{html.escape(target.name)} — git history "
        f"({n} commits)</h1><div class='sub'>{html.escape(str(target))} · "
        f"generated {ts} · newest first · click a commit to expand"
        f"</div></header><main>" + "".join(cards) + "</main>",
        encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
