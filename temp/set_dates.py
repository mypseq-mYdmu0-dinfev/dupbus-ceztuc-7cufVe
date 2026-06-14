#!/usr/bin/env python3
"""Set a file's Created, Modified and Date-Added timestamps to one value.

Usage: python3 set_dates.py <YYYYMMDDHHmm> <path> [path ...]
The timestamp is interpreted in the machine's LOCAL timezone (Sydney here).
Sets ATTR_CMN_CRTIME (Created), ATTR_CMN_MODTIME (Modified) and
ATTR_CMN_ADDEDTIME (Date Added) in a single setattrlist() call.
"""
import ctypes, sys, time, os
from ctypes import Structure, c_ushort, c_uint, c_long, c_char_p, c_void_p, c_size_t, c_ulong, c_int, byref, sizeof

libc = ctypes.CDLL("/usr/lib/libSystem.dylib", use_errno=True)

class attrlist(Structure):
    _fields_ = [
        ("bitmapcount", c_ushort),
        ("reserved", c_ushort),
        ("commonattr", c_uint),
        ("volattr", c_uint),
        ("dirattr", c_uint),
        ("fileattr", c_uint),
        ("forkattr", c_uint),
    ]

class timespec(Structure):
    _fields_ = [("tv_sec", c_long), ("tv_nsec", c_long)]

ATTR_BIT_MAP_COUNT = 5
ATTR_CMN_CRTIME    = 0x00000200
ATTR_CMN_MODTIME   = 0x00000400
ATTR_CMN_ADDEDTIME = 0x10000000

libc.setattrlist.argtypes = [c_char_p, c_void_p, c_void_p, c_size_t, c_ulong]
libc.setattrlist.restype = c_int

def parse_ts(s):
    if len(s) != 12 or not s.isdigit():
        raise ValueError("timestamp must be YYYYMMDDHHmm (12 digits)")
    y, mo, d = int(s[0:4]), int(s[4:6]), int(s[6:8])
    h, mi = int(s[8:10]), int(s[10:12])
    return int(time.mktime((y, mo, d, h, mi, 0, 0, 0, -1)))

def set_dates(path, sec):
    al = attrlist()
    al.bitmapcount = ATTR_BIT_MAP_COUNT
    al.commonattr = ATTR_CMN_CRTIME | ATTR_CMN_MODTIME | ATTR_CMN_ADDEDTIME
    # buffer order follows the bitmap by increasing bit value:
    # CRTIME (0x200) -> MODTIME (0x400) -> ADDEDTIME (0x10000000)
    buf = (timespec * 3)()
    for i in range(3):
        buf[i].tv_sec = sec
        buf[i].tv_nsec = 0
    rc = libc.setattrlist(path.encode("utf-8"), byref(al), byref(buf), sizeof(buf), 0)
    if rc != 0:
        e = ctypes.get_errno()
        raise OSError(e, os.strerror(e), path)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    sec = parse_ts(sys.argv[1])
    for p in sys.argv[2:]:
        set_dates(p, sec)
        print("set", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(sec)), "->", p)
