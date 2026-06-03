#!/usr/bin/env python3
# #sync — refresh OTG SHA-permalinks. See universal/sync.md. Rewrites a scope's index so every file URL is pinned to that file's last-commit SHA (immutable -> never served stale by CWI/CDN caches), then pins the index's own permalink inside the prefs file. Commits + pushes ONLY those two control files; content files must already be committed+pushed (else it aborts untouched).
import sys, subprocess, os, re

OWNER = "mypseq-mYdmu0-dinfev"
REPO = "dupbus-ceztuc-7cufVe"
PREFIX = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/"

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                      capture_output=True, text=True).stdout.strip()


def git_out(*a):
    r = subprocess.run(["git", *a], capture_output=True, text=True, cwd=ROOT)
    if r.returncode:
        sys.exit(f"git {' '.join(a)} failed:\n{r.stderr}")
    return r.stdout.strip()


def resolve_scope(scope):
    # universal uses index_otg.md + preferences.md; every CP uses CP_index_otg.md + CP_instr.md
    if scope == "universal":
        return "universal/index_otg.md", "universal/preferences.md"
    return f"{scope}/CP_index_otg.md", f"{scope}/CP_instr.md"


def parse_url(url):
    if not url.startswith(PREFIX):
        return None, None
    ref, _, path = url[len(PREFIX):].partition("/")
    return ref, path


def main():
    scope = sys.argv[1] if len(sys.argv) > 1 else "universal"
    index_rel, prefs_rel = resolve_scope(scope)
    index_path = os.path.join(ROOT, index_rel)
    prefs_path = os.path.join(ROOT, prefs_rel)
    if not os.path.exists(index_path):
        sys.exit(f"no index for scope '{scope}': {index_rel} not found")

    # Pin each file (paths come from the index itself, so CP indexes may list
    # files outside the CP folder, e.g. seek/context/*) to its last-commit SHA.
    out, changed = [], []
    for ln in open(index_path).read().splitlines():
        ref, path = parse_url(ln.strip())
        if path is None:
            out.append(ln)
            continue
        if git_out("status", "--porcelain", "--", path):
            sys.exit(f"ABORT: '{path}' has uncommitted changes.\n"
                     f"Commit & push it (GH Desktop) first, then re-run #sync. "
                     f"Nothing was changed.")
        new = f"{PREFIX}{git_out('log', '-1', '--format=%H', '--', path)}/{path}"
        if new != ln.strip():
            changed.append(path)
        out.append(new)

    if changed:
        open(index_path, "w").write("\n".join(out) + "\n")
        print("Updated URLs:", ", ".join(changed))
    else:
        print("No file URLs changed.")

    # ---- guarded commit: ONLY this scope's 2 control files ----
    marker = os.path.join(ROOT, ".git", "SYNC_ACTIVE")
    open(marker, "w").write(index_rel + "\n" + prefs_rel + "\n")
    try:
        if changed:
            git_out("add", index_rel)
            git_out("commit", "-m", f"#sync {scope}: refresh file SHA-permalinks")

        index_url = f"{PREFIX}{git_out('log', '-1', '--format=%H', '--', index_rel)}/{index_rel}"
        ptext = open(prefs_path).read()
        ptext2 = re.sub(re.escape(PREFIX) + r"[^/\s]+/" + re.escape(index_rel),
                        index_url, ptext)
        if ptext2 != ptext:
            open(prefs_path, "w").write(ptext2)
            git_out("add", prefs_rel)
            git_out("commit", "-m", f"#sync {scope}: pin index permalink")

        if changed or ptext2 != ptext:
            git_out("push", "origin", "HEAD:main")
            print("Pushed.")
        else:
            print("Nothing to push.")
    finally:
        os.remove(marker)

    print("\n=== index URL for userPref ===")
    print(index_url)
    print("\n=== full prefs (paste whole thing if you prefer) ===")
    print(open(prefs_path).read())


if __name__ == "__main__":
    main()
