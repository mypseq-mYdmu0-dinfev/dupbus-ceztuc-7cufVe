#!/usr/bin/env python3
"""
git_history.py —— Git History, human-readable (macOS; renamed from ghist.py)

Renders ONE file's full git history as a single self-contained HTML page,
GitHub-web style: one card per commit (newest first) with the commit message,
date, and a WORD-LEVEL inline diff (red = removed, green = added) — built for
prose .md files, works on code too. Follows renames (`git log --follow`).

Page features (user 202607080322 §285): dark-mode toggle (defaults to the
macOS light/dark state via prefers-color-scheme); HTML/Code view toggle
(HTML = the post-commit markdown rendered rich-text, GH-Preview-style;
Code = the word-diff; the button names its DESTINATION); Avenir fonts; the
SHA chip copies itself AND opens the commit on GitHub in a new tab (without
collapsing the card); no usernames anywhere (privacy); Help pop-up; subtle
confidentiality footer at the very bottom.

Two further toolbar toggles (every button names its DESTINATION, matching the
existing HTML/Code one):
  - Show More / Show Less — DEFAULT is Show Less, which lists ONLY the commits
    since (inclusive of) the file's most recent rename, hiding the older
    history under prior names; clicking Show More reveals every identified
    commit. The rename boundary reuses the same rename detection already drawn
    on each card (plus any structural-bridge boundary).
  - Full Content / Changes Only — DEFAULT is Changes Only, a diff-hunk view of
    just the changed lines plus 3 lines of context above/below each change
    (GitHub-style `@@` hunk headers); clicking Full Content restores the whole
    file for that commit. The scoping applies to BOTH the Code word-diff AND
    the HTML markdown preview: HTML + Changes Only renders the .md preview of
    only the changed+context lines. All four Code/HTML × Full/Changes
    combinations render (pure client-side CSS class toggles).

USAGE (DXMF-style activation)
-----------------------------
1. Place an instruction file with a .txt or .md extension beside this script
   (any name except `temp.txt`/`blank.md`/`README.md` or a `❌_`-prefixed
   name; `parked/` is ignored). EACH non-empty, non-`#` line = one target
   file path (macOS "copy file path" absolute form; surrounding quotes
   tolerated) → one output .html. A single-path file still yields one page.
2. Run:  python3 git_history.py
   Alternatively pass paths as CLI args (`python3 git_history.py A B ...`) or
   pipe them on stdin (one path per line); each mode produces one page per
   path. CLI args win over stdin, stdin over the beside-script file.
3. Output: `git_history_[target-stem]_[YYYYMMDDHHmm].html` beside this script,
   one per input path.

The target must live inside a git repository (found automatically). Every
commit body is a collapsed <details> block, so long histories open instantly.
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
    print(f"git_history: {msg}", file=sys.stderr)
    sys.exit(1)


def _lines_to_targets(text: str) -> list[Path]:
    """Every non-empty, non-`#` line (quotes tolerated) → one target path."""
    out: list[Path] = []
    for line in text.splitlines():
        line = line.strip().strip("'\"")
        if line and not line.startswith("#"):
            out.append(Path(line).expanduser())
    return out


def _instruction_targets() -> list[Path]:
    """First qualifying instruction .txt/.md beside the script → ALL its path
    lines (one output page each), not just the first."""
    for p in sorted(SCRIPT_DIR.iterdir()):
        if not p.is_file() or p.suffix.lower() not in (".txt", ".md"):
            continue
        # blank.md is the renamed temp.txt; ❌_ marks a file parked in place.
        if p.name.lower() in ("temp.txt", "blank.md", "readme.md") or p.name.startswith(
                ("ghist_", "git_history_", "ajap_logs_", "ajap_runtime_log", "❌_")):
            continue
        targets = _lines_to_targets(
            p.read_text(encoding="utf-8", errors="replace"))
        if targets:
            return targets
    die("no instruction .txt/.md with a file path found beside the script")


def read_targets() -> list[Path]:
    """Multi-path entry point: CLI args (one path each) win over piped stdin
    lines, which win over the beside-script instruction file. Each yields one
    output .html per path."""
    args = [a for a in sys.argv[1:] if a.strip()]
    if args:
        return [Path(a.strip().strip("'\"")).expanduser() for a in args]
    if not sys.stdin.isatty():                       # paths piped on stdin
        try:
            piped = _lines_to_targets(sys.stdin.read())
        except Exception:
            piped = []
        if piped:
            return piped
    return _instruction_targets()


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
        raise RuntimeError(f"{target} is not inside a git repository")
    return Path(r.stdout.strip())


def github_base(repo: Path) -> str:
    """https://github.com/[user]/[repo] from the origin remote ('' if none)."""
    try:
        url = git(repo, "remote", "get-url", "origin").strip()
    except RuntimeError:
        return ""
    m = re.search(r"github\.com[:/]+([^/]+)/([^/\s]+?)(?:\.git)?$", url)
    return f"https://github.com/{m.group(1)}/{m.group(2)}" if m else ""


def history(repo: Path, rel: str) -> list[dict]:
    """[{hash, date, subject, path}], newest first, rename-following."""
    out = git(repo, "log", "--follow", "-M20%", "--name-only",
              "--format=@@@%H%x09%ad%x09%s",
              "--date=format:%Y-%m-%d %H:%M", "--", rel)
    commits: list[dict] = []
    cur: dict | None = None
    for line in out.splitlines():
        if line.startswith("@@@"):
            h, ad, s = (line[3:].split("\t", 2) + ["", ""])[:3]
            cur = {"hash": h, "date": ad, "subject": s, "path": rel}
            commits.append(cur)
        elif line.strip() and cur is not None:
            cur["path"] = line.strip()          # the file's name AT that commit
    return commits


def _name_tokens(path: str) -> set:
    return {t for t in re.split(r"[^a-z0-9]+", Path(path).stem.lower()) if t}


def _vanished_sources(repo: Path, commit: str) -> list:
    """Paths that DISAPPEARED from their old location in `commit` — rename
    sources (Rxx old→new) and deletions (D)."""
    try:
        out = git(repo, "show", "--name-status", "-M20%", "--format=", commit)
    except RuntimeError:
        return []
    gone: list = []
    for line in out.splitlines():
        parts = line.split("\t")
        if parts and parts[0].startswith("R") and len(parts) >= 3:
            gone.append(parts[1])
        elif parts and parts[0] == "D" and len(parts) >= 2:
            gone.append(parts[1])
    return gone


def _bridge_candidates(dead_path: str, gone: list) -> list:
    """GitHub-parity shortlist (202607090137 §353.5): the sole vanished path
    qualifies outright; amongst several, filename-token overlap ranks them
    (numeric-only tokens like the _00/_01 duplication suffixes are ignored —
    they pair the wrong twins) and zero overlap disqualifies."""
    if not gone:
        return []
    if len(gone) == 1:
        return list(gone)
    base = {t for t in _name_tokens(dead_path) if not t.isdigit()}
    scored = sorted(((len(base & {t for t in _name_tokens(g)
                                  if not t.isdigit()})
                      / max(len(base | _name_tokens(g)), 1), g)
                     for g in gone), key=lambda t: (-t[0], t[1]))
    return [g for s, g in scored if s > 0]


_FOLLOW_MEMO: dict = {}


def _follow_before(repo: Path, upto: str, path: str, seen: set) -> list:
    """git log --follow strictly BEFORE `upto` for `path` → fresh commit
    dicts (newest first), skipping hashes already seen."""
    memo_key = (upto, path)
    if memo_key not in _FOLLOW_MEMO:
        try:
            _FOLLOW_MEMO[memo_key] = git(
                repo, "log", "--follow", "-M20%", "--name-only",
                "--format=@@@%H%x09%ad%x09%s",
                "--date=format:%Y-%m-%d %H:%M", f"{upto}^", "--", path)
        except RuntimeError:
            _FOLLOW_MEMO[memo_key] = ""
    extra, cur = [], None
    for line in _FOLLOW_MEMO[memo_key].splitlines():
        if line.startswith("@@@"):
            h, ad, sub = (line[3:].split("\t", 2) + ["", ""])[:3]
            cur = ({"hash": h, "date": ad, "subject": sub, "path": path}
                   if h not in seen else None)
            if cur:
                extra.append(cur)
        elif line.strip() and cur is not None:
            cur["path"] = line.strip()
    return extra


def _bridge_depth(repo: Path, oldest: dict, seen: set, hops: int) -> int:
    """Lookahead: how many commits the best recursive bridging from `oldest`
    ultimately reaches — the pick between same-score candidates (e.g. the
    user's zoom_w1 vs Potential-Advisors twins at f75d8f8) must go to the one
    whose chain digs deepest, matching or beating GitHub's."""
    if hops <= 0:
        return 0
    best = 0
    for cand in _bridge_candidates(
            oldest["path"], _vanished_sources(repo, oldest["hash"]))[:3]:
        chain = _follow_before(repo, oldest["hash"], cand, seen)
        if not chain:
            continue
        d = len(chain) + _bridge_depth(
            repo, chain[-1], seen | {c["hash"] for c in chain}, hops - 1)
        best = max(best, d)
    return best


def extend_history(repo: Path, commits: list) -> list:
    """--follow can still dead-end on a rename whose commit also heavily
    edited the file (similarity < threshold). Keep digging: from the OLDEST
    known commit, re-run --follow on that commit's PATH strictly before it,
    and append whatever appears. Capped; dedup by hash.
    Final fallback per hop = the STRUCTURAL BRIDGE (user 202607090137 §336):
    when the oldest commit plain-ADDED the file (nothing content-based can
    ever dig deeper), hop to the best-matching path that VANISHED in that
    same commit — exactly what GitHub's history view does silently. The hop
    is content-unrelated by construction, so the first bridged commit is
    MARKED (c["bridge"]) and rendered behind a warning divider: this script
    then always shows at least what GitHub shows, minus the pretence."""
    seen = {c["hash"] for c in commits}
    for _ in range(10):
        oldest = commits[-1]
        try:
            out = git(repo, "log", "--follow", "-M20%", "--name-only",
                      "--format=@@@%H%x09%ad%x09%s",
                      "--date=format:%Y-%m-%d %H:%M",
                      f"{oldest['hash']}^", "--", oldest["path"])
        except RuntimeError:
            break
        extra, cur = [], None
        for line in out.splitlines():
            if line.startswith("@@@"):
                h, ad, sub = (line[3:].split("\t", 2) + ["", ""])[:3]
                cur = {"hash": h, "date": ad, "subject": sub,
                       "path": oldest["path"]}
                if h not in seen:
                    extra.append(cur)
                    seen.add(h)
                else:
                    cur = None
            elif line.strip() and cur is not None:
                cur["path"] = line.strip()
        if not extra:
            # non-atomic rename (the file was plain-ADDED under this name —
            # the user's _00/_[TS] suffix conventions): dig by basename core
            core = re.sub(r"(_\d{1,12})+$", "", Path(oldest["path"]).stem)
            try:
                out2 = git(repo, "log", "--name-only",
                           "--format=@@@%H%x09%ad%x09%s",
                           "--date=format:%Y-%m-%d %H:%M",
                           f"{oldest['hash']}^", "--", f"*{core}*")
            except RuntimeError:
                break
            cur = None
            for line in out2.splitlines():
                if line.startswith("@@@"):
                    h, ad, sub = (line[3:].split("\t", 2) + ["", ""])[:3]
                    cur = ({"hash": h, "date": ad, "subject": sub, "path": ""}
                           if h not in seen else None)
                elif line.strip() and cur is not None:
                    cand = line.strip()
                    if re.sub(r"(_\d{1,12})+$", "",
                              Path(cand).stem) == core:
                        cur["path"] = cand
                        extra.append(cur)
                        seen.add(cur["hash"])
                        cur = None
            if not extra:
                # structural bridge (GH-parity; see docstring): try the
                # shortlisted vanished paths, keep the DEEPEST-digging one
                best_chain, best_score = [], 0
                for cand in _bridge_candidates(
                        oldest["path"],
                        _vanished_sources(repo, oldest["hash"]))[:3]:
                    chain = _follow_before(repo, oldest["hash"], cand, seen)
                    if not chain:
                        continue
                    score = len(chain) + _bridge_depth(
                        repo, chain[-1],
                        seen | {c["hash"] for c in chain}, hops=4)
                    if score > best_score:
                        best_chain, best_score = chain, score
                if not best_chain:
                    break
                best_chain[0]["bridge"] = (
                    f"{Path(oldest['path']).name} was plain-ADDED in "
                    f"{oldest['hash'][:7]}; rows below continue as "
                    f"{best_chain[0]['path']} — a path that vanished in that "
                    f"same commit (GitHub-style structural guess, "
                    f"content-unrelated)")
                extra = best_chain
                seen |= {c["hash"] for c in extra}
            if not extra:
                break
        commits.extend(extra)
    return commits


def content_at(repo: Path, commit: str, path: str) -> str:
    try:
        return git(repo, "show", f"{commit}:{path}")
    except RuntimeError:
        return ""


_TOKEN = re.compile(r"\n|[ \t]+|[^\s]+")


def word_diff_html(old: str, new: str) -> str:
    """Inline word-level diff: <del> red, <ins> green."""
    a, b = _TOKEN.findall(old), _TOKEN.findall(new)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    out: list[str] = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            out.append(html.escape("".join(a[i1:i2])))
        if op in ("delete", "replace") and i2 > i1:
            seg = html.escape("".join(a[i1:i2]))
            out.append(f"<del>{seg}</del>" if seg.strip() else seg)
        if op in ("insert", "replace") and j2 > j1:
            seg = html.escape("".join(b[j1:j2]))
            out.append(f"<ins>{seg}</ins>" if seg.strip() else seg)
    return "".join(out)


def md_to_html(text: str) -> str:
    """Minimal markdown → HTML for the GH-Preview-style view: headings,
    bold/italic, inline code, fenced code, lists, hr, links, paragraphs."""
    esc = html.escape(text)
    lines = esc.splitlines()
    out: list[str] = []
    in_code = False
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    def inline(s: str) -> str:
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<![*\w])\*([^*]+)\*(?![*\w])", r"<em>\1</em>", s)
        s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
                   r'<a href="\2" target="_blank">\1</a>', s)
        return s

    for ln in lines:
        if ln.strip().startswith("```"):
            close_list()
            out.append("<pre class='mdcode'>" if not in_code else "</pre>")
            in_code = not in_code
            continue
        if in_code:
            out.append(ln)
            continue
        m = re.match(r"(#{1,6})\s+(.*)", ln)
        if m:
            close_list()
            lvl = min(len(m.group(1)) + 1, 6)   # h1 reserved for the page
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            continue
        if re.match(r"\s*([-*+]|\d+\.)\s+", ln):
            if not in_list:
                out.append("<ul>")
                in_list = True
            item = re.sub(r"^\s*([-*+]|\d+\.)\s+", "", ln)
            out.append(f"<li>{inline(item)}</li>")
            continue
        if re.match(r"\s*(-{3,}|\*{3,})\s*$", ln):
            close_list()
            out.append("<hr>")
            continue
        if not ln.strip():
            close_list()
            out.append("")
            continue
        close_list()
        out.append(f"<p>{inline(ln)}</p>")
    close_list()
    if in_code:
        out.append("</pre>")
    return "\n".join(out)


CONTEXT = 3          # lines shown above/below each change in Changes-Only view


def changes_diff_html(old: str, new: str, context: int = CONTEXT) -> str:
    """Diff-hunk word-level view (Changes-Only, Code): only changed lines plus
    `context` lines of surrounding context, grouped into GitHub-style `@@`
    hunks. Context lines are plain; changed blocks keep the inline word diff."""
    a, b = old.splitlines(), new.splitlines()
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    groups = list(sm.get_grouped_opcodes(context))
    if not groups:
        return "<p class='note'>no line-level changes in this commit</p>"
    chunks: list[str] = []
    for group in groups:
        o0, n0 = group[0][1], group[0][3]
        o1, n1 = group[-1][2], group[-1][4]
        chunks.append(
            f"<span class='hunk-hd'>@@ -{o0 + 1},{o1 - o0} "
            f"+{n0 + 1},{n1 - n0} @@</span>\n")
        for tag, i1, i2, j1, j2 in group:
            if tag == "equal":
                for line in a[i1:i2]:
                    chunks.append(html.escape(line) + "\n")
            else:
                chunks.append(word_diff_html("\n".join(a[i1:i2]),
                                             "\n".join(b[j1:j2])))
                chunks.append("\n")
    return "".join(chunks)


def changes_md_html(old: str, new: str, context: int = CONTEXT) -> str:
    """Changes-Only, HTML: the markdown preview of ONLY the new-side changed
    lines plus `context` context lines (the same hunks as changes_diff_html),
    not the whole file. Hunks are separated by a blank line."""
    a, b = old.splitlines(), new.splitlines()
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    groups = list(sm.get_grouped_opcodes(context))
    if not groups:
        return "<p class='note'>no line-level changes in this commit</p>"
    blocks: list[str] = []
    for group in groups:
        lines: list[str] = []
        for _tag, _i1, _i2, j1, j2 in group:
            lines.extend(b[j1:j2])          # new-side lines (context + adds)
        blocks.append("\n".join(lines))
    return md_to_html("\n\n".join(blocks))


CSS = """
:root{--bg:#f6f8fa;--card:#fff;--fg:#1f2328;--muted:#57606a;--line:#d0d7de;
      --chip:#ddf4ff;--chipfg:#0969da;--hd:#24292f;--hdfg:#fff;--hdmut:#c9d1d9;
      --insbg:#dafbe1;--insfg:#116329;--delbg:#ffebe9;--delfg:#82071e;
      --hover:#f3f4f6}
body.dark{--bg:#0d1117;--card:#161b22;--fg:#e6edf3;--muted:#8d96a0;
      --line:#30363d;--chip:#121d2f;--chipfg:#58a6ff;--hd:#010409;
      --hdfg:#e6edf3;--hdmut:#8d96a0;--insbg:#12261e;--insfg:#3fb950;
      --delbg:#25171c;--delfg:#f85149;--hover:#1c2129}
*{font-family:Avenir,'Avenir Next',-apple-system,sans-serif}
body{font-size:15px;line-height:1.55;margin:0;background:var(--bg);
     color:var(--fg)}
header{background:var(--hd);color:var(--hdfg);padding:12px 22px;display:flex;
       align-items:flex-start;gap:14px}
header .grow{flex:1;min-width:0}
header h1{font-size:17px;margin:0}
header .sub{color:var(--hdmut);font-size:12px;margin-top:3px}
header .sub a{color:var(--hdmut);text-decoration:underline;cursor:pointer}
.btn{background:transparent;border:1px solid var(--hdmut);color:var(--hdfg);
     border-radius:6px;font-size:12px;padding:4px 10px;cursor:pointer;
     white-space:nowrap;margin-top:2px}
.btn:hover{border-color:var(--hdfg)}
main{max-width:980px;margin:18px auto;padding:0 14px}
.commit{background:var(--card);border:1px solid var(--line);border-radius:8px;
        margin-bottom:14px;overflow:hidden}
.commit summary{cursor:pointer;padding:10px 14px;display:flex;gap:10px;
        align-items:baseline;flex-wrap:wrap;list-style:none}
.commit summary::-webkit-details-marker{display:none}
.commit summary:hover{background:var(--hover)}
.hash{font-family:ui-monospace,Menlo,monospace;font-size:12px;
      color:var(--chipfg);background:var(--chip);border-radius:4px;
      padding:1px 6px;cursor:pointer}
.hash:hover{outline:1px solid var(--chipfg)}
.subj{font-weight:600}
.meta{color:var(--muted);font-size:12.5px;margin-left:auto;white-space:nowrap}
.rename{font-size:12px;color:#9a6700;background:#fff8c5;border-radius:4px;
        padding:1px 6px}
body.dark .rename{background:#2b2300;color:#e3b341}
.bridge{border:1px dashed #9a6700;color:#9a6700;background:#fff8c5;
        border-radius:8px;padding:8px 14px;margin-bottom:14px;font-size:12.5px}
body.dark .bridge{background:#2b2300;color:#e3b341;border-color:#e3b341}
.body{border-top:1px solid var(--line);padding:12px 16px;background:var(--card)}
pre.diff{white-space:pre-wrap;word-wrap:break-word;margin:0;
         font-family:ui-monospace,Menlo,monospace;font-size:12.8px}
pre.mdcode{white-space:pre-wrap;background:var(--bg);border-radius:6px;
           padding:8px 10px;font-family:ui-monospace,Menlo,monospace;
           font-size:12.8px}
del{background:var(--delbg);color:var(--delfg);text-decoration:line-through}
ins{background:var(--insbg);color:var(--insfg);text-decoration:none}
.note{color:var(--muted);font-size:12.5px;margin:0 0 8px}
.view-html .code-view{display:none}
body:not(.view-html) .html-view{display:none}
/* Full Content vs Changes Only: exactly one of the .full-view/.changes-view
   variants shows, orthogonal to the Code/HTML toggle above → all four
   combinations render. Default (no .full-content) = Changes Only. */
body:not(.full-content) .full-view{display:none}
body.full-content .changes-view{display:none}
/* Show Less (default, no .show-all) hides commits + bridge dividers older
   than the file's most recent rename boundary. */
body:not(.show-all) .old-commit{display:none}
body:not(.show-all) .old-bridge{display:none}
.hunk-hd{color:var(--chipfg);font-weight:600}
.html-view h2,.html-view h3{margin:0.7em 0 0.3em}
.html-view code{background:var(--bg);border-radius:4px;padding:0 4px;
                font-family:ui-monospace,Menlo,monospace;font-size:0.9em}
.html-view hr{border:0;border-top:1px solid var(--line)}
footer{color:var(--muted);font-size:12px;text-align:center;padding:26px 0 18px}
#helpbox{display:none;position:fixed;top:64px;right:22px;background:var(--card);
        border:1px solid var(--line);border-radius:8px;padding:12px 16px;
        font-size:13px;box-shadow:0 6px 24px rgba(0,0,0,.25);z-index:9}
#toast{position:fixed;bottom:22px;left:50%;transform:translateX(-50%);
       background:var(--hd);color:var(--hdfg);border-radius:6px;
       padding:6px 14px;font-size:12.5px;display:none;z-index:9}
"""

JS = """
const body = document.body;
const TOTAL = +(body.dataset.total || 0);
if (window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches)
  body.classList.add('dark');
syncBtns();
updateCount();
function syncBtns(){
  document.getElementById('copybtn').textContent =
    window.copyOnly ? 'Copy+GH' : 'Copy Only';
  document.getElementById('darkbtn').textContent =
    body.classList.contains('dark') ? 'Light Mode' : 'Dark Mode';
  document.getElementById('viewbtn').textContent =
    body.classList.contains('view-html') ? 'Code' : 'HTML';
  // buttons name their DESTINATION (dark_mode.html convention)
  document.getElementById('showbtn').textContent =
    body.classList.contains('show-all') ? 'Show Less' : 'Show More';
  document.getElementById('contentbtn').textContent =
    body.classList.contains('full-content') ? 'Changes Only' : 'Full Content';
}
function updateCount(){
  const el = document.getElementById('shown');
  if (!el) return;
  const vis = [].slice.call(document.querySelectorAll('.commit'))
    .filter(c => c.offsetParent !== null).length;
  el.textContent = (vis === TOTAL) ? (TOTAL + ' commits')
    : ('showing ' + vis + ' of ' + TOTAL);
}
function toggleDark(){ body.classList.toggle('dark'); syncBtns(); }
function toggleCopy(){ window.copyOnly = !window.copyOnly; syncBtns(); }
function toggleView(){ body.classList.toggle('view-html'); syncBtns(); }
function toggleShow(){ body.classList.toggle('show-all'); syncBtns(); updateCount(); }
function toggleContent(){ body.classList.toggle('full-content'); syncBtns(); }
function toggleHelp(){ const h = document.getElementById('helpbox');
  h.style.display = h.style.display === 'block' ? 'none' : 'block'; }
function shaClick(ev, sha, url){
  ev.preventDefault(); ev.stopPropagation();
  navigator.clipboard && navigator.clipboard.writeText(sha);
  const t = document.getElementById('toast');
  t.textContent = sha + ' copied'; t.style.display = 'block';
  setTimeout(()=>{ t.style.display='none'; }, 1400);
  if (url && !window.copyOnly) window.open(url, '_blank');
}
"""


def build_page(target: Path) -> Path:
    """Render ONE target file's history to a self-contained .html beside the
    script; returns the output path. Raises RuntimeError on per-file problems
    (not inside a repo / no history) so a multi-file run can skip and continue."""
    repo = repo_root(target)
    rel = str(target.resolve().relative_to(repo))
    gh = github_base(repo)
    commits = history(repo, rel)
    if not commits:
        raise RuntimeError(f"no git history for {rel}")
    commits = extend_history(repo, commits)
    n = len(commits)
    texts: list[str] = []
    for c in reversed(commits):                  # oldest first
        texts.append(content_at(repo, c["hash"], c["path"]))

    # Show-Less boundary: the newest name change (a detected rename OR a
    # structural bridge). Text-independent, so pre-scanned here; commits at or
    # newer than it stay visible by default, older ones become .old-commit.
    boundary = None
    for idx in range(n):
        older = commits[idx + 1] if idx + 1 < n else None
        cross = older is not None and bool(older.get("bridge"))
        renamed = (older is not None and not cross
                   and older["path"] != commits[idx]["path"])
        if renamed or cross:
            boundary = idx
            break

    cards: list[str] = []
    for idx, c in enumerate(commits):            # newest first
        new_i = n - 1 - idx
        new_text = texts[new_i]
        older = commits[idx + 1] if new_i > 0 else None
        # across a structural bridge the "previous" content is a DIFFERENT
        # file's — a word-diff there is meaningless, so treat as created
        cross = older is not None and bool(older.get("bridge"))
        old_text = "" if (new_i == 0 or cross) else texts[new_i - 1]
        renamed = (older is not None and not cross
                   and older["path"] != c["path"])
        is_old = boundary is not None and idx > boundary
        if len(old_text) + len(new_text) > MAX_RENDER_CHARS:
            body = ("<p class='note'>diff too large to render word-by-word "
                    f"({len(new_text)} chars).</p>")
        else:
            label = ("file created in this commit" if new_i == 0 else
                     "file ADDED here — older rows continue via the "
                     "structural bridge below" if cross else
                     f"vs previous commit ({older['hash'][:7]})")
            body = (f"<p class='note'>{html.escape(label)}"
                    + (f" · renamed from <code>{html.escape(older['path'])}</code>"
                       if renamed else "")
                    + "</p>"
                    # four variants; CSS shows exactly one per Code/HTML ×
                    # Full/Changes toggle state
                    + "<div class='code-view full-view'><pre class='diff'>"
                    + word_diff_html(old_text, new_text) + "</pre></div>"
                    + "<div class='code-view changes-view'><pre class='diff'>"
                    + changes_diff_html(old_text, new_text) + "</pre></div>"
                    + "<div class='html-view full-view'>"
                    + md_to_html(new_text) + "</div>"
                    + "<div class='html-view changes-view'>"
                    + changes_md_html(old_text, new_text) + "</div>")
        url = f"{gh}/commit/{c['hash']}" if gh else ""
        open_attr = " open" if idx == 0 else ""
        if c.get("bridge"):
            cards.append("<div class='bridge"
                         + (" old-bridge" if is_old else "")
                         + "'>⚠️ Structural Bridge: "
                         f"{html.escape(c['bridge'])}</div>")
        cards.append(
            "<details class='commit"
            + (" old-commit" if is_old else "")
            + f"'{open_attr}><summary>"
            f"<span class='hash' title='copy SHA + open on GitHub' "
            f"onclick=\"shaClick(event,'{c['hash'][:7]}','{url}')\">"
            f"{c['hash'][:7]}</span>"
            f"<span class='subj'>{html.escape(c['subject'])}</span>"
            + ("<span class='rename'>renamed</span>" if renamed else "")
            + f"<span class='meta'>{html.escape(c['date'])}</span>"
            f"</summary><div class='body'>{body}</div></details>")
    ts = datetime.now().strftime("%Y%m%d%H%M")
    out = SCRIPT_DIR / f"git_history_{target.stem}_{ts}.html"
    out.write_text(
        "<!doctype html><meta charset='utf-8'>"
        f"<title>Git History — {html.escape(target.name)}</title>"
        f"<style>{CSS}</style><body data-total='{n}'>"
        "<header><div class='grow'>"
        f"<h1>Git History ({n}): {html.escape(target.name)}</h1>"
        f"<div class='sub'>{html.escape(rel)}</div>"
        f"<div class='sub'>Generated {ts} · <span id='shown'></span> · "
        "<a onclick='toggleHelp()'>Help</a></div>"
        "</div>"
        "<button class='btn' id='showbtn' onclick='toggleShow()'>Show More</button>"
        "<button class='btn' id='contentbtn' onclick='toggleContent()'>Full Content</button>"
        "<button class='btn' id='viewbtn' onclick='toggleView()'>HTML</button>"
        "<button class='btn' id='copybtn' onclick='toggleCopy()'>Copy Only</button>"
        "<button class='btn' id='darkbtn' onclick='toggleDark()'>Dark Mode</button>"
        "</header>"
        "<div id='helpbox'>- Newest first<br>- Click commit bar to expand or collapse<br>"
        "- Click SHA chip to copy it & open the commit on GitHub<br>"
        "- Show More / Show Less: Show Less (default) lists only commits since "
        "the file's last rename; Show More lists every commit<br>"
        "- Full Content / Changes Only: Changes Only (default) shows changed "
        "lines + 3 context lines as @@ hunks; Full Content shows the whole file<br>"
        "- HTML View: the file as rendered rich text after that commit<br>"
        "- Code View: word-level diff vs the previous commit<br>"
        "- ⚠️ Structural Bridge: rows below it are GitHub-style guesses "
        "(a same-commit vanished path), NOT verified content lineage<br>"
        "- Dark Mode follows macOS setting by default</div>"
        "<div id='toast'></div>"
        "<main>" + "".join(cards) + "</main>"
        "<footer>Confidential Intellectual Property of Culous Yu</footer>"
        f"<script>{JS}</script></body>",
        encoding="utf-8")
    return out


def main() -> None:
    targets = read_targets()
    produced = 0
    for target in targets:
        if not target.exists():
            print(f"git_history: skip (not found): {target}", file=sys.stderr)
            continue
        try:
            out = build_page(target)
        except RuntimeError as e:
            print(f"git_history: {target}: {e}", file=sys.stderr)
            continue
        produced += 1
        print(f"wrote {out}")
    if produced == 0:
        die("no output produced (see messages above)")


if __name__ == "__main__":
    main()
