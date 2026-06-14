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
catalog value.

USAGE
-----
1. In THIS script's own directory, create exactly one .txt file (any name
   except `temp.txt`) containing:
       Line 1: the target filename (e.g. dissertation_response_202606041852.md)
       Line 2: the desired Date Added timestamp in YYYYMMDDHHmm (Sydney time)
2. Run:  python3 DAMF.py
3. The script searches the whole GitHub repo for that filename, and if exactly
   one match is found, sets its Date Added.

It STOPS with an alert if: 0 or >1 instruction .txt files exist; the .txt is
malformed; the timestamp is invalid; or 0 / >1 target files are found in repo.
"""

import ctypes
import ctypes.util
import plistlib
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


def die(msg: str) -> None:
    """Print an alert and stop immediately."""
    print(f"⚠️  STOPPED —— {msg}")
    sys.exit(1)


def find_instruction_file() -> Path:
    """Exactly one eligible .txt must sit beside this script."""
    candidates = [
        p for p in SCRIPT_DIR.glob("*.txt")
        if p.name not in EXCLUDED_TXT
    ]
    if not candidates:
        die(f"no instruction .txt found in {SCRIPT_DIR} (excluding {sorted(EXCLUDED_TXT)}).")
    if len(candidates) > 1:
        names = ", ".join(sorted(p.name for p in candidates))
        die(f"multiple .txt files found ({names}); leave exactly one.")
    return candidates[0]


def parse_instructions(txt: Path) -> tuple[str, datetime]:
    """Line 1 = target filename, Line 2 = YYYYMMDDHHmm (Sydney local)."""
    lines = [ln.strip() for ln in txt.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if len(lines) < 2:
        die(f"{txt.name} needs 2 non-empty lines (filename, then YYYYMMDDHHmm).")
    target_name, ts_raw = lines[0], lines[1]

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
    return target_name, dt


def find_target_in_repo(filename: str) -> Path:
    """Exactly one file of that name must exist anywhere under the repo."""
    if not REPO_ROOT.is_dir():
        die(f"repo root not found: {REPO_ROOT}")
    matches = [p for p in REPO_ROOT.rglob(filename) if p.is_file()]
    if not matches:
        die(f"'{filename}' not found anywhere under {REPO_ROOT.name}/.")
    if len(matches) > 1:
        listing = "\n   ".join(str(p) for p in matches)
        die(f"{len(matches)} files named '{filename}' found:\n   {listing}")
    return matches[0]


def set_date_added(path: Path, dt: datetime) -> None:
    """Set the filesystem catalog 'Date Added' via setattrlist()."""
    libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)

    class attrlist(ctypes.Structure):
        _fields_ = [
            ("bitmapcount", ctypes.c_ushort),
            ("reserved",    ctypes.c_uint16),
            ("commonattr",  ctypes.c_uint32),
            ("volattr",     ctypes.c_uint32),
            ("dirattr",     ctypes.c_uint32),
            ("fileattr",    ctypes.c_uint32),
            ("forkattr",    ctypes.c_uint32),
        ]

    class timespec(ctypes.Structure):
        _fields_ = [("tv_sec", ctypes.c_long), ("tv_nsec", ctypes.c_long)]

    ATTR_BIT_MAP_COUNT = 5
    ATTR_CMN_ADDEDTIME = 0x10000000

    al = attrlist()
    al.bitmapcount = ATTR_BIT_MAP_COUNT
    al.commonattr = ATTR_CMN_ADDEDTIME
    buf = timespec(int(dt.timestamp()), 0)

    libc.setattrlist.argtypes = [
        ctypes.c_char_p, ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_size_t, ctypes.c_ulong,
    ]
    rc = libc.setattrlist(
        str(path).encode(), ctypes.byref(al),
        ctypes.byref(buf), ctypes.sizeof(buf), 0,
    )
    if rc != 0:
        die(f"setattrlist failed (errno={ctypes.get_errno()}) on {path}")

    # Keep Spotlight's mirror in agreement (CFDate plist; naive UTC for plistlib).
    utc_naive = dt.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
    cfdate = plistlib.dumps(utc_naive, fmt=plistlib.FMT_BINARY)
    libc.setxattr(
        str(path).encode(), b"com.apple.metadata:kMDItemDateAdded",
        cfdate, len(cfdate), 0, 0,
    )


def main() -> None:
    txt = find_instruction_file()
    target_name, dt = parse_instructions(txt)
    target = find_target_in_repo(target_name)
    set_date_added(target, dt)

    stamp = dt.strftime("%d/%m/%Y %H:%M")
    print(f"✅ Date Added set —— {target_name}")
    print(f"   {stamp} AEST/AEDT")
    print(f"   {target}")


if __name__ == "__main__":
    main()
