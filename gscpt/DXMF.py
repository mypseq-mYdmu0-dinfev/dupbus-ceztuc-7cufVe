#!/usr/bin/env python3
"""
DXMF.py —— Date eXtended Manual Fixer (macOS)

Upgraded from DAMF.py (which set only "Date Added"). DXMF sets ALL FOUR
Finder-visible dates to a single target value:

    1. Date Created     (catalog ATTR_CMN_CRTIME)
    2. Date Modified    (catalog ATTR_CMN_MODTIME)
    3. Date Added       (catalog ATTR_CMN_ADDEDTIME + Spotlight mirror)
    4. Date Last Opened (xattr com.apple.lastuseddate#PS = {int64 sec, int64 nsec} LE)

WHY THESE MECHANISMS
--------------------
Finder's "Date Added" and "Date Last Opened" are NOT plain mtime/atime.
Date Added lives in the filesystem catalog attribute ATTR_CMN_ADDEDTIME
(Swift's addedToDirectoryDate is get-only), so we set it via the low-level
setattrlist() syscall. Date Last Opened is held in the per-file extended
attribute `com.apple.lastuseddate#PS` (two little-endian 64-bit ints: seconds
then nanoseconds), so we write that directly. Created and Modified are set in
the same setattrlist() call. The inode change-time (ctime) cannot be set; macOS
forces it to "now" on any metadata write, but it is not shown in Finder Get Info
and does not survive copy/zip/upload.

SYMLINK SAFETY
--------------
All writes use NOFOLLOW (FSOPT_NOFOLLOW / follow_symlinks=False) so a symlink's
own dates are changed, never its target's. This matters when scrubbing trees
that contain venvs whose symlinks point at system binaries.

USAGE
-----
Instruction file (DAMF-compatible):
   Place exactly one .txt beside this script (any name except temp.txt):
       Line 1: a filename to find anywhere in the repo, OR a path
               (relative to the repo root, or absolute) to a file or folder
       Line 2: the target timestamp in YYYYMMDDHHmm (Sydney local time)
   Then run:  python3 DXMF.py
   A path that resolves to a folder is scrubbed recursively (the folder itself
   plus every file and subfolder within).

Timestamps are interpreted in Australia/Sydney local time.
"""

import ctypes
import ctypes.util
import plistlib
import struct
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# ---------------------------------------------------------------- configuration
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(
    "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe"
)
SYDNEY = ZoneInfo("Australia/Sydney")
EXCLUDED_TXT = {"temp.txt"}  # never treat these as the instruction file

# catalog attribute bits (sys/attr.h)
ATTR_BIT_MAP_COUNT = 5
ATTR_CMN_CRTIME    = 0x00000200
ATTR_CMN_MODTIME   = 0x00000400
ATTR_CMN_ADDEDTIME = 0x10000000
FSOPT_NOFOLLOW     = 0x00000001  # setattrlist option
XATTR_NOFOLLOW     = 0x00000001  # setxattr option
LASTUSED_XATTR     = b"com.apple.lastuseddate#PS"

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
# macOS CPython has no os.setxattr; call libc directly.
# int setxattr(path, name, value, size, position, options)
_libc.setxattr.argtypes = [
    ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p,
    ctypes.c_size_t, ctypes.c_uint32, ctypes.c_int,
]


def _setxattr(path: Path, name: bytes, value: bytes) -> int:
    """Write one extended attribute without following symlinks."""
    return _libc.setxattr(
        str(path).encode(), name, value, len(value), 0, XATTR_NOFOLLOW,
    )


def die(msg: str) -> None:
    """Print an alert and stop immediately."""
    print(f"⚠️  STOPPED —— {msg}")
    sys.exit(1)


# ----------------------------------------------------------------- date setting
def set_all_dates(path: Path, dt: datetime) -> None:
    """Set Created, Modified, Added and Last Opened on one item (NOFOLLOW)."""
    sec = int(dt.timestamp())
    raw = str(path).encode()

    # 1-3) Created + Modified + Added in one catalog write.
    # Buffer order follows the bitmap by increasing bit value:
    # CRTIME (0x200) -> MODTIME (0x400) -> ADDEDTIME (0x10000000).
    al = _attrlist()
    al.bitmapcount = ATTR_BIT_MAP_COUNT
    al.commonattr = ATTR_CMN_CRTIME | ATTR_CMN_MODTIME | ATTR_CMN_ADDEDTIME
    buf = (_timespec * 3)(_timespec(sec, 0), _timespec(sec, 0), _timespec(sec, 0))
    rc = _libc.setattrlist(
        raw, ctypes.byref(al), ctypes.byref(buf), ctypes.sizeof(buf),
        FSOPT_NOFOLLOW,
    )
    if rc != 0:
        raise OSError(ctypes.get_errno(), "setattrlist failed", str(path))

    # Keep Spotlight's Date Added mirror in agreement (CFDate plist, naive UTC).
    utc_naive = dt.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
    cfdate = plistlib.dumps(utc_naive, fmt=plistlib.FMT_BINARY)
    _setxattr(path, b"com.apple.metadata:kMDItemDateAdded", cfdate)
    # (mirror is best-effort; the catalog value is authoritative)

    # 4) Date Last Opened: {int64 seconds, int64 nanoseconds} little-endian.
    _setxattr(path, LASTUSED_XATTR, struct.pack("<qq", sec, 0))


def collect_targets(target: Path) -> list[Path]:
    """A file -> [file]; a directory -> the dir plus all descendants,
    deepest first so parents are written last."""
    if target.is_dir() and not target.is_symlink():
        items = [target, *target.rglob("*")]
        items.sort(key=lambda p: len(p.parts), reverse=True)
        return items
    return [target]


# ------------------------------------------------------------------ input modes
def parse_ts(ts_raw: str) -> datetime:
    if len(ts_raw) != 12 or not ts_raw.isdigit():
        die(f"timestamp '{ts_raw}' is not 12 digits (YYYYMMDDHHmm).")
    try:
        return datetime(
            int(ts_raw[0:4]), int(ts_raw[4:6]), int(ts_raw[6:8]),
            int(ts_raw[8:10]), int(ts_raw[10:12]), tzinfo=SYDNEY,
        )
    except ValueError as exc:
        die(f"invalid timestamp '{ts_raw}': {exc}.")


def resolve_target(token: str) -> Path:
    """Resolve a token to a path: try as repo-relative, then absolute,
    else search the repo for a unique file of that name (DAMF behaviour)."""
    for cand in (REPO_ROOT / token, Path(token)):
        if cand.exists():
            return cand
    matches = [p for p in REPO_ROOT.rglob(token) if p.is_file()]
    if not matches:
        die(f"'{token}' not found as a path or a filename under {REPO_ROOT.name}/.")
    if len(matches) > 1:
        listing = "\n   ".join(str(p) for p in matches)
        die(f"{len(matches)} files named '{token}' found:\n   {listing}")
    return matches[0]


def find_instruction_file() -> Path:
    candidates = [
        p for p in SCRIPT_DIR.glob("*.txt") if p.name not in EXCLUDED_TXT
    ]
    if not candidates:
        die(f"no instruction .txt found in {SCRIPT_DIR} (excluding {sorted(EXCLUDED_TXT)}).")
    if len(candidates) > 1:
        names = ", ".join(sorted(p.name for p in candidates))
        die(f"multiple .txt files found ({names}); leave exactly one.")
    return candidates[0]


def run(targets: list[Path], dt: datetime) -> None:
    done, failed = 0, []
    for target in targets:
        for item in collect_targets(target):
            try:
                set_all_dates(item, dt)
                done += 1
            except OSError as exc:
                failed.append((item, exc))

    stamp = dt.strftime("%d/%m/%Y %H:%M")
    print(f"✅ All 4 dates set on {done} item(s) —— {stamp} AEST/AEDT")
    if failed:
        print(f"⚠️  {len(failed)} item(s) failed:")
        for item, exc in failed[:20]:
            print(f"   {item} —— {exc}")
        sys.exit(1)


def main() -> None:
    txt = find_instruction_file()
    lines = [ln.strip() for ln in txt.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if len(lines) < 2:
        die(f"{txt.name} needs 2 non-empty lines (target, then YYYYMMDDHHmm).")
    dt = parse_ts(lines[1])
    run([resolve_target(lines[0])], dt)


if __name__ == "__main__":
    main()
