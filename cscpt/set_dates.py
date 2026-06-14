#!/usr/bin/env python3
"""
set_dates.py —— CC's macOS date setter (terminal-driven).

Sets any one or all of a file/folder's four Finder-visible dates to a target
timestamp. Built for Claude Code's own use; run it WITHOUT reading this file
(see cscpt/README.md for usage). Sibling of gscpt/DXMF.py (the user's .txt-driven
variant); this one takes terminal arguments and offers per-date modes.

USAGE
    python3 cscpt/set_dates.py <mode> <YYYYMMDDHHmm> <path> [more paths...]

MODES
    1 = Date Created only
    2 = Date Modified only
    3 = Date Added only
    4 = Date Last Opened only
    5 = all four dates

NOTES
    - Timestamp is Australia/Sydney local time (12 digits, YYYYMMDDHHmm).
    - A path may be a file or a directory; directories are processed recursively
      (the folder itself plus every file and subfolder within), deepest first.
    - All writes are symlink-safe (NOFOLLOW), so a symlink's own dates change,
      never its target's —— matters for trees containing venvs.
    - Mechanisms: Created/Modified/Added use the filesystem catalogue via
      setattrlist(); Added also refreshes the Spotlight mirror; Last Opened is
      the `com.apple.lastuseddate#PS` xattr ({int64 sec, int64 nsec} LE).
      macOS CPython has no os.setxattr, so libc.setxattr is called directly.
    - The inode change-time (ctime) cannot be set (macOS forces it to now); it
      is not shown in Get Info and does not survive copy/upload.
    - Spotlight's DISPLAYED kMDItemLastUsedDate can lag a manual xattr edit; the
      stored xattr is authoritative.
"""

import ctypes
import ctypes.util
import plistlib
import struct
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

SYDNEY = ZoneInfo("Australia/Sydney")

ATTR_BIT_MAP_COUNT = 5
ATTR_CMN_CRTIME    = 0x00000200
ATTR_CMN_MODTIME   = 0x00000400
ATTR_CMN_ADDEDTIME = 0x10000000
FSOPT_NOFOLLOW     = 0x00000001
XATTR_NOFOLLOW     = 0x00000001
LASTUSED_XATTR     = b"com.apple.lastuseddate#PS"
DATEADDED_XATTR    = b"com.apple.metadata:kMDItemDateAdded"

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
_libc.setxattr.argtypes = [
    ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p,
    ctypes.c_size_t, ctypes.c_uint32, ctypes.c_int,
]


def die(msg: str) -> None:
    print(f"⚠️  STOPPED —— {msg}")
    sys.exit(1)


def _catalogue_set(path: Path, attr_bits: list[int], sec: int) -> None:
    """Set one or more catalogue time attributes (NOFOLLOW). attr_bits must be
    ordered by ascending bit value to match the syscall's buffer layout."""
    al = _attrlist()
    al.bitmapcount = ATTR_BIT_MAP_COUNT
    al.commonattr = 0
    for b in attr_bits:
        al.commonattr |= b
    buf = (_timespec * len(attr_bits))(*[_timespec(sec, 0) for _ in attr_bits])
    rc = _libc.setattrlist(
        str(path).encode(), ctypes.byref(al), ctypes.byref(buf),
        ctypes.sizeof(buf), FSOPT_NOFOLLOW,
    )
    if rc != 0:
        raise OSError(ctypes.get_errno(), "setattrlist failed", str(path))


def _setxattr(path: Path, name: bytes, value: bytes) -> None:
    _libc.setxattr(str(path).encode(), name, value, len(value), 0, XATTR_NOFOLLOW)


def set_dates(path: Path, dt: datetime, mode: int) -> None:
    sec = int(dt.timestamp())
    if mode == 1:
        _catalogue_set(path, [ATTR_CMN_CRTIME], sec)
    elif mode == 2:
        _catalogue_set(path, [ATTR_CMN_MODTIME], sec)
    elif mode == 3:
        _catalogue_set(path, [ATTR_CMN_ADDEDTIME], sec)
        _mirror_added(path, dt)
    elif mode == 4:
        _setxattr(path, LASTUSED_XATTR, struct.pack("<qq", sec, 0))
    elif mode == 5:
        _catalogue_set(
            path, [ATTR_CMN_CRTIME, ATTR_CMN_MODTIME, ATTR_CMN_ADDEDTIME], sec
        )
        _mirror_added(path, dt)
        _setxattr(path, LASTUSED_XATTR, struct.pack("<qq", sec, 0))


def _mirror_added(path: Path, dt: datetime) -> None:
    """Keep Spotlight's Date Added mirror in step (best-effort)."""
    utc_naive = dt.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
    cfdate = plistlib.dumps(utc_naive, fmt=plistlib.FMT_BINARY)
    _setxattr(path, DATEADDED_XATTR, cfdate)


def collect(target: Path) -> list[Path]:
    if target.is_dir() and not target.is_symlink():
        items = [target, *target.rglob("*")]
        items.sort(key=lambda p: len(p.parts), reverse=True)
        return items
    return [target]


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


def main() -> None:
    args = sys.argv[1:]
    if len(args) < 3:
        die("usage: python3 set_dates.py <mode 1-5> <YYYYMMDDHHmm> <path> [more...]")
    if args[0] not in {"1", "2", "3", "4", "5"}:
        die(f"mode '{args[0]}' invalid (use 1=Created 2=Modified 3=Added 4=LastOpened 5=all).")
    mode = int(args[0])
    dt = parse_ts(args[1])

    done, failed = 0, []
    for token in args[2:]:
        target = Path(token)
        if not target.exists():
            die(f"path not found: {token}")
        for item in collect(target):
            try:
                set_dates(item, dt, mode)
                done += 1
            except OSError as exc:
                failed.append((item, exc))

    label = {1: "Created", 2: "Modified", 3: "Added", 4: "Last Opened", 5: "all 4 dates"}[mode]
    print(f"✅ {label} set on {done} item(s) —— {dt:%d/%m/%Y %H:%M} AEST/AEDT")
    if failed:
        print(f"⚠️  {len(failed)} item(s) failed:")
        for item, exc in failed[:20]:
            print(f"   {item} —— {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
