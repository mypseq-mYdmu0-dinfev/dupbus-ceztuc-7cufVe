"""
Batch Git-Move Generator (2-stage)

Moves a large number of files/folders from one or more source locations into
a SINGLE destination folder, via generated + reviewed `git mv` commands. No
renaming (destination keeps each file's original basename). If a source is a
FOLDER, its CONTENTS (all files, any depth) are moved individually into the
destination, flattened --- subfolder structure is NOT preserved, and the now-
empty source subfolders are left behind untouched (never auto-deleted; Void
Rule applies to the user, not to folders left empty by a move).

USAGE
-----
Run:  python3 nscpt/git_move_batch.py
This script always looks for `nscpt/gmb_*.md` first and picks ONE of two
stages based on what it finds:

STAGE 1 --- no `nscpt/gmb_*.md` exists yet:
  Writes `nscpt/gmb_[current_TS].md`, an empty fill-in-the-blank template:

    # Batch Moving [current_TS]

    ## From


    ## To

  Edit it: under `## From`, one line per file/folder to move (quotes
  optional). Under `## To`, EXACTLY one line = the single destination folder
  (must already exist). Example:

    # Batch Moving 202607080639

    ## From
    '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/temp/temp_misc'

    ## To
    '/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/nscpt'

  (If `temp_misc/` contains a subfolder `cd_teset/` holding `test-100.html`,
  that file alone moves to `nscpt/test-100.html` --- the empty `cd_teset/`
  stays behind.)

STAGE 2 --- one `nscpt/gmb_*.md` exists:
  Validates it (see ERRORS below), then writes `nscpt/gmb_[match_TS].sh`
  (`[match_TS]` = the `.md`'s own TS) containing one `git mv` per file, a
  clean-tree guard, and a commit --- same pattern as `nscpt/git_move_rename.sh`.
  Prints the `.sh` filename and asks you to review it, then type `yes` at
  the prompt to run it immediately.
  - On success: notifies you, then VOIDS both the `.md` and the `.sh`
    (renamed `❌_...`, per Void Rule --- delete them yourself once you've
    checked the repo).
  - On failure (e.g. uncommitted changes, a source path no longer exists):
    prints the error; both files are left as-is so you can fix and rerun.

ERRORS (stage 2 refuses to write the `.sh` and just prints the problem)
  - More than one `nscpt/gmb_*.md` found.
  - `## To` has 0 lines, or more than 1 line.
  - The `## To` line isn't an existing path, or isn't a folder.
  - Any `## From` line isn't an existing file/folder.
  - `## From` has 0 usable lines.
"""

import os
import sys
import glob
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)

TEMPLATE = """# Batch Moving {ts}

## From


## To

"""


def sydney_ts():
    out = subprocess.run(
        ["date", "+%Y%m%d%H%M"],
        env={**os.environ, "TZ": "Australia/Sydney"},
        capture_output=True, text=True, check=True,
    )
    return out.stdout.strip()


def strip_quotes(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        s = s[1:-1]
    return s.strip()


def stage1():
    ts = sydney_ts()
    path = os.path.join(HERE, f"gmb_{ts}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(TEMPLATE.format(ts=ts))
    print(f"Template created: nscpt/gmb_{ts}.md --- fill it in, then rerun this script.")


def parse_gmb(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    m = re.search(r"##\s*From\s*\n(.*?)\n##\s*To\s*\n(.*)", text, re.S)
    if not m:
        return None, None, "Couldn't find '## From' / '## To' sections."

    from_lines = [strip_quotes(l) for l in m.group(1).splitlines() if l.strip()]
    to_lines = [strip_quotes(l) for l in m.group(2).splitlines() if l.strip()]
    return from_lines, to_lines, None


def validate(from_lines, to_lines):
    if not from_lines:
        return "No entries under '## From'."
    if len(to_lines) == 0:
        return "No destination under '## To'."
    if len(to_lines) > 1:
        return "'## To' has more than 1 line --- exactly 1 destination folder required."
    dest = to_lines[0]
    if not os.path.exists(dest):
        return f"'## To' path doesn't exist: {dest}"
    if not os.path.isdir(dest):
        return f"'## To' path is a file, not a folder: {dest}"
    for src in from_lines:
        if not os.path.exists(src):
            return f"'## From' path doesn't exist: {src}"
    return None


def collect_files(from_lines):
    """Flatten: folders contribute every file found inside (any depth)."""
    files = []
    for src in from_lines:
        if os.path.isfile(src):
            files.append(src)
        else:
            for root, _dirs, names in os.walk(src):
                for name in names:
                    files.append(os.path.join(root, name))
    return files


def write_sh(sh_path, files, dest):
    lines = [
        f"cd '{REPO_ROOT}'",
        "",
        'git diff --quiet && git diff --cached --quiet || '
        '{ echo "Uncommitted changes detected. Commit or stash them first."; exit 1; }',
        "",
        "set -e",
    ]
    for f in files:
        basename = os.path.basename(f)
        lines.append(f"git mv '{f}' '{os.path.join(dest, basename)}'")
    lines.append("")
    lines.append(f'git commit -m "Batch move: {len(files)} file(s) into {dest}"')
    with open(sh_path, "w", encoding="utf-8") as out:
        out.write("\n".join(lines) + "\n")


def void(path):
    d, b = os.path.split(path)
    os.rename(path, os.path.join(d, f"❌_{b}"))


def stage2(md_path):
    ts_match = re.search(r"gmb_(\d{12})\.md$", os.path.basename(md_path))
    match_ts = ts_match.group(1) if ts_match else "unknown"

    from_lines, to_lines, err = parse_gmb(md_path)
    if err:
        print(f"ERROR: {err}")
        return
    err = validate(from_lines, to_lines)
    if err:
        print(f"ERROR: {err}")
        return

    dest = to_lines[0]
    files = collect_files(from_lines)
    if not files:
        print("ERROR: no actual files found under '## From' entries.")
        return

    sh_path = os.path.join(HERE, f"gmb_{match_ts}.sh")
    write_sh(sh_path, files, dest)
    print(f"Created: nscpt/gmb_{match_ts}.sh --- {len(files)} file(s) to move into {dest}")
    print("Review it, then type 'yes' to run it now (anything else cancels):")

    answer = input().strip().lower()
    if answer != "yes":
        print("Cancelled --- .md and .sh left in place.")
        return

    result = subprocess.run(["bash", sh_path], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Success --- {len(files)} file(s) moved and committed.")
        void(md_path)
        void(sh_path)
    else:
        print("FAILED:")
        print(result.stdout)
        print(result.stderr)


def main():
    candidates = glob.glob(os.path.join(HERE, "gmb_*.md"))
    if len(candidates) > 1:
        print(f"ERROR: multiple nscpt/gmb_*.md found --- resolve to exactly 1: {candidates}")
        return
    if len(candidates) == 1:
        stage2(candidates[0])
    else:
        stage1()


if __name__ == "__main__":
    main()
