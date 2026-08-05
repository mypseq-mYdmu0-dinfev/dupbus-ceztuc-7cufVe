#!/usr/bin/env python3
"""Regression test —— `gscpt/DAMF.py` + `gscpt/DXMF.py` take an ABSOLUTE path
(file or folder) on Line 1, and never search for anything.

WHY THIS EXISTS (self-contained; no conversation or comms file explains it):

Both scripts rewrite macOS Finder date metadata —— DAMF sets "Date Added",
DXMF sets all four dates. There is no undo, and the damage is invisible: the
file's CONTENT is fine, only the dates the user sorts and searches by are
wrong, and he will not notice until a folder sorts oddly weeks later. Every
invariant below is therefore about never touching the wrong item.

WHAT CHANGED, AND WHY EACH FAILURE MODE IS PINNED HERE:

1. Line 1 was a BARE FILENAME that the script hunted for across the repo,
   proceeding whenever exactly one match came back. "Exactly one match" is not
   the same as "the file he meant" —— a single match in the wrong folder was
   stamped silently. Line 1 is now an absolute path and NOTHING is searched.

2. A RELATIVE Line 1 used to resolve against the process cwd (the old code
   tried `REPO_ROOT / v` and then `Path(v)`), so the identical instruction file
   hit different targets depending on which directory the script was run from.
   Relative paths are now refused outright, and the tests below run the scripts
   from a directory that is NOT the repo to keep that honest.

3. A FOLDER on Line 1 is stamped RECURSIVELY and INCLUSIVELY —— the folder
   itself plus every descendant —— because a shallow stamp would move the
   folder's own Finder row whilst leaving its contents sorting elsewhere, which
   is the inconsistency the tools exist to remove. Order is deepest-first:
   writing into a directory bumps that directory's own Date Modified, so a
   parent written before its children would have its stamp silently undone.
   test_folder_is_recursive_and_parent_survives_children pins exactly that.

4. SYMLINKS are stamped but never followed or descended into. A followed
   symlink is how a scrub of one folder reaches files outside it —— venv
   symlinks pointing at system binaries are the live example. The traversal
   uses os.walk(followlinks=False) rather than rglob because rglob's
   symlink-recursion behaviour differs between Python versions; the tests here
   check the behaviour, not the implementation.

5. A SAFETY FENCE (ALLOWED_ROOTS) once confined targets to the GitHub/ folder
   holding every repo. It was REMOVED: most real runs are on files OUTSIDE the
   repos (re-dating a deliverable), so the fence refused the common case ——
   a regression, not a safeguard. test_outside_any_repo_is_stamped pins the
   case he actually uses, and it is the one test whose failure means the tools
   are useless to him rather than merely unsafe.

6. WHAT REPLACES THE FENCE restricts nothing by location, only by SHAPE: a
   mount point (`/` and every volume root), `/Users`, `/Volumes`, or the home
   folder itself is refused, on either the path or its symlink target. Those
   are what a copied path trimmed one component too far lands on, and each
   would rewrite hundreds of thousands of items with no undo. System paths
   (`/usr`, `/System`) are deliberately absent —— unreachable by truncating a
   Finder "Copy as Pathname" value —— so a test asserting they are refused
   would be pinning protection that does not, and should not, exist.

EVERY CASE RUNS ON TEMP FIXTURES. These scripts mutate real file metadata, so a
test that pointed at a repo file would corrupt the very thing it protects.
Nothing here reads, writes, or even names a real repo path except to COPY the
two scripts out of `gscpt/` and to grep them and `gscpt/README.md` for the
documentation contract.

THE THREE CASES THAT MUST NAME A REAL SYSTEM PATH (`/`, `/Users`, `/Volumes`)
cannot be faked —— os.path.ismount has no sandbox equivalent, and a refusal
proven only against a stand-in proves nothing about the real one. They are run
with --dry-run AND a subprocess timeout, so a broken refusal fails the test
(and is killed mid-walk) instead of writing anything: dry-run returns before
the write loop is even reached. The home-folder case needs neither, because
Path.home() follows $HOME and is injected into the sandbox.

RUN:
    cd "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe"
    python3 cp/ccsim/sandbox/gscpt_path_target_regression_test.py

Dependency-free by design (PyYAML is not installed system-wide on this Mac).
macOS-only: the date-reading helpers call getattrlist(2).
"""

import ctypes
import ctypes.util
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
REAL_GSCPT = os.path.join(REPO, "gscpt")
SCRIPTS = ("DAMF.py", "DXMF.py")

TS = "202607091852"                    # 09/07/2026 18:52 Sydney
TS_OTHER = "202501020304"              # a second, clearly different stamp

failures = []
checks = 0


def check(ok, msg):
    global checks
    checks += 1
    if not ok:
        failures.append(msg)
    return ok


# ------------------------------------------------------------- date readers
_libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
ATTR_BIT_MAP_COUNT = 5
ATTR_CMN_ADDEDTIME = 0x10000000
FSOPT_NOFOLLOW = 0x00000001


class _attrlist(ctypes.Structure):
    _fields_ = [("bitmapcount", ctypes.c_ushort), ("reserved", ctypes.c_uint16),
                ("commonattr", ctypes.c_uint32), ("volattr", ctypes.c_uint32),
                ("dirattr", ctypes.c_uint32), ("fileattr", ctypes.c_uint32),
                ("forkattr", ctypes.c_uint32)]


_libc.getattrlist.argtypes = [ctypes.c_char_p, ctypes.c_void_p, ctypes.c_void_p,
                              ctypes.c_size_t, ctypes.c_ulong]


def date_added(path):
    """Finder's catalog 'Date Added' in epoch seconds (NOFOLLOW)."""
    al = _attrlist()
    al.bitmapcount = ATTR_BIT_MAP_COUNT
    al.commonattr = ATTR_CMN_ADDEDTIME
    buf = ctypes.create_string_buffer(64)
    if _libc.getattrlist(str(path).encode(), ctypes.byref(al), buf, len(buf),
                         FSOPT_NOFOLLOW) != 0:
        raise OSError(ctypes.get_errno(), "getattrlist", str(path))
    sec, _nsec = struct.unpack_from("qq", buf, 4)
    return sec


def mtime(path):
    return int(os.lstat(path).st_mtime)


def expected_epoch(ts):
    """The scripts read TS as Sydney local time; ask the same libraries they do
    rather than hard-coding an offset (DST would make that wrong half the year)."""
    from datetime import datetime
    from zoneinfo import ZoneInfo
    return int(datetime(int(ts[0:4]), int(ts[4:6]), int(ts[6:8]), int(ts[8:10]),
                        int(ts[10:12]), tzinfo=ZoneInfo("Australia/Sydney"))
               .timestamp())


EPOCH = expected_epoch(TS)


# ----------------------------------------------------------------- sandbox
def make_sandbox():
    """A throwaway GitHub/-shaped tree holding COPIES of the real scripts.

    Layout (realpath'd so /var -> /private/var can never confuse a comparison):
        <tmp>/GitHub/testrepo/gscpt/{DAMF,DXMF}.py   <- the scripts under test
        <tmp>/GitHub/testrepo/sessions/...           <- inside-a-repo fixtures
        <tmp>/outside/...                            <- outside-any-repo fixtures,
                                                        i.e. his ACTUAL main case
    The repo shape is kept even though no fence reads it: it is what proves the
    scripts treat in-repo and out-of-repo targets identically.
    """
    tmp = os.path.realpath(tempfile.mkdtemp(prefix="gscpt_pathtarget_"))
    github = os.path.join(tmp, "GitHub")
    repo = os.path.join(github, "testrepo")
    gscpt = os.path.join(repo, "gscpt")
    sessions = os.path.join(repo, "sessions")
    outside = os.path.join(tmp, "outside")
    for d in (gscpt, sessions, outside):
        os.makedirs(d, exist_ok=True)
    for name in SCRIPTS:
        shutil.copy2(os.path.join(REAL_GSCPT, name), os.path.join(gscpt, name))
    return {"tmp": tmp, "github": github, "repo": repo, "gscpt": gscpt,
            "sessions": sessions, "outside": outside}


def write_instruction(sb, line1, ts=TS, name="inst.txt", header=None):
    """Drop one instruction file beside the copied scripts, clearing any other."""
    for f in os.listdir(sb["gscpt"]):
        if f.endswith((".txt", ".md")):
            os.remove(os.path.join(sb["gscpt"], f))
    body = ""
    if header:
        body += header + "\n\n"
    body += f"{line1}\n{ts}\n"
    with open(os.path.join(sb["gscpt"], name), "w", encoding="utf-8") as fh:
        fh.write(body)


def run(sb, script, args=(), env_extra=None, timeout=None):
    """Run the copied script from a cwd that is NOT the repo, with stdin piped
    (so it is never a tty —— the confirmation gate must not be able to block).
    `timeout` is used only by the cases that name a real system path: if the
    refusal ever breaks, the run is killed mid-walk instead of grinding."""
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    try:
        return subprocess.run(
            [sys.executable, os.path.join(sb["gscpt"], script), *args],
            capture_output=True, text=True, input="", cwd=sb["tmp"], env=env,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(
            args=script, returncode=124,
            stdout="", stderr=f"TIMED OUT after {timeout}s —— it started "
                              f"walking instead of refusing.",
        )


def touch(path, content="x"):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    return path


def out_of(proc):
    return (proc.stdout or "") + (proc.stderr or "")


# ------------------------------------------------------------------- cases
def test_file_path_is_stamped():
    """The headline case: an absolute FILE path, run from an unrelated cwd."""
    for script in SCRIPTS:
        sb = make_sandbox()
        try:
            target = touch(os.path.join(sb["sessions"], "one.md"))
            before = mtime(target)
            write_instruction(sb, target)
            p = run(sb, script)
            check(p.returncode == 0, f"{script}: file path should succeed —— {out_of(p)}")
            check(date_added(target) == EPOCH,
                  f"{script}: Date Added not set ({date_added(target)} != {EPOCH})")
            if script == "DXMF.py":
                check(mtime(target) == EPOCH,
                      f"{script}: Date Modified not set ({mtime(target)} != {EPOCH})")
                check(int(os.lstat(target).st_birthtime) == EPOCH,
                      f"{script}: Date Created not set")
            else:
                check(mtime(target) == before,
                      "DAMF.py: must not touch Date Modified")
        finally:
            shutil.rmtree(sb["tmp"], ignore_errors=True)


def test_quoted_and_tilde_paths_still_work():
    """The user pastes from Finder's 'Copy as Pathname'; the parked historical
    instruction files show that arriving single-quoted. A leading ~ likewise."""
    for script in SCRIPTS:
        sb = make_sandbox()
        try:
            target = touch(os.path.join(sb["sessions"], "quoted target.md"))
            write_instruction(sb, f"'{target}'")
            p = run(sb, script)
            check(p.returncode == 0, f"{script}: quoted path should succeed —— {out_of(p)}")
            check(date_added(target) == EPOCH, f"{script}: quoted path not stamped")

            tilde = touch(os.path.join(sb["sessions"], "tilde.md"))
            write_instruction(sb, "~/sessions/tilde.md")
            p = run(sb, script, env_extra={"HOME": sb["repo"]})
            check(p.returncode == 0, f"{script}: ~ path should succeed —— {out_of(p)}")
            check(date_added(tilde) == EPOCH, f"{script}: ~ path not stamped")
        finally:
            shutil.rmtree(sb["tmp"], ignore_errors=True)


def test_folder_is_recursive_and_parent_survives_children():
    """A folder means the folder ITSELF plus every descendant, at any depth ——
    and the parent's stamp must survive its children being written."""
    for script in SCRIPTS:
        sb = make_sandbox()
        try:
            folder = os.path.join(sb["sessions"], "2026")
            deep = os.path.join(folder, "202607", "nested")
            os.makedirs(deep)
            top = touch(os.path.join(folder, "top.md"))
            mid = touch(os.path.join(folder, "202607", "mid.md"))
            low = touch(os.path.join(deep, "low.md"))
            write_instruction(sb, folder)
            p = run(sb, script)
            check(p.returncode == 0, f"{script}: folder should succeed —— {out_of(p)}")
            for item in (folder, os.path.join(folder, "202607"), deep, top, mid, low):
                check(date_added(item) == EPOCH,
                      f"{script}: folder member not stamped —— {item}")
            if script == "DXMF.py":
                check(mtime(folder) == EPOCH,
                      "DXMF.py: parent folder's Date Modified was undone by its "
                      "children (deepest-first ordering broken)")
                check(mtime(os.path.join(folder, "202607")) == EPOCH,
                      "DXMF.py: mid-level folder's Date Modified was undone")
        finally:
            shutil.rmtree(sb["tmp"], ignore_errors=True)


def test_bare_filename_is_refused_and_tells_him_what_to_type():
    """The break the user accepted —— but the error has to be actionable, and
    the file a search WOULD have found must be left alone."""
    for script in SCRIPTS:
        sb = make_sandbox()
        try:
            decoy = touch(os.path.join(sb["sessions"], "findme.md"))
            before = date_added(decoy)
            write_instruction(sb, "findme.md")
            fake_home = os.path.join(sb["tmp"], "home")
            os.makedirs(fake_home, exist_ok=True)
            p = run(sb, script, env_extra={"HOME": fake_home})
            text = out_of(p)
            check(p.returncode == 1, f"{script}: bare filename must fail —— {text}")
            check("ABSOLUTE path" in text,
                  f"{script}: error must say an absolute path is required —— {text}")
            check("⌘⌥C" in text and "Copy as Pathname" in text,
                  f"{script}: error must give the exact keystroke, not a menu "
                  f"path he does not use —— {text}")
            check(text.index("FIX:") < text.index("Why not just the filename?"),
                  f"{script}: the fix must come BEFORE the rationale —— an error "
                  f"that opens with history buries the one actionable line: {text}")
            check("ANYWHERE on this Mac" in text,
                  f"{script}: the example must not imply targets are repo-only "
                  f"—— they are not, and a repo-shaped hint would mislead: {text}")
            example = os.path.join(fake_home, "Downloads", "Some Deliverable.pages")
            check(example in text,
                  f"{script}: error must show a concrete full-path example —— {text}")
            check(date_added(decoy) == before,
                  f"{script}: refused run still changed the decoy's Date Added")
        finally:
            shutil.rmtree(sb["tmp"], ignore_errors=True)


def test_relative_path_is_refused():
    """Not just bare names: any relative path is cwd-ambiguous and must stop."""
    for script in SCRIPTS:
        sb = make_sandbox()
        try:
            touch(os.path.join(sb["sessions"], "rel.md"))
            write_instruction(sb, "sessions/rel.md")
            p = run(sb, script)
            check(p.returncode == 1, f"{script}: relative path must fail")
            check("ABSOLUTE path" in out_of(p),
                  f"{script}: relative path error must name the requirement")
        finally:
            shutil.rmtree(sb["tmp"], ignore_errors=True)


def test_missing_path_fails_loud():
    for script in SCRIPTS:
        sb = make_sandbox()
        try:
            write_instruction(sb, os.path.join(sb["sessions"], "nope.md"))
            p = run(sb, script)
            check(p.returncode == 1, f"{script}: missing path must fail")
            check("does not exist" in out_of(p),
                  f"{script}: missing-path error must say so —— {out_of(p)}")
        finally:
            shutil.rmtree(sb["tmp"], ignore_errors=True)


def test_empty_folder_fails_loud():
    for script in SCRIPTS:
        sb = make_sandbox()
        try:
            empty = os.path.join(sb["sessions"], "empty")
            os.makedirs(empty)
            write_instruction(sb, empty)
            p = run(sb, script)
            check(p.returncode == 1, f"{script}: empty folder must fail")
            check("empty" in out_of(p),
                  f"{script}: empty-folder error must say so —— {out_of(p)}")
        finally:
            shutil.rmtree(sb["tmp"], ignore_errors=True)


def test_outside_any_repo_is_stamped():
    """HIS MAIN CASE, and the reason the old fence was removed: most runs
    re-date a deliverable that lives nowhere near a repo. A file and a folder,
    both outside every GitHub/ tree, must be stamped exactly like an in-repo
    one —— if this fails the tools do not do the job he uses them for."""
    for script in SCRIPTS:
        sb = make_sandbox()
        try:
            lone = touch(os.path.join(sb["outside"], "Deliverable.pages"))
            write_instruction(sb, lone)
            p = run(sb, script)
            check(p.returncode == 0,
                  f"{script}: outside-any-repo file must be stamped —— {out_of(p)}")
            check(date_added(lone) == EPOCH,
                  f"{script}: outside-any-repo file not stamped")

            folder = os.path.join(sb["outside"], "Client Pack")
            os.makedirs(folder)
            member = touch(os.path.join(folder, "brief.md"))
            write_instruction(sb, folder)
            p = run(sb, script)
            check(p.returncode == 0,
                  f"{script}: outside-any-repo folder must be stamped —— {out_of(p)}")
            check(date_added(folder) == EPOCH and date_added(member) == EPOCH,
                  f"{script}: outside-any-repo folder not stamped recursively")
        finally:
            shutil.rmtree(sb["tmp"], ignore_errors=True)


def test_a_symlink_is_stamped_but_never_its_target():
    """With no fence, a symlink target elsewhere is legitimate —— so the
    guarantee is NOFOLLOW, not refusal: the link's own dates move and the file
    it points at is left completely alone."""
    for script in SCRIPTS:
        sb = make_sandbox()
        try:
            stranger = touch(os.path.join(sb["outside"], "stranger.md"))
            before_m, before_a = mtime(stranger), date_added(stranger)
            link = os.path.join(sb["sessions"], "link.md")
            os.symlink(stranger, link)
            write_instruction(sb, link)
            p = run(sb, script)
            check(p.returncode == 0, f"{script}: symlink target —— {out_of(p)}")
            check(date_added(link) == EPOCH,
                  f"{script}: the symlink itself was not stamped")
            check(mtime(stranger) == before_m and date_added(stranger) == before_a,
                  f"{script}: the symlink's TARGET was written (NOFOLLOW broken)")
        finally:
            shutil.rmtree(sb["tmp"], ignore_errors=True)


def test_the_home_folder_itself_is_refused():
    """Path.home() follows $HOME, so this one runs entirely in the sandbox ——
    no real home directory is ever named, and the write path is exercised for
    real (no --dry-run) because nothing outside the sandbox can be reached."""
    for script in SCRIPTS:
        sb = make_sandbox()
        try:
            fake_home = os.path.join(sb["tmp"], "home")
            os.makedirs(fake_home)
            victim = touch(os.path.join(fake_home, "doc.md"))
            before = date_added(victim)
            write_instruction(sb, fake_home)
            p = run(sb, script, env_extra={"HOME": fake_home})
            check(p.returncode == 1,
                  f"{script}: the home folder itself must be refused —— {out_of(p)}")
            check("home folder itself" in out_of(p),
                  f"{script}: home refusal must say what it refused —— {out_of(p)}")
            check(date_added(victim) == before,
                  f"{script}: refused home target still had contents stamped")
        finally:
            shutil.rmtree(sb["tmp"], ignore_errors=True)


def test_real_catastrophic_targets_are_refused():
    """`/` (a mount point), `/Users` and `/Volumes` cannot be simulated ——
    os.path.ismount has no sandbox equivalent, and the whole point is that the
    REAL ones stop. Run with --dry-run so no write path exists at all even if
    the refusal is broken, plus a timeout so a broken refusal is killed
    mid-walk and reported rather than grinding for minutes."""
    # The volume the repo itself sits on: the single most dangerous plausible
    # truncation (`/Volumes/FURY 2TB/Fury Documents/...` trimmed back to the
    # drive). Derived, never hard-coded, and skipped where it is not a mount ——
    # a suite that only proved `/` would be claiming more than it tested.
    extra = []
    probe = os.path.abspath(REPO)
    while probe != os.path.dirname(probe):
        if os.path.ismount(probe) and probe != "/":
            extra.append((probe, "volume root"))
            break
        probe = os.path.dirname(probe)

    for script in SCRIPTS:
        sb = make_sandbox()
        try:
            for target, phrase in [("/", "volume root"),
                                   ("/Users", "every user"),
                                   ("/Volumes", "every user")] + extra:
                write_instruction(sb, target)
                p = run(sb, script, args=("--dry-run",), timeout=25)
                check(p.returncode == 1,
                      f"{script}: {target} must be refused —— {out_of(p)}")
                check(phrase in out_of(p),
                      f"{script}: {target} refusal must say why —— {out_of(p)}")
        finally:
            shutil.rmtree(sb["tmp"], ignore_errors=True)


def test_a_symlink_cannot_be_a_door_to_a_catastrophic_target():
    """The refusal reads the link AND what it points at, so an innocent name
    in a normal folder cannot smuggle in a volume root."""
    for script in SCRIPTS:
        sb = make_sandbox()
        try:
            door = os.path.join(sb["sessions"], "backup.md")
            os.symlink("/Volumes", door)
            write_instruction(sb, door)
            p = run(sb, script, args=("--dry-run",), timeout=25)
            check(p.returncode == 1,
                  f"{script}: a symlink to /Volumes must be refused —— {out_of(p)}")
            check("every user" in out_of(p),
                  f"{script}: symlink-door refusal must say why —— {out_of(p)}")
        finally:
            shutil.rmtree(sb["tmp"], ignore_errors=True)


def test_symlinks_inside_a_scrubbed_tree_are_never_followed():
    """The venv case: a scrub must stop at a symlink, both for files and dirs."""
    for script in SCRIPTS:
        sb = make_sandbox()
        try:
            keep = touch(os.path.join(sb["outside"], "keepme.md"))
            deepdir = os.path.join(sb["outside"], "deep")
            os.makedirs(deepdir)
            inner = touch(os.path.join(deepdir, "inner.md"))
            keep_m, inner_m = mtime(keep), mtime(inner)
            keep_a, inner_a = date_added(keep), date_added(inner)

            folder = os.path.join(sb["sessions"], "tree")
            os.makedirs(folder)
            touch(os.path.join(folder, "real.md"))
            os.symlink(keep, os.path.join(folder, "link.md"))
            os.symlink(deepdir, os.path.join(folder, "linkdir"))

            write_instruction(sb, folder)
            p = run(sb, script)
            check(p.returncode == 0, f"{script}: tree with symlinks —— {out_of(p)}")
            check(mtime(keep) == keep_m and date_added(keep) == keep_a,
                  f"{script}: followed a file symlink out of the tree")
            check(mtime(inner) == inner_m and date_added(inner) == inner_a,
                  f"{script}: descended into a symlinked directory")
        finally:
            shutil.rmtree(sb["tmp"], ignore_errors=True)


def test_large_tree_needs_confirmation():
    """A path that expands to a whole tree is either intended or a typo. With
    stdin piped (never a tty) the run must stop rather than silently proceed."""
    for script in SCRIPTS:
        sb = make_sandbox()
        try:
            folder = os.path.join(sb["sessions"], "big")
            os.makedirs(folder)
            members = [touch(os.path.join(folder, f"f{i:03d}.md")) for i in range(60)]
            before = date_added(members[0])
            write_instruction(sb, folder)

            p = run(sb, script)
            check(p.returncode == 1, f"{script}: big tree must stop without --yes")
            check("not a terminal" in out_of(p),
                  f"{script}: gate must explain the stop —— {out_of(p)}")
            check(date_added(members[0]) == before,
                  f"{script}: gate stopped but items were stamped anyway")

            p = run(sb, script, args=("--yes",))
            check(p.returncode == 0, f"{script}: --yes must proceed —— {out_of(p)}")
            check(date_added(members[0]) == EPOCH,
                  f"{script}: --yes did not stamp the tree")
        finally:
            shutil.rmtree(sb["tmp"], ignore_errors=True)


def test_dry_run_changes_nothing():
    for script in SCRIPTS:
        sb = make_sandbox()
        try:
            target = touch(os.path.join(sb["sessions"], "dry.md"))
            before_a, before_m = date_added(target), mtime(target)
            write_instruction(sb, target)
            p = run(sb, script, args=("--dry-run",))
            check(p.returncode == 0, f"{script}: dry-run should succeed —— {out_of(p)}")
            check("(dry-run)" in out_of(p), f"{script}: dry-run must say so")
            check(date_added(target) == before_a and mtime(target) == before_m,
                  f"{script}: dry-run changed dates")
        finally:
            shutil.rmtree(sb["tmp"], ignore_errors=True)


def test_instruction_file_may_be_md_with_a_heading():
    """The user believed these took a .md. They now do —— matching the sibling
    git_history.py in the same folder —— and a Markdown heading is skipped."""
    for script in SCRIPTS:
        sb = make_sandbox()
        try:
            target = touch(os.path.join(sb["sessions"], "md_inst.md"))
            write_instruction(sb, target, name="target.md", header="# Target")
            p = run(sb, script)
            check(p.returncode == 0, f"{script}: .md instruction —— {out_of(p)}")
            check(date_added(target) == EPOCH, f"{script}: .md instruction not honoured")
        finally:
            shutil.rmtree(sb["tmp"], ignore_errors=True)


def test_generated_artefacts_are_not_mistaken_for_instructions():
    """Every gscpt script DROPS its output in this same folder, and accepting
    .md widens what can be mistaken for an instruction. The exclusions must
    cover the artefacts that really land here —— DATS_<ts>.txt (a list of file
    PATHS, so it reads as a valid instruction file), ajap_* inputs, and
    quote_fix.py's <stem>_processed.md/.txt, which needs a STEM check because
    it is a suffix, not a prefix."""
    for script in SCRIPTS:
        sb = make_sandbox()
        try:
            target = touch(os.path.join(sb["sessions"], "real.md"))
            write_instruction(sb, target)
            touch(os.path.join(sb["gscpt"], "DATS_202607091852.txt"), "junk\n")
            touch(os.path.join(sb["gscpt"], "ajap_logs_input_202607091852.md"), "junk\n")
            touch(os.path.join(sb["gscpt"], "receipt_processed.md"), "junk\n")
            touch(os.path.join(sb["gscpt"], "notes_processed.txt"), "junk\n")
            touch(os.path.join(sb["gscpt"], "blank.md"), "")
            touch(os.path.join(sb["gscpt"], "README.md"), "docs\n")
            p = run(sb, script)
            check(p.returncode == 0,
                  f"{script}: artefacts beside the script must be ignored —— {out_of(p)}")
            check(date_added(target) == EPOCH, f"{script}: real instruction not honoured")
        finally:
            shutil.rmtree(sb["tmp"], ignore_errors=True)


def test_zero_or_many_instruction_files_stop():
    for script in SCRIPTS:
        sb = make_sandbox()
        try:
            p = run(sb, script)
            check(p.returncode == 1, f"{script}: no instruction file must fail")
            check("no instruction" in out_of(p),
                  f"{script}: missing-instruction error must say so —— {out_of(p)}")

            target = touch(os.path.join(sb["sessions"], "two.md"))
            write_instruction(sb, target, name="a.txt")
            with open(os.path.join(sb["gscpt"], "b.md"), "w", encoding="utf-8") as fh:
                fh.write(f"{target}\n{TS_OTHER}\n")
            p = run(sb, script)
            check(p.returncode == 1, f"{script}: two instruction files must fail")
            check("multiple instruction files" in out_of(p),
                  f"{script}: ambiguity error must say so —— {out_of(p)}")
        finally:
            shutil.rmtree(sb["tmp"], ignore_errors=True)


def test_bad_timestamp_stops():
    for script in SCRIPTS:
        sb = make_sandbox()
        try:
            target = touch(os.path.join(sb["sessions"], "ts.md"))
            before = date_added(target)
            write_instruction(sb, target, ts="20260709185")     # 11 digits
            p = run(sb, script)
            check(p.returncode == 1, f"{script}: short timestamp must fail")
            write_instruction(sb, target, ts="202613091852")    # month 13
            p = run(sb, script)
            check(p.returncode == 1, f"{script}: impossible timestamp must fail")
            check(date_added(target) == before,
                  f"{script}: a bad timestamp still wrote something")
        finally:
            shutil.rmtree(sb["tmp"], ignore_errors=True)


# --------------------------------------------------- documentation contract
def test_scripts_carry_a_root_scope_line():
    """coding.md: any script that resolves repo paths names its roots in its
    header. These resolve NONE —— so the line must say that outright, and say
    it is deliberate. An unrestricted target that merely LOOKS unrestricted is
    indistinguishable from a fence someone deleted by accident."""
    for script in SCRIPTS:
        src = open(os.path.join(REAL_GSCPT, script), encoding="utf-8").read()
        head = src.split('"""')[1] if src.count('"""') >= 2 else ""
        check("Root scope:" in head,
              f"{script}: header is missing its `Root scope:` line")
        check("AJAP_repo" in head,
              f"{script}: `Root scope:` must settle the AJAP_repo question")
        check("DELIBERATE" in head,
              f"{script}: `Root scope:` must state that having no root "
              f"restriction is deliberate, not an oversight")
        for shape in ("ismount", "/Users", "/Volumes", "HOME folder"):
            check(shape in head,
                  f"{script}: `Root scope:` must name what IS refused ({shape})")


def test_no_search_code_survives():
    """A returning rglob-over-the-repo would reinstate the silent-wrong-file
    failure this whole change removed."""
    for script in SCRIPTS:
        src = open(os.path.join(REAL_GSCPT, script), encoding="utf-8").read()
        code = "\n".join(
            ln for ln in src.splitlines()
            if not ln.lstrip().startswith("#")
        )
        check("rglob(" not in code, f"{script}: a repo-wide rglob search is back")


def test_the_two_scripts_have_not_drifted():
    """They are deliberately standalone (no shared import), so the contract they
    share is checked instead of trusted."""
    keys = ("INSTRUCTION_SUFFIXES", "EXCLUDED_NAMES", "EXCLUDED_PREFIXES",
            "EXCLUDED_STEM_SUFFIXES", "CONFIRM_THRESHOLD", "NEVER_TARGET")
    seen = {}
    for script in SCRIPTS:
        src = open(os.path.join(REAL_GSCPT, script), encoding="utf-8").read()
        for key in keys:
            m = re.search(rf"^{key} = (.+)$", src, re.M)
            if not m:
                failures.append(f"{script}: {key} not found")
                continue
            seen.setdefault(key, []).append((script, m.group(1).split("#")[0].strip()))
    for key, pairs in seen.items():
        vals = {v for _s, v in pairs}
        check(len(vals) == 1,
              f"DAMF/DXMF disagree on {key}: {pairs}")


def test_readme_documents_the_new_contract():
    readme = open(os.path.join(REAL_GSCPT, "README.md"), encoding="utf-8").read()
    # Only the per-script entries in the Scripts list, not prose that happens to
    # name both scripts at once.
    for line in readme.splitlines():
        if line.startswith("- `DAMF.py` ——") or line.startswith("- `DXMF.py` ——"):
            check("absolute path" in line.lower(),
                  f"README line must say the target is an absolute path: {line}")
            check("folder" in line.lower(),
                  f"README line must say a folder is accepted: {line}")
    check("DAMF.py" in readme and "DXMF.py" in readme,
          "README no longer lists both scripts")
    check("Anywhere on this Mac" in readme,
          "README still implies targets are confined to a root")
    check("ALLOWED_ROOTS" not in readme,
          "README still tells him to widen ALLOWED_ROOTS, which no longer exists")
    check("⌘⌥C" in readme,
          "README must name the keystroke he actually uses to copy a path")


# --------------------------------------------------- .md across the folder
# Which gscpt scripts take a TEXT input file at all. The others are excluded on
# purpose and the reason is recorded here so the audit is not re-run blind:
#   DATS.py            —— no input file; it scans SCAN_DIRS
#   ocr_reads.py       —— inputs are .jpg/.png/.pdf; .md is meaningless
#   trade_records.py   —— input is an IBKR .csv statement
#   transport_records.py —— input is an Opal .csv statement
#   ajap_logs_legacy.py —— FROZEN backup, not to be run or edited (and it
#                          already accepts both extensions)
TEXT_INPUT_SCRIPTS = ("DAMF.py", "DXMF.py", "git_history.py", "quote_fix.py",
                      "battery_logs.py", "shopping_records.py")


def test_every_text_input_script_declares_md():
    """He no longer saves anything as .txt, so a .txt-only scan finds nothing
    and says nothing. Source-level guard: each script's input-extension
    declaration must contain '.md'. Weaker than an end-to-end run, and named
    as such —— the two scripts that were actually CHANGED are exercised for
    real below."""
    for script in TEXT_INPUT_SCRIPTS:
        src = open(os.path.join(REAL_GSCPT, script), encoding="utf-8").read()
        decl = re.findall(r"^[A-Z_]*(?:EXTS|SUFFIXES|EXTENSIONS) *= *\(?\{?(.+)$",
                          src, re.M)
        inline = re.findall(r'suffix\.lower\(\) (?:not )?in \((.+?)\)', src)
        blob = " ".join(decl + inline)
        check('".md"' in blob or "'.md'" in blob,
              f"{script}: takes a text input but does not declare .md ({blob!r})")


def test_battery_and_shopping_actually_read_an_md_input():
    """The two scripts the .md change touched, run for real on a .md input in
    a throwaway folder —— 'declares .md' is not 'reads .md'."""
    cases = (
        ("battery_logs.py", "2130\n86%\n2200\n83% charging\n", "Battery Logs "),
        ("shopping_records.py", "Milk\n5.47\nBread\n3.20\n", "Shopping Records "),
    )
    for script, body, out_prefix in cases:
        tmp = os.path.realpath(tempfile.mkdtemp(prefix="gscpt_mdinput_"))
        try:
            shutil.copy2(os.path.join(REAL_GSCPT, script),
                         os.path.join(tmp, script))
            touch(os.path.join(tmp, "readings.md"), body)
            # An artefact that .md acceptance newly exposes: it must be skipped.
            touch(os.path.join(tmp, "stale_processed.md"), "junk\n")
            p = subprocess.run([sys.executable, os.path.join(tmp, script)],
                               capture_output=True, text=True, cwd=tmp)
            check(p.returncode == 0, f"{script}: .md input run failed —— {out_of(p)}")
            outs = [f for f in os.listdir(tmp) if f.endswith(".csv")]
            check(any(f.startswith(out_prefix) for f in outs),
                  f"{script}: no CSV produced from a .md input —— {outs} {out_of(p)}")
            check(not any("stale_processed" in f for f in outs),
                  f"{script}: consumed quote_fix.py's *_processed output —— {outs}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


def main():
    test_file_path_is_stamped()
    test_quoted_and_tilde_paths_still_work()
    test_folder_is_recursive_and_parent_survives_children()
    test_bare_filename_is_refused_and_tells_him_what_to_type()
    test_relative_path_is_refused()
    test_missing_path_fails_loud()
    test_empty_folder_fails_loud()
    test_outside_any_repo_is_stamped()
    test_a_symlink_is_stamped_but_never_its_target()
    test_the_home_folder_itself_is_refused()
    test_real_catastrophic_targets_are_refused()
    test_a_symlink_cannot_be_a_door_to_a_catastrophic_target()
    test_symlinks_inside_a_scrubbed_tree_are_never_followed()
    test_large_tree_needs_confirmation()
    test_dry_run_changes_nothing()
    test_instruction_file_may_be_md_with_a_heading()
    test_generated_artefacts_are_not_mistaken_for_instructions()
    test_zero_or_many_instruction_files_stop()
    test_bad_timestamp_stops()
    test_scripts_carry_a_root_scope_line()
    test_no_search_code_survives()
    test_the_two_scripts_have_not_drifted()
    test_readme_documents_the_new_contract()
    test_every_text_input_script_declares_md()
    test_battery_and_shopping_actually_read_an_md_input()

    if failures:
        print("FAIL —— %d of %d check(s) failed:" % (len(failures), checks))
        for f in failures:
            print("  - %s" % f)
        return 1
    print("PASS —— %d checks: absolute-path targets anywhere on this Mac, "
          "recursive folders, symlink containment, catastrophic-target "
          "refusals, .md inputs, and every stop condition." % checks)
    return 0


if __name__ == "__main__":
    sys.exit(main())
