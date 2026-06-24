#!/usr/bin/env python3
"""DATS — "Date Added = TS". One run fixes query + close + wrap comms files
(never response): sets each file's macOS "Date Added" to the 12-digit TS in its
own filename, repairing drift caused by atomic-save edits/drags. Zero-token, local.

Run:  python3 DATS.py [--dry-run|-n]
  (no file-type argument — all three types are processed every run.)

Date-Added method (matches DAMF.py): setattrlist(ATTR_CMN_ADDEDTIME) moves
Finder's catalog "Date Added", and a kMDItemDateAdded xattr keeps Spotlight/mdls
in agreement (xattr alone never moves Finder's column; the syscall is the one
that counts).

Per-type rules:
  - query, wrap : set Date Added = filename TS. (A wrap's line 1 carries only a
                  month, so wrap is treated exactly like query — no content check.)
  - close       : filename TS must equal the 2nd (range-end) TS on content line 1.
                  A close that mismatches is skipped + reported; every CONFORMING
                  close still proceeds (one bad close no longer blocks the rest).
  - any type    : a non-template target whose name lacks a TS is a SERIOUS ERROR;
                  that one file is skipped + reported loudly, but the rest of its
                  type (and all other types) still proceed.

Gates (across the whole run's to-fix set):
  - files <24h off are auto-fixed; files >=24h off need a typed `yes`.
  - if >=10 files would change, the list is written to CONFIRM_DIR/DATS_<ts>.txt
    and a typed `yes` is required for the whole batch.
"""
import os, re, sys, ctypes, ctypes.util, struct, subprocess, plistlib
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# ---- config (edit FOLDERS to add more) ----
REPO = "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe"
FOLDERS = ["sessions", "seek/investigation"]
CONFIRM_DIR = os.path.join(REPO, "gscpt")
TYPES = ["query", "close", "wrap"]  # response is intentionally never processed
SYDNEY = ZoneInfo("Australia/Sydney")
TS_RE = re.compile(r"(20\d{10})")

# ---- macOS Date Added (catalog attr + Spotlight mirror) ----
libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
ATTR_BIT_MAP_COUNT = 5
ATTR_CMN_ADDEDTIME = 0x10000000


class attrlist(ctypes.Structure):
    _fields_ = [("bitmapcount", ctypes.c_ushort), ("reserved", ctypes.c_uint16),
                ("commonattr", ctypes.c_uint32), ("volattr", ctypes.c_uint32),
                ("dirattr", ctypes.c_uint32), ("fileattr", ctypes.c_uint32),
                ("forkattr", ctypes.c_uint32)]


class timespec(ctypes.Structure):
    _fields_ = [("tv_sec", ctypes.c_long), ("tv_nsec", ctypes.c_long)]


libc.getattrlist.argtypes = [ctypes.c_char_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_ulong]
libc.setattrlist.argtypes = [ctypes.c_char_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_ulong]
libc.setxattr.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.c_int]


def get_added(p):
    al = attrlist(); al.bitmapcount = ATTR_BIT_MAP_COUNT; al.commonattr = ATTR_CMN_ADDEDTIME
    buf = ctypes.create_string_buffer(64)
    if libc.getattrlist(p.encode(), ctypes.byref(al), buf, len(buf), 0) != 0:
        raise OSError(ctypes.get_errno(), "getattrlist")
    sec, _ = struct.unpack_from("qq", buf, 4)
    return sec


def set_added(p, dt):
    al = attrlist(); al.bitmapcount = ATTR_BIT_MAP_COUNT; al.commonattr = ATTR_CMN_ADDEDTIME
    buf = timespec(int(dt.timestamp()), 0)
    if libc.setattrlist(p.encode(), ctypes.byref(al), ctypes.byref(buf), ctypes.sizeof(buf), 0) != 0:
        raise OSError(ctypes.get_errno(), "setattrlist")
    cf = plistlib.dumps(dt.astimezone(timezone.utc).replace(tzinfo=None), fmt=plistlib.FMT_BINARY)
    libc.setxattr(p.encode(), b"com.apple.metadata:kMDItemDateAdded", cf, len(cf), 0, 0)


def ts_dt(ts):
    return datetime(int(ts[0:4]), int(ts[4:6]), int(ts[6:8]), int(ts[8:10]), int(ts[10:12]), tzinfo=SYDNEY)


def now_ts():
    return subprocess.run(["date", "+%Y%m%d%H%M"], capture_output=True, text=True,
                          env={**os.environ, "TZ": "Australia/Sydney"}).stdout.strip()


def gather(ftype):
    """-> (targets[(path,ts,dt)], note|None). A note lists ONLY the skipped
    offender(s) — a no-TS filename, or (close) a content-TS mismatch. Every
    conforming file of the type is still returned, so one bad file never blocks
    the rest (per-file skip, not per-type abort)."""
    name_re = re.compile(rf"^(?:[A-Za-z0-9]+_)?{ftype}_")
    bare_re = re.compile(rf"^(?:[A-Za-z0-9]+_)?{ftype}_\.md$")
    targets, missing = [], []
    for fold in FOLDERS:
        for dp, _, fs in os.walk(os.path.join(REPO, fold)):
            for f in fs:
                if not f.endswith(".md") or not name_re.match(f):
                    continue
                if bare_re.match(f):
                    continue
                m = TS_RE.search(f)
                if not m:
                    missing.append(os.path.join(dp, f))
                else:
                    targets.append((os.path.join(dp, f), m.group(1)))
    notes = []
    if missing:
        notes.append("SERIOUS ERROR — target(s) without a TS in filename (skipped; others proceed):\n  " + "\n  ".join(missing))
    if ftype == "close":
        good, bad = [], []
        for p, ts in targets:
            with open(p) as fh:
                first = fh.readline()
            found = TS_RE.findall(first)
            end = found[-1] if found else None
            if end != ts:
                bad.append(f"  filename={ts}  content_end={end}  {p}")
            else:
                good.append((p, ts))
        if bad:
            notes.append("close: filename TS != content range-end TS (these skipped; others proceed):\n" + "\n".join(bad))
        targets = good
    return [(p, ts, ts_dt(ts)) for p, ts in targets], ("\n".join(notes) if notes else None)


def fmt(x):
    p, ts, cur, d = x
    return f"{datetime.fromtimestamp(cur).strftime('%Y%m%d%H%M')}->{ts}  ({round(d/3600,1)}h)  {p}"


def main():
    raw = sys.argv[1:]
    dry = ("--dry-run" in raw) or ("-n" in raw)

    all_targets, blocked = [], []
    for t in TYPES:
        tg, err = gather(t)
        all_targets += tg
        if err:
            blocked.append((t, err))
    for t, err in blocked:
        print(f"⚠️ [{t}: offender(s) skipped, rest proceeding] {err}\n")

    dtmap = {p: dt for p, ts, dt in all_targets}
    to_fix = []
    for p, ts, dt in all_targets:
        cur = get_added(p)
        if abs(cur - int(dt.timestamp())) >= 60:
            to_fix.append((p, ts, cur, abs(cur - int(dt.timestamp()))))

    if not to_fix:
        print(f"☑️ DATS: nothing to fix ({len(all_targets)} files already aligned).")
        return

    if len(to_fix) >= 10:
        print(f"DATS: {len(to_fix)} files to fix (≥10).")
        if dry:
            print("(dry-run) would write DATS_<ts>.txt and prompt. Files:")
            for x in to_fix:
                print("  " + fmt(x))
            return
        txt = os.path.join(CONFIRM_DIR, f"DATS_{now_ts()}.txt")
        with open(txt, "w") as fh:
            for x in to_fix:
                fh.write(fmt(x) + "\n")
        print(f"👀 List written to:\n  {txt}")
        if input("🚦 Review it, then type yes to fix ALL: ").strip() != "yes":
            print("⚠️ Aborted; changed nothing.")
            return
        for x in to_fix:
            set_added(x[0], dtmap[x[0]])
        print(f"✅ Fixed {len(to_fix)} files.")
    else:
        near = [x for x in to_fix if x[3] < 24 * 3600]
        far = [x for x in to_fix if x[3] >= 24 * 3600]
        if dry:
            print(f"(dry-run) would fix {len(near)} file(s) <24h:")
            for x in near:
                print("  " + fmt(x))
            if far:
                print(f"(dry-run) would PROMPT for {len(far)} file(s) >=24h:")
                for x in far:
                    print("  " + fmt(x))
            return
        for x in near:
            set_added(x[0], dtmap[x[0]])
        if near:
            print(f"✅ Fixed {len(near)} file(s) (<24h):")
            for x in near:
                print("  " + fmt(x))
        if far:
            print(f"{len(far)} file(s) are ≥24h off — review:")
            for x in far:
                print("  " + fmt(x))
            if input("🚦 Type yes to also fix these: ").strip() == "yes":
                for x in far:
                    set_added(x[0], dtmap[x[0]])
                print(f"✅ Fixed {len(far)} file(s).")
            else:
                print("☑️ Left the ≥24h files unchanged.")


if __name__ == "__main__":
    main()
