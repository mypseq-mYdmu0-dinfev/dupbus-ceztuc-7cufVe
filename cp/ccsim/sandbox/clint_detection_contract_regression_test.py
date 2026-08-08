#!/usr/bin/env python3
"""Regression test for cscpt/clint.py's ALWAYS-YELLOW demotion.

RENAMED from `clint_always_red_regression_test.py`: that name pinned clint's
PRIOR rewrite (the always-blocking "ALWAYS RED" policy); this file now pins
the policy's own successor, the ALWAYS-YELLOW demotion, so the old name had
stopped describing what the suite actually tests. Whoever commits this
should still keep the rename and the content rewrite in SEPARATE commits
where practical (coding.md § Git Discipline: a rename plus a heavy edit in
one commit permanently severs the file's history, since git re-detects
renames by content similarity rather than storing them).

WHY this test exists (coding.md: "a fix without its test is unfinished").
clint.py used to BLOCK (exit 2) on every chat-prose breach -- the "ALWAYS RED"
policy this file once pinned. That policy fired exactly as designed and was
reversed BECAUSE it worked: every block forced one more model turn, and once
nothing new was left to declare in that extra turn, the agent resolved the
deadlock by re-emitting its declaration batch -- exactly the breach being
enforced against. Observed repeatedly, across sessions, as duplicate chapter
markers and increasingly erratic turn-end behaviour. The owner ordered every
RED block DEMOTED to a YELLOW warning: clint's exit code is now
UNCONDITIONALLY 0, and a breach is an exit-0 `{"systemMessage": ...}` JSON on
stdout shown to the USER plus a log line -- never anything the model sees or
can react to (a Stop hook's exit-0 output never reaches the model; see
`cp/ccsim/hook_guide.md` § Which Channel Reaches The Model). This test pins:

  A. NO CEILING, STILL -- three successive breaches under ONE promptId each
     get their own log line and their own exit 0; nothing suppresses the 2nd
     or 3rd (the old ledger this once guarded against is still gone).
  B. THE RETIRED LOOP GUARD IS INERT, AND HARMLESSLY SO -- `stop_hook_active`
     and an injected "Stop hook feedback:" continuation line USED TO withhold
     the block entirely (tagged `loop_guard`); now that nothing blocks, both
     signals are simply ignored and a breach in that situation logs its
     ordinary granular `yellow:` class like any other turn. The SCAN BOUNDARY
     behaviour the guard used to share context with (a feedback line still
     opens a fresh boundary, so only text AFTER it is in scope) is separately
     pinned here too.
  C. the `yn` exemption, using the three REAL prompts mined from this Mac's
     own transcripts (coding.md: "mine historical/real data for fixtures") --
     unchanged by the demotion (it was never a "block", just a skip), so
     still exempt outright and still exit 0.
  D. the `DATS` exemption's exact boundaries -- unchanged in shape; the
     negative cases (too many words, a 2nd line) now exit 0 like everything
     else, but MUST still log their own `yellow:` class rather than being
     silently swallowed as if exempt.
  E. harness-authored assistant text (`isApiErrorMessage`) never counts as a
     breach, since the model did not write it -- unaffected by the demotion.
  F. READER mode -- a session whose cwd is exactly the parent `GitHub/`
     folder still owes ZERO chat text, so a declaration glyph there still
     logs a breach (now `yellow:reader`, exit 0, never a block); sibling
     repos under `GitHub/` still are NOT dragged into that rule.
  G. every fail-safe path still exits 0 (malformed payload, out-of-scope,
     missing transcript) -- unaffected; these never blocked in the first
     place.
  I. the WARNING message -- delivered via an exit-0 `{"systemMessage": ...}`
     JSON on STDOUT (never stderr, never exit 2), reaches the user in BOTH
     modes, and pins: present, delivered on EVERY breach class identically,
     REPO's message still names `response_` as a courtesy hint (now for the
     human reading it afterwards, not a remedy the agent could act on -- the
     agent never reads this message at all), glyph-free, digit-free bar a
     protocol section reference, class-free, REPO vs READER differ
     appropriately, and an exempt turn still emits NOTHING (the retired
     `loop_guard` silence has no successor case -- that state no longer
     exists, see B).
  H. the diagnostic log SELF-PRUNES -- unaffected by the demotion; still
     capped at a recent window, still newest-first, still fail-safe.
  J. the lone `.` escape (root CLAUDE.md §3.1.6.2) -- CLEAN under its own
     `clean:dot` tag in REPO, UNCHANGED. NEWLY (Change 2, unrelated to the
     demotion): the SAME escape is now ALSO clean in READER mode, under its
     own `clean:dot_reader` tag, because the owner has a standing need to
     send/receive a lone `.` there purely to open a session-limit window --
     `universal/glossary.md` and the `GitHub/` CLAUDE.md both already mandate
     that exact reply. The matching rule stays byte-for-byte identical in
     both modes: `..`, `...`, trailing text, a bold `**.**`, and a dot
     sharing the turn with any other line all still flag -- in REPO as
     `yellow:prose`, in READER as `yellow:reader`.
  K. the SIXTH declaration class, `🦈` (root CLAUDE.md §3.2.4) -- the turn's
     commit SHAs, which the owner split out of `➡️` into a class of their own.
     Because clint's design is GLYPH OWNERSHIP, a glyph it does not know is
     not "unrecognised" but PROSE: before this was taught, every COMPLIANT
     batch under the new protocol logged `yellow:prose`, so the log -- clint's
     PRIMARY artefact since the demotion -- recorded correct behaviour as a
     breach. Pins that the new class is clean alone and inside a real batch,
     that a malformed one still flags under its own `sha_shape` class, that
     the cross-type test is symmetric, that the other five are untouched, and
     that READER mode is NOT widened by it.
  M. the SOLO-LABEL check, `sha_label` (root CLAUDE.md §3.2.4.4–5) -- a repo
     shorthand (`Default:`) is sanctioned ONLY on the multi-repo form's
     multiple `🦈` lines, so a window holding exactly ONE `🦈` line declared
     one repo by construction and ANY label on it is a breach. The owner's
     own insight closed the old "one line at a time" objection: no per-line
     context is needed, only the window's `🦈`-line COUNT, which clint
     already has where the verdicts are gathered. Pins: the lone labelled
     line flags under its OWN class (never folded into `sha_shape` -- the
     next-prompt tally names the class, and "drop the label" is a different
     correction from "that is not a SHA list"); the bare lone line stays
     clean; the 2+-line multi-repo form is NEVER touched; a malformed lone
     line keeps `sha_shape` (the coarser defect subsumes the label); READER
     and the exemptions are unchanged.
  L. SENTINEL LISTS (root CLAUDE.md §5.3–§5.4) -- a post-compaction turn OWES
     the user chat lists by root §5, and mlint (SHAPE C, hook_guide §6.9.9)
     BLOCKS the turn until they exist, so before the fix every genuine
     compaction logged `yellow:prose` -- two Stop hooks of the same suite
     mandating and forbidding the SAME lines, and the log (clint's PRIMARY
     artefact) recording compliant behaviour as a breach. Pins: the mandated
     shape is clean under its own `clean:compaction` tag; the escape arms
     ONLY on the exact §3.2.6 canon; it sanctions ONLY the two §5 list
     shapes, and only out of class `prose`; every other class, the
     no-sentinel case, and READER mode are untouched; and the real
     multi-wake window (mined from this Mac's own transcript) keeps flagging
     its stray dots whilst the mandated lists walk free.
  N. the MISSING-LABEL check, `sha_nolabel` (root CLAUDE.md §3.2.4.5) -- the
     solo-label check's exact mirror, added when the owner ordered the scan
     reversed: with 2+ `🦈` lines in the window (the multi-repo form), EVERY
     line owes its repo shorthand, so a bare one flags under its OWN class.
     The panic-proof CONDITIONAL wording of its next-prompt correction is
     pinned in the tally suite, where that wording lives.
  W. the BASH-WRITE CATCH (`bashw=` log field) -- a comms file written via a
     Bash command (heredoc, redirect, tee, in-place edit) fires NO
     PostToolUse lint, so clint records it at Stop for hlint to advise on at
     the next prompt. Pins the real bypass incident replayed verbatim, the
     legitimate-Bash silences (reads, git, hand-run lints, the Move Rule's
     `mv`), the mtime gate, and the field's independence from the chat
     verdict and its exemptions.

It drives the REAL registered command from ~/.claude/settings.json
(`python3 .../cscpt/clint.py`, Stop hook) with synthesised payloads and
synthesised transcripts, so the behaviour is proven through the wiring the
harness actually uses, not through imported internals (coding.md: "'exists +
unit-tested' != done -- done only when WIRED and exercised end-to-end").

Self-contained: every transcript is written into a throwaway tempdir at run
time and CLINT_LOG is redirected there, so the real cscpt/.clint.log is
neither read nor polluted. Run directly:

    python3 "cp/ccsim/sandbox/clint_detection_contract_regression_test.py"

Exits 0 if every case matches its expected verdict, 1 otherwise (per-case
PASS/FAIL on stdout, full diagnostics on any FAIL, and the resulting log lines
printed at the end).
"""
import json
import os
import re
import subprocess
import sys
import tempfile

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.realpath(os.path.join(_THIS_DIR, "..", "..", ".."))
# BASELINE OVERRIDE, mirroring the tally suite's documented pattern:
# `CLINT_UNDER_TEST=<path>` points the whole suite at another copy of
# clint.py -- used to demonstrate each NEW case failing against the
# pre-change file (CCSIM CLAUDE.md §4.4), so "the fix exists" and "the fix
# is what makes these pass" stay two separately proven claims. CAVEAT the
# hlint suite shares: clint derives its repo root from its OWN location, so
# a baseline copy must sit under a directory tree whose root matches the
# payload `cwd`s this suite sends (REPO_ROOT) -- a git worktree checked out
# elsewhere, with THIS file copied in and run from there, satisfies both.
CLINT = (os.environ.get("CLINT_UNDER_TEST")
         or os.path.join(REPO_ROOT, "cscpt", "clint.py"))

# The Reader session's working directory: this repo's immediate parent. Its own
# CLAUDE.md mandates zero chat text, hence clint's stricter second rule.
READER_CWD = os.path.dirname(REPO_ROOT)
# A sibling repo under the same parent -- must NOT inherit the Reader rule.
SIBLING_CWD = os.path.join(READER_CWD, "AJAP_repo")

# The 6 declaration glyphs, base codepoints (the emoji variation selector is
# irrelevant to a substring search). Kept in ONE place so section A and section
# I can never drift into checking different sets: naming any of these in the
# message the user reads would teach exactly which prefixes pass. `🦈` (§3.2.4,
# the turn's commit SHAs) joined the set when the owner split the SHA line out
# of `➡️` into a class of its own —— see section K.
GLYPHS = ("✅", "⇠", "➡", "\U0001f988", "⚠", "\U0001f6a8")

# A protocol section reference such as `§3.2`. Its digits are an ADDRESS, not a
# threshold, so they are stripped before the message is checked for digits --
# see section I for why any surviving digit is the actual hazard.
SECTION_REF_RE = re.compile(r"§\d+(?:\.\d+)*")

# clint's own log tags. None may appear in the message the user reads: the
# class is a diagnostic for the human reading the LOG, and telling the reader
# WHICH check caught it is telling them what to file the next attempt under
# (moot for the agent now -- it never reads this message at all -- but the
# constraint is kept as cheap insurance; see clint.py docstring GLYPH-FREE,
# CLASS-FREE, NUMBER-FREE MESSAGE). `block:` and `loop_guard` are RETIRED tags
# (the always-RED policy and its loop guard are both gone) and are
# deliberately absent here -- they can no longer leak because they no longer
# exist.
CLASS_TOKENS = ("io_shape", "sha_shape", "sha_label", "sentinel",
                "warn_empty", "warn_shape", "warn_words", "warn_hyphens",
                "warn_chars", "warn_progress", "sic_overrun", "reader",
                "yellow:", "exempt:")

_RESULTS = []


def _record(label, ok, detail=None):
    print("[%s] %s" % ("PASS" if ok else "FAIL", label))
    if not ok and detail is not None:
        print("        %s" % detail)
    _RESULTS.append(ok)
    return ok


# --- fixture builders ------------------------------------------------------
# Transcript line shapes copied from real captured transcripts on this Mac
# (keys verified live: user lines carry `promptId`/`isMeta`, the harness's
# post-block injection is a `type:"user"`, `isMeta:true` line whose content
# starts with "Stop hook feedback:").

def _user(text, pid="pid-A"):
    return {"type": "user", "isSidechain": False, "promptId": pid,
            "message": {"role": "user", "content": text}}


def _stop_feedback(pid="pid-A"):
    """The harness's own continuation line after a Stop hook blocked. Kept as
    a fixture even though clint no longer blocks: OTHER Stop hooks in this
    repo can still force this exact shape, and the SCAN BOUNDARY must still
    treat it as a genuine boundary-mover (see section B)."""
    return {"type": "user", "isSidechain": False, "promptId": pid,
            "isMeta": True,
            "message": {"role": "user", "content":
                        "Stop hook feedback:\n[clint.py]: Chat-prose breach"}}


def _assistant(text, api_error=False):
    o = {"type": "assistant", "isSidechain": False,
         "message": {"role": "assistant",
                     "content": [{"type": "text", "text": text}]}}
    if api_error:
        o["isApiErrorMessage"] = True
    return o


def _write_transcript(path, objs):
    with open(path, "w", encoding="utf-8") as fh:
        for o in objs:
            fh.write(json.dumps(o) + "\n")
    return path


def _payload(transcript_path, cwd=REPO_ROOT, stop_hook_active=False,
             sid="clinttest"):
    """Exact Stop-payload key set as captured live this session.
    `stop_hook_active` is still accepted (the real harness still sends it),
    but clint no longer reads it -- see section B."""
    return {"session_id": sid, "transcript_path": transcript_path,
            "prompt_id": "pid-A", "permission_mode": "default",
            "hook_event_name": "Stop", "stop_hook_active": stop_hook_active,
            "cwd": cwd}


def _extract_message(stdout_text):
    """The `systemMessage` string clint writes as exit-0 JSON on stdout for a
    demoted breach (see clint.py docstring ALWAYS RED -> ALWAYS YELLOW), or
    "" if there was none or it did not parse -- exactly the shape a clean,
    exempt, or out-of-scope turn produces (no stdout at all)."""
    try:
        obj = json.loads(stdout_text)
        if isinstance(obj, dict):
            m = obj.get("systemMessage")
            if isinstance(m, str):
                return m
    except Exception:
        pass
    return ""


def _run(payload, log_path, raw=None):
    """Invoke clint exactly as settings.json does; return (exit, last_log,
    message). `message` is the user-facing warning text (see
    `_extract_message`) -- empty for any turn that did not warn."""
    before = _log_lines(log_path)
    stdin = raw if raw is not None else json.dumps(payload)
    r = subprocess.run([sys.executable, CLINT], input=stdin,
                       capture_output=True, text=True,
                       env=dict(os.environ, CLINT_LOG=log_path))
    after = _log_lines(log_path)
    new = after[len(before):]
    return r.returncode, (new[-1] if new else ""), _extract_message(r.stdout)


def _log_lines(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return [ln for ln in fh.read().splitlines() if ln.strip()]
    except OSError:
        return []


def _action(log_line):
    for f in log_line.split("\t"):
        if f.startswith("action="):
            return f[len("action="):]
    return "<none>"


def _family(action):
    """Tag family —— the part before the ':' qualifier.

    clint's log tags carry a granular class suffix (`yellow:prose`,
    `yellow:warn_words`, `exempt:sic`, ...) so a breach can be audited by
    REASON. A test that asserts the family (`yellow`) stays correct as new
    classes are added; a test that needs one specific class simply passes the
    full tag and still gets exact matching. Comparing families never blurs
    the outcomes that matter —— `yellow`, `exempt`, `clean` and `out_of_scope`
    remain distinct.
    """
    return action.split(":", 1)[0]


def _check(label, got, want_exit, want_action):
    code, line, _ = got
    got_action = _action(line)
    if ":" in want_action:          # caller asked for one exact class
        action_ok = got_action == want_action
    else:                           # caller asked for the family
        action_ok = _family(got_action) == want_action
    ok = (code == want_exit and action_ok)
    return _record("%s -> exit %d, action=%s" % (label, want_exit, want_action),
                   ok, "got exit=%s action=%s line=%r"
                   % (code, got_action, line))


# --- A. the once-per-prompt ceiling is (still) gone ------------------------

def section_no_ceiling(tmp):
    print("\n--- A. no ceiling: 3 breaches, ONE promptId, each logs its own "
          "class, none block ---")
    log = os.path.join(tmp, "A.log")
    tp = os.path.join(tmp, "A.jsonl")
    objs = [_user("do the thing", pid="pid-SAME")]
    for n in (1, 2, 3):
        objs.append(_assistant("Breach %d: unauthorised chat prose." % n))
        _write_transcript(tp, objs)
        _check("breach %d (same pid, an old ledger would have downgraded "
               "2 and 3)" % n, _run(_payload(tp), log), 0, "yellow")
    # And the message the user actually receives must never name a glyph:
    _, _, msg = _run(_payload(tp), log)
    _record("message stays glyph-free (cannot teach which prefixes pass)",
            msg.strip() != "" and not any(g in msg for g in GLYPHS),
            "message=%r" % msg)


# --- B. the retired loop guard is inert -------------------------------------

def section_loop_guard(tmp):
    print("\n--- B. retired loop guard: now inert; a forced continuation is "
          "an ordinary turn ---")
    log = os.path.join(tmp, "B.log")

    # (a) payload flag alone: used to withhold the block outright (guard
    # signal (a)). Demotion made the whole guard moot -- this now just logs
    # its ordinary granular class like any other breach.
    tp = os.path.join(tmp, "B1.jsonl")
    _write_transcript(tp, [_user("go"), _assistant("More prose in the retry.")])
    _check("stop_hook_active is now IGNORED (was guard signal (a))",
           _run(_payload(tp, stop_hook_active=True), log), 0, "yellow:prose")

    # (b) injected feedback line alone: used to withhold the block (flag
    # false, the case that once relied purely on the deleted ledger). Now
    # inert too -- same ordinary outcome.
    tp2 = os.path.join(tmp, "B2.jsonl")
    _write_transcript(tp2, [_user("go"), _assistant("First breach."),
                            _stop_feedback(),
                            _assistant("Still prose after being blocked.")])
    _check("injected feedback line is now IGNORED (was guard signal (b))",
           _run(_payload(tp2, stop_hook_active=False), log), 0, "yellow:prose")

    # A human merely QUOTING the phrase was never a real continuation either
    # way -- the SCAN BOUNDARY treats it as ordinary prose, not a marker.
    tp3 = os.path.join(tmp, "B3.jsonl")
    _write_transcript(tp3, [_user("Stop hook feedback: is what I want to discuss"),
                            _assistant("Sure, here is prose about it.")])
    _check("a human message quoting the marker is ordinary prose",
           _run(_payload(tp3), log), 0, "yellow:prose")

    # SCAN BOUNDARY, still pinned even without the guard: only text AFTER the
    # feedback line is in scope. A DIFFERENT breach class sits before it and a
    # distinctive one sits after; `first=` must report the AFTER text only --
    # proof the boundary still moves correctly now that nothing depends on it
    # to stop a loop.
    tp4 = os.path.join(tmp, "B4.jsonl")
    _write_transcript(tp4, [_user("go"),
                            _assistant("⚠️ `cscpt/clint.py`"),   # warn_shape, BEFORE
                            _stop_feedback(),
                            _assistant("Prose after the boundary line.")])  # AFTER
    code, line, _ = _run(_payload(tp4, stop_hook_active=False), log)
    _record("scan boundary still moves past the feedback line (reports the "
            "AFTER text, not the before text)",
            code == 0 and _action(line) == "yellow:prose"
            and "after the boundary" in line,
            "action=%s line=%r" % (_action(line), line))

    # A NEW human prompt still starts a fresh scan, exactly as before.
    tp5 = os.path.join(tmp, "B5.jsonl")
    _write_transcript(tp5, [_user("go", pid="pid-1"),
                            _assistant("First breach."), _stop_feedback("pid-1"),
                            _assistant("Second breach."),
                            _user("next thing please", pid="pid-2"),
                            _assistant("Fresh prose under a new prompt.")])
    _check("a new human prompt still starts a fresh scan",
           _run(_payload(tp5, stop_hook_active=False), log), 0, "yellow:prose")


# --- C. the `yn` exemption, on real mined prompts ---------------------------

def section_yn(tmp):
    print("\n--- C. ` yn` override exempts the turn (real mined prompts) ---")
    log = os.path.join(tmp, "C.log")
    # Verbatim from this Mac's own transcripts.
    real = [
        ("mid-message ` yn`, two instruction lines after it",
         "Was your last turn fully completed? yn\nIf yes, stop & do nothing\n"
         "If no, continue then update the `response_`"),
        ("trailing ` yn` after a multi-line brief",
         "FYI: i've enriched `nscpt/` with zsh/terminal commands that were "
         "originally saved in my Apple Notes; NO NEED to read them\n"
         "tell if noted yn"),
        ("trailing ` yn` after a quoted project name",
         'trying to test out Claude Design (CD)\ntell if you can access the CD '
         'project namely "Tall Poppy Syndrome research recruitment" yn'),
    ]
    for i, (label, prompt) in enumerate(real):
        tp = os.path.join(tmp, "C%d.jsonl" % i)
        # "Yes" is the exact one-word reply the log shows really being flagged
        # before this exemption existed.
        _write_transcript(tp, [_user(prompt), _assistant("Yes")])
        _check("yn: %s" % label, _run(_payload(tp), log), 0, "exempt:yn")

    # The leading space is load-bearing: a word merely ENDING in "yn" is not
    # the override and must still be policed (now: still logged, never blocks).
    tp = os.path.join(tmp, "Cneg.jsonl")
    _write_transcript(tp, [_user("Tell me about Brooklyn and synergy"),
                           _assistant("Brooklyn is a borough of New York.")])
    _check("`Brooklyn`/`synergy` do NOT count as the override",
           _run(_payload(tp), log), 0, "yellow:prose")


# --- D. the `DATS` exemption's exact boundaries ----------------------------

def section_dats(tmp):
    print("\n--- D. single sanctioned `DATS` status line is exempt ---")
    log = os.path.join(tmp, "D.log")

    cases = [
        ("sanctioned exact form (5 words)", "DATS done. Fixed 3 file(s).",
         0, "exempt:dats"),
        ("sanctioned variable form at the 10-word ceiling",
         "DATS incomplete. One two three four five six seven eight.",
         0, "exempt:dats"),
        ("11 words -- one over the ceiling, no longer that protocol line",
         "DATS incomplete. One two three four five six seven eight nine.",
         0, "yellow:prose"),
    ]
    for i, (label, text, want_exit, want_action) in enumerate(cases):
        tp = os.path.join(tmp, "D%d.jsonl" % i)
        _write_transcript(tp, [_user("#close"), _assistant(text)])
        _check("DATS: %s" % label, _run(_payload(tp), log),
               want_exit, want_action)

    # 2-line DATS block: the mandated line plus anything else is prose again.
    tp = os.path.join(tmp, "Dmulti.jsonl")
    _write_transcript(tp, [_user("#close"),
                           _assistant("DATS done. Fixed 3 file(s).\n"
                                      "DATS also stamped the close file.")])
    _check("DATS: 2-line block is NOT exempt", _run(_payload(tp), log),
           0, "yellow:prose")

    # A declaration batch AROUND the DATS line must not defeat the exemption:
    # glyph lines and blanks never enter the offending set in the first place.
    tp = os.path.join(tmp, "Dbatch.jsonl")
    _write_transcript(tp, [_user("#close"),
                           _assistant("✅ `universal/close.md`\n"
                                      "➡️ `202607/close_202607262230.md`\n"
                                      "\nDATS done. Fixed 2 file(s).")])
    _check("DATS: exemption survives a real declaration batch above it",
           _run(_payload(tp), log), 0, "exempt:dats")


# --- E. harness-authored assistant text ------------------------------------

def section_api_error(tmp):
    print("\n--- E. CLI-authored assistant lines are not the model's prose ---")
    log = os.path.join(tmp, "E.log")
    tp = os.path.join(tmp, "E.jsonl")
    # Verbatim shape captured from a real transcript.
    _write_transcript(tp, [
        _user("do the thing"),
        _assistant("✅ `cscpt/clint.py`"),
        _assistant("You've hit your session limit · resets 11:40am "
                   "(Australia/Sydney)", api_error=True)])
    _check("usage-limit line does not warn about text the model never wrote",
           _run(_payload(tp), log), 0, "clean")


# --- F. READER mode ---------------------------------------------------------

def section_reader(tmp):
    print("\n--- F. READER mode (parent GitHub/ folder): zero chat text ---")
    log = os.path.join(tmp, "F.log")
    tp = os.path.join(tmp, "F.jsonl")
    # A real Reader breach, verbatim from that project's own transcripts: the
    # declaration glyphs it emits are permitted HERE but forbidden THERE.
    _write_transcript(tp, [
        _user("response_202607092157.md"),
        _assistant("✅ `dupbus-ceztuc-7cufVe/universal/ww.md`\n"
                   "⇠ `202607/response_202607092157.md`")])
    _check("declaration glyphs are a breach in the Reader session",
           _run(_payload(tp, cwd=READER_CWD), log), 0, "yellow:reader")
    _check("the very same lines are clean in THIS repo",
           _run(_payload(tp, cwd=REPO_ROOT), log), 0, "clean")

    # Real Reader prose, verbatim.
    tp2 = os.path.join(tmp, "F2.jsonl")
    _write_transcript(tp2, [_user("ww it"),
                            _assistant("Reading instructions for #ww workflow.")])
    _check("Reader prose is a breach", _run(_payload(tp2, cwd=READER_CWD), log),
           0, "yellow:reader")

    # A genuinely silent Reader turn (tool calls only, no text block).
    tp3 = os.path.join(tmp, "F3.jsonl")
    _write_transcript(tp3, [_user("ww it"), _assistant("   \n\n")])
    _check("a silent Reader turn is clean",
           _run(_payload(tp3, cwd=READER_CWD), log), 0, "clean")

    # The exemptions are repo-only: the Reader owes silence NO MATTER WHAT.
    tp4 = os.path.join(tmp, "F4.jsonl")
    _write_transcript(tp4, [_user("did you read it yn"), _assistant("Yes")])
    _check("`yn` does NOT exempt the Reader",
           _run(_payload(tp4, cwd=READER_CWD), log), 0, "yellow:reader")

    # Sub-path of the Reader folder that is a DIFFERENT repo -> not policed.
    _check("a sibling repo under GitHub/ is out of scope, not Reader-policed",
           _run(_payload(tp2, cwd=SIBLING_CWD), log), 0, "out_of_scope")

    # A sub-path of THIS repo stays repo mode (exact-match is Reader-only).
    _check("a sub-path of this repo is still repo mode",
           _run(_payload(tp, cwd=os.path.join(REPO_ROOT, "cp", "ccsim")), log),
           0, "clean")


# --- G. fail-safes ----------------------------------------------------------

def section_failsafe(tmp):
    print("\n--- G. fail-safe paths: never break a turn ---")
    log = os.path.join(tmp, "G.log")
    tp = os.path.join(tmp, "G.jsonl")
    _write_transcript(tp, [_user("go"), _assistant("✅ `cscpt/clint.py`")])

    _check("clean turn (declarations only)", _run(_payload(tp), log), 0, "clean")
    _check("out-of-scope project", _run(_payload(tp, cwd="/tmp/some-other-repo"),
                                        log), 0, "out_of_scope")
    _check("malformed payload (not JSON)",
           _run(None, log, raw="{not json at all"), 0, "no_stdin")
    _check("valid JSON but not an object",
           _run(None, log, raw='["a", "list"]'), 0, "no_stdin")
    _check("missing transcript file",
           _run(_payload(os.path.join(tmp, "nope.jsonl")), log),
           0, "no_transcript")

    # Empty stdin -- the shape a mis-wired harness would send.
    _check("empty stdin", _run(None, log, raw=""), 0, "no_stdin")


# --- I. the WARNING message: present, safe, never a block -------------------

# One fixture per REPO breach CLASS, so the message is proven identical on all
# of them rather than on plain prose alone. Each `text` is a line clint really
# classifies as the named class (the trigger message is what arms `sic`).
_CLASS_FIXTURES = (
    ("prose", "do the thing",
     "The fleet finished; three agents reported clean."),
    ("io_shape", "do the thing",
     "✅ Read the plan and then carried on working."),
    ("sha_shape", "do the thing",
     "🦈 `97ae25ba` committed and pushed everything cleanly."),
    ("sentinel", "do the thing",
     "**🚨 Compaction Detected —— stopped all tasks.**"),
    ("warn_progress", "do the thing", "⚠️ Fleet running; awaiting reports."),
    ("warn_words", "do the thing",
     "⚠️ Blocked because the upstream service failed again"),
    ("warn_empty", "do the thing", "⚠️"),
    ("warn_shape", "do the thing", "⚠️ `cscpt/clint.py`"),
    ("warn_hyphens", "do the thing", "⚠️ auth-token-store-load-x failed"),
    ("warn_chars", "do the thing",
     "⚠️ auth_token_store_unavailable auth_token_store_unavailable "
     "auth_token_store_unavailable"),
    ("sic_overrun", "sic what did you find",
     "I found eleven separate issues across the four scripts and fixed "
     "every single one of them today."),
    # The solo-label breach (section M): a lone, labelled, otherwise
    # shape-valid SHA line -- must draw the SAME message as every other
    # class, so it rides this list like the rest.
    ("sha_label", "do the thing", "🦈 Default: `302d7d8c`"),
)


def section_redirect(tmp):
    print("\n--- I. WARNING message: present, safe, delivered, NEVER blocks ---")
    log = os.path.join(tmp, "I.log")

    # Everything below is asserted against the bytes the model's USER really
    # receives from the registered command (the exit-0 `systemMessage` JSON on
    # stdout), never an imported constant: the message is the entire payload
    # of a warning, so a test that trusts the source rather than the real
    # stdout proves nothing about what actually gets shown.
    tp = os.path.join(tmp, "I0.jsonl")
    _write_transcript(tp, [_user("do the thing"),
                           _assistant("The fleet finished; three agents "
                                      "reported clean.")])
    repo = _run(_payload(tp), log)
    reader = _run(_payload(tp, cwd=READER_CWD), log)
    repo_msg, reader_msg = repo[2], reader[2]

    print("    REPO message:   %s" % repo_msg)
    print("    READER message: %s" % reader_msg)

    _check("a REPO breach still logs, but NEVER blocks", repo, 0, "yellow:prose")
    _check("a READER breach still logs, but NEVER blocks", reader, 0, "yellow:reader")

    # I1. THE COURTESY HINT SURVIVES. It no longer corrects the agent (the
    # agent never reads this message at all -- see ALWAYS RED -> ALWAYS
    # YELLOW), but it still tells the HUMAN reading it where to look.
    _record("I1 REPO message names where lost content might belong (`response_`)",
            "response_" in repo_msg, "message=%r" % repo_msg)

    # I2. THE WARNING FRAMING IS UNMISTAKABLE. These clauses must be present so
    # the message reads as a fact about what already happened, never as an
    # instruction telling an (absent) reader what to do next.
    kept = ("WARNING (root CLAUDE.md §3.2)", "Logged only",
            "no longer blocks the turn or reaches the agent")
    missing = [k for k in kept if k not in repo_msg]
    _record("I2 the WARNING framing survives intact (%d clauses)" % len(kept),
            not missing, "missing=%r" % missing)

    # I3. GLYPH-FREE, both modes. Naming a permitted prefix would teach which
    # one to bolt onto prose next time -- moot for the agent (it never reads
    # this), kept as insurance regardless (see clint.py docstring GLYPH-FREE,
    # CLASS-FREE, NUMBER-FREE MESSAGE).
    for label, msg in (("REPO", repo_msg), ("READER", reader_msg)):
        hit = [g for g in GLYPHS if g in msg]
        _record("I3 %s message names no declaration glyph" % label,
                msg.strip() != "" and not hit, "found=%r in %r" % (hit, msg))

    # I4. NO NUMBER LEAKS. `§3.2` is an address and is stripped first; any
    # digit surviving that is a threshold, exactly why the character cap
    # lives only in the script's CCSIM block.
    for label, msg in (("REPO", repo_msg), ("READER", reader_msg)):
        bare = SECTION_REF_RE.sub("", msg)
        digits = [c for c in bare if c.isdigit()]
        _record("I4 %s message carries no digit outside a section reference"
                % label, not digits, "digits=%r in %r" % (digits, bare))

    # I5. NO BREACH CLASS OR LOG TAG LEAKS. ("prose" is deliberately absent
    # from CLASS_TOKENS: it is ordinary English in the WARNING sentence and
    # predates the tag of the same name -- what must never appear is the TAG,
    # `yellow:prose`, which `yellow:` covers.)
    for label, msg in (("REPO", repo_msg), ("READER", reader_msg)):
        hit = [t for t in CLASS_TOKENS if t in msg]
        _record("I5 %s message names no breach class or log tag" % label,
                not hit, "found=%r in %r" % (hit, msg))

    # I6. REPO-ONLY HINT. READER creates no files at all, so a hint of where
    # to look would point nowhere; its whole message is just the fact itself.
    _record("I6 READER message gets NO `response_` hint (creates no files)",
            "response_" not in reader_msg, "message=%r" % reader_msg)
    _record("I6b READER message still states plainly that nothing was fixed",
            "no longer blocks the turn or reaches the agent" in reader_msg,
            "message=%r" % reader_msg)

    # I7. SHORT. A long message is a worse message even read by a human alone.
    for label, msg in (("REPO", repo_msg), ("READER", reader_msg)):
        _record("I7 %s message stays short (%d chars, cap 400)"
                % (label, len(msg)), len(msg) <= 400, "message=%r" % msg)

    # I8. DELIVERED ON EVERY CLASS, IDENTICALLY, AND NEVER BLOCKING. The
    # per-class log tags stay distinct (now `yellow:`, not `block:`) so the
    # human diagnostic keeps the detail the message itself does not carry.
    seen = {}
    for i, (klass, prompt, text) in enumerate(_CLASS_FIXTURES):
        tpc = os.path.join(tmp, "I%d.jsonl" % (i + 1))
        _write_transcript(tpc, [_user(prompt), _assistant(text)])
        got = _run(_payload(tpc), log)
        _check("I8 %s still logs its own class and never blocks" % klass,
               got, 0, "yellow:" + klass)
        seen[klass] = got[2]
    same = [k for k, v in seen.items() if v != repo_msg]
    _record("I8b every REPO breach class receives the SAME message (%d classes)"
            % len(seen), not same, "differing=%r" % same)

    # I9. NOTHING IS SAID WHERE NOTHING BREACHED. An exempt turn stays silent
    # -- the message belongs to a logged breach, never advice volunteered to a
    # turn that was let through. (The old `loop_guard` silence has no
    # successor case here: that state no longer exists -- see section B,
    # where the same shapes now log an ordinary `yellow:` class instead.)
    quiet = (
        ("exempt:override", _user("override, just tell me in chat")),
        ("exempt:yn", _user("did it work yn")),
        ("exempt:dats", _user("#close")),
    )
    texts = {"exempt:override": "Here is the answer in plain chat prose.",
             "exempt:yn": "Yes",
             "exempt:dats": "DATS done. Fixed 3 file(s)."}
    for j, (tag, trigger) in enumerate(quiet):
        tpq = os.path.join(tmp, "Iq%d.jsonl" % j)
        _write_transcript(tpq, [trigger, _assistant(texts[tag])])
        got = _run(_payload(tpq), log)
        _check("I9 %s still passes" % tag, got, 0, tag)
        _record("I9 %s emits no message at all" % tag, got[2] == "",
                "message=%r" % got[2])


# --- J. the lone `.` escape (root CLAUDE.md §3.1.6.2, DOT ESCAPE) ----------

def section_dot_escape(tmp):
    print("\n--- J. lone `.`: sanctioned no-op reply, BOTH modes now ---")
    log = os.path.join(tmp, "J.log")

    # J1-J2: the bare token, with and without incidental whitespace -> CLEAN
    # in REPO, under its OWN tag (never the plain `clean` a declaration-only
    # turn gets), and NEVER a warning message.
    clean_cases = [
        ("bare lone dot", "."),
        ("dot padded with leading/trailing whitespace", "   .   "),
    ]
    for i, (label, text) in enumerate(clean_cases):
        tp = os.path.join(tmp, "Jc%d.jsonl" % i)
        _write_transcript(tp, [_user("do the thing"), _assistant(text)])
        got = _run(_payload(tp), log)
        _check("dot (REPO): %s" % label, got, 0, "clean:dot")
        _record("dot (REPO): %s emits no message (nothing breached)" % label,
                got[2] == "", "message=%r" % got[2])

    # J1r-J2r: CHANGE 2 -- the SAME shapes are now ALSO clean in READER mode,
    # under the distinct `clean:dot_reader` tag, for a reason that has nothing
    # to do with REPO's deadlock history (see clint.py docstring DOT ESCAPE):
    # the owner sends/receives this exact exchange purely to open a
    # session-limit window, and `universal/glossary.md` / the `GitHub/`
    # CLAUDE.md both already mandate that reply.
    for i, (label, text) in enumerate(clean_cases):
        tp = os.path.join(tmp, "Jr%d.jsonl" % i)
        _write_transcript(tp, [_user("."), _assistant(text)])
        got = _run(_payload(tp, cwd=READER_CWD), log)
        _check("dot (READER, Change 2): %s" % label, got, 0, "clean:dot_reader")
        _record("dot (READER): %s emits no message (nothing breached)" % label,
                got[2] == "", "message=%r" % got[2])

    # J3-J6: near misses, each failing the match for a NAMED reason -- every
    # one must still flag as an ordinary breach in REPO (no separate
    # carve-out earns a special tag; the strict shape either matches or it is
    # just chat text), and NEVER block regardless.
    block_cases = [
        ("two dots is not ONE full stop", ".."),
        ("an ellipsis is not ONE full stop", "..."),
        ("more text after the dot, same line", ". hello"),
        ("a bold-wrapped dot is not the bare token", "**.**"),
    ]
    for i, (label, text) in enumerate(block_cases):
        tp = os.path.join(tmp, "Jb%d.jsonl" % i)
        _write_transcript(tp, [_user("do the thing"), _assistant(text)])
        _check("dot (REPO): %s" % label, _run(_payload(tp), log),
               0, "yellow:prose")

    # J3r: the same near-miss shape ALSO still flags in READER mode -- Change
    # 2 widened only the one EXACT lone dot, never these near misses.
    tp = os.path.join(tmp, "Jbr.jsonl")
    _write_transcript(tp, [_user("."), _assistant("..")])
    _check("dot (READER): near-miss still flags, not widened by Change 2",
           _run(_payload(tp, cwd=READER_CWD), log), 0, "yellow:reader")

    # J7: a `.` sharing the turn with an otherwise well-formed declaration on
    # a SEPARATE line must still flag in REPO -- the escape is for a turn with
    # NOTHING else to say, not a vehicle for pairing a decorative dot onto a
    # real declaration batch. Checked over ALL non-blank lines, not only the
    # ones already flagged, precisely so this case cannot slip through.
    tp = os.path.join(tmp, "Jpair.jsonl")
    _write_transcript(tp, [_user("do the thing"),
                           _assistant(".\n✅ `cscpt/clint.py`")])
    _check("dot (REPO): alongside an otherwise-clean declaration is NOT exempt",
           _run(_payload(tp), log), 0, "yellow:prose")

    # J7r: the same pairing in READER mode -- also NOT exempt there either.
    tp = os.path.join(tmp, "Jpairr.jsonl")
    _write_transcript(tp, [_user("."), _assistant(".\nsomething else")])
    _check("dot (READER): alongside another line is NOT exempt",
           _run(_payload(tp, cwd=READER_CWD), log), 0, "yellow:reader")

    # J9: an ORDINARY clean turn (declarations only, no dot in sight) must
    # keep logging under the plain `clean` tag -- EXACTLY, not merely by
    # family, since `clean:dot`'s family is also "clean" and would otherwise
    # let this assertion pass even if `clean` had silently become an alias.
    tp = os.path.join(tmp, "Jordinary.jsonl")
    _write_transcript(tp, [_user("do the thing"),
                           _assistant("✅ `cscpt/clint.py`")])
    code, line, _ = _run(_payload(tp), log)
    _record("an ordinary clean turn logs as exactly `clean`, never `clean:dot`",
            code == 0 and _action(line) == "clean",
            "got exit=%s action=%s" % (code, _action(line)))


# --- H. the diagnostic log self-prunes -------------------------------------

def _prune_consts():
    """The three retention numbers, read from clint.py itself.

    Every OTHER assertion in this file goes through the real subprocess and
    imports nothing, deliberately. These are the one exception, and only
    because they are CONSTANTS, not behaviour: hard-coding 1000/800 here would
    let the test and the script drift apart silently, so that a retuned cap
    would still "pass" whilst asserting the wrong bound entirely."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("_clint_consts", CLINT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return (mod._LOG_MAX_LINES, mod._LOG_KEEP_LINES,
            mod._LOG_MIN_BYTES_PER_LINE)


def _prefill(path, n):
    """Write `n` realistic, already-aged records, each individually
    identifiable so the test can prove WHICH ones survived a prune rather than
    merely counting them."""
    with open(path, "w", encoding="utf-8") as fh:
        for i in range(n):
            fh.write("2026-01-01T%02d:%02d:%02d\tsession=fill%04d\tpid=pid-FILL"
                     "\tmode=repo\taction=clean\tlines=0\tfirst=filler-%06d\n"
                     % (i // 3600 % 24, i // 60 % 60, i % 60, i % 10000, i))


def section_prune(tmp):
    print("\n--- H. log retention: bounded, newest kept, never fatal ---")
    max_lines, keep_lines, min_bytes = _prune_consts()
    tp = os.path.join(tmp, "H.jsonl")
    # A clean turn: the prune must be exercised on the ordinary path, not only
    # on a breach, since the ordinary path is what runs on almost every turn.
    _write_transcript(tp, [_user("go"), _assistant("✅ `cscpt/clint.py`")])

    # --- H1-H4: over the mark -> prune, keeping the NEWEST window. ----------
    d1 = os.path.join(tmp, "H1")
    os.makedirs(d1)
    log = os.path.join(d1, "H1.log")
    over = max_lines + 300
    _prefill(log, over)
    code, _, _ = _run(_payload(tp), log)
    lines = _log_lines(log)
    blob = "\n".join(lines)

    _record("H1 bounded: %d pre-existing + 1 new -> %d lines (cap %d, keep %d)"
            % (over, len(lines), max_lines, keep_lines),
            code == 0 and len(lines) == keep_lines,
            "exit=%s len=%d" % (code, len(lines)))
    _record("H2 the line written THIS invocation is the last one, never a "
            "casualty of its own prune",
            bool(lines) and _action(lines[-1]) == "clean",
            "last=%r" % (lines[-1] if lines else ""))
    _record("H3 newest history kept, oldest dropped",
            ("filler-%06d" % (over - 1)) in blob
            and "filler-000000" not in blob,
            "newest_present=%s oldest_present=%s"
            % (("filler-%06d" % (over - 1)) in blob, "filler-000000" in blob))
    _record("H4 no temp file left behind after a successful prune",
            sorted(os.listdir(d1)) == ["H1.log"],
            "dir=%r" % sorted(os.listdir(d1)))

    # --- H5: under the mark -> left completely alone. -----------------------
    # An eager prune would throw away history that is still inside the window,
    # and would pay the rewrite on every turn instead of one in two hundred.
    d2 = os.path.join(tmp, "H2")
    os.makedirs(d2)
    log2 = os.path.join(d2, "H2.log")
    under = max_lines - 5
    _prefill(log2, under)
    _run(_payload(tp), log2)
    lines2 = _log_lines(log2)
    _record("H5 under the mark: %d + 1 -> %d lines, oldest still present"
            % (under, len(lines2)),
            len(lines2) == under + 1
            and "filler-000000" in "\n".join(lines2),
            "len=%d" % len(lines2))

    # --- H6: repeated invocations stay bounded, run after run. --------------
    d3 = os.path.join(tmp, "H3")
    os.makedirs(d3)
    log3 = os.path.join(d3, "H3.log")
    _prefill(log3, over)
    counts = []
    for _ in range(4):
        _run(_payload(tp), log3)
        counts.append(len(_log_lines(log3)))
    _record("H6 stays bounded across repeated turns: %s (all <= %d)"
            % (counts, max_lines),
            all(c <= max_lines for c in counts) and counts[0] == keep_lines,
            "counts=%s" % counts)

    # --- H7: the prune CANNOT run -> nothing breaks, nothing is lost. -------
    # Simulated by making the log's directory unwritable: appending to an
    # existing file still succeeds (that needs write permission on the FILE),
    # whilst creating the sibling temp file fails outright. That is exactly the
    # surgical failure to test -- the append must land, the prune must give up
    # silently, and the turn's verdict must be completely unaffected.
    d4 = os.path.join(tmp, "H4")
    os.makedirs(d4)
    log4 = os.path.join(d4, "H4.log")
    _prefill(log4, over)
    os.chmod(d4, 0o500)
    try:
        code4, _, _ = _run(_payload(tp), log4)
        lines4 = _log_lines(log4)
        entries4 = sorted(os.listdir(d4))
    finally:
        os.chmod(d4, 0o700)
    _record("H7 prune failure is survivable: verdict still exit 0",
            code4 == 0, "exit=%s" % code4)
    _record("H8 prune failure loses nothing: %d + 1 -> %d lines, log intact"
            % (over, len(lines4)),
            len(lines4) == over + 1, "len=%d" % len(lines4))
    _record("H9 prune failure still appended THIS turn's line",
            bool(lines4) and _action(lines4[-1]) == "clean",
            "last=%r" % (lines4[-1] if lines4 else ""))
    _record("H10 a failed prune leaves no debris",
            entries4 == ["H4.log"], "dir=%r" % entries4)

    # --- H11: the cheap pre-gate's assumption, pinned. ----------------------
    # The prune skips reading the file when its SIZE proves it cannot hold too
    # many lines, which is only valid whilst every real record is at least
    # `_LOG_MIN_BYTES_PER_LINE` long. If the record format ever shrinks below
    # that floor, prunes would be skipped and the log would grow unbounded
    # again -- silently. So the floor is measured against every line this suite
    # actually made clint write, never assumed.
    real = []
    for name in sorted(os.listdir(tmp)):
        if name.endswith(".log"):           # sections A-I only: clint-written
            real.extend(_log_lines(os.path.join(tmp, name)))
    shortest = min((len(ln.encode("utf-8")) + 1 for ln in real), default=0)
    _record("H11 every real record is >= the %d-byte floor the pre-gate "
            "assumes (shortest seen: %d bytes, over %d records)"
            % (min_bytes, shortest, len(real)),
            bool(real) and shortest >= min_bytes,
            "shortest=%d records=%d" % (shortest, len(real)))


# --- K. the SIXTH declaration class, `🦈` (root CLAUDE.md §3.2.4) -----------

def section_sha_declaration(tmp):
    """Pins the glyph added when the owner split the turn's commit SHAs out of
    `➡️` into a declaration class of their own.

    WHY THIS SECTION EXISTS, stated as the defect it pins: clint's whole design
    is GLYPH OWNERSHIP, so a glyph it does not know about is not "unrecognised",
    it is PROSE. Before the fix, the real registered command logged
    `yellow:prose` for every one of the compliant batches below —— i.e. every
    turn that obeyed the new protocol was recorded as a breach, and the log is
    now clint's PRIMARY artefact. Measured through the real command, not
    reasoned about: `🦈 `abc12345`` returned `yellow:prose` before and returns
    `clean` after.

    K1 the new declaration alone is CLEAN, in each sanctioned shape;
    K2 it is CLEAN in combination with the other five;
    K3 a malformed one is STILL flagged, under its own `sha_shape` class ——
       so the class was taught, not merely whitelisted;
    K4 the existing five are UNCHANGED by its arrival.
    """
    print("\n--- K. `🦈` SHA declaration (§3.2.4): the sixth class ---")
    log = os.path.join(tmp, "K.log")

    def run(name, text, want_action, cwd=REPO_ROOT):
        tp = os.path.join(tmp, "K%s.jsonl" % re.sub(r"\W+", "_", name)[:40])
        _write_transcript(tp, [_user("do the thing"), _assistant(text)])
        return _check(name, _run(_payload(tp, cwd=cwd), log), 0, want_action)

    # K1. CLEAN ALONE. Every shape §3.2.4 sanctions. The LENGTH rule is
    # asymmetric on purpose and both ends are pinned here: §3.2.4.3's 8 is a
    # FLOOR (shorter is a real breach, K3e), whilst anything longer stays clean
    # because `git rev-parse --short=8` LENGTHENS its own output on an
    # ambiguous prefix -- flagging that would punish the agent for running the
    # exact command §3.2.4.3 prescribes.
    run("K1a single SHA", "🦈 `97ae25ba`", "clean")
    run("K1b two SHAs, one line (§3.2.4.4)", "🦈 `97ae25ba`, `470481d8`", "clean")
    run("K1c multi-repo shorthands (§3.2.4.5)",
        "🦈 Default: `97ae25ba`, `470481d8`\n🦈 AJAP: `1a2b3c4d`", "clean")
    run("K1d 9-char, git lengthening an ambiguous prefix", "🦈 `97ae25ba4`",
        "clean")
    run("K1e full 40-char SHA", "🦈 `%s`" % ("97ae25ba470481d8" + "0" * 24), "clean")
    run("K1f bold wrapper tolerated, as elsewhere", "**🦈 `97ae25ba`**", "clean")
    # K1g. THE PROTOCOL'S OWN EXAMPLE. Root §3.1.6.3 prints a worked batch; if
    # clint rejected the very lines CC is shown to copy, the example would
    # teach a breach. Pinned verbatim so a future edit to either side is caught
    # by whichever is edited second.
    run("K1g root §3.1.6.3's own worked example",
        "🦈 Default: `deadbeef`, `cafef00d`\n🦈 AJAP: `0ddba115`, `feedface`",
        "clean")

    # K2. CLEAN IN COMPANY. The real artefact is a BATCH: §3.1.6.3 ends its
    # example on the `🦈` lines, so the mixed case is the one that actually
    # ships and a per-line rule that only works in isolation is worthless.
    run("K2a full TEA3 batch, `🦈` last",
        "✅ `career/CP_notes.md`, `cscpt/dlint.py`\n"
        "⇠ `202605/query_202605300226.md`\n"
        "➡️ **`202605/response_202605300226.md`**\n"
        "🦈 `97ae25ba`, `470481d8`", "clean")
    run("K2b alongside the blocker and the sentinel",
        "🦈 `97ae25ba`\n⚠️ Push denied; auth failed\n"
        "🚨 Compaction Detected —— stopped all tasks.", "clean")

    # K3. STILL FLAGGED WHEN MALFORMED, under its OWN class. The prose tail is
    # the smuggling vector the whole ownership design exists to block; the
    # non-hex case is what stops a sentence being backticked into place.
    run("K3a prose tail after the SHA",
        "🦈 `97ae25ba` committed and pushed everything", "yellow:sha_shape")
    run("K3b bare glyph declaring nothing", "🦈", "yellow:sha_shape")
    run("K3c SHA not backticked", "🦈 97ae25ba", "yellow:sha_shape")
    run("K3d non-hex token wearing the glyph", "🦈 `xyz67890`", "yellow:sha_shape")
    run("K3e too short to be an abbrev", "🦈 `97ae2`", "yellow:sha_shape")
    run("K3e2 7 chars: under §3.2.4.3's floor of 8", "🦈 `97ae25b`",
        "yellow:sha_shape")
    run("K3f label is a phrase, not a shorthand",
        "🦈 Default repo here: `97ae25ba`", "yellow:sha_shape")
    run("K3g a file path is not a SHA", "🦈 `cscpt/clint.py`", "yellow:sha_shape")
    run("K3h a paragraph in backticks is still a paragraph",
        "🦈 `the fleet finished and every agent reported clean`",
        "yellow:sha_shape")

    # K3i. CROSS-TYPE, both directions —— the ownership rule is symmetric or it
    # is not a rule. A SHA list wearing the blocker glyph is another type's
    # declaration; a file list wearing the SHA glyph is likewise.
    run("K3i SHA list wearing the blocker glyph",
        "⚠️ Default: `97ae25ba`, `470481d8`", "yellow:warn_shape")
    run("K3j file list wearing the SHA glyph",
        "🦈 `cscpt/clint.py`, `cscpt/mlint.py`", "yellow:sha_shape")

    # K4. THE OTHER FIVE ARE UNCHANGED. Re-asserted HERE, not merely elsewhere
    # in the suite, because the failure this guards against is a shared
    # constant (`_GLYPHS`) being edited to add one glyph and quietly losing
    # another —— which only a check that names all six can catch.
    run("K4a `✅` file list still clean", "✅ `cscpt/clint.py`", "clean")
    run("K4b `⇠` comms read still clean", "⇠ `202605/query_202605300226.md`", "clean")
    run("K4c `➡️` write still clean", "➡️ **`202605/response_202605300226.md`**",
        "clean")
    run("K4d `⚠️` blocker still clean", "⚠️ Push denied; auth failed", "clean")
    run("K4e `🚨` sentinel still clean",
        "🚨 Compaction Detected —— stopped all tasks.", "clean")
    run("K4f prose still `prose`, not the new class",
        "The fleet finished; three agents reported clean.", "yellow:prose")

    # K5. READER MODE IS NOT WIDENED. That folder owes ZERO chat text, so the
    # new glyph is a breach there exactly like the other five —— a new
    # declaration class is a REPO concept and must not leak across.
    run("K5 `🦈` is still a breach in READER mode", "🦈 `97ae25ba`",
        "yellow:reader", cwd=READER_CWD)


# --- M. the SOLO-LABEL check: one `🦈` line, one repo, so no label ----------

def section_sha_label(tmp):
    """M. `sha_label` (root CLAUDE.md §3.2.4.4–5): a repo shorthand on a
    single-repo turn's lone SHA line is a breach.

    WHY THIS SECTION EXISTS, stated as the defect it pins: `_sha_ok` accepts
    an optional one-word label because the §3.2.4.5 multi-repo form is legal,
    so `🦈 Default: `302d7d8c`` on a SINGLE-repo turn passed as clean -- a
    per-line rule cannot see that the label's precondition (multiple repos,
    hence multiple `🦈` lines) is absent. The owner's insight closed that gap
    without breaking the per-line design: exactly ONE `🦈` line in the window
    means one repo by construction, so ANY label on it is wrong, and the
    window-wide count is already available where the verdicts are gathered.
    Measured through the real registered command, not reasoned about: the M1
    fixture returned `clean` before the fix and returns `yellow:sha_label`
    after.

    M1 the lone labelled line flags, under its OWN class (both live
       shorthands, and the multi-SHA body §3.1.6.3's example draws);
    M2 it flags inside a full, otherwise-clean TEA3 batch -- the real
       artefact -- and the residue count proves the batch walked free;
    M3 the lone BARE line stays clean -- the check reclassifies labels,
       never the sanctioned §3.2.4.4 shape;
    M4 the 2+-line multi-repo form is NEVER touched, labels and all;
    M5 the bold wrapper changes nothing, as everywhere else;
    M6 a malformed lone line keeps `sha_shape` -- the coarser defect
       subsumes the label, one class per line;
    M7 READER mode is unchanged -- §3.2.4 is this repo's protocol;
    M8 with 2 `🦈` lines a malformed one keeps its own class and the
       labelled one is NOT flagged -- the count gate reads 2, so labels
       are legal even while a sibling line is in breach;
    M9 the `override` exemption still outranks the new class.
    """
    print("\n--- M. `🦈` solo-label check (§3.2.4.4–5): one line, one repo, "
          "no label ---")
    log = os.path.join(tmp, "M.log")

    def run(name, text, want_action, cwd=REPO_ROOT, prompt="do the thing"):
        tp = os.path.join(tmp, "M%s.jsonl" % re.sub(r"\W+", "_", name)[:40])
        _write_transcript(tp, [_user(prompt), _assistant(text)])
        got = _run(_payload(tp, cwd=cwd), log)
        _check(name, got, 0, want_action)
        return got

    # M1. THE BREACH. Real shapes: both shorthands root §3.1.6.3's own
    # example prints, and real SHAs mined from this repo's log -- each on a
    # turn whose window holds no other `🦈` line.
    run("M1a lone `Default:`-labelled SHA line", "🦈 Default: `302d7d8c`",
        "yellow:sha_label")
    run("M1b lone `AJAP:`-labelled SHA line", "🦈 AJAP: `0ddba115`",
        "yellow:sha_label")
    run("M1c label + several SHAs is still one repo",
        "🦈 Default: `302d7d8c`, `0896f26c`", "yellow:sha_label")

    # M2. INSIDE THE REAL ARTEFACT. The batch's other declarations stay
    # clean; lines=1 and first= prove the ONE reclassified line is the whole
    # residue, so the check cannot have bled onto its neighbours.
    tp = os.path.join(tmp, "M2.jsonl")
    _write_transcript(tp, [_user("do the thing"),
                           _assistant("✅ `universal/coding.md`\n"
                                      "⇠ `202608/query_202608080100.md`\n"
                                      "➡️ **`202608/response_202608080100.md`**\n"
                                      "🦈 Default: `302d7d8c`")])
    code2, line2, _ = _run(_payload(tp), log)
    _record("M2 lone labelled line flags inside a clean TEA3 batch",
            code2 == 0 and _action(line2) == "yellow:sha_label",
            "got exit=%s action=%s" % (code2, _action(line2)))
    _record("M2b residue is that line alone (lines=1, first= the SHA line)",
            "\tlines=1\t" in line2 and "first=🦈 Default:" in line2,
            "line=%r" % line2)

    # M3. THE SANCTIONED SHAPE. §3.2.4.4's bare one-liner must stay clean --
    # the check may only ever reclassify a LABELLED line.
    run("M3 lone bare SHA line stays clean", "🦈 `302d7d8c`", "clean")

    # M4. THE LEGAL MULTI-REPO FORM, NEVER TOUCHED. Both directions of the
    # rule pinned: with 2+ lines the labels are the mandated §3.2.4.5 shape
    # (K1c/K1g pin the same from the ownership side; this pins it against
    # the new count gate specifically).
    run("M4 two labelled lines are the legal §3.2.4.5 form",
        "🦈 Default: `deadbeef`, `cafef00d`\n🦈 AJAP: `0ddba115`", "clean")

    # M5. The §3.1.6 bold wrapper is tolerated everywhere else, so it must
    # neither hide a label from this check nor break the glyph count.
    run("M5 bold-wrapped lone labelled line still flags",
        "**🦈 Default: `302d7d8c`**", "yellow:sha_label")

    # M6. PRECEDENCE. A lone line already in breach keeps `sha_shape`: the
    # label rides a body that is not a SHA list at all, and one line gets
    # one class -- the truer, coarser verdict.
    run("M6a lone labelled line with a non-hex token keeps sha_shape",
        "🦈 Default: `xyz67890`", "yellow:sha_shape")
    run("M6b lone labelled line with a prose tail keeps sha_shape",
        "🦈 Default: `302d7d8c` pushed cleanly", "yellow:sha_shape")

    # M7. READER owes zero chat text; the new class must not leak there.
    run("M7 READER mode is unchanged by the solo-label check",
        "🦈 Default: `302d7d8c`", "yellow:reader", cwd=READER_CWD)

    # M8. COUNT GATE UNDER FIRE: two `🦈` lines, one malformed. The count is
    # 2, so the labelled line is legal; only the malformed one flags, under
    # its own class, and lines=1 proves the labelled line walked free.
    tp8 = os.path.join(tmp, "M8.jsonl")
    _write_transcript(tp8, [_user("do the thing"),
                            _assistant("🦈 Default: `302d7d8c`\n"
                                       "🦈 AJAP: not backticked here")])
    code8, line8, _ = _run(_payload(tp8), log)
    _record("M8 2 lines: malformed keeps sha_shape, labelled walks free "
            "(lines=1)",
            code8 == 0 and _action(line8) == "yellow:sha_shape"
            and "\tlines=1\t" in line8,
            "got exit=%s action=%s line=%r" % (code8, _action(line8), line8))

    # M9. The exemption ladder still outranks the new class: a user typing
    # `override` disarms the whole lint, this check included.
    run("M9 `override` still exempts a solo-label breach",
        "🦈 Default: `302d7d8c`", "exempt:override",
        prompt="override, labels are fine today")


def section_sha_nolabel(tmp):
    """N. `sha_nolabel` (root CLAUDE.md §3.2.4.5): a BARE SHA line amongst a
    multi-repo turn's multiple `🦈` lines is a breach —— the solo-label
    check's exact MIRROR, added when the owner ordered the scan reversed.

    WHY THIS SECTION EXISTS, stated as the defect it pins: `_sha_ok` accepts
    a label-free body because §3.2.4.4's single-repo one-liner is legal, so
    a bare `🦈` line beside a labelled one passed as clean -- yet with 2+
    `🦈` lines the window IS the multi-repo form (m2.md's mid-turn push
    declares no `🦈` of its own, its SHA waits for TEA3, so no same-repo
    turn legitimately emits two), and §3.2.4.5.1 makes the shorthand
    mandatory on EVERY line there: a bare line's hashes belong to no repo
    the reader can name. Baseline-proven per coding.md: run with
    `CLINT_UNDER_TEST` at a pre-change copy and N1/N2/N5/N6/N9 fail (clean
    where the breach stands) and N8 with them (an exemption can only be
    LOGGED once a breach exists to exempt); the boundaries N3/N4/N7 pass
    either side, pinning that the mirror widened NOTHING it should not.

    THE PANIC HALF LIVES IN HLINT'S SUITE, said here so nobody hunts for it
    in this file: this class's correction reaches the model at the NEXT
    turn's start, and that turn is usually SINGLE-repo, where adding a
    label is the OPPOSITE breach (`sha_label`). The conditional wording
    that stops the advisory converting one breach into its mirror is
    pinned by `hlint_chat_tally_regression_test.py`.

    N1 two bare lines flag; a bare line beside a labelled one flags ALONE;
    N2 it flags inside a full, otherwise-clean TEA3 batch;
    N3 the fully labelled multi-repo form stays clean through the new check;
    N4 the lone bare line stays clean -- 0-1 lines are the solo check's;
    N5 the bold wrapper hides nothing;
    N6 precedence both ways: a malformed sibling keeps `sha_shape`, a bare
       one still draws `sha_nolabel`, one class per line, both counted;
    N7 READER mode is unchanged;
    N8 `override` still exempts;
    N9 three lines, two bare -> both flagged (lines=2).
    """
    print("\n--- N. `🦈` missing-label check (§3.2.4.5): 2+ lines, every "
          "line owes its shorthand ---")
    log = os.path.join(tmp, "N.log")

    def run(name, text, want_action, cwd=REPO_ROOT, prompt="do the thing"):
        tp = os.path.join(tmp, "N%s.jsonl" % re.sub(r"\W+", "_", name)[:40])
        _write_transcript(tp, [_user(prompt), _assistant(text)])
        got = _run(_payload(tp, cwd=cwd), log)
        _check(name, got, 0, want_action)
        return got

    # N1. THE BREACH, both populations. SHAs are real ones mined from this
    # repo's own `🦈` history (root §3.1.6.3's example set).
    _, l1a, _ = run("N1a two bare lines both flag",
                    "🦈 `deadbeef`, `cafef00d`\n🦈 `0ddba115`",
                    "yellow:sha_nolabel")
    _record("N1a residue counts BOTH bare lines (lines=2)",
            "\tlines=2\t" in l1a, "line=%r" % l1a)
    _, l1b, _ = run("N1b bare line beside a labelled one flags alone",
                    "🦈 Default: `deadbeef`\n🦈 `0ddba115`",
                    "yellow:sha_nolabel")
    _record("N1b labelled sibling walks free (lines=1, first= the bare line)",
            "\tlines=1\t" in l1b and "first=🦈 `0ddba115`" in l1b,
            "line=%r" % l1b)

    # N2. INSIDE THE REAL ARTEFACT -- the multi-repo TEA3 batch root
    # §3.1.6.3's own example draws, with one label dropped.
    tp = os.path.join(tmp, "N2.jsonl")
    _write_transcript(tp, [_user("do the thing"),
                           _assistant("✅ `universal/coding.md`\n"
                                      "⇠ `202608/query_202608080100.md`\n"
                                      "➡️ **`202608/response_202608080100.md`**\n"
                                      "🦈 `deadbeef`, `cafef00d`\n"
                                      "🦈 AJAP: `0ddba115`")])
    code2, line2, _ = _run(_payload(tp), log)
    _record("N2 bare line flags inside an otherwise-clean multi-repo batch "
            "(lines=1)",
            code2 == 0 and _action(line2) == "yellow:sha_nolabel"
            and "\tlines=1\t" in line2,
            "got exit=%s action=%s line=%r" % (code2, _action(line2), line2))

    # N3/N4. THE BOUNDARIES, pinned from the new check's side: the legal
    # fully labelled form (M4's twin) and the solo check's own territory.
    run("N3 fully labelled multi-repo form stays clean",
        "🦈 Default: `deadbeef`, `cafef00d`\n🦈 AJAP: `0ddba115`", "clean")
    run("N4 lone bare line stays clean (0-1 lines are solo territory)",
        "🦈 `deadbeef`", "clean")

    # N5. The §3.1.6 bold wrapper must not hide bareness from the check.
    run("N5 bold-wrapped bare line amongst 2 still flags",
        "**🦈 `deadbeef`**\n🦈 AJAP: `0ddba115`", "yellow:sha_nolabel")

    # N6. PRECEDENCE under fire, both orders: the malformed line keeps its
    # own coarser class, the bare sibling still draws the new one, and
    # lines=2 proves both were counted (M8's labelled sibling gave lines=1).
    tp6 = os.path.join(tmp, "N6a.jsonl")
    _write_transcript(tp6, [_user("do the thing"),
                            _assistant("🦈 AJAP: not backticked here\n"
                                       "🦈 `deadbeef`")])
    code6, line6, _ = _run(_payload(tp6), log)
    _record("N6a malformed first: verdict sha_shape, bare sibling still "
            "counted (lines=2)",
            code6 == 0 and _action(line6) == "yellow:sha_shape"
            and "\tlines=2\t" in line6,
            "got exit=%s action=%s line=%r" % (code6, _action(line6), line6))
    tp6b = os.path.join(tmp, "N6b.jsonl")
    _write_transcript(tp6b, [_user("do the thing"),
                             _assistant("🦈 `deadbeef`\n"
                                        "🦈 AJAP: not backticked here")])
    code6b, line6b, _ = _run(_payload(tp6b), log)
    _record("N6b bare first: verdict sha_nolabel, malformed keeps its class "
            "in the count (lines=2)",
            code6b == 0 and _action(line6b) == "yellow:sha_nolabel"
            and "\tlines=2\t" in line6b,
            "got exit=%s action=%s line=%r"
            % (code6b, _action(line6b), line6b))

    # N7/N8. READER owes zero chat text regardless, and the exemption
    # ladder still outranks the new class.
    run("N7 READER mode is unchanged by the missing-label check",
        "🦈 `deadbeef`\n🦈 AJAP: `0ddba115`", "yellow:reader",
        cwd=READER_CWD)
    run("N8 `override` still exempts a missing-label breach",
        "🦈 `deadbeef`\n🦈 `0ddba115`", "exempt:override",
        prompt="override, no labels today")

    # N9. Three lines, two bare: every bare line is reclassified, not just
    # the first found.
    _, l9, _ = run("N9 three lines, two bare -> both flagged",
                   "🦈 Default: `deadbeef`\n🦈 `cafef00d`\n🦈 `0ddba115`",
                   "yellow:sha_nolabel")
    _record("N9 residue is the two bare lines (lines=2)",
            "\tlines=2\t" in l9, "line=%r" % l9)


# --- W. BASH-WRITE CATCH: comms writes that dodge every PostToolUse lint ---

# The real bypassed file (mined fixture, used READ-ONLY -- the suite never
# writes to the live sessions/ tree; the same precedent nlint's suite set).
# If this file is ever archived/moved, W0 fails NAMING that cause -- update
# the constant to any committed comms .md rather than weakening the section.
INCIDENT_REL = "sessions/2026/202608/ccsim_response_202608081357.md"
INCIDENT_ABS = os.path.join(REPO_ROOT, INCIDENT_REL)
INCIDENT_BASE = os.path.basename(INCIDENT_REL)

# A replica of the incident's own command shape: a `python3` heredoc that
# read the file, transformed the text, and wrote it back with mode "w" --
# the exact write no PostToolUse hook ever saw.
INCIDENT_CMD = ('cd "%s" && python3 - <<\'PYEOF\'\n'
                'p="%s"; s=open(p,encoding="utf-8").read()\n'
                's=s.replace("a","a")\n'
                'open(p,"w",encoding="utf-8").write(s); print("updated")\n'
                'PYEOF' % (REPO_ROOT, INCIDENT_REL))

# Trigger timestamps for the mtime gate: PAST accepts any existing file's
# mtime as "modified this turn"; FUTURE proves a mere MENTION of a write
# shape is suppressed when the file demonstrably did not change.
TS_PAST = "2020-01-01T00:00:00.000Z"
TS_FUTURE = "2099-01-01T00:00:00.000Z"


def _user_ts(text, ts, pid="pid-W"):
    o = _user(text, pid)
    o["timestamp"] = ts
    return o


def _assistant_bash(cmd, text=None):
    """An assistant message carrying a Bash tool_use block (the shape the
    live transcript stores) and, optionally, a text block too."""
    blocks = [{"type": "tool_use", "name": "Bash", "input": {"command": cmd}}]
    if text is not None:
        blocks.append({"type": "text", "text": text})
    return {"type": "assistant", "isSidechain": False,
            "message": {"role": "assistant", "content": blocks}}


def _field(log_line, key):
    for f in log_line.split("\t"):
        if f.startswith(key + "="):
            return f[len(key) + 1:]
    return "<none>"


def section_bash_write(tmp):
    """W. BASH-WRITE CATCH (`bashw=` log field; clint.py docstring section
    of that name): a comms file written or edited THROUGH A BASH COMMAND is
    seen by NO PostToolUse lint -- they all register on Write|Edit|MultiEdit
    -- so clint's Stop scan, which already parses the turn's window, records
    the write in its log line's `bashw=` field for hlint to advise on at the
    next prompt (that delivery half is pinned by the tally suite).

    WHY THIS SECTION EXISTS, stated as the incident it pins: a real turn
    appended eleven numbered sub-points to a live `response_` via a
    `python3 - <<'PY'` heredoc (`open(path, "w")`); nlint's tenth-sibling
    rule fires when SHOWN that file -- proven by hand against the real
    hook -- but no PostToolUse hook ever ran, the breach shipped, and the
    owner read the miss as "nlint is not working". The lint was bypassed,
    not broken; this section pins the mechanical catch for the bypass.
    Baseline-proven per coding.md: against a pre-change copy
    (`CLINT_UNDER_TEST`) EVERY W case bar the W0 preflight fails, the
    silences included -- the `bashw=` field does not exist there at all,
    so even "stays `-`" is unmeetable. That totality is the point: the
    whole field, not merely its firing rule, is what this change adds.

    W0 the mined fixture file still exists where this suite pins it;
    W1 THE INCIDENT REPLICA: heredoc write -> chat-clean turn, `bashw=`
       carries the basename;
    W2 legitimate Bash never fires it: reads, greps, `git`, a hand-run
       dlint, and the Move Rule's `mv` all leave `bashw=-`;
    W3 the other write shapes fire too: `>` redirect and `tee`;
    W4 the MTIME GATE: a write-shaped command whose file did not change
       this turn (future trigger timestamp) is suppressed;
    W5 a write aimed at an absent comms file is suppressed (nothing
       unlinted exists);
    W6 READER mode records nothing -- comms conventions are this repo's;
    W7 `override` exempts the CHAT verdict but the field still records --
       exemptions govern chat text, never lint coverage;
    W8 the field rides a breach verdict unchanged.
    """
    print("\n--- W. BASH-WRITE CATCH: comms writes that dodge every "
          "PostToolUse lint ---")
    log = os.path.join(tmp, "W.log")

    def run_bash(name, cmd, ts=TS_PAST, text="✅ `universal/coding.md`",
                 cwd=REPO_ROOT, prompt="do the thing"):
        tp = os.path.join(tmp, "W%s.jsonl" % re.sub(r"\W+", "_", name)[:40])
        _write_transcript(tp, [_user_ts(prompt, ts),
                               _assistant_bash(cmd, text)])
        return _run(_payload(tp, cwd=cwd), log)

    # W0. PREFLIGHT on the mined fixture, so a future archival of the real
    # file fails loudly HERE instead of as a mystery in W1.
    _record("W0 mined fixture file still present: %s" % INCIDENT_REL,
            os.path.isfile(INCIDENT_ABS),
            "move/archive detected -- repoint INCIDENT_REL at a committed "
            "comms .md")

    # W1. THE INCIDENT REPLICA. The turn's chat is clean; the write must be
    # recorded all the same -- the real incident's turn was exactly that,
    # which is why a chat-only lint never saw it.
    code1, line1, _ = run_bash("1 incident heredoc", INCIDENT_CMD)
    _record("W1 heredoc write -> action=clean, bashw= names the file",
            code1 == 0 and _action(line1) == "clean"
            and _field(line1, "bashw") == INCIDENT_BASE,
            "got exit=%s action=%s bashw=%r line=%r"
            % (code1, _action(line1), _field(line1, "bashw"), line1))

    # W2. LEGITIMATE BASH, the false-positive population that would turn
    # this catch into wallpaper: reads, searches, git plumbing, the
    # §3.5.5-mandated hand run of dlint, and the Move Rule's `mv`.
    for tag, cmd in (
            ("cat", 'cat "%s"' % INCIDENT_ABS),
            ("grep", 'grep -n "199.4" "%s" | head -5' % INCIDENT_ABS),
            ("git", 'cd "%s" && git add "%s" && git commit -m "x"'
             % (REPO_ROOT, INCIDENT_REL)),
            ("dlint", 'cd "%s" && python3 cscpt/dlint.py --quick %s'
             % (REPO_ROOT, INCIDENT_REL)),
            ("mv", 'cd "%s" && mv "%s" "sessions/2026/202608/❌_%s"'
             % (REPO_ROOT, INCIDENT_REL, INCIDENT_BASE))):
        code2, line2, _ = run_bash("2 legit %s" % tag, cmd)
        _record("W2 legitimate `%s` stays bashw=-" % tag,
                code2 == 0 and _field(line2, "bashw") == "-",
                "got bashw=%r line=%r" % (_field(line2, "bashw"), line2))

    # W3. THE OTHER WRITE SHAPES. A `>` redirect aimed at the comms file,
    # and a `tee` carrying it.
    code3, line3, _ = run_bash(
        "3 redirect", 'cd "%s" && printf \'%%s\' "x" > %s'
        % (REPO_ROOT, INCIDENT_REL))
    _record("W3a `>` redirect into the comms file fires",
            code3 == 0 and _field(line3, "bashw") == INCIDENT_BASE,
            "got bashw=%r line=%r" % (_field(line3, "bashw"), line3))
    code3b, line3b, _ = run_bash(
        "3b tee", 'echo "x" | tee "%s" >/dev/null' % INCIDENT_ABS)
    _record("W3b `tee` into the comms file fires",
            code3b == 0 and _field(line3b, "bashw") == INCIDENT_BASE,
            "got bashw=%r line=%r" % (_field(line3b, "bashw"), line3b))
    for tag, flag in (("sed -i", "sed -i ''"), ("perl -pi", "perl -pi")):
        code3c, line3c, _ = run_bash(
            "3c %s" % tag, "%s -e 's/x/y/' \"%s\"" % (flag, INCIDENT_ABS))
        _record("W3c in-place `%s` fires (clustered flag included)" % tag,
                code3c == 0 and _field(line3c, "bashw") == INCIDENT_BASE,
                "got bashw=%r line=%r" % (_field(line3c, "bashw"), line3c))
    code3d, line3d, _ = run_bash(
        "3d piped grep -i", 'sed \'s/a/b/\' "%s" | grep -i foo'
        % INCIDENT_ABS)
    _record("W3d `sed … | grep -i` does NOT read as in-place (pipe stops "
            "the flag scan)",
            code3d == 0 and _field(line3d, "bashw") == "-",
            "got bashw=%r line=%r" % (_field(line3d, "bashw"), line3d))

    # W4. THE MTIME GATE. Same heredoc, but the trigger timestamp is later
    # than the file's mtime -> the file provably did not change this turn,
    # so a command that merely LOOKS like a write is suppressed.
    code4, line4, _ = run_bash("4 mtime gate", INCIDENT_CMD, ts=TS_FUTURE)
    _record("W4 write-shaped command, file untouched this turn -> bashw=-",
            code4 == 0 and _field(line4, "bashw") == "-",
            "got bashw=%r line=%r" % (_field(line4, "bashw"), line4))

    # W5. ABSENT TARGET. A failed or fictitious write leaves nothing
    # unlinted on disk -> quiet.
    code5, line5, _ = run_bash(
        "5 absent", 'echo "x" > sessions/2026/202608/'
        'ccsim_response_209912312358.md')
    _record("W5 write aimed at an absent comms file -> bashw=-",
            code5 == 0 and _field(line5, "bashw") == "-",
            "got bashw=%r line=%r" % (_field(line5, "bashw"), line5))

    # W6. READER MODE. Comms conventions are this repo's; the Reader
    # session records nothing (no text block, so its zero-text rule has
    # nothing to flag either).
    code6, line6, _ = run_bash("6 reader", INCIDENT_CMD, cwd=READER_CWD,
                               text=None)
    _record("W6 READER mode: no catch (bashw=-)",
            code6 == 0 and _field(line6, "bashw") == "-",
            "got bashw=%r line=%r" % (_field(line6, "bashw"), line6))

    # W7/W8. ORTHOGONALITY. The exemptions govern CHAT text, never lint
    # coverage, so the field rides an exempt verdict; and a breach verdict
    # carries it unchanged.
    code7, line7, _ = run_bash("7 override", INCIDENT_CMD,
                               text="chatting away regardless",
                               prompt="override, prose is fine today")
    _record("W7 `override` turn: exempt verdict, bashw still recorded",
            code7 == 0 and _action(line7) == "exempt:override"
            and _field(line7, "bashw") == INCIDENT_BASE,
            "got action=%s bashw=%r line=%r"
            % (_action(line7), _field(line7, "bashw"), line7))
    code8, line8, _ = run_bash("8 breach", INCIDENT_CMD,
                               text="free prose, no glyph")
    _record("W8 breach turn: yellow verdict, bashw recorded alongside",
            code8 == 0 and _action(line8) == "yellow:prose"
            and _field(line8, "bashw") == INCIDENT_BASE,
            "got action=%s bashw=%r line=%r"
            % (_action(line8), _field(line8, "bashw"), line8))


# --- L. SENTINEL LISTS: root §5's mandated compaction output is not a breach

# The §3.2.6 canon, copied VERBATIM (clint compares the whole stripped line).
SENTINEL = "🚨 Compaction Detected —— stopped all tasks."

# The §5.3/§5.4 shape as the protocol's own example draws it: a `:`-headed
# list of still-useful reads, then a second such list of the remainder.
S5_LISTS = ("Previously read —— likely still needed:\n"
            "- `dupbus-ceztuc-7cufVe/CLAUDE.md`\n"
            "- `universal/glossary.md`\n\n"
            "Not useful any more:\n"
            "- `temp/scratch_202608.md`")


def section_sentinel_lists(tmp):
    """L. SENTINEL LISTS (root CLAUDE.md §5.3–§5.4).

    WHY THIS SECTION EXISTS, stated as the defect it pins: root §5.2–§5.4
    MANDATE chat output after a compaction —— the exact §3.2.6 sentinel plus
    two non-numbered lists of what was read —— and mlint (SHAPE C, hook_guide
    §6.9.9) BLOCKS the turn until that output exists. clint then flagged those
    very lines as `yellow:prose`: one suite mandating and forbidding the SAME
    output, and the log —— clint's PRIMARY artefact since the demotion ——
    recording every genuine compaction as a breach. Measured through the real
    registered command, not reasoned about: the L1 fixture returned
    `yellow:prose lines=5` before the fix and `clean:compaction` after; the
    L7 fixture (mined from this Mac's own transcript, session 0b6a0a90,
    2026-08-07, which logged `yellow:prose lines=17`) now flags ONLY its two
    stray dots.

    L1 the mandated shape is CLEAN, under its own `clean:compaction` tag;
    L2 the SAME lists without the sentinel are STILL prose —— the escape
       arms on the canon, never on bullets alone;
    L3 a free paragraph inside a sentinel window STILL flags —— only the two
       §5 list shapes are sanctioned, and the residue count proves the lists
       themselves walked free;
    L4 a `:`-header NOT followed by a list item is STILL prose —— the header
       shape is adjacency, not punctuation;
    L5 a paraphrased or bold-wrapped sentinel does NOT arm the escape ——
       an approximable sentinel is worthless, so both stay `yellow:sentinel`;
    L6 READER mode is NOT widened —— §5 is this repo's protocol;
    L7 the real multi-wake window: dot wakes + sentinel + lists +
       declaration batch -> only the dots remain in breach;
    L8 a glyph-misuse line inside a sentinel window keeps its OWN class ——
       the escape only ever touches class `prose`.
    """
    print("\n--- L. sentinel lists (root §5.3–§5.4): mandated compaction "
          "output is not a breach ---")
    log = os.path.join(tmp, "L.log")

    def run(name, blocks, want_action, cwd=REPO_ROOT):
        tp = os.path.join(tmp, "L%s.jsonl" % re.sub(r"\W+", "_", name)[:40])
        objs = [_user("do the thing")] + [_assistant(b) for b in blocks]
        _write_transcript(tp, objs)
        got = _run(_payload(tp, cwd=cwd), log)
        _check(name, got, 0, want_action)
        return got

    # L1. The mandated shape, exactly as §5 draws it, logs its OWN clean tag
    # (never bare `clean`: a genuine compaction must stay auditable).
    run("L1 sentinel + both §5 lists -> clean:compaction",
        [SENTINEL + "\n\n" + S5_LISTS], "clean:compaction")

    # L2. TRIGGER PINNED: the very same lists WITHOUT the canon are ordinary
    # prose. Bullets alone must never become a licence.
    run("L2 same lists, no sentinel -> still prose",
        [S5_LISTS], "yellow:prose")

    # L3. Only the two list shapes are sanctioned: a free paragraph in the
    # same window keeps flagging, and it flags ALONE -- lines=1 proves the
    # mandated lists were excused whilst the paragraph was not.
    _, line3, _ = run("L3 free paragraph beside the lists -> still prose",
                      [SENTINEL + "\n\n" + S5_LISTS +
                       "\nResuming the sprint from its latest block now."],
                      "yellow:prose")
    _record("L3b residue is the paragraph alone (lines=1)",
            "\tlines=1\t" in line3, "line=%r" % line3)

    # L4. The header shape is ADJACENCY (next non-blank line is a `- ` item),
    # not merely ending in `:` -- otherwise any sentence could dress as one.
    run("L4 `:`-line not followed by a list item -> still prose",
        [SENTINEL + "\nEverything below is fine and settled:\nno list here"],
        "yellow:prose")

    # L5. EXACT CANON ONLY, same standard as the sentinel's own pass rule:
    # a paraphrase (or a bold wrapper) is class `sentinel`, and it must not
    # arm the escape for the bullets riding under it either.
    run("L5a paraphrased sentinel does not arm the escape",
        ["🚨 Compaction detected —— all tasks stopped.\n- `a.md`"],
        "yellow:sentinel")
    run("L5b bold-wrapped sentinel does not arm the escape",
        ["**" + SENTINEL + "**\n- `a.md`"], "yellow:sentinel")

    # L6. READER owes ZERO chat text and owns no §5 protocol; the whole
    # compaction package stays a breach there.
    run("L6 sentinel + lists in READER mode -> still reader",
        [SENTINEL + "\n\n" + S5_LISTS], "yellow:reader", cwd=READER_CWD)

    # L7. THE REAL WINDOW, mined not synthesised: task-notification wakes do
    # not move the scan boundary, so the live shape is dot wakes AND the §5
    # package AND the declaration batch in ONE window. The dots stay flagged
    # (a lone `.` is only sanctioned alone -- see section J), the mandated
    # lists and the batch walk free, and the count says exactly that.
    _, line7, _ = run("L7 live multi-wake window -> only the dots flag",
                      [".", SENTINEL + "\n\n" + S5_LISTS, ".",
                       "✅ `universal/qq.md`, `cscpt/clint.py`\n"
                       "➡️ **`202608/ccsim_response_202608070502.md`**"],
                      "yellow:prose")
    _record("L7b residue is the two dots (lines=2, first=.)",
            "\tlines=2\t" in line7 and line7.rstrip().endswith("first=."),
            "line=%r" % line7)

    # L8. NON-PROSE CLASSES ARE NEVER TOUCHED: a glyph carrying the wrong
    # body keeps its own granular class even inside a sentinel window.
    run("L8 glyph misuse beside the lists keeps its own class",
        [SENTINEL + "\n\n" + S5_LISTS + "\n✅ read everything important"],
        "yellow:io_shape")


def main():
    print("clint.py ALWAYS-YELLOW regression test")
    print("target: %s" % CLINT)
    with tempfile.TemporaryDirectory(prefix="clint-yellow-") as tmp:
        section_no_ceiling(tmp)
        section_loop_guard(tmp)
        section_yn(tmp)
        section_dats(tmp)
        section_api_error(tmp)
        section_reader(tmp)
        section_failsafe(tmp)
        section_redirect(tmp)
        section_dot_escape(tmp)
        section_sha_declaration(tmp)
        section_sha_label(tmp)
        section_sha_nolabel(tmp)
        section_bash_write(tmp)
        section_sentinel_lists(tmp)
        # LAST on purpose: H11 measures the shortest record this suite made
        # clint write, so every other section must have run first.
        section_prune(tmp)

        print("\n--- resulting log lines (all sections, in order) ---")
        for name in sorted(os.listdir(tmp)):
            if not name.endswith(".log"):
                continue
            for ln in _log_lines(os.path.join(tmp, name)):
                # Drop the leading timestamp so the output is stable to read.
                print("  " + ln.split("\t", 1)[1])

    total, passed = len(_RESULTS), sum(1 for r in _RESULTS if r)
    print("\n%d/%d passed" % (passed, total))
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
