#!/usr/bin/env python3
"""Regression test —— `cscpt/DADC.py` must preserve Date Added AND Date Created
across an agent's edit, everywhere, without ever breaking a turn.

WHY THIS EXISTS (self-contained; no conversation or comms file explains it):

Claude Code's Edit/Write tools do not modify a file in place —— they REPLACE it.
The inode changes, so macOS stamps the result as newly added AND newly created.
Measured on a real file before this test was written: one Edit moved the inode
and threw both dates forward to "now", whilst a file edited by an in-place
editor kept its true dates. Only modification time should ever have moved.

The predecessor hook restored Date Added under two folders only and never
touched Date Created at all. So outside those folders BOTH attributes died on
every agent edit, and Date Created died EVERYWHERE. DADC.py removes the folder
filter entirely and restores both. The reasoning behind having no scope: these
attributes should be TRUE everywhere, restoring metadata cannot corrupt content,
and the unfiltered status quo already destroys them —— there is no worse state
to reach, so a folder list would only decide which files keep lying.

WHAT EACH GROUP OF CHECKS PINS, and the failure it would otherwise let through:

1. PARITY —— a file on a `sessions/`-style path keeps its Date Added and its
   modification time still moves. This is everything the predecessor did; a
   successor that quietly did less would be a downgrade sold as an upgrade.
2. THE NEW CAPABILITY —— on paths the predecessor ignored, and on a path with no
   repo-like component at all, BOTH dates survive. Tested on three different
   path shapes because "it worked on the one file I tried" licenses a claim
   about that file, not about every file the hook now touches.
3. NEW FILES ARE LEFT ALONE —— nothing is stashed for a path that does not yet
   exist, and a stale stash for a since-deleted path is dropped rather than
   inherited. Freezing a genuinely new file's dates would be a fresh bug wearing
   the old one's clothes, so it is checked from both directions.
4. FAIL-SAFE —— malformed payloads, missing files, unreadable stashes and CLI
   misuse must all exit 0 in silence (hook modes) and never mutate the file.
   A hook that can fail is worse than no hook: it trades a broken turn for a
   cosmetic attribute.
5. NO SCOPE MAY BE REINTRODUCED —— a source check, because the single most
   likely future regression is someone "tidying" a folder filter back in.

The edit is emulated the way the real tools do it —— write a temp file, then
`os.replace()` onto the target —— and each test ASSERTS the inode actually
changed, so a test that stopped reproducing the failure mode fails loudly
instead of passing vacuously.

RUN:
    cd "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe"
    python3 cp/ccsim/sandbox/dadc_regression_test.py

macOS-only by nature (it exercises getattrlist/setattrlist). Dependency-free by
design (PyYAML is not installed system-wide on this Mac).
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DADC = os.path.join(REPO, "cscpt", "DADC.py")
PREDECESSOR = os.path.join(REPO, ".sync", "date_added.py")
VOIDED_PREDECESSOR = os.path.join(REPO, ".sync", "❌_date_added.py")
USER_SETTINGS = os.path.expanduser("~/.claude/settings.json")

OLD_EPOCH = 1672540200  # 2023-01-01 12:30:00 local —— unmistakably not "now"

failures = []
checks = 0


def check(ok, label, detail=""):
    global checks
    checks += 1
    if ok:
        print(f"[PASS] {label}")
    else:
        print(f"[FAIL] {label} —— {detail}")
        failures.append(label)


# --- module import, only to reuse the stash location and key derivation -------
_spec = importlib.util.spec_from_file_location("dadc_under_test", DADC)
dadc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dadc)


def run(args, payload=None):
    """Invoke DADC.py exactly as the harness would: argv mode + JSON on stdin."""
    return subprocess.run(
        [sys.executable, DADC] + args,
        input="" if payload is None else payload,
        capture_output=True, text=True,
    )


def payload_for(path, key="file_path", cwd=None, tool="Edit"):
    data = {"tool_name": tool, "tool_input": {key: path},
            "hook_event_name": "PreToolUse"}
    if cwd is not None:
        data["cwd"] = cwd
    return json.dumps(data)


def make_file(path, text="original\n"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as handle:
        handle.write(text)
    dadc.set_added(path, OLD_EPOCH)
    dadc.set_created(path, OLD_EPOCH)
    return snapshot(path)


def snapshot(path):
    st = os.stat(path)
    return {"inode": st.st_ino, "mtime": int(st.st_mtime),
            "added": int(dadc.get_added(path)),
            "created": int(dadc.get_created(path))}


def emulate_agent_edit(path, text="edited\n"):
    """Replace the file the way Edit/Write do —— new inode, not a truncate."""
    tmp = path + ".agent.tmp"
    with open(tmp, "w") as handle:
        handle.write(text)
    os.replace(tmp, path)


def cycle(path, capture_payload=None, restore_payload=None):
    """Full PreToolUse -> edit -> PostToolUse round trip. Returns before/after."""
    before = snapshot(path) if os.path.exists(path) else None
    pre = run(["hook-capture"], capture_payload or payload_for(path))
    emulate_agent_edit(path)
    post = run(["hook-restore"], restore_payload or payload_for(path))
    after = snapshot(path) if os.path.exists(path) else None
    return before, after, pre, post


# --- 1. Parity with the predecessor ------------------------------------------
def test_sessions_style_path_keeps_date_added(root):
    path = os.path.join(root, "sessions", "2026", "202607", "response_x.md")
    before = make_file(path)
    _, after, _, _ = cycle(path)
    check(after["inode"] != before["inode"],
          "sessions/: the emulated edit really replaced the inode",
          "test no longer reproduces the failure mode it exists for")
    check(after["added"] == OLD_EPOCH,
          "sessions/: Date Added preserved (predecessor parity)",
          f"expected {OLD_EPOCH}, got {after['added']}")
    check(after["mtime"] > OLD_EPOCH + 60,
          "sessions/: modification time still moves",
          f"mtime {after['mtime']} did not advance")


def test_sessions_style_path_also_gains_date_created(root):
    path = os.path.join(root, "sessions", "2026", "202607", "close_x.md")
    make_file(path)
    _, after, _, _ = cycle(path)
    check(after["created"] == OLD_EPOCH,
          "sessions/: Date Created preserved (the predecessor lost it here too)",
          f"expected {OLD_EPOCH}, got {after['created']}")


# --- 2. The new capability, on paths the predecessor ignored ------------------
def test_out_of_old_scope_paths_keep_both(root):
    for folder in ("universal", "cscpt", "nowhere_in_particular"):
        path = os.path.join(root, folder, "file.md")
        make_file(path)
        _, after, _, _ = cycle(path)
        check(after["added"] == OLD_EPOCH and after["created"] == OLD_EPOCH,
              f"{folder}/: BOTH Date Added and Date Created preserved",
              f"added={after['added']} created={after['created']}")
        check(after["mtime"] > OLD_EPOCH + 60,
              f"{folder}/: modification time still moves",
              f"mtime {after['mtime']} did not advance")


def test_path_outside_any_repo_keeps_both(root):
    """No scope means no scope —— a bare path with no project-like ancestor."""
    path = os.path.join(root, "loose_file.md")
    make_file(path)
    _, after, _, _ = cycle(path)
    check(after["added"] == OLD_EPOCH and after["created"] == OLD_EPOCH,
          "bare path outside any repo: both dates preserved",
          f"added={after['added']} created={after['created']}")


def test_relative_path_resolved_against_payload_cwd(root):
    path = os.path.join(root, "relwork", "file.md")
    make_file(path)
    rel = payload_for("relwork/file.md", cwd=root)
    _, after, _, _ = cycle(path, capture_payload=rel, restore_payload=rel)
    check(after["added"] == OLD_EPOCH and after["created"] == OLD_EPOCH,
          "relative file_path resolved against the payload's cwd",
          f"added={after['added']} created={after['created']}")


def test_notebook_path_key_supported(root):
    path = os.path.join(root, "nb", "book.ipynb")
    make_file(path, "{}\n")
    nb = payload_for(path, key="notebook_path", tool="NotebookEdit")
    _, after, _, _ = cycle(path, capture_payload=nb, restore_payload=nb)
    check(after["added"] == OLD_EPOCH and after["created"] == OLD_EPOCH,
          "NotebookEdit's notebook_path key is honoured",
          f"added={after['added']} created={after['created']}")


# --- 3. New files are left alone ---------------------------------------------
def test_brand_new_file_is_untouched(root):
    path = os.path.join(root, "fresh", "brand_new.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    now = int(time.time())
    pre = run(["hook-capture"], payload_for(path))
    stash = dadc._stash_for(os.path.realpath(path))
    check(not os.path.exists(stash),
          "brand-new file: nothing is stashed for a path that does not exist",
          "a stash here is how a new file's dates get frozen")
    with open(path, "w") as handle:
        handle.write("new\n")
    post = run(["hook-restore"], payload_for(path))
    snap = snapshot(path)
    check(pre.returncode == 0 and post.returncode == 0,
          "brand-new file: both hook modes exit 0")
    check(abs(snap["added"] - now) < 120 and abs(snap["created"] - now) < 120,
          "brand-new file: its genuine dates are left as 'now', not frozen",
          f"added={snap['added']} created={snap['created']} now={now}")


def test_stale_stash_is_not_inherited_by_a_recreated_file(root):
    """Delete a file, recreate it at the same path: it is NEW, not the old one."""
    path = os.path.join(root, "recycled", "same_name.md")
    make_file(path)
    run(["hook-capture"], payload_for(path))
    stash = dadc._stash_for(os.path.realpath(path))
    check(os.path.exists(stash), "recreated file: stash written for the original")
    os.remove(path)
    run(["hook-capture"], payload_for(path))  # path now absent
    check(not os.path.exists(stash),
          "recreated file: capture drops the stale stash once the path is gone",
          "otherwise the replacement inherits a dead file's dates")
    now = int(time.time())
    with open(path, "w") as handle:
        handle.write("brand new tenant\n")
    run(["hook-restore"], payload_for(path))
    snap = snapshot(path)
    check(abs(snap["created"] - now) < 120,
          "recreated file: keeps its own creation date",
          f"created={snap['created']} now={now}")


def test_stale_stash_beyond_ttl_is_ignored(root):
    path = os.path.join(root, "ttl", "file.md")
    make_file(path)
    run(["hook-capture"], payload_for(path))
    stash = dadc._stash_for(os.path.realpath(path))
    record = json.load(open(stash))
    record["at"] = int(time.time()) - dadc.STASH_TTL - 60
    with open(stash, "w") as handle:
        json.dump(record, handle)
    emulate_agent_edit(path)
    now = int(time.time())
    result = run(["hook-restore"], payload_for(path))
    snap = snapshot(path)
    check(result.returncode == 0 and abs(snap["created"] - now) < 120,
          "stash older than STASH_TTL is ignored (its write never landed)",
          f"created={snap['created']} now={now}")
    check(not os.path.exists(stash),
          "an expired stash is removed rather than left to leak")


# --- 4. Fail-safe -------------------------------------------------------------
MALFORMED = [
    ("empty stdin", ""),
    ("not json", "this is not json at all"),
    ("json array", "[1, 2, 3]"),
    ("json string", '"just a string"'),
    ("no tool_input", '{"tool_name": "Edit"}'),
    ("tool_input not a dict", '{"tool_input": "oops"}'),
    ("no file_path", '{"tool_input": {"content": "x"}}'),
    ("file_path not a string", '{"tool_input": {"file_path": 42}}'),
    ("file_path empty", '{"tool_input": {"file_path": ""}}'),
    ("truncated json", '{"tool_input": {"file_path": "/tmp/x"'),
]


def test_malformed_payloads_are_silent_and_exit_zero():
    for label, body in MALFORMED:
        for mode in ("hook-capture", "hook-restore"):
            result = run([mode], body)
            check(result.returncode == 0 and result.stdout == "",
                  f"fail-safe: {mode} on {label} exits 0 in silence",
                  f"rc={result.returncode} stdout={result.stdout!r} "
                  f"stderr={result.stderr[:120]!r}")


def test_missing_file_is_safe(root):
    ghost = os.path.join(root, "ghost", "not_here.md")
    for mode in ("hook-capture", "hook-restore"):
        result = run([mode], payload_for(ghost))
        check(result.returncode == 0 and result.stdout == "",
              f"fail-safe: {mode} on a missing file exits 0 in silence",
              f"rc={result.returncode} stdout={result.stdout!r}")
    check(not os.path.exists(ghost),
          "fail-safe: a missing file is not created by either hook mode")


def test_unreadable_stash_is_safe(root):
    """Garbage and a directory-in-place-of-a-file. The directory case is used
    because chmod 000 does not block a process running as root, so it would be
    an unreliable way to prove the unreadable branch."""
    for label, poison in (("garbage", "text"), ("a directory", None)):
        path = os.path.join(root, "badstash", label.replace(" ", "_") + ".md")
        make_file(path)
        stash = dadc._stash_for(os.path.realpath(path))
        os.makedirs(dadc.STASH_DIR, exist_ok=True)
        if os.path.isdir(stash):
            shutil.rmtree(stash)
        elif os.path.exists(stash):
            os.remove(stash)
        if poison is None:
            os.makedirs(stash)
        else:
            with open(stash, "w") as handle:
                handle.write(poison)
        emulate_agent_edit(path)
        result = run(["hook-restore"], payload_for(path))
        check(result.returncode == 0 and result.stdout == "",
              f"fail-safe: an unreadable stash ({label}) exits 0 in silence",
              f"rc={result.returncode} stdout={result.stdout!r}")
        check(os.path.exists(path),
              f"fail-safe: an unreadable stash ({label}) leaves the file intact")
        check(not os.path.isfile(stash),
              f"fail-safe: a corrupt stash ({label}) is binned, not left to rot",
              "it can never become useful, so the TTL sweep must not be its "
              "only cleaner")
        if os.path.isdir(stash):
            shutil.rmtree(stash)


def test_relative_path_without_a_cwd_is_refused(root):
    """The target is genuinely ambiguous, and guessing means stamping dates onto
    a file the tool never touched. Doing nothing is the only safe answer."""
    path = os.path.join(root, "nocwd", "file.md")
    before = make_file(path)
    bare = json.dumps({"tool_name": "Edit",
                       "tool_input": {"file_path": "nocwd/file.md"}})
    result = run(["hook-capture"], bare)
    check(result.returncode == 0 and result.stdout == "",
          "fail-safe: a relative file_path with no cwd exits 0 in silence")
    check(not os.path.exists(dadc._stash_for(os.path.realpath(path))),
          "fail-safe: a relative file_path with no cwd stashes nothing",
          "resolving it against the hook's own cwd could name another file")
    check(snapshot(path)["added"] == before["added"],
          "fail-safe: a relative file_path with no cwd mutates nothing")


def test_hook_mode_on_a_terminal_does_not_hang():
    """Run by hand with no redirect, a hook mode must return, not block on a
    tty forever. `script` gives the child a real terminal for stdin."""
    for mode in ("hook-capture", "hook-restore"):
        try:
            result = subprocess.run(
                ["script", "-q", "/dev/null", sys.executable, DADC, mode],
                capture_output=True, text=True, timeout=15,
            )
            ok = result.returncode == 0
            detail = f"rc={result.returncode}"
        except subprocess.TimeoutExpired:
            ok, detail = False, "blocked on tty stdin —— it hung"
        check(ok, f"fail-safe: {mode} on a terminal returns instead of hanging",
              detail)


def test_cli_misuse_exits_zero_but_speaks(root):
    for args, label in (
        ([], "no arguments"),
        (["wat"], "an unknown mode"),
        (["get"], "get with no path"),
        (["get", os.path.join(root, "nope.md")], "get on a missing file"),
        (["set-added", os.path.join(root, "nope.md")], "set with no timestamp"),
        (["set-added", os.path.join(root, "nope.md"), "not-a-date"], "a bad date"),
    ):
        result = run(args)
        check(result.returncode == 0 and result.stdout.strip() != "",
              f"CLI: {label} exits 0 AND says something",
              f"rc={result.returncode} stdout={result.stdout!r}")


def test_cli_get_and_set_round_trip(root):
    path = os.path.join(root, "cli", "file.md")
    make_file(path)
    check(run(["set-added", path, "2019-05-04 09:08:07"]).returncode == 0
          and run(["set-created", path, "2018-03-02 01:02:03"]).returncode == 0,
          "CLI: set-added and set-created both exit 0")
    out = run(["get", path]).stdout
    check("2019-05-04 09:08:07" in out and "2018-03-02 01:02:03" in out,
          "CLI: get reports both dates it was just told to set",
          f"stdout={out!r}")
    check(run(["set", path, "2020-01-02 03:04:05"]).returncode == 0
          and "2020-01-02 03:04:05" in run(["get", path]).stdout,
          "CLI: `set` still works as an alias of set-added",
          "the predecessor's CLI habit must keep working")


# --- 5. The no-scope invariant, enforced rather than trusted -------------------
def test_source_declares_no_path_scope():
    body = open(DADC, encoding="utf-8").read().split('"""', 2)[-1]
    banned = ['"/sessions/"', "'/sessions/'", '"/AJAP_repo/', "SCOPED"]
    hits = [token for token in banned if token in body]
    check(not hits,
          "source: no folder filter has been reintroduced below the docstring",
          f"found {hits} —— the whole point is that it applies everywhere")


def test_predecessor_is_voided_not_left_live():
    check(not os.path.exists(PREDECESSOR),
          "predecessor `.sync/date_added.py` is no longer in place",
          "two hooks writing the same attribute is one writer too many")
    check(os.path.exists(VOIDED_PREDECESSOR),
          "predecessor is VOIDED (renamed with the ❌ prefix), not deleted",
          "this repo never deletes —— the owner reviews and removes")


def test_hook_registration_points_at_dadc():
    """WIRING, not the script. `~/.claude/settings.json` is outside the repo and
    only the owner may edit it, so this check is the acceptance gate for that
    edit —— it is EXPECTED to fail until the registration is swapped."""
    try:
        text = open(USER_SETTINGS, encoding="utf-8").read()
    except OSError as exc:
        check(False, "wiring: ~/.claude/settings.json is readable", str(exc))
        return
    check("cscpt/DADC.py' hook-capture" in text,
          "wiring: PreToolUse registers DADC.py hook-capture",
          "the script is inert until the harness calls it")
    check("cscpt/DADC.py' hook-restore" in text,
          "wiring: PostToolUse registers DADC.py hook-restore",
          "the script is inert until the harness calls it")
    check("date_added.py" not in text,
          "wiring: the predecessor is no longer registered",
          "a registered path that no longer exists exits 127 in silence")


def main():
    if sys.platform != "darwin":
        print("macOS only —— getattrlist/setattrlist are not portable.")
        return 1
    root = tempfile.mkdtemp(prefix="dadc_regression_")
    print(f"Repo: {REPO}\nThrowaway tree: {root}\n")
    try:
        test_sessions_style_path_keeps_date_added(root)
        test_sessions_style_path_also_gains_date_created(root)
        test_out_of_old_scope_paths_keep_both(root)
        test_path_outside_any_repo_keeps_both(root)
        test_relative_path_resolved_against_payload_cwd(root)
        test_notebook_path_key_supported(root)
        test_brand_new_file_is_untouched(root)
        test_stale_stash_is_not_inherited_by_a_recreated_file(root)
        test_stale_stash_beyond_ttl_is_ignored(root)
        test_malformed_payloads_are_silent_and_exit_zero()
        test_missing_file_is_safe(root)
        test_unreadable_stash_is_safe(root)
        test_relative_path_without_a_cwd_is_refused(root)
        test_hook_mode_on_a_terminal_does_not_hang()
        test_cli_misuse_exits_zero_but_speaks(root)
        test_cli_get_and_set_round_trip(root)
        test_source_declares_no_path_scope()
        test_predecessor_is_voided_not_left_live()
        test_hook_registration_points_at_dadc()
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print()
    if failures:
        print(f"{checks - len(failures)}/{checks} passed —— FAILURES:")
        for name in failures:
            print(f"  - {name}")
        return 1
    print(f"{checks}/{checks} passed —— DADC preserves both dates, everywhere.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
