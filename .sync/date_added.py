#!/usr/bin/env python3
"""Read/set a file's macOS "Date Added" (ATTR_CMN_ADDEDTIME) — the exact
attribute Finder's "Date Added" column uses. Finder reads the live FS attr,
so this fixes ordering even when Spotlight/mdls lags.

Usage:
  python3 .sync/date_added.py get  <path>
  python3 .sync/date_added.py set  <path> "YYYY-MM-DD HH:MM:SS"   # local time
  python3 .sync/date_added.py reset <path>   # set Date Added = file's creation (birth) time
"""
import sys, ctypes, ctypes.util, struct, time, datetime, os

ATTR_BIT_MAP_COUNT = 5
ATTR_CMN_ADDEDTIME = 0x10000000
libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)


class attrlist(ctypes.Structure):
    _fields_ = [("bitmapcount", ctypes.c_ushort), ("reserved", ctypes.c_ushort),
                ("commonattr", ctypes.c_uint), ("volattr", ctypes.c_uint),
                ("dirattr", ctypes.c_uint), ("fileattr", ctypes.c_uint),
                ("forkattr", ctypes.c_uint)]


def get_added(path):
    al = attrlist(ATTR_BIT_MAP_COUNT, 0, ATTR_CMN_ADDEDTIME, 0, 0, 0, 0)
    buf = ctypes.create_string_buffer(64)
    if libc.getattrlist(path.encode(), ctypes.byref(al), buf, len(buf), 0) != 0:
        raise OSError(ctypes.get_errno(), "getattrlist failed")
    sec, _nsec = struct.unpack_from("qq", buf, 4)
    return sec


def set_added(path, epoch):
    al = attrlist(ATTR_BIT_MAP_COUNT, 0, ATTR_CMN_ADDEDTIME, 0, 0, 0, 0)
    data = struct.pack("qq", int(epoch), 0)
    cbuf = ctypes.create_string_buffer(data, len(data))
    if libc.setattrlist(path.encode(), ctypes.byref(al), cbuf, len(data), 0) != 0:
        raise OSError(ctypes.get_errno(), "setattrlist failed")


if __name__ == "__main__":
    cmd, path = sys.argv[1], sys.argv[2]
    if cmd == "get":
        s = get_added(path)
        print(datetime.datetime.fromtimestamp(s).strftime("%Y-%m-%d %H:%M:%S") if s else "none")
    elif cmd == "set":
        dt = datetime.datetime.strptime(sys.argv[3], "%Y-%m-%d %H:%M:%S")
        set_added(path, time.mktime(dt.timetuple()))
        print("set ok")
    elif cmd == "reset":
        set_added(path, os.stat(path).st_birthtime)
        print("reset to birth time ok")
    else:
        sys.exit("unknown command: " + cmd)
