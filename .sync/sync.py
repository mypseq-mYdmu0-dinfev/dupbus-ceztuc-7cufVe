#!/usr/bin/env python3
# #sync — refresh OTG SHA-permalinks. See universal/sync.md. Rewrites a scope's index so every file URL is pinned to that file's last-commit SHA (immutable -> never served stale by CWI/CDN caches), then pins the index's own permalink inside the prefs file. Commits + pushes ONLY those two control files; content files must already be committed+pushed (else it aborts untouched). Reads the content of ONLY the 2 control files — every listed file uses git metadata only, never opened.
import sys, subprocess, os, re, platform

# Cloud CC (Linux) can't push to main -> push to one fixed branch; SHA permalinks
# resolve from any branch, so the printed URL still works OTG. Local (Darwin) -> main.
IS_CLOUD = platform.system() == "Linux"
CLOUD_BRANCH = "otg-sync"

OWNER = "mypseq-mYdmu0-dinfev"
REPO = "dupbus-ceztuc-7cufVe"
PREFIX = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/"
# match a raw URL ANYWHERE in a line (handles bare URLs and "Label: <url>" forms)
URL_RE = re.compile(re.escape(PREFIX) + r"([0-9a-fA-F]{7,40}|main)/(\S+)")

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                      capture_output=True, text=True).stdout.strip()


def git_out(*a):
    r = subprocess.run(["git", *a], capture_output=True, text=True, cwd=ROOT)
    if r.returncode:
        sys.exit(f"git {' '.join(a)} failed:\n{r.stderr}")
    return r.stdout.strip()


def resolve_scope(scope):
    if scope == "universal":
        return "universal/index_otg.md", "universal/preferences.md"
    return f"{scope}/CP_index_otg.md", f"{scope}/CP_instr.md"


def sha_of(path):
    s = git_out("log", "-1", "--format=%H", "--", path)
    if not s:
        sys.exit(f"ABORT: '{path}' (referenced in the index) is not committed to git. "
                 f"Commit & push it first, then re-run. Nothing was changed.")
    return s


def main():
    scope = sys.argv[1] if len(sys.argv) > 1 else "universal"
    index_rel, prefs_rel = resolve_scope(scope)
    index_path = os.path.join(ROOT, index_rel)
    prefs_path = os.path.join(ROOT, prefs_rel)
    if not os.path.exists(index_path):
        sys.exit(f"no index for scope '{scope}': {index_rel} not found")

    # Cloud clones are often SHALLOW -> per-file `git log` collapses to the shallow-boundary
    # commit, breaking idempotency & true per-file SHAs. Unshallow first (cloud only, best-effort).
    if IS_CLOUD and subprocess.run(["git", "rev-parse", "--is-shallow-repository"],
                                   capture_output=True, text=True, cwd=ROOT).stdout.strip() == "true":
        subprocess.run(["git", "fetch", "--unshallow"], cwd=ROOT)

    # ---- pin every referenced file (anywhere in the index) to its last-commit SHA ----
    text = open(index_path).read()
    paths = sorted({p for _ref, p in URL_RE.findall(text)})
    # Nothing #sync touches may carry pending USER edits: the index, the prefs, and every
    # listed file must already be committed+pushed, so your edits land in their own commits,
    # kept separate from #sync's pin commits. Otherwise abort, untouched.
    for p in [index_rel, prefs_rel] + paths:
        if git_out("status", "--porcelain", "--", p):
            sys.exit(f"ABORT: '{p}' has uncommitted changes. Commit & push it (GH Desktop) "
                     f"first, then re-run #sync. Nothing was changed.")
    shamap = {p: sha_of(p) for p in paths}
    changed = []

    def repl(m):
        ref, p = m.group(1), m.group(2)
        if ref != shamap[p]:
            changed.append(p)
        return f"{PREFIX}{shamap[p]}/{p}"

    newtext = URL_RE.sub(repl, text)
    if newtext != text:
        open(index_path, "w").write(newtext)
        print("Updated URLs:", ", ".join(sorted(set(changed))))
    else:
        print("No file URLs changed.")

    # ---- guarded commit: ONLY this scope's 2 control files ----
    marker = os.path.join(ROOT, ".git", "SYNC_ACTIVE")
    open(marker, "w").write(index_rel + "\n" + prefs_rel + "\n")
    pushed = False
    try:
        if newtext != text:
            git_out("add", index_rel)
            git_out("commit", "-m", f"#sync {scope}: refresh file SHA-permalinks")

        index_sha = sha_of(index_rel)
        index_url = f"{PREFIX}{index_sha}/{index_rel}"
        ptext = open(prefs_path).read()
        # the prefs file is expected to reference the index by its path
        if index_rel not in ptext:
            print(f"WARNING: {prefs_rel} does not reference {index_rel} — its entry URL "
                  f"was NOT updated. Fix the prefs to point at {index_rel}, then re-run.")
            ptext2 = ptext
        else:
            ptext2 = re.sub(re.escape(PREFIX) + r"(?:[0-9a-fA-F]{7,40}|main)/" + re.escape(index_rel),
                            index_url, ptext)
            if ptext2 != ptext:
                open(prefs_path, "w").write(ptext2)
                git_out("add", prefs_rel)
                git_out("commit", "-m", f"#sync {scope}: pin index permalink")

        if newtext != text or ptext2 != ptext:
            if IS_CLOUD:
                git_out("push", "--force", "origin", f"HEAD:{CLOUD_BRANCH}")
            else:
                git_out("push", "origin", "HEAD:main")
            pushed = True
    finally:
        os.remove(marker)

    if pushed:
        target = f"branch '{CLOUD_BRANCH}' (cloud)" if IS_CLOUD else "main"
        print(f"Pushed to {target}.")
        print("=== index URL for userPref ===")
        print(index_url)
    else:
        print(f"NO CHANGE: '{scope}' URLs unchanged —— do NOT report a URL for this scope.")


if __name__ == "__main__":
    main()
