#!/usr/bin/env python3
"""#sync — refresh OTG SHA-permalinks. See universal/sync.md.

Rewrites a scope's index_otg.md so every file URL is pinned to THAT file's
last-commit SHA (immutable -> never served stale by CWI/CDN caches), then pins
index_otg.md's own permalink inside preferences.md.

Option B: content files are committed+pushed by the USER beforehand. This script
commits+pushes ONLY the scope's index_otg.md + preferences.md.
"""
import sys, subprocess, os, re

OWNER = "mypseq-mYdmu0-dinfev"
REPO = "dupbus-ceztuc-7cufVe"
PREFIX = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/"

# Each scope -> its control files. Add CPs here as needed.
SCOPES = {
    "universal": {"index": "universal/index_otg.md", "prefs": "universal/preferences.md"},
    # "career": {"index": "career/index_otg.md", "prefs": "career/preferences.md"},
}

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                      capture_output=True, text=True).stdout.strip()


def git_out(*a):
    r = subprocess.run(["git", *a], capture_output=True, text=True, cwd=ROOT)
    if r.returncode:
        sys.exit(f"git {' '.join(a)} failed:\n{r.stderr}")
    return r.stdout.strip()


def parse_url(url):
    if not url.startswith(PREFIX):
        return None, None
    ref, _, path = url[len(PREFIX):].partition("/")
    return ref, path


def main():
    scope = sys.argv[1] if len(sys.argv) > 1 else "universal"
    if scope not in SCOPES:
        sys.exit(f"unknown scope '{scope}' (known: {', '.join(SCOPES)})")
    cfg = SCOPES[scope]
    index_path = os.path.join(ROOT, cfg["index"])
    prefs_path = os.path.join(ROOT, cfg["prefs"])

    out, changed = [], []
    for ln in open(index_path).read().splitlines():
        ref, path = parse_url(ln.strip())
        if path is None:
            out.append(ln)
            continue
        if git_out("status", "--porcelain", "--", path):
            sys.exit(f"ABORT: '{path}' has uncommitted changes.\n"
                     f"Commit & push it (GH Desktop) first, then re-run #sync.")
        new = f"{PREFIX}{git_out('log', '-1', '--format=%H', '--', path)}/{path}"
        if new != ln.strip():
            changed.append(path)
        out.append(new)

    if changed:
        open(index_path, "w").write("\n".join(out) + "\n")
        print("Updated URLs:", ", ".join(changed))
    else:
        print("No file URLs changed.")

    # ---- guarded commit: ONLY the 2 control files ----
    marker = os.path.join(ROOT, ".git", "SYNC_ACTIVE")
    open(marker, "w").write(cfg["index"] + "\n" + cfg["prefs"] + "\n")
    try:
        if changed:
            git_out("add", cfg["index"])
            git_out("commit", "-m", f"#sync {scope}: refresh file SHA-permalinks")

        index_url = f"{PREFIX}{git_out('log', '-1', '--format=%H', '--', cfg['index'])}/{cfg['index']}"
        ptext = open(prefs_path).read()
        ptext2 = re.sub(re.escape(PREFIX) + r"[^/\s]+/" + re.escape(cfg["index"]),
                        index_url, ptext)
        if ptext2 != ptext:
            open(prefs_path, "w").write(ptext2)
            git_out("add", cfg["prefs"])
            git_out("commit", "-m", f"#sync {scope}: pin index permalink in preferences")

        if changed or ptext2 != ptext:
            git_out("push", "origin", "HEAD:main")
            print("Pushed.")
        else:
            print("Nothing to push.")
    finally:
        os.remove(marker)

    print("\n=== paste into userPref ===")
    print(open(prefs_path).read())


if __name__ == "__main__":
    main()
