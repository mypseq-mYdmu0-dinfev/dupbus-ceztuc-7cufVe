#!/usr/bin/env python3
"""Date Added & Date Created Preserver (PreToolUse + PostToolUse hook)

=== NON-CCSIM —— start of all you need to RUN it ===
WHAT: keeps a file's macOS Date Added and Date Created intact across an agent's
edit. The harness runs it on every write; you normally never invoke it.

CLI   python3 cscpt/DADC.py get <path>
      python3 cscpt/DADC.py set-added   <path> "YYYY-MM-DD HH:MM:SS"
      python3 cscpt/DADC.py set-created <path> "YYYY-MM-DD HH:MM:SS"

* Hook modes: `hook-capture` (PreToolUse), `hook-restore` (PostToolUse).
* ALWAYS exits 0 —— it can never block a tool call or break a turn.
* Brand-new files are left alone; only modification time legitimately moves.
* Applies everywhere: no folder, repo, or filename filter.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
* THE DEFECT IT EXISTS FOR: Claude Code's Edit/Write tools do not modify a file
  in place —— they REPLACE it. The inode changes, so macOS stamps the result as
  newly added AND newly created. Measured on a real file: one Edit moved the
  inode and threw both dates forward to "now", whilst a file edited by the
  owner's own editor (which writes in place) kept its true dates. Only
  modification time should ever have moved.
* WHY THERE IS NO PATH SCOPE, and why one must not be reintroduced: the
  predecessor restored Date Added under two folders only and never touched Date
  Created at all, so outside those folders BOTH attributes died on every agent
  edit and Date Created died EVERYWHERE. These attributes should be TRUE
  everywhere; restoring metadata cannot corrupt content; and the unfiltered
  status quo already destroys them, so there is no worse state to reach. A
  folder list here would only decide which files keep lying.
* SHAPE: two phases. `hook-capture` on PreToolUse reads both dates and stashes
  them; `hook-restore` on PostToolUse writes them back and deletes the stash.
  The stash is a JSON file in the OS temp dir, named by SHA-1 of the resolved
  path, holding `{path, added, created, at}`.
* NEW FILES ARE UNTOUCHABLE, deliberately, and by two independent mechanisms:
  capture stashes nothing when the path does not already exist, and restore
  acts only on a stash it can read. Freezing a genuinely new file's dates would
  be a fresh bug wearing the old one's clothes. Capture additionally DELETES any
  stale stash for a path that no longer exists —— otherwise a file deleted and
  recreated at the same path would inherit the dead file's dates.
* STASH_TTL exists because capture and restore are seconds apart in practice, so
  a surviving stash means the write never landed (blocked by another hook,
  permission denied, process killed). Such a stash is ignored and removed; a
  cheap sweep in capture stops a globally-registered hook growing the temp dir
  without bound.
* IDENTITY: both the stash key and the syscall target are `os.path.realpath`, so
  the two phases always agree on one file. If the tool replaced a symlink with a
  regular file the two realpaths differ, no stash matches, and nothing happens
  —— the safe outcome, reached without a special case for it.
* A relative `file_path` is joined to the payload's `cwd` and to nothing else. A
  user-level hook fires in EVERY project on this Mac, so the hook process's own
  cwd is not a safe base —— resolving against it could name a DIFFERENT real
  file, and this script then stamps dates onto a file the tool never touched.
  With no absolute `cwd` in the payload the target is simply ambiguous, so it
  returns None and does nothing. Never guess a target.
* CONCURRENCY, stated as the accepted limitation it is: two agents editing the
  SAME file at once can interleave capture/restore such that the second capture
  reads the first edit's fresh dates, and the true dates are lost. The repo's
  one-writer rule already forbids that overlap, and the predecessor had the same
  exposure; a lock here would buy nothing and could deadlock a turn.
* PAYLOAD KEYS: `tool_input.file_path` covers Edit/Write/MultiEdit; NotebookEdit
  sends `notebook_path`. The predecessor read `file_path` only, so it was
  registered for NotebookEdit and silently did nothing there.
* SYSCALLS: `getattrlist`/`setattrlist` with ATTR_CMN_CRTIME (0x200) and
  ATTR_CMN_ADDEDTIME (0x10000000). ONE call PER attribute on purpose —— a
  combined call packs values into the buffer in ASCENDING bit order, where a
  mis-ordered list silently writes the wrong date into the wrong field, and a
  per-attribute call also means one attribute failing cannot cost the other.
  The returned buffer is a `u_int32` length followed by a `{int64 sec, int64
  nsec}` timespec, hence the offset of 4.
* ORDER vs MODIFICATION TIME: restore runs AFTER the write, so mtime is "now"
  and the restored creation date is older —— no clamping. HFS+/APFS pull the
  creation date DOWN to the modification date when mtime is earlier, so never
  restore mtime here; modification time is the one date that SHOULD move.
* The Spotlight mirror xattr (`com.apple.metadata:kMDItemDateAdded`) is
  deliberately NOT written. Finder's Date Added column reads the live filesystem
  attribute, which is what this sets. `cscpt/set_dates.py` does refresh the
  mirror because it performs an explicit user-driven restamp; here most files
  carry no such xattr at all, and inventing one on every edit would ADD state
  rather than preserve it.
* FAIL-SAFE, without exception: every path is guarded and the process always
  exits 0. A hook that can fail is worse than no hook —— it would turn an
  unreadable payload, an unsupported filesystem (SMB/NFS expose no
  ATTR_CMN_ADDEDTIME) or a permissions error into a broken turn, in exchange for
  a cosmetic attribute. Even the libc load is guarded, so an import-time failure
  cannot produce a non-zero exit either.
* CLI misuse still PRINTS —— silence is right for a hook and useless for a human
  at a terminal —— but it too exits 0, so the invariant has no exception to
  remember. `set` is kept as an alias of `set-added` for anyone carrying over
  the predecessor's CLI habit.
* Pinned by `cp/ccsim/sandbox/dadc_regression_test.py`; run it after any edit.
* Registration lives in `~/.claude/settings.json` (user-level —— project-level
  hook registration is a silent no-op in the Claude Desktop app). Renaming or
  moving this file is therefore a WIRING change that no git diff will show.
* `cscpt/README.md` carries a one-line summary —— keep the two in step.
"""

import ctypes
import ctypes.util
import datetime
import hashlib
import json
import os
import select
import stat
import struct
import sys
import tempfile
import time

ATTR_BIT_MAP_COUNT = 5
ATTR_CMN_CRTIME    = 0x00000200
ATTR_CMN_ADDEDTIME = 0x10000000

STASH_DIR = os.path.join(tempfile.gettempdir(), "cc_dadc_stash")
STASH_TTL = 6 * 60 * 60  # seconds; a survivor means the write never landed

HOOK_MODES = ("hook-capture", "hook-restore")
USAGE = "get | set-added | set-created | hook-capture | hook-restore"

try:
    _libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
except Exception:  # pragma: no cover —— guarded so no exit can be non-zero
    _libc = None


class _attrlist(ctypes.Structure):
    _fields_ = [
        ("bitmapcount", ctypes.c_ushort),
        ("reserved",    ctypes.c_ushort),
        ("commonattr",  ctypes.c_uint),
        ("volattr",     ctypes.c_uint),
        ("dirattr",     ctypes.c_uint),
        ("fileattr",    ctypes.c_uint),
        ("forkattr",    ctypes.c_uint),
    ]


def _get_time(path, attr_bit):
    """One catalogue timestamp as epoch seconds; 0 when the attribute is unset."""
    if _libc is None:
        raise OSError("libc unavailable")
    al = _attrlist(ATTR_BIT_MAP_COUNT, 0, attr_bit, 0, 0, 0, 0)
    buf = ctypes.create_string_buffer(64)
    if _libc.getattrlist(path.encode(), ctypes.byref(al), buf, len(buf), 0) != 0:
        raise OSError(ctypes.get_errno(), "getattrlist failed", path)
    sec, _nsec = struct.unpack_from("qq", buf, 4)
    return sec


def _set_time(path, attr_bit, epoch):
    if _libc is None:
        raise OSError("libc unavailable")
    al = _attrlist(ATTR_BIT_MAP_COUNT, 0, attr_bit, 0, 0, 0, 0)
    data = struct.pack("qq", int(epoch), 0)
    cbuf = ctypes.create_string_buffer(data, len(data))
    if _libc.setattrlist(path.encode(), ctypes.byref(al), cbuf, len(data), 0) != 0:
        raise OSError(ctypes.get_errno(), "setattrlist failed", path)


def get_added(path):
    return _get_time(path, ATTR_CMN_ADDEDTIME)


def get_created(path):
    return _get_time(path, ATTR_CMN_CRTIME)


def set_added(path, epoch):
    _set_time(path, ATTR_CMN_ADDEDTIME, epoch)


def set_created(path, epoch):
    _set_time(path, ATTR_CMN_CRTIME, epoch)


# `isatty()` alone was NOT enough, which is why a bounded wait sits beside it: a
# caller holding an empty pipe open (a background runner, an agent shell) is not
# a terminal, so the old guard waved it through to a `read()` that never
# returned —— one such process was found still alive ten minutes on. Two seconds
# is far longer than a local payload write and far shorter than a lost session.
#
# AND READINESS IS NOT ARRIVAL. `/dev/null`, a closed descriptor and a pipe
# already at EOF are all READY —— a read on them returns at once, with nothing
# —— so a readiness-only test passes them straight through to a parse that
# fails, and the mode then does nothing in complete silence. An agent shell
# hands its children `/dev/null`, which is precisely where a hand invocation
# comes from, so that was the common case, not the exotic one. The emptiness of
# what actually arrived is therefore checked too, not merely whether something
# could be read.
_STDIN_WAIT_S = 2.0


def _no_payload():
    """The loud refusal. Exit status stays 0 by the header's FAIL-SAFE rule, so
    the MESSAGE is the only signal there is —— it must deny the pass outright."""
    mode = sys.argv[1] if len(sys.argv) > 1 else "hook-capture"
    sys.stderr.write(
        "DADC: no hook payload arrived on stdin, so NOTHING was preserved.\n"
        "`%s` is a hook mode driven by the harness, not a command you run by "
        "hand.\nFor a hand restamp use: %s\n" % (mode, USAGE))
    return {}


def _stdin_is_pipe():
    """True when stdin is the pipe or socket a harness hands a hook body.

    An EMPTY payload means opposite things on either side of this line. Over a
    PIPE it is the harness sending nothing, which must stay a silent no-op ——
    the FAIL-SAFE rule in the header allows no exception. Over `/dev/null`, a
    closed descriptor, a terminal or a plain file no payload was ever coming,
    which is a hand invocation and must be told so. An unknowable shape counts
    as a pipe, so an odd environment can only ever fail towards silence.
    """
    try:
        mode = os.fstat(sys.stdin.fileno()).st_mode
        return stat.S_ISFIFO(mode) or stat.S_ISSOCK(mode)
    except Exception:
        return True


def _payload():
    """The hook JSON on stdin, or {} for anything unreadable or unexpected.

    A hand invocation now gets a LOUD refusal where it used to get a silent
    `{}`. Doing nothing quietly looks exactly like having preserved the dates,
    and that ambiguity is what makes a missing payload dangerous rather than
    merely useless —— the same confusion that let a sibling hook's hang be
    filed as a clean pass. The exit status stays 0 (the header's FAIL-SAFE rule
    has no exception), so the MESSAGE, not the status, carries the warning.
    """
    try:
        if sys.stdin is None or sys.stdin.isatty() or not select.select(
                [sys.stdin], [], [], _STDIN_WAIT_S)[0]:
            return _no_payload()
        piped = _stdin_is_pipe()
        raw = sys.stdin.read()
        if not raw.strip():
            return {} if piped else _no_payload()
        data = json.loads(raw)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _target(data):
    """Absolute, symlink-resolved path the tool is writing, or None."""
    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    raw = None
    for key in ("file_path", "notebook_path", "path"):
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            raw = value
            break
    if not raw:
        return None
    if not os.path.isabs(raw):
        cwd = data.get("cwd")
        if not isinstance(cwd, str) or not os.path.isabs(cwd):
            return None  # never GUESS a target: see the ambiguity note above
        raw = os.path.join(cwd, raw)
    return os.path.realpath(raw)


def _stash_for(path):
    return os.path.join(STASH_DIR, hashlib.sha1(path.encode()).hexdigest())


def _drop(stash):
    try:
        os.remove(stash)
    except OSError:
        pass


def _sweep():
    """Remove stashes whose write never landed, so the temp dir stays bounded."""
    try:
        now = time.time()
        with os.scandir(STASH_DIR) as entries:
            for entry in entries:
                try:
                    if now - entry.stat().st_mtime > STASH_TTL:
                        _drop(entry.path)
                except OSError:
                    pass
    except OSError:
        pass


def hook_capture():
    path = _target(_payload())
    if not path:
        return
    _sweep()
    stash = _stash_for(path)
    if not os.path.isfile(path):
        _drop(stash)  # a new file must never inherit a dead one's dates
        return
    record = {"path": path, "at": int(time.time())}
    for name, reader in (("added", get_added), ("created", get_created)):
        try:
            record[name] = int(reader(path))
        except Exception:
            record[name] = 0
    if not record["added"] and not record["created"]:
        _drop(stash)
        return
    os.makedirs(STASH_DIR, exist_ok=True)
    tmp = "%s.%d.tmp" % (stash, os.getpid())
    try:
        with open(tmp, "w") as handle:
            json.dump(record, handle)
        os.replace(tmp, stash)  # atomic: a half-written stash must never be read
    except Exception:
        _drop(tmp)


def hook_restore():
    path = _target(_payload())
    if not path:
        return
    stash = _stash_for(path)
    try:
        with open(stash) as handle:
            record = json.load(handle)
    except Exception:
        # No stash (the ordinary new-file case) —— or one that exists but cannot
        # be read or parsed, which can never become useful, so bin it now rather
        # than leave the TTL sweep as its only cleaner.
        if os.path.exists(stash):
            _drop(stash)
        return
    try:
        if not isinstance(record, dict):
            return
        if int(time.time()) - int(record.get("at") or 0) > STASH_TTL:
            return
        if not os.path.isfile(path):
            return
        for name, writer in (("added", set_added), ("created", set_created)):
            value = record.get(name)
            try:
                if isinstance(value, int) and value > 0:
                    writer(path, value)
            except Exception:
                pass  # one attribute failing must not cost the other
    finally:
        _drop(stash)


def _fmt(sec):
    if not sec:
        return "none"
    return datetime.datetime.fromtimestamp(sec).strftime("%Y-%m-%d %H:%M:%S")


def _cli(argv):
    mode = argv[0]
    if mode == "get":
        print("Date Added:   %s" % _fmt(get_added(argv[1])))
        print("Date Created: %s" % _fmt(get_created(argv[1])))
    elif mode in ("set", "set-added", "set-created"):
        parsed = datetime.datetime.strptime(argv[2], "%Y-%m-%d %H:%M:%S")
        epoch = time.mktime(parsed.timetuple())
        (set_created if mode == "set-created" else set_added)(argv[1], epoch)
        print("set ok")
    else:
        print("DADC: unknown mode '%s' (%s)" % (mode, USAGE))


def main():
    argv = sys.argv[1:]
    try:
        if not argv:
            print("DADC: no mode given (%s)" % USAGE)
        elif argv[0] == "hook-capture":
            hook_capture()
        elif argv[0] == "hook-restore":
            hook_restore()
        else:
            _cli(argv)
    except Exception as exc:
        if not argv or argv[0] not in HOOK_MODES:
            print("DADC: %s: %s" % (type(exc).__name__, exc))
    sys.exit(0)  # absolute: a metadata nicety may never break a turn


if __name__ == "__main__":
    main()
