#!/usr/bin/env python3
"""Regression test for nscpt/fury_unmounted.sh — the ~/.claude rescue script.

WHY this test exists (coding.md: "pin EVERY fixed bug w/ a regression test
encoding the exact failing scenario", and "'exists + unit-tested' != done").
The script's whole value is that a non-expert can run it under stress after a
FURY-unmounted event, so two properties must be mechanically guaranteed, never
merely intended:

  A. IT NEVER DESTROYS. The one prior migration on this Mac that ran
     `rm -rf SRC && ln -s DST SRC` gutted ~34,500 files when the `rm` failed
     half-way and the `&&` skipped the `ln -s`. The rescue script therefore
     RENAMES a stray directory aside and never removes one. F5 proves the stray
     survives byte-for-byte under a `.stray-<TS>` name, and F5b proves it again
     for a stray that carries auto-memory (the one thing no repo can restore).

  B. IT NEVER FAKES A FIX. A symlink pointing at an absent volume looks healthy
     to every subsequent check whilst Claude silently runs with no hooks and no
     memory — exactly the invisible failure the hook system exists to prevent.
     F1/F1b/F9 prove the script refuses to link when the drive is absent or
     carries no .claude, and leaves the filesystem untouched.

The remaining cases pin the detection matrix (healthy / wrong target / stray /
missing / leftover mount point), idempotency (F7 — a second run must not mint a
second stray), and the hook-liveness verification (F10 — a registration whose
command file no longer exists must FAIL, because such a hook exits 127 and the
harness carries on in total silence).

Self-contained: every case builds a throwaway HOME and a throwaway stand-in for
the FURY volume under a temp dir, and drives the REAL script end-to-end through
its actual command-line contract. The live ~/.claude is never touched — the
script reads HOME and FURY_VOL from the environment, and FURY_SELFTEST=1 tells
it to take the mount answer from FURY_TEST_MOUNTED (a test cannot mount a real
volume) and to skip the running-Claude guard (no running Claude can be using a
sandbox HOME). Run directly:

    python3 "cp/ccsim/sandbox/fury_unmounted_regression_test.py"

Exits 0 if every case matches its expected verdict, 1 otherwise (with a
per-case PASS/FAIL report, and the raw output on any FAIL so a break is
diagnosable without re-running by hand).
"""
import os
import shutil
import subprocess
import sys
import tempfile

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", ".."))
SCRIPT = os.path.join(REPO_ROOT, "nscpt", "fury_unmounted.sh")

# A hook command that certainly resolves on any Mac, so the "all hooks alive"
# path is exercised without depending on this repo's own file layout.
LIVE_HOOK_CMD = "/bin/echo hook"
DEAD_HOOK_CMD = "/nonexistent/path/to/a/renamed_lint.py"

SETTINGS_TEMPLATE = """{
  "someUnrelatedPreference": true,
  "hooks": {
    "PostToolUse": [
      {"matcher": "Edit|Write", "hooks": [{"type": "command", "command": "%s"}]}
    ]
  }
}
"""


class Sandbox:
    """A throwaway HOME + stand-in volume, torn down on exit."""

    def __init__(self, mounted=True, volume_dir=True, claude_dir=True,
                 hook_cmd=LIVE_HOOK_CMD):
        self.root = tempfile.mkdtemp(prefix="fury_unmounted_test_")
        self.home = os.path.join(self.root, "home")
        self.vol = os.path.join(self.root, "VOLUME")
        self.target = os.path.join(self.vol, ".claude")
        self.link = os.path.join(self.home, ".claude")
        self.mounted = mounted
        os.makedirs(self.home)
        if volume_dir:
            os.makedirs(self.vol)
        if volume_dir and claude_dir:
            os.makedirs(self.target)
            with open(os.path.join(self.target, "settings.json"), "w") as f:
                f.write(SETTINGS_TEMPLATE % hook_cmd)
            os.makedirs(os.path.join(self.target, "projects"))

    def env(self):
        e = dict(os.environ)
        e["HOME"] = self.home
        e["FURY_VOL"] = self.vol
        e["FURY_SELFTEST"] = "1"
        e["FURY_TEST_MOUNTED"] = "yes" if self.mounted else "no"
        return e

    def run(self):
        return subprocess.run(["bash", SCRIPT], env=self.env(),
                              capture_output=True, text=True, timeout=60)

    def strays(self):
        return sorted(n for n in os.listdir(self.home)
                      if n.startswith(".claude.stray-"))

    def link_state(self):
        """('symlink'|'dir'|'file'|'absent', readlink target or '')."""
        if os.path.islink(self.link):
            return "symlink", os.readlink(self.link)
        if os.path.isdir(self.link):
            return "dir", ""
        if os.path.exists(self.link):
            return "file", ""
        return "absent", ""

    def close(self):
        shutil.rmtree(self.root, ignore_errors=True)


def _report(label, ok, r, notes):
    print("[%s] %s" % ("PASS" if ok else "FAIL", label))
    for n in notes:
        print("        %s" % n)
    if not ok:
        print("        exit=%s" % r.returncode)
        print("        stdout=%r" % r.stdout)
        print("        stderr=%r" % r.stderr)
    return ok


def case_f1():
    """Drive absent, mount point gone -> refuse, change nothing."""
    sb = Sandbox(mounted=False, volume_dir=False, claude_dir=False)
    try:
        r = sb.run()
        state, _ = sb.link_state()
        ok = (r.returncode == 1
              and "NOT MOUNTED" in r.stdout
              and "STOPPED" in r.stdout
              and state == "absent")
        return _report("F1 — drive absent: refuses, creates no symlink", ok, r,
                       ["link state after run: %s" % state])
    finally:
        sb.close()


def case_f1b():
    """Drive absent but the mount-point FOLDER survived on the internal disk.

    This is the dangerous variant: anything following ~/.claude would read and
    write a decoy on the internal disk instead of failing loudly. The script
    must name it and still refuse to act.
    """
    sb = Sandbox(mounted=False, volume_dir=True, claude_dir=True)
    try:
        r = sb.run()
        state, _ = sb.link_state()
        ok = (r.returncode == 1
              and "LEFTOVER" in r.stdout
              and "decoy" in r.stdout
              and state == "absent")
        return _report("F1b — leftover mount point: warns about the decoy, "
                       "still refuses", ok, r,
                       ["link state after run: %s" % state])
    finally:
        sb.close()


def case_f2():
    """Already correct -> healthy, idempotent no-op."""
    sb = Sandbox()
    try:
        os.symlink(sb.target, sb.link)
        r = sb.run()
        state, tgt = sb.link_state()
        ok = (r.returncode == 0
              and "HEALTHY" in r.stdout
              and state == "symlink" and tgt == sb.target
              and sb.strays() == [])
        return _report("F2 — already correct: HEALTHY, nothing renamed", ok, r,
                       ["strays: %s" % sb.strays()])
    finally:
        sb.close()


def case_f4():
    """Symlink pointing somewhere else -> repointed."""
    sb = Sandbox()
    try:
        other = os.path.join(sb.root, "elsewhere")
        os.makedirs(other)
        os.symlink(other, sb.link)
        r = sb.run()
        state, tgt = sb.link_state()
        ok = (r.returncode == 0
              and "REPAIRED" in r.stdout
              and state == "symlink" and tgt == sb.target
              and os.path.isdir(other))          # the old target is untouched
        return _report("F4 — wrong target: repointed, old target untouched",
                       ok, r, ["now -> %s" % tgt])
    finally:
        sb.close()


def case_f5():
    """A real folder replaced the symlink -> RENAMED aside, never deleted."""
    sb = Sandbox()
    try:
        os.makedirs(os.path.join(sb.link, "projects", "slug"))
        marker = os.path.join(sb.link, "projects", "slug", "written_offline.jsonl")
        with open(marker, "w") as f:
            f.write("data written while the drive was away\n")
        r = sb.run()
        state, tgt = sb.link_state()
        strays = sb.strays()
        preserved = (len(strays) == 1 and os.path.isfile(os.path.join(
            sb.home, strays[0], "projects", "slug", "written_offline.jsonl")))
        content_ok = preserved and open(os.path.join(
            sb.home, strays[0], "projects", "slug",
            "written_offline.jsonl")).read() == \
            "data written while the drive was away\n"
        ok = (r.returncode == 0
              and "REPAIRED" in r.stdout
              and state == "symlink" and tgt == sb.target
              and preserved and content_ok
              and "Stray preserved" in r.stdout)
        return _report("F5 — stray folder: RENAMED aside with contents intact "
                       "(never deleted)", ok, r,
                       ["strays: %s" % strays,
                        "stray file preserved: %s" % preserved])
    finally:
        sb.close()


def case_f5b():
    """A stray carrying auto-memory must be flagged before it is moved.

    The auto-memory under projects/*/memory/ is the one thing on the drive that
    no repo and no cloud copy can restore, so the user has to be told it is in
    the stray rather than silently inheriting a renamed folder.
    """
    sb = Sandbox()
    try:
        mem = os.path.join(sb.link, "projects", "slug", "memory")
        os.makedirs(mem)
        with open(os.path.join(mem, "MEMORY.md"), "w") as f:
            f.write("# Memory Index\n")
        r = sb.run()
        strays = sb.strays()
        kept = (len(strays) == 1 and os.path.isfile(os.path.join(
            sb.home, strays[0], "projects", "slug", "memory", "MEMORY.md")))
        ok = (r.returncode == 0
              and "auto-memory" in r.stdout
              and kept)
        return _report("F5b — stray with auto-memory: flagged and preserved",
                       ok, r, ["memory survived in stray: %s" % kept])
    finally:
        sb.close()


def case_f6():
    """Nothing at ~/.claude at all -> symlink created."""
    sb = Sandbox()
    try:
        r = sb.run()
        state, tgt = sb.link_state()
        ok = (r.returncode == 0 and "REPAIRED" in r.stdout
              and state == "symlink" and tgt == sb.target)
        return _report("F6 — missing: symlink created", ok, r,
                       ["now -> %s" % tgt])
    finally:
        sb.close()


def case_f7():
    """Re-running after a repair must be a clean no-op, not a second stray."""
    sb = Sandbox()
    try:
        os.makedirs(sb.link)
        first = sb.run()
        second = sb.run()
        strays = sb.strays()
        ok = (first.returncode == 0 and second.returncode == 0
              and "REPAIRED" in first.stdout
              and "HEALTHY" in second.stdout
              and len(strays) == 1)
        return _report("F7 — idempotent: second run is HEALTHY, no second "
                       "stray", ok, second, ["strays: %s" % strays])
    finally:
        sb.close()


def case_f9():
    """Drive mounted but carrying no .claude -> refuse (do not link to it)."""
    sb = Sandbox(claude_dir=False)
    try:
        r = sb.run()
        state, _ = sb.link_state()
        ok = (r.returncode == 1
              and "STOPPED" in r.stdout
              and "doomsday" in r.stdout
              and state == "absent")
        return _report("F9 — mounted but no .claude on it: refuses to link",
                       ok, r, ["link state after run: %s" % state])
    finally:
        sb.close()


def case_f10():
    """A registered hook whose command file is gone must be reported DEAD.

    Such a hook exits 127 and the harness carries on in silence, so a script
    that only checked "settings.json exists" would hand back a false all-clear.
    """
    sb = Sandbox(hook_cmd=DEAD_HOOK_CMD)
    try:
        os.symlink(sb.target, sb.link)
        r = sb.run()
        ok = (r.returncode == 1
              and "DEAD" in r.stdout
              and "STILL BROKEN" in r.stdout
              and "hooks_user_settings.reference.json" in r.stdout)
        return _report("F10 — hook command path missing: reported DEAD, not a "
                       "false all-clear", ok, r, [])
    finally:
        sb.close()


def case_f11():
    """The live-probe instruction must always be printed.

    Every check the script can make is a FILE check; only editing the probe
    file proves the harness actually invokes the hooks. Losing that closing
    instruction would quietly turn the script into the very kind of
    self-deception the hook guide was written to stop.
    """
    sb = Sandbox()
    try:
        os.symlink(sb.target, sb.link)
        r = sb.run()
        ok = ("hook_probe_response_.md" in r.stdout
              and "BLOCKS" in r.stdout)
        return _report("F11 — always prints the one-step live hook probe",
                       ok, r, [])
    finally:
        sb.close()


def main():
    if not os.path.isfile(SCRIPT):
        print("FAIL: script not found at %s" % SCRIPT)
        return 1
    syntax = subprocess.run(["bash", "-n", SCRIPT], capture_output=True,
                            text=True)
    if syntax.returncode != 0:
        print("FAIL: bash -n rejected the script:\n%s" % syntax.stderr)
        return 1
    print("[PASS] F0 — bash -n accepts the script")

    results = [True]
    for case in (case_f1, case_f1b, case_f2, case_f4, case_f5, case_f5b,
                 case_f6, case_f7, case_f9, case_f10, case_f11):
        results.append(case())

    passed = sum(1 for r in results if r)
    print("\n%d/%d passed" % (passed, len(results)))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
