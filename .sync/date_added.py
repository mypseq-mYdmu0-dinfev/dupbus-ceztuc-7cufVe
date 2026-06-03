#!/usr/bin/env python3
"""Read/set a file's macOS "Date Added" (ATTR_CMN_ADDEDTIME) — the exact
attribute Finder's "Date Added" column uses (Finder reads the live FS attr, so
this works even when Spotlight/mdls lags).

CLI:
  python3 .sync/date_added.py get <path>
  python3 .sync/date_added.py set <path> "YYYY-MM-DD HH:MM:SS"   # local time

Hook modes (stdin = Claude Code hook JSON). They capture a file's Date Added
before an Edit/Write and restore it after, so editing a file under sessions/ or
seek/investigation/ never shifts its Date-Added ordering. New files (no prior
value) are left as-is. Always exit 0 so a tool call is never blocked.
  python3 .sync/date_added.py hook-capture   # wire to PreToolUse
  python3 .sync/date_added.py hook-restore   # wire to PostToolUse
"""
import sys, ctypes, ctypes.util, struct, time, datetime, os, json, hashlib, tempfile

ATTR_BIT_MAP_COUNT = 5
ATTR_CMN_ADDEDTIME = 0x10000000
libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
SCOPED = ("/sessions/", "/seek/investigation/")
STASH = os.path.join(tempfile.gettempdir(), "cc_da_stash")


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
    sec, _ = struct.unpack_from("qq", buf, 4)
    return sec


def set_added(path, epoch):
    al = attrlist(ATTR_BIT_MAP_COUNT, 0, ATTR_CMN_ADDEDTIME, 0, 0, 0, 0)
    data = struct.pack("qq", int(epoch), 0)
    cbuf = ctypes.create_string_buffer(data, len(data))
    if libc.setattrlist(path.encode(), ctypes.byref(al), cbuf, len(data), 0) != 0:
        raise OSError(ctypes.get_errno(), "setattrlist failed")


def _hook_path():
    try:
        data = json.load(sys.stdin)
        return (data.get("tool_input") or {}).get("file_path")
    except Exception:
        return None


def _stash_for(path):
    return os.path.join(STASH, hashlib.sha1(os.path.abspath(path).encode()).hexdigest())


def hook_capture():
    p = _hook_path()
    if not p or not any(s in p for s in SCOPED) or not os.path.exists(p):
        return
    os.makedirs(STASH, exist_ok=True)
    open(_stash_for(p), "w").write(str(get_added(p)))


def hook_restore():
    p = _hook_path()
    if not p:
        return
    s = _stash_for(p)
    if os.path.exists(s):
        try:
            set_added(p, int(open(s).read().strip()))
        finally:
            os.remove(s)


if __name__ == "__main__":
    try:
        cmd = sys.argv[1]
        if cmd == "get":
            v = get_added(sys.argv[2])
            print(datetime.datetime.fromtimestamp(v).strftime("%Y-%m-%d %H:%M:%S") if v else "none")
        elif cmd == "set":
            dt = datetime.datetime.strptime(sys.argv[3], "%Y-%m-%d %H:%M:%S")
            set_added(sys.argv[2], time.mktime(dt.timetuple()))
            print("set ok")
        elif cmd == "hook-capture":
            hook_capture()
        elif cmd == "hook-restore":
            hook_restore()
    except Exception:
        pass  # never block a tool call
    sys.exit(0)
