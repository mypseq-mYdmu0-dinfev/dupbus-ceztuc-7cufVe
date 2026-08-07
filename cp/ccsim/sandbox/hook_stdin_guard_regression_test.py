#!/usr/bin/env python3
"""Regression test —— a hook body must never hang, and never fake a pass.

WHY THIS EXISTS (self-contained; no conversation or comms file explains it):

Every lint in `cscpt/` is a HOOK BODY. The harness pipes a JSON payload on
stdin and closes it; argv carries a mode word at most, never a file to check.
Run by hand the way a CLI would be —— `python3 cscpt/nlint.py some_file.md` ——
the payload read blocked FOREVER: stdin was still open, no payload was ever
coming, and the process simply waited. One such invocation was found alive ten
minutes after it started.

THE REAL DAMAGE IS NOT THE WASTED TIME. A hook that hangs prints nothing. A
hook that passes also prints nothing. The two are indistinguishable from the
caller's side, so the hang MANUFACTURES verification: a file was recorded as
"nlint clean" on the strength of a command that never linted anything and never
finished. In a repo whose whole discipline is "running a script by hand proves
the script and nothing else", a silent hang is the single most expensive
failure mode available, because it converts a missing check into a passing one.

TWO STDIN SHAPES HANG, AND ONLY ONE OF THEM IS A TERMINAL. `isatty()` alone is
not a sufficient guard —— `DADC.py` already had one and still hung, because a
caller that holds an EMPTY PIPE open (a background runner, an agent's shell) is
not a tty. So the guard is `isatty()` OR a bounded `select`, and this suite
checks BOTH shapes for every target. A fix tested only against a terminal would
have shipped with half the defect intact.

THE REFUSAL MUST BE LOUD AND NON-ZERO. Swapping the hang for a quiet `exit 0`
would be the same false pass wearing a different hat: the caller still sees
silence and still concludes "clean". Hence `test_refusal_is_loud` (stderr must
carry an explicit "nothing was checked/preserved") and `test_refusal_exit_code`
(non-zero, and specifically NOT 2 —— a 2 on Pre/PostToolUse BLOCKS the tool
call, and a hand invocation must never be able to block anything).

`DADC.py` is the one deliberate exception on exit code: its header states an
absolute, at length and with reasons, that every path exits 0 so a metadata
nicety can never break a turn. Its guard therefore refuses LOUDLY at exit 0 ——
the message, not the status, carries the warning. That exception is pinned here
so it stays a considered carve-out rather than drifting into an oversight.

AND THE PUBLISHED RECIPE IS EXERCISED, NOT ASSUMED. Each guard prints the
correct incantation. A recipe that no longer works would satisfy every other
check here whilst still leaving the next caller stuck, so
`test_published_recipe_actually_runs` executes the literal command each script
prints and checks it reaches the lint instead of bouncing off the guard.

KNOWN RESIDUAL, pinned so it cannot be forgotten: the five `*_hook.sh` shims
refuse on a terminal but still wait on a held-open empty pipe. Bounding that
wait means replacing `$(cat)` with `read -t` —— a bashism in files documented as
POSIX sh, and not byte-equivalent to `$(cat)` —— which is too much risk for a
gate that BLOCKS writes, on a path only a hand-invoker reaches. The `.py` bodies
those shims front are fully bounded, so the linting side is covered.
`test_shims_document_their_residual` keeps that reasoning in the files.

RUN:
    cd "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe"
    python3 cp/ccsim/sandbox/hook_stdin_guard_regression_test.py

Dependency-free by design (PyYAML is not installed system-wide on this Mac).
"""

import ast
import json
import os
import pty
import re
import subprocess
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
CSCPT = os.path.join(REPO, "cscpt")

# How long a target may take before we call it hung. The guard's own bounded
# wait is 2.0s, so this must exceed it comfortably without making the suite
# slow: a real refusal lands at ~2.1s, a hang never lands at all.
HANG_LIMIT = 6.0

# Python hook bodies, with the argv the harness passes (empty where none).
PY_HOOKS = [
    ("alint.py", []),
    ("clint.py", []),
    ("dlint_quick.py", []),
    ("flint.py", ["pre"]),
    ("hlint.py", []),
    ("mlint.py", []),
    ("nlint.py", []),
    ("plint.py", []),
    ("tlint.py", ["post"]),
]

# DADC is a hook body too, but exits 0 by a documented absolute (see above).
DADC = ("DADC.py", ["hook-capture"])

# The shell shims the harness actually invokes, with their interpreter and arg.
SH_HOOKS = [
    ("alint_hook.sh", "bash", []),
    ("dlint_hook.sh", "bash", []),
    ("flint_hook.sh", "sh", ["pre"]),
    ("nlint_hook.sh", "bash", []),
    ("tlint_hook.sh", "sh", ["post"]),
]

# A payload every target accepts as well-formed. Scope checks in these scripts
# fail OPEN, so this is enough to carry each one past the guard and into its
# real body —— which is the point: the guard must be invisible here.
LIVE_PAYLOAD = json.dumps({
    "session_id": "guardsuite",
    "cwd": REPO,
    "hook_event_name": "PostToolUse",
    "tool_name": "Write",
    "tool_input": {"file_path": os.path.join(CSCPT, "README.md")},
    "prompt": "probe",
})

# Any of these in stderr means the guard fired and nothing was checked.
REFUSAL_MARKERS = ("nothing was checked", "nothing was preserved")

checks = 0
failures = []


def check(condition, label, why):
    global checks
    checks += 1
    if not condition:
        failures.append("%s —— %s" % (label, why))


def cmd_for(name, argv):
    if name.endswith(".sh"):
        interp = "sh" if name in ("flint_hook.sh", "tlint_hook.sh") else "bash"
        return [interp, os.path.join(CSCPT, name)] + list(argv)
    return ["python3", os.path.join(CSCPT, name)] + list(argv)


def run_with_tty(argv):
    """Run with a real pty on stdin —— the shape a human at a terminal gets."""
    master, slave = pty.openpty()
    proc = subprocess.Popen(argv, stdin=slave, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    os.close(slave)
    try:
        out, err = proc.communicate(timeout=HANG_LIMIT)
        return proc.returncode, out.decode("utf-8", "replace"), \
            err.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        return None, "", ""
    finally:
        os.close(master)


def run_with_open_pipe(argv):
    """Run with a pipe nobody writes to and nobody closes —— NOT a tty, which
    is exactly why an `isatty()`-only guard misses it."""
    read_fd, write_fd = os.pipe()
    proc = subprocess.Popen(argv, stdin=read_fd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    os.close(read_fd)
    started = time.time()
    try:
        while time.time() - started < HANG_LIMIT:
            if proc.poll() is not None:
                return proc.returncode, proc.stdout.read().decode(
                    "utf-8", "replace"), proc.stderr.read().decode(
                    "utf-8", "replace")
            time.sleep(0.05)
        proc.kill()
        proc.communicate()
        return None, "", ""
    finally:
        os.close(write_fd)


def run_piped(argv, payload=LIVE_PAYLOAD):
    """Run the way the harness does: payload written, stdin closed."""
    try:
        done = subprocess.run(argv, input=payload.encode(),
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=HANG_LIMIT * 4)
        return done.returncode, done.stdout.decode("utf-8", "replace"), \
            done.stderr.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return None, "", ""


def all_targets():
    for name, argv in PY_HOOKS:
        yield name, argv
    yield DADC
    for name, _interp, argv in SH_HOOKS:
        yield name, argv


# ---------------------------------------------------------------------------
# 1. NEITHER HANGING SHAPE MAY HANG
# ---------------------------------------------------------------------------
def test_terminal_invocation_refuses_fast():
    for name, argv in all_targets():
        rc, _out, _err = run_with_tty(cmd_for(name, argv))
        check(
            rc is not None,
            "%s exits on a terminal" % name,
            "it hung with stdin on a tty; silence from a hang reads exactly "
            "like silence from a clean pass, so the caller records a "
            "verification that never happened",
        )


def test_held_open_pipe_refuses_fast():
    # The shims are excluded ON PURPOSE —— see KNOWN RESIDUAL in the module
    # docstring and in each shim's own header. The bodies they front are what
    # a person actually runs by hand, and those are covered here.
    for name, argv in PY_HOOKS + [DADC]:
        rc, _out, _err = run_with_open_pipe(cmd_for(name, argv))
        check(
            rc is not None,
            "%s exits on a held-open empty pipe" % name,
            "it hung on a pipe that is NOT a tty —— the shape an `isatty()`-"
            "only guard waves straight through into a blocking read",
        )


# ---------------------------------------------------------------------------
# 2. THE REFUSAL MUST BE LOUD, AND MUST NOT MASQUERADE AS SUCCESS
# ---------------------------------------------------------------------------
def test_refusal_is_loud():
    for name, argv in all_targets():
        _rc, _out, err = run_with_tty(cmd_for(name, argv))
        low = err.lower()
        check(
            any(marker in low for marker in REFUSAL_MARKERS),
            "%s says outright that nothing was checked" % name,
            "a refusal the caller cannot see is the same false pass as the "
            "hang it replaced; the message must deny the pass explicitly",
        )


def test_refusal_exit_code():
    for name, argv in PY_HOOKS:
        rc, _out, _err = run_with_tty(cmd_for(name, argv))
        check(rc not in (0, None), "%s refuses non-zero" % name,
              "a quiet exit 0 would let a hand run be filed as a pass")
        check(rc != 2, "%s does not refuse with 2" % name,
              "2 BLOCKS the tool call on Pre/PostToolUse, and a hand "
              "invocation must never be able to block anything")
    for name, _interp, argv in SH_HOOKS:
        rc, _out, _err = run_with_tty(cmd_for(name, argv))
        check(rc not in (0, None), "%s refuses non-zero" % name,
              "a quiet exit 0 would let a hand run be filed as a pass")
        check(rc != 2, "%s does not refuse with 2" % name,
              "2 BLOCKS the tool call, and a hand run must not block")


def test_dadc_exception_is_loud_not_silent():
    """DADC keeps exit 0 by a documented absolute —— so its MESSAGE must carry
    the whole warning. Pinned so the carve-out stays deliberate."""
    name, argv = DADC
    rc, _out, err = run_with_tty(cmd_for(name, argv))
    check(rc == 0, "DADC.py still exits 0 on refusal",
          "its header states, with reasons, that no path may exit non-zero; "
          "changing that here would break the invariant silently")
    check("nothing was preserved" in err.lower(),
          "DADC.py refusal names the consequence",
          "at exit 0 the message is the ONLY signal, so it must say plainly "
          "that no dates were kept")


# ---------------------------------------------------------------------------
# 3. THE GUARD MUST BE INVISIBLE ON THE REAL (PIPED) PATH
# ---------------------------------------------------------------------------
def test_piped_payload_is_untouched():
    for name, argv in all_targets():
        rc, _out, err = run_piped(cmd_for(name, argv))
        check(rc is not None, "%s completes on a piped payload" % name,
              "the guard must never stall the path the harness uses")
        low = err.lower()
        check(
            not any(marker in low for marker in REFUSAL_MARKERS),
            "%s does not refuse a real piped payload" % name,
            "a guard that fires under the harness would disarm the lint —— "
            "far worse than the hang it was added to fix",
        )


def test_guard_runs_before_the_payload_read():
    """Structural: a guard placed after the read would never get to run."""
    for name, _argv in PY_HOOKS:
        text = open(os.path.join(CSCPT, name)).read()
        match = re.search(r"^def main\(.*?\):\n(?:    \"\"\".*?\"\"\"\n)?(.*)$",
                          text, re.M | re.S)
        check(match is not None, "%s has a recognisable main()" % name,
              "the guard's placement cannot be verified without one")
        if not match:
            continue
        body = match.group(1)
        guard_at = body.find("_require_hook_payload(")
        read_at = body.find("json.load(sys.stdin)")
        check(guard_at != -1, "%s calls the guard in main()" % name,
              "a defined-but-uncalled guard protects nothing")
        check(0 <= guard_at < read_at, "%s guards BEFORE reading stdin" % name,
              "after the read the process is already blocked, so the guard "
              "would never execute")


# ---------------------------------------------------------------------------
# 4. THE PUBLISHED RECIPE MUST ACTUALLY WORK
# ---------------------------------------------------------------------------
HOWTO_RE = re.compile(r"^_HOOK_STDIN_HOWTO = \(\n(.*?)^\)\n", re.M | re.S)


def published_recipe(name):
    text = open(os.path.join(CSCPT, name)).read()
    match = HOWTO_RE.search(text)
    if not match:
        return None
    return ast.literal_eval("(" + match.group(1) + ")")


def test_every_py_hook_publishes_a_recipe():
    for name, _argv in PY_HOOKS:
        recipe = published_recipe(name)
        check(bool(recipe), "%s publishes a hand-invocation recipe" % name,
              "telling a caller it is holding the tool wrong, without saying "
              "how to hold it right, just moves the dead end")


def test_published_recipe_actually_runs():
    """Run the literal command each script prints. A recipe that bounces off
    the guard is a recipe that does not work, however plausible it reads."""
    target = os.path.join(CSCPT, "README.md")
    for name, _argv in PY_HOOKS:
        recipe = published_recipe(name)
        if not recipe:
            continue
        # The runnable pipeline is the leading run of lines ending in `\`
        # plus the line that completes it; any lines after that are prose.
        lines = [ln for ln in recipe.split("\n") if ln.strip()]
        pipeline = []
        for line in lines:
            pipeline.append(line)
            if not line.rstrip().endswith("\\"):
                break
        command = "\n".join(pipeline).replace("/abs/file.md", target)
        done = subprocess.run(["bash", "-c", command], cwd=REPO,
                              stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=HANG_LIMIT * 4)
        low = done.stderr.decode("utf-8", "replace").lower()
        check(
            not any(marker in low for marker in REFUSAL_MARKERS),
            "%s's published recipe reaches the lint" % name,
            "the command the script itself prints was refused by the very "
            "guard that printed it —— the caller is left with no way in",
        )


def test_dlint_quick_points_at_the_full_linter():
    """The false pass happened whilst trying to lint prose by hand. The one
    thing that guard must say is which tool DOES lint prose by hand."""
    recipe = published_recipe("dlint_quick.py") or ""
    check("dlint.py --quick" in recipe,
          "dlint_quick.py names the FULL linter as the hand tool",
          "a caller reaching for a prose lint needs the working command, not "
          "only the news that this one is not it")


# ---------------------------------------------------------------------------
# 5. THE RESIDUAL MUST STAY WRITTEN DOWN
# ---------------------------------------------------------------------------
def test_shims_document_their_residual():
    for name, _interp, _argv in SH_HOOKS:
        text = open(os.path.join(CSCPT, name)).read()
        check("KNOWN RESIDUAL" in text,
              "%s records its held-open-pipe residual" % name,
              "an undocumented known gap is indistinguishable from an "
              "oversight, and the next editor cannot weigh what they cannot "
              "see")


# ---------------------------------------------------------------------------
# 6. READINESS IS NOT ARRIVAL —— THE SHAPE THE FIRST GUARD MISSED
# ---------------------------------------------------------------------------
# The first version of this guard tested whether stdin was READY. `/dev/null`,
# a closed descriptor and a plain file are all ready: a read returns at once,
# with nothing. So every one of them sailed through into a payload read that
# yielded zero bytes, a parse that failed, and a silent `exit 0` —— the SAME
# false pass as the hang, reached by a shorter route.
#
# THIS IS NOT A HYPOTHETICAL SHAPE. An agent shell runs its commands with
# `< /dev/null`, so `python3 cscpt/nlint.py some_file.md` typed by an agent
# landed on exactly it. Measured before the fix: 9 of the 10 python bodies and
# all 5 shims exited 0 in silence there, with and without a file argument.
#
# AND THE COUNTER-CONTRACT MUST SURVIVE THE CURE. An EMPTY PIPE means the
# HARNESS sent nothing, and every lint here fails OPEN on that by a contract
# its own suite pins (alint J4, clint no_stdin, hlint H10.6, plint R14.5, flint
# F16.7/T10.7, tlint F1). A guard that refused all emptiness broke six of them
# at once. `test_empty_pipe_still_fails_open` is that boundary, kept here so
# the two halves are read together and never re-traded one for the other.
def run_from_devnull(argv):
    """The shape an agent shell hands its children —— a character device that
    is ready, is not a tty, and delivers nothing."""
    done = subprocess.run(argv, stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=HANG_LIMIT * 4)
    return done.returncode, done.stdout.decode("utf-8", "replace"), \
        done.stderr.decode("utf-8", "replace")


def run_from_file(argv, path):
    """stdin redirected from a plain file —— what a caller tries next when the
    argument is ignored. Ready, not a tty, and not a payload."""
    with open(path, "rb") as handle:
        done = subprocess.run(argv, stdin=handle, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=HANG_LIMIT * 4)
    return done.returncode, done.stdout.decode("utf-8", "replace"), \
        done.stderr.decode("utf-8", "replace")


def test_devnull_stdin_refuses():
    for name, argv in all_targets():
        rc, _out, err = run_from_devnull(cmd_for(name, argv))
        low = err.lower()
        check(
            any(marker in low for marker in REFUSAL_MARKERS),
            "%s refuses when stdin is /dev/null" % name,
            "this is the shape an agent shell gives, so it is the ORDINARY "
            "hand invocation; before the fix it exited 0 in silence, which "
            "reads as a clean pass to whoever ran it",
        )
        if not name.startswith("DADC"):
            check(rc not in (0, None), "%s refuses non-zero on /dev/null" % name,
                  "a silent-looking exit 0 is the whole defect")


def test_file_argument_refuses_whatever_stdin_is():
    """The literal mistake: handing a hook body the file to check. No stdin
    shape may let that read as a pass —— not even a VALID payload alongside
    it, since the argument names one file and the payload another."""
    target = os.path.join(CSCPT, "README.md")
    for name, argv in PY_HOOKS:
        for label, kwargs in (("devnull", {"stdin": subprocess.DEVNULL}),
                              ("empty pipe", {"input": b""}),
                              ("real payload", {"input": LIVE_PAYLOAD.encode()})):
            done = subprocess.run(cmd_for(name, argv) + [target],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  timeout=HANG_LIMIT * 4, **kwargs)
            low = done.stderr.decode("utf-8", "replace").lower()
            check(
                any(marker in low for marker in REFUSAL_MARKERS)
                and done.returncode not in (0, None),
                "%s refuses a file argument (stdin=%s)" % (name, label),
                "argv naming a file is a caller treating a hook body as a "
                "CLI; the file to check arrives in the payload and the "
                "argument is silently discarded",
            )


def test_empty_pipe_still_fails_open():
    """THE BOUNDARY. An empty PIPE is the harness sending nothing, and every
    lint here must stay silent at exit 0 on it. Refusing that broke six pinned
    fail-open contracts the first time, so it is pinned from this side too."""
    for name, argv in all_targets():
        done = subprocess.run(cmd_for(name, argv), input=b"",
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=HANG_LIMIT * 4)
        noise = done.stdout.decode("utf-8", "replace").strip() or \
            done.stderr.decode("utf-8", "replace").strip()
        check(
            done.returncode == 0 and not noise,
            "%s fails OPEN on an empty pipe" % name,
            "an empty pipe is the HARNESS sending nothing, not a caller "
            "holding the tool wrong; a lint that shouts or exits non-zero "
            "there breaks the fail-open contract its own suite pins",
        )


def test_junk_argv_still_falls_through():
    """flint M5, restated here because the argv rule could quietly kill it: an
    UNRECOGNISED but path-less argument must fall through to the payload's
    `hook_event_name`, not be mistaken for a caller passing a file."""
    done = subprocess.run(
        ["python3", os.path.join(CSCPT, "flint.py"), "banana"],
        input=LIVE_PAYLOAD.encode(), stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, timeout=HANG_LIMIT * 4)
    low = done.stderr.decode("utf-8", "replace").lower()
    check(
        done.returncode == 0 and not any(m in low for m in REFUSAL_MARKERS),
        "flint.py still tolerates a junk, path-less argv",
        "flint deliberately falls back to hook_event_name when argv makes no "
        "sense (its own suite, M5); a guard that refused every unknown "
        "argument would delete that fallback",
    )


def test_guard_distinguishes_pipe_from_not_a_pipe():
    """Structural: the discriminator must be IN the file, not in this test."""
    for name, _argv in PY_HOOKS:
        text = open(os.path.join(CSCPT, name)).read()
        check("S_ISFIFO" in text, "%s inspects the stdin FILE TYPE" % name,
              "readiness cannot tell a harness pipe from /dev/null; only the "
              "descriptor's type can, and without it the guard is blind to "
              "the shape that produced the false pass")
    for name, _interp, _argv in SH_HOOKS:
        text = open(os.path.join(CSCPT, name)).read()
        check("-p /dev/stdin" in text, "%s inspects the stdin FILE TYPE" % name,
              "same reason as the python bodies —— `[ -t 0 ]` alone cannot "
              "see /dev/null")


def main():
    print("Repo: %s" % REPO)
    print("Targets: %d python bodies + DADC + %d shims\n"
          % (len(PY_HOOKS), len(SH_HOOKS)))
    test_terminal_invocation_refuses_fast()
    test_held_open_pipe_refuses_fast()
    test_refusal_is_loud()
    test_refusal_exit_code()
    test_dadc_exception_is_loud_not_silent()
    test_piped_payload_is_untouched()
    test_guard_runs_before_the_payload_read()
    test_every_py_hook_publishes_a_recipe()
    test_published_recipe_actually_runs()
    test_dlint_quick_points_at_the_full_linter()
    test_shims_document_their_residual()
    test_devnull_stdin_refuses()
    test_file_argument_refuses_whatever_stdin_is()
    test_empty_pipe_still_fails_open()
    test_junk_argv_still_falls_through()
    test_guard_distinguishes_pipe_from_not_a_pipe()
    if failures:
        print("%d/%d passed —— FAILURES:" % (checks - len(failures), checks))
        for item in failures:
            print("  - %s" % item)
        return 1
    print("%d/%d passed —— no hook body hangs, and no refusal can pass for a "
          "pass." % (checks, checks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
