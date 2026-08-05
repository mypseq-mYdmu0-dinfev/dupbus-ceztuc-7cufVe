#!/usr/bin/env python3
"""
DAMF.py —— Date Added Manual Fixer (macOS)

WHAT THE PROBLEM WAS
--------------------
Finder's "Date Added" is NOT the same thing as the Spotlight metadata that
`xattr`/`mdls` expose. Finder reads the filesystem catalog attribute
ATTR_CMN_ADDEDTIME (exposed in Swift as URLResourceValues.addedToDirectoryDate).
Writing the `com.apple.metadata:kMDItemDateAdded` extended attribute only
updates Spotlight's mirror —— Finder's column never moves. And Swift's
addedToDirectoryDate property is GET-ONLY, so it can't set it either.

HOW IT IS FIXED
---------------
Call the low-level setattrlist() syscall (via ctypes) with
ATTR_CMN_ADDEDTIME = 0x10000000 and a `struct timespec` holding the target
time. We also refresh the kMDItemDateAdded xattr so Spotlight agrees with the
catalog value. Every write is NOFOLLOW: a symlink's own Date Added moves and
its target's never does. That is not cosmetic —— once a whole folder can be
stamped, a followed symlink would reach outside the named tree.

USAGE
-----
1. In THIS script's own directory, leave exactly one instruction file, `.txt`
   or `.md` (any name except `temp.txt`/`blank.md`/`README.md`, a `❌_`-prefixed
   name, or a generated artefact such as `DATS_*`; anything inside `parked/`
   is ignored), containing:
       Line 1: the ABSOLUTE path of the target —— a FILE or a FOLDER.
               Finder: right-click → hold ⌥ → "Copy as Pathname", then paste.
               Surrounding quotes, backslash-escaped spaces and a leading `~`
               are all tolerated; `#`-leading and blank lines are skipped.
       Line 2: the desired Date Added timestamp in YYYYMMDDHHmm (Sydney time)
2. Run:  python3 DAMF.py
       --dry-run / -n   list what would be stamped, change nothing
       --yes / -y       skip the large-batch confirmation

FOLDER SEMANTICS
----------------
A folder target is stamped RECURSIVELY —— the folder itself, plus every file
and subfolder inside it, at any depth. Both halves of that are deliberate:
  - RECURSIVE, because the point of these dates is Finder sorting and
    searching. A shallow stamp would move the folder's own row whilst leaving
    everything nested inside it sorting somewhere else, which is the very
    inconsistency the tool exists to remove.
  - INCLUSIVE of the directory itself, because the folder's own Finder row is
    usually the row the user is looking at.
Items are written DEEPEST-FIRST so a parent is always written after its
children —— writing into a directory bumps that directory's own dates, so the
reverse order would silently undo the parent's stamp.
Symlinked directories are listed (and stamped, NOFOLLOW) but never descended
into, so a venv symlink pointing at a system binary can never drag this script
outside the tree that was named.

NO SEARCH HAPPENS
-----------------
Line 1 used to accept a bare filename that the script then hunted for across
the repo. That is gone, and both reasons matter. A search that landed on the
wrong single match rewrote the wrong file's dates silently. And a RELATIVE path
was resolved against the process cwd, so one instruction file hit different
targets depending on which directory the script happened to be run from. An
absolute path has exactly one meaning from anywhere.

Root scope: no root is searched or walked to FIND anything —— Line 1 names its
own. The only root that matters is the safety fence ALLOWED_ROOTS: the target
must sit under `.../Fury Documents/GitHub/`, derived from this script's own
`__file__` (never the process cwd, which a caller can point anywhere). That one
root covers every repo kept there —— dupbus-ceztuc-7cufVe, AJAP_repo, and any
sibling —— which is why no repo is named in code and why "should this also
search AJAP_repo?" no longer has anything to decide. Everything else on this
Mac is excluded on purpose: this script rewrites Finder metadata irreversibly
and recursively, so a single mistyped path outside the repos would quietly
rewrite the dates the user sorts and searches by, with no undo. Widen
ALLOWED_ROOTS deliberately if that ever needs to change.

It STOPS with an alert if: 0 or >1 instruction files exist; the instruction
file is malformed; the timestamp is invalid; Line 1 is not an absolute path;
the path does not exist; the path is outside ALLOWED_ROOTS (or IS one of those
roots); or the folder is empty.
"""

import ctypes
import ctypes.util
import os
import plistlib
import shlex
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# ---------------------------------------------------------------- configuration
SCRIPT_DIR = Path(__file__).resolve().parent          # .../<repo>/gscpt
REPO_ROOT = SCRIPT_DIR.parent                         # .../<repo>
# Safety fence, anchored on __file__ (never cwd). See "Root scope" above.
ALLOWED_ROOTS = (REPO_ROOT.parent,)                   # .../GitHub —— all repos
SYDNEY = ZoneInfo("Australia/Sydney")
INSTRUCTION_SUFFIXES = (".txt", ".md")
# Never treat these as the instruction file (blank.md is the renamed temp.txt).
EXCLUDED_NAMES = {"temp.txt", "blank.md", "readme.md"}  # compared lowercase
# Parked-in-place marker, plus artefacts other gscpt scripts DROP in this folder
# (DATS writes DATS_<ts>.txt here) —— those are output, never instructions.
EXCLUDED_PREFIXES = ("❌_", "DATS_", "ajap_logs_", "ajap_runtime_log")
CONFIRM_THRESHOLD = 50  # a tree this size is a decision, not a typo's collateral

# catalog attribute bits (sys/attr.h)
ATTR_BIT_MAP_COUNT = 5
ATTR_CMN_ADDEDTIME = 0x10000000
FSOPT_NOFOLLOW     = 0x00000001  # setattrlist option
XATTR_NOFOLLOW     = 0x00000001  # setxattr option

_libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)


class _attrlist(ctypes.Structure):
    _fields_ = [
        ("bitmapcount", ctypes.c_ushort),
        ("reserved",    ctypes.c_uint16),
        ("commonattr",  ctypes.c_uint32),
        ("volattr",     ctypes.c_uint32),
        ("dirattr",     ctypes.c_uint32),
        ("fileattr",    ctypes.c_uint32),
        ("forkattr",    ctypes.c_uint32),
    ]


class _timespec(ctypes.Structure):
    _fields_ = [("tv_sec", ctypes.c_long), ("tv_nsec", ctypes.c_long)]


_libc.setattrlist.argtypes = [
    ctypes.c_char_p, ctypes.c_void_p, ctypes.c_void_p,
    ctypes.c_size_t, ctypes.c_ulong,
]
# macOS CPython has no os.setxattr; call libc directly. Declaring argtypes is
# NOT optional: an undeclared size_t is passed as a 32-bit int on arm64.
# int setxattr(path, name, value, size, position, options)
_libc.setxattr.argtypes = [
    ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p,
    ctypes.c_size_t, ctypes.c_uint32, ctypes.c_int,
]


def die(msg: str) -> None:
    """Print an alert and stop immediately."""
    print(f"⚠️  STOPPED —— {msg}")
    sys.exit(1)


# ------------------------------------------------------------ instruction file
def find_instruction_file() -> Path:
    """Exactly one eligible .txt/.md must sit beside this script."""
    candidates = [
        p for p in sorted(SCRIPT_DIR.iterdir())
        if p.is_file() and p.suffix.lower() in INSTRUCTION_SUFFIXES
        and p.name.lower() not in EXCLUDED_NAMES
        and not p.name.startswith(EXCLUDED_PREFIXES)
    ]  # top-level only: anything inside parked/ (or any subfolder) never matches
    if not candidates:
        die(f"no instruction .txt/.md found in {SCRIPT_DIR} "
            f"(excluding {sorted(EXCLUDED_NAMES)} and "
            f"{'/'.join(EXCLUDED_PREFIXES)}* names).")
    if len(candidates) > 1:
        names = ", ".join(p.name for p in candidates)
        die(f"multiple instruction files found ({names}); leave exactly one.\n"
            f"   Park the others: move them into parked/, or prefix a name "
            f"with ❌_ to park it in place.")
    return candidates[0]


def parse_instructions(inst: Path) -> tuple[str, datetime]:
    """Line 1 = absolute target path, Line 2 = YYYYMMDDHHmm (Sydney local).
    Blank and `#`-leading lines are skipped so a .md can carry a heading."""
    lines = [
        ln.strip() for ln in inst.read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]
    if len(lines) < 2:
        die(f"{inst.name} needs 2 content lines: an ABSOLUTE path "
            f"(file or folder), then YYYYMMDDHHmm.")
    target_token, ts_raw = lines[0], lines[1]

    if len(ts_raw) != 12 or not ts_raw.isdigit():
        die(f"timestamp '{ts_raw}' is not 12 digits (YYYYMMDDHHmm).")
    try:
        dt = datetime(
            int(ts_raw[0:4]), int(ts_raw[4:6]), int(ts_raw[6:8]),
            int(ts_raw[8:10]), int(ts_raw[10:12]),
            tzinfo=SYDNEY,
        )
    except ValueError as exc:
        die(f"invalid timestamp '{ts_raw}': {exc}.")
    return target_token, dt


# --------------------------------------------------------------- path handling
def path_variants(token: str) -> list[str]:
    """Forms to try for a copied path, in order. Raw is first so a plain
    'Copy as Pathname' value (literal spaces) is honoured before shell-style
    unescaping; quote-stripping and shlex then cover drag-and-drop / quoted
    paths without mangling the literal-spaces case."""
    token = token.strip()
    out: list[str] = []

    def add(t: str) -> None:
        if t and t not in out:
            out.append(t)

    add(token)
    if len(token) >= 2 and token[0] in "'\"" and token[-1] == token[0]:
        add(token[1:-1])                       # surrounding quotes
    try:
        parts = shlex.split(token)             # backslash-escaped spaces, etc.
        if len(parts) == 1:                    # ignore if it split a real space
            add(parts[0])
    except ValueError:
        pass
    return out


def _not_absolute_help(given: str) -> str:
    example = ALLOWED_ROOTS[0] / REPO_ROOT.name / "sessions/2026/202607/notes.md"
    return (
        f"Line 1 must be an ABSOLUTE path, but it reads: {given}\n"
        f"   Bare filenames are no longer searched for —— a search that found "
        f"the wrong\n"
        f"   single match rewrote the wrong file's dates silently, and a "
        f"relative path\n"
        f"   meant different files depending on where the script was run from.\n"
        f"   Type the full path instead. In Finder: right-click the file or "
        f"folder →\n"
        f"   hold ⌥ → \"Copy as Pathname\", then paste it as Line 1. It must "
        f"start with\n"
        f"   a '/', and it may name a FILE or a whole FOLDER, e.g.\n"
        f"     {example}\n"
        f"   Line 2 stays the 12-digit YYYYMMDDHHmm timestamp."
    )


def _outside_help(p: Path) -> str:
    roots = "\n     ".join(str(r) for r in ALLOWED_ROOTS)
    return (
        f"target is outside the roots this script may touch: {p}\n"
        f"   Nothing was changed. Allowed:\n     {roots}\n"
        f"   That fence exists because this script rewrites Finder dates "
        f"recursively\n"
        f"   and irreversibly. If the path really is intentional, add its root "
        f"to\n"
        f"   ALLOWED_ROOTS at the top of this script —— deliberately, not in "
        f"passing."
    )


def _inside_allowed(real: Path) -> bool:
    for root in ALLOWED_ROOTS:
        try:
            real.relative_to(root)
        except ValueError:
            continue
        return True
    return False


def resolve_target(token: str) -> Path:
    """Line 1 -> an existing absolute path inside ALLOWED_ROOTS. No search, no
    guessing: every failure mode below stops the run instead of picking one."""
    variants = [Path(v).expanduser() for v in path_variants(token)]
    absolute = [v for v in variants if v.is_absolute()]
    if not absolute:
        die(_not_absolute_help(token.strip()))

    for v in absolute:
        # normpath collapses '..' TEXTUALLY; resolve() is deliberately avoided
        # so a symlink target stays the symlink itself (writes are NOFOLLOW).
        p = Path(os.path.normpath(str(v)))
        if not p.exists() and not p.is_symlink():
            continue
        real = Path(os.path.realpath(p))
        # Fence-check the REAL path: a symlink inside the roots that points out
        # of them must not become a way through the fence.
        if real in ALLOWED_ROOTS or p in ALLOWED_ROOTS:
            die(f"target IS one of the allowed roots ({p}) —— that would stamp "
                f"every repo inside it.\n"
                f"   Name a repo, a folder, or a file within it instead.")
        if not _inside_allowed(real):
            die(_outside_help(p))
        return p

    die(f"path does not exist: {absolute[0]}\n"
        f"   Nothing was changed. Check the path (a stale copy, a renamed "
        f"folder, or\n"
        f"   an unmounted volume are the usual causes) and run again.")


def collect_targets(target: Path) -> list[Path]:
    """A file (or symlink) -> [it]. A directory -> the directory itself plus
    every descendant at any depth, deepest-first so parents are written last.
    os.walk(followlinks=False) pins the no-symlink-recursion behaviour to this
    script rather than to the running Python's glob semantics, which changed."""
    if target.is_symlink() or not target.is_dir():
        return [target]

    items = [target]
    for dirpath, dirnames, filenames in os.walk(target, followlinks=False):
        for name in dirnames + filenames:
            items.append(Path(dirpath) / name)
    if len(items) == 1:
        die(f"target folder is empty: {target}\n"
            f"   Nothing was changed. An empty folder is almost always a "
            f"mistyped or\n"
            f"   stale path —— check it, or name the file itself as Line 1.")
    items.sort(key=lambda p: len(p.parts), reverse=True)
    return items


# ----------------------------------------------------------------- date setting
def set_date_added(path: Path, dt: datetime) -> None:
    """Set the filesystem catalog 'Date Added' via setattrlist() (NOFOLLOW)."""
    raw = str(path).encode()

    al = _attrlist()
    al.bitmapcount = ATTR_BIT_MAP_COUNT
    al.commonattr = ATTR_CMN_ADDEDTIME
    buf = _timespec(int(dt.timestamp()), 0)
    rc = _libc.setattrlist(
        raw, ctypes.byref(al), ctypes.byref(buf), ctypes.sizeof(buf),
        FSOPT_NOFOLLOW,
    )
    if rc != 0:
        raise OSError(ctypes.get_errno(), "setattrlist failed", str(path))

    # Keep Spotlight's mirror in agreement (CFDate plist; naive UTC for plistlib).
    utc_naive = dt.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
    cfdate = plistlib.dumps(utc_naive, fmt=plistlib.FMT_BINARY)
    _libc.setxattr(
        raw, b"com.apple.metadata:kMDItemDateAdded",
        cfdate, len(cfdate), 0, XATTR_NOFOLLOW,
    )  # best-effort mirror; the catalog value above is the authoritative one


# ------------------------------------------------------------------------- run
def confirm_if_large(items: list[Path], assume_yes: bool) -> bool:
    """A big expansion is either intended or a mistyped path. Ask, unless told
    not to. Returns False if the user declined."""
    if len(items) < CONFIRM_THRESHOLD or assume_yes:
        return True
    print(f"👀 That path expands to {len(items)} items —— a whole tree, not one "
          f"file. First few:")
    for p in items[:5]:
        print(f"   {p}")
    if not sys.stdin.isatty():
        die(f"{len(items)} items (≥{CONFIRM_THRESHOLD}) needs confirmation, but "
            f"stdin is not a terminal.\n"
            f"   Re-run with --yes if that is genuinely what you mean.")
    if input("🚦 Type yes to stamp them all: ").strip() != "yes":
        print("☑️  Aborted; nothing was changed.")
        return False
    return True


def main() -> None:
    args = sys.argv[1:]
    dry = ("--dry-run" in args) or ("-n" in args)
    assume_yes = ("--yes" in args) or ("-y" in args)

    inst = find_instruction_file()
    token, dt = parse_instructions(inst)
    target = resolve_target(token)
    items = collect_targets(target)
    stamp = dt.strftime("%d/%m/%Y %H:%M")

    print(f"🎯 {target}")
    print(f"   {len(items)} item(s) → Date Added {stamp} AEST/AEDT")
    if dry:
        for p in items:
            print(f"   (dry-run) {p}")
        print("(dry-run) nothing was changed.")
        return
    if not confirm_if_large(items, assume_yes):
        return

    done, failed = 0, []
    for item in items:
        try:
            set_date_added(item, dt)
            done += 1
        except OSError as exc:
            failed.append((item, exc))

    print(f"✅ Date Added set on {done} item(s) —— {stamp} AEST/AEDT")
    if failed:
        print(f"⚠️  {len(failed)} item(s) failed:")
        for item, exc in failed[:20]:
            print(f"   {item} —— {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
