#!/usr/bin/env python3
"""Regression test for cscpt/clint.py's ALWAYS-RED rewrite.

WHY this test exists (coding.md: "a fix without its test is unfinished").
clint.py used to tier its verdicts: the FIRST chat-prose breach under a given
user prompt blocked (exit 2), every later breach under that same prompt was
downgraded to a log-only "yellow" by a ledger read back from clint's own log.
The owner reversed that: EVERY breach must block, the ledger and the yellow
tier are gone, and two narrow exemptions were added (the `yn` one-word-answer
override, and the single `DATS` status line that `universal/close.md` mandates
after a #close). This test pins:

  A. the ceiling is really gone -- three successive breaches under ONE promptId
     all exit 2 (under the old ledger, breaches 2 and 3 exited 0);
  B. the loop is still impossible -- a continuation that was itself forced by a
     block never blocks again, via EITHER guard independently, so the two
     guards are proven to work alone and not merely together;
  C. the `yn` exemption, using the three REAL prompts mined from this Mac's own
     transcripts (coding.md: "mine historical/real data for fixtures") --
     including one where ` yn` sits mid-message, not at the end, which is why
     the check is a plain substring and not a trailing match;
  D. the `DATS` exemption's exact boundaries -- the sanctioned one-liner is
     exempt, a 2-line block is not, an 11-word line is not;
  E. harness-authored assistant text (`isApiErrorMessage`) never triggers a
     block, since the model did not write it;
  F. READER mode -- a session whose cwd is exactly the parent `GitHub/` folder
     owes ZERO chat text, so even a declaration glyph blocks there, whilst the
     same line is clean in this repo; and sibling repos under `GitHub/` are NOT
     dragged into that rule;
  G. every fail-safe path still exits 0 (malformed payload, out-of-scope,
     missing transcript);
  I. the breach message REDIRECTS instead of only forbidding -- a block used to
     tell the agent to stop and nothing else, so an agent that had something
     worth saying said it in the wrong channel, was told to stop, and then
     SWALLOWED it: the point died precisely BECAUSE the lint worked. The REPO
     message now also names where that content belongs (`response_`), and I
     pins all six things that remedy must be at once: present, delivered on
     EVERY breach class identically, prohibition-preserving (the original
     wording still there verbatim, so this is an addition and never a
     softening), glyph-free, digit-free bar a protocol section reference (a
     number in the message would tell the agent how close it came to a
     threshold), class-free, and REPO-ONLY -- the Reader session may create no
     file at all, so telling it to write one would instruct a breach of the
     rule being enforced. It also pins that an exempt or loop-guarded turn
     still emits NOTHING, so the remedy can never fire where no block did; and
  H. the diagnostic log SELF-PRUNES -- it used to grow one line per invocation
     forever, so it is now capped at a recent window. H pins all four things
     that cap has to be at once: bounded (never past the high-water mark),
     newest-first (the line written this very invocation is never the casualty
     of its own prune), non-eager (a log under the mark is left alone), and
     utterly fail-safe -- a prune that CANNOT run must leave the log intact and
     the turn unaffected, which H6 proves by making the temp file
     uncreatable and checking the appended line survives anyway; and
  J. the lone `.` escape (root CLAUDE.md §3.1.6.2, added to break a genuine
     deadlock: a Stop-hook block forces one more turn, and by then the agent
     has nothing new to declare and is forbidden from repeating what it
     already said) -- a turn whose ONLY non-blank content, across every text
     block, is a single line reading exactly one full stop is CLEAN in REPO
     mode, under its own `clean:dot` tag kept distinct from plain `clean` so
     the two stay separately auditable. Two dots, an ellipsis, trailing text
     on the same line, a bold `**.**` wrapper, and a dot sharing the turn with
     ANY other line -- even an otherwise well-formed declaration -- all stay
     breaches: the escape is for a turn with nothing else to say, not a
     vehicle for pairing a decorative dot with real content. REPO-only: it
     still blocks in READER mode, which needs no such escape of its own (a
     genuinely blank turn already clears there, per F3) and never writes a
     `response_` for the dot's redirect to reach.

It drives the REAL registered command from ~/.claude/settings.json
(`python3 .../cscpt/clint.py`, Stop hook) with synthesised payloads and
synthesised transcripts, so the behaviour is proven through the wiring the
harness actually uses, not through imported internals (coding.md: "'exists +
unit-tested' != done -- done only when WIRED and exercised end-to-end").

Self-contained: every transcript is written into a throwaway tempdir at run
time and CLINT_LOG is redirected there, so the real cscpt/.clint.log is
neither read nor polluted. Run directly:

    python3 "cp/ccsim/sandbox/clint_always_red_regression_test.py"

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
CLINT = os.path.join(REPO_ROOT, "cscpt", "clint.py")

# The Reader session's working directory: this repo's immediate parent. Its own
# CLAUDE.md mandates zero chat text, hence clint's stricter second rule.
READER_CWD = os.path.dirname(REPO_ROOT)
# A sibling repo under the same parent -- must NOT inherit the Reader rule.
SIBLING_CWD = os.path.join(READER_CWD, "AJAP_repo")

# The 5 declaration glyphs, base codepoints (the emoji variation selector is
# irrelevant to a substring search). Kept in ONE place so section A and section
# I can never drift into checking different sets: naming any of these in the
# stderr the model receives would teach exactly which prefixes pass.
GLYPHS = ("✅", "⇠", "➡", "⚠", "\U0001f6a8")

# A protocol section reference such as `§3.2`. Its digits are an ADDRESS, not a
# threshold, so they are stripped before the message is checked for digits --
# see section I for why any surviving digit is the actual hazard.
SECTION_REF_RE = re.compile(r"§\d+(?:\.\d+)*")

# clint's own log tags. None may appear in the stderr the model reads: the class
# is a diagnostic for the human reading the log, and telling the agent WHICH
# check caught it is telling it what to file the next attempt under.
CLASS_TOKENS = ("io_shape", "sentinel", "warn_empty", "warn_shape",
                "warn_words", "warn_hyphens", "warn_chars", "warn_progress",
                "sic_overrun", "reader", "block:", "exempt:", "loop_guard")

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
    """The harness's own continuation line after a Stop hook blocked."""
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
    """Exact Stop-payload key set as captured live this session."""
    return {"session_id": sid, "transcript_path": transcript_path,
            "prompt_id": "pid-A", "permission_mode": "default",
            "hook_event_name": "Stop", "stop_hook_active": stop_hook_active,
            "cwd": cwd}


def _run(payload, log_path, raw=None):
    """Invoke clint exactly as settings.json does; return (exit, last_log)."""
    before = _log_lines(log_path)
    stdin = raw if raw is not None else json.dumps(payload)
    r = subprocess.run([sys.executable, CLINT], input=stdin,
                       capture_output=True, text=True,
                       env=dict(os.environ, CLINT_LOG=log_path))
    after = _log_lines(log_path)
    new = after[len(before):]
    return r.returncode, (new[-1] if new else ""), r.stderr


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

    clint's log tags carry a granular class suffix (`block:prose`,
    `block:warn_words`, `exempt:sic`, ...) so a breach can be audited by REASON.
    A test that asserts the family (`block`) stays correct as new classes are
    added; a test that needs one specific class simply passes the full tag and
    still gets exact matching. Comparing families never blurs the outcomes that
    matter —— `block`, `exempt`, `clean` and `out_of_scope` remain distinct.
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


# --- A. the once-per-prompt ceiling is gone --------------------------------

def section_always_red(tmp):
    print("\n--- A. RED always: 3 breaches, ONE promptId, all must block ---")
    log = os.path.join(tmp, "A.log")
    tp = os.path.join(tmp, "A.jsonl")
    objs = [_user("do the thing", pid="pid-SAME")]
    for n in (1, 2, 3):
        objs.append(_assistant("Breach %d: unauthorised chat prose." % n))
        _write_transcript(tp, objs)
        _check("breach %d (same pid, ledger would have downgraded 2 and 3)" % n,
               _run(_payload(tp), log), 2, "block")
    # And the stderr the model actually receives must never name a glyph:
    _, _, err = _run(_payload(tp), log)
    _record("stderr stays glyph-free (cannot teach which prefixes pass)",
            err.strip() != "" and not any(g in err for g in GLYPHS),
            "stderr=%r" % err)


# --- B. the loop is still impossible ---------------------------------------

def section_loop_guard(tmp):
    print("\n--- B. loop guard: each signal must withhold the block ALONE ---")
    log = os.path.join(tmp, "B.log")

    # (a) payload flag alone: no feedback line in the transcript at all.
    tp = os.path.join(tmp, "B1.jsonl")
    _write_transcript(tp, [_user("go"), _assistant("More prose in the retry.")])
    _check("guard (a) stop_hook_active alone",
           _run(_payload(tp, stop_hook_active=True), log), 0, "loop_guard")

    # (b) transcript marker alone: stop_hook_active FALSE, as it would be if
    # the harness ever omitted the field -- the case that used to rely purely
    # on the deleted ledger.
    tp2 = os.path.join(tmp, "B2.jsonl")
    _write_transcript(tp2, [_user("go"), _assistant("First breach."),
                            _stop_feedback(),
                            _assistant("Still prose after being blocked.")])
    _check("guard (b) injected feedback line alone (flag false)",
           _run(_payload(tp2, stop_hook_active=False), log), 0, "loop_guard")

    # A human merely QUOTING the phrase must not be able to buy immunity.
    tp3 = os.path.join(tmp, "B3.jsonl")
    _write_transcript(tp3, [_user("Stop hook feedback: is what I want to discuss"),
                            _assistant("Sure, here is prose about it.")])
    _check("a human message quoting the marker is NOT a continuation",
           _run(_payload(tp3), log), 2, "block")

    # (b)'s one real gap, named in the docstring: a system wrapper appended
    # AFTER the feedback line displaces it as the scan boundary. Guard (a)
    # must still hold, which is why both guards are kept.
    tp4 = os.path.join(tmp, "B4.jsonl")
    _write_transcript(tp4, [_user("go"), _assistant("First breach."),
                            _stop_feedback(),
                            {"type": "user", "isSidechain": False,
                             "promptId": "pid-A",
                             "message": {"role": "user",
                                         "content": "<task-notification>done"}},
                            _assistant("Prose after the wrapper.")])
    _check("known wrapper after the feedback line: (b) still holds",
           _run(_payload(tp4, stop_hook_active=False), log), 0, "loop_guard")
    _check("UNKNOWN wrapper displaces (b) -- guard (a) must cover it",
           _run(_payload(tp4, stop_hook_active=True), log), 0, "loop_guard")

    # A NEW human prompt re-arms the block: the guard is per continuation
    # chain, never a per-prompt ceiling (that ledger is gone).
    tp5 = os.path.join(tmp, "B5.jsonl")
    _write_transcript(tp5, [_user("go", pid="pid-1"),
                            _assistant("First breach."), _stop_feedback("pid-1"),
                            _assistant("Second breach, guarded."),
                            _user("next thing please", pid="pid-2"),
                            _assistant("Fresh prose under a new prompt.")])
    _check("a new human prompt re-arms the block",
           _run(_payload(tp5, stop_hook_active=False), log), 2, "block")


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
        # "Yes" is the exact one-word reply the log shows really being blocked
        # before this exemption existed.
        _write_transcript(tp, [_user(prompt), _assistant("Yes")])
        _check("yn: %s" % label, _run(_payload(tp), log), 0, "exempt:yn")

    # The leading space is load-bearing: a word merely ENDING in "yn" is not
    # the override and must still be policed.
    tp = os.path.join(tmp, "Cneg.jsonl")
    _write_transcript(tp, [_user("Tell me about Brooklyn and synergy"),
                           _assistant("Brooklyn is a borough of New York.")])
    _check("`Brooklyn`/`synergy` do NOT count as the override",
           _run(_payload(tp), log), 2, "block")


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
         2, "block"),
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
           2, "block")

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
    _check("usage-limit line does not block the model for text it never wrote",
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
    _check("declaration glyphs block in the Reader session",
           _run(_payload(tp, cwd=READER_CWD), log), 2, "block")
    _check("the very same lines are clean in THIS repo",
           _run(_payload(tp, cwd=REPO_ROOT), log), 0, "clean")

    # Real Reader prose, verbatim.
    tp2 = os.path.join(tmp, "F2.jsonl")
    _write_transcript(tp2, [_user("ww it"),
                            _assistant("Reading instructions for #ww workflow.")])
    _check("Reader prose blocks", _run(_payload(tp2, cwd=READER_CWD), log),
           2, "block")

    # A genuinely silent Reader turn (tool calls only, no text block).
    tp3 = os.path.join(tmp, "F3.jsonl")
    _write_transcript(tp3, [_user("ww it"), _assistant("   \n\n")])
    _check("a silent Reader turn is clean",
           _run(_payload(tp3, cwd=READER_CWD), log), 0, "clean")

    # The exemptions are repo-only: the Reader owes silence NO MATTER WHAT.
    tp4 = os.path.join(tmp, "F4.jsonl")
    _write_transcript(tp4, [_user("did you read it yn"), _assistant("Yes")])
    _check("`yn` does NOT exempt the Reader",
           _run(_payload(tp4, cwd=READER_CWD), log), 2, "block")

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


# --- I. the breach message redirects, and destroys nothing ------------------

# One fixture per REPO breach CLASS, so the message is proven identical on all
# of them rather than on plain prose alone. Each `text` is a line clint really
# classifies as the named class (the trigger message is what arms `sic`).
_CLASS_FIXTURES = (
    ("prose", "do the thing",
     "The fleet finished; three agents reported clean."),
    ("io_shape", "do the thing",
     "✅ Read the plan and then carried on working."),
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
)


def section_redirect(tmp):
    print("\n--- I. breach message REDIRECTS the content, never buries it ---")
    log = os.path.join(tmp, "I.log")

    # Everything below is asserted against the bytes the model REALLY receives
    # from the registered command, never an imported constant: the message is
    # the entire payload of a block, so a test that trusts the source rather
    # than the stderr proves nothing about what the agent was told.
    tp = os.path.join(tmp, "I0.jsonl")
    _write_transcript(tp, [_user("do the thing"),
                           _assistant("The fleet finished; three agents "
                                      "reported clean.")])
    repo = _run(_payload(tp), log)
    reader = _run(_payload(tp, cwd=READER_CWD), log)
    repo_err, reader_err = repo[2], reader[2]

    print("    REPO stderr:   %s" % repo_err)
    print("    READER stderr: %s" % reader_err)

    _check("a REPO breach still blocks", repo, 2, "block:prose")
    _check("a READER breach still blocks", reader, 2, "block:reader")

    # I1. THE REMEDY EXISTS. Without it the agent is told to stop and nothing
    # else, so the content it meant to deliver is simply dropped.
    _record("I1 REPO message names where the content must go (`response_`)",
            "response_" in repo_err, "stderr=%r" % repo_err)

    # I2. THE PROHIBITION IS UNTOUCHED. The remedy is an ADDITION; if any of
    # these clauses ever go missing the message has been softened, not extended.
    kept = ("Chat-prose breach (root CLAUDE.md §3.2)", "emit ONLY",
            "never prose behind a glyph", "Avoid further prose.")
    missing = [k for k in kept if k not in repo_err]
    _record("I2 the original prohibition survives verbatim (%d clauses)"
            % len(kept), not missing, "missing=%r" % missing)

    # I3. GLYPH-FREE, both modes. Naming a permitted prefix teaches the agent
    # which one to bolt onto prose next time.
    for label, err in (("REPO", repo_err), ("READER", reader_err)):
        hit = [g for g in GLYPHS if g in err]
        _record("I3 %s message names no declaration glyph" % label,
                err.strip() != "" and not hit, "found=%r in %r" % (hit, err))

    # I4. NO NUMBER LEAKS. `§3.2` is an address and is stripped first; any
    # digit surviving that is a threshold the agent could spend up to, which is
    # exactly why the character cap lives only in the script's CCSIM block.
    for label, err in (("REPO", repo_err), ("READER", reader_err)):
        bare = SECTION_REF_RE.sub("", err)
        digits = [c for c in bare if c.isdigit()]
        _record("I4 %s message carries no digit outside a section reference"
                % label, not digits, "digits=%r in %r" % (digits, bare))

    # I5. NO BREACH CLASS LEAKS. The class is the log's business. ("prose" is
    # deliberately absent from CLASS_TOKENS: it is ordinary English in the
    # prohibition sentence and predates the tag of the same name -- what must
    # never appear is the TAG, `block:prose`, which `block:` covers.)
    for label, err in (("REPO", repo_err), ("READER", reader_err)):
        hit = [t for t in CLASS_TOKENS if t in err]
        _record("I5 %s message names no breach class or log tag" % label,
                not hit, "found=%r in %r" % (hit, err))

    # I6. REPO-ONLY. The Reader folder's CLAUDE.md forbids creating or editing
    # ANY file, so it writes no `response_` at all: a redirect there would
    # order a breach of the very rule being enforced, and its whole remedy is
    # to end silently.
    _record("I6 READER message gets NO redirect (that session creates no file)",
            "response_" not in reader_err, "stderr=%r" % reader_err)
    _record("I6b READER message keeps its own terminal instruction",
            "NO chat text at all" in reader_err
            and "End the turn silently" in reader_err,
            "stderr=%r" % reader_err)

    # I7. SHORT. The one channel reaching the model at Stop is this string, and
    # a long message is a worse message -- the cap is a ratchet against the
    # accretion that makes it skimmable-past.
    for label, err in (("REPO", repo_err), ("READER", reader_err)):
        _record("I7 %s message stays short (%d chars, cap 400)"
                % (label, len(err)), len(err) <= 400, "stderr=%r" % err)

    # I8. DELIVERED ON EVERY CLASS, IDENTICALLY. The remedy must not depend on
    # which check caught the line -- and the per-class log tags must still be
    # distinct, so the human diagnostic keeps the detail the model is denied.
    seen = {}
    for i, (klass, prompt, text) in enumerate(_CLASS_FIXTURES):
        tpc = os.path.join(tmp, "I%d.jsonl" % (i + 1))
        _write_transcript(tpc, [_user(prompt), _assistant(text)])
        got = _run(_payload(tpc), log)
        _check("I8 %s still exits 2 under its own log tag" % klass,
               got, 2, "block:" + klass)
        seen[klass] = got[2]
    same = [k for k, v in seen.items() if v != repo_err]
    _record("I8b every REPO breach class receives the SAME message (%d classes)"
            % len(seen), not same, "differing=%r" % same)

    # I9. NOTHING IS SAID WHERE NOTHING WAS BLOCKED. An exempt or loop-guarded
    # turn must stay silent: the remedy is part of a block, never advice
    # volunteered to a turn that was let through.
    quiet = (
        ("exempt:override", _user("override, just tell me in chat"), False),
        ("exempt:yn", _user("did it work yn"), False),
        ("exempt:dats", _user("#close"), False),
        ("loop_guard", _user("go"), True),
    )
    texts = {"exempt:override": "Here is the answer in plain chat prose.",
             "exempt:yn": "Yes",
             "exempt:dats": "DATS done. Fixed 3 file(s).",
             "loop_guard": "Prose in the forced continuation."}
    for j, (tag, trigger, flag) in enumerate(quiet):
        tpq = os.path.join(tmp, "Iq%d.jsonl" % j)
        _write_transcript(tpq, [trigger, _assistant(texts[tag])])
        got = _run(_payload(tpq, stop_hook_active=flag), log)
        _check("I9 %s still passes" % tag, got, 0, tag)
        _record("I9 %s emits no message at all" % tag, got[2] == "",
                "stderr=%r" % got[2])


# --- J. the lone `.` escape (root CLAUDE.md §3.1.6.2, DOT ESCAPE) ----------

def section_dot_escape(tmp):
    print("\n--- J. lone `.`: sanctioned no-op reply to a Stop-hook block ---")
    log = os.path.join(tmp, "J.log")

    # J1-J2: the bare token, with and without incidental whitespace -> CLEAN,
    # under its OWN tag (never the plain `clean` a declaration-only turn gets).
    clean_cases = [
        ("bare lone dot", "."),
        ("dot padded with leading/trailing whitespace", "   .   "),
    ]
    for i, (label, text) in enumerate(clean_cases):
        tp = os.path.join(tmp, "Jc%d.jsonl" % i)
        _write_transcript(tp, [_user("do the thing"), _assistant(text)])
        got = _run(_payload(tp), log)
        _check("dot: %s" % label, got, 0, "clean:dot")
        _record("dot: %s emits no stderr (nothing was blocked)" % label,
                got[2] == "", "stderr=%r" % got[2])

    # J3-J6: near misses, each failing the match for a NAMED reason -- every
    # one must still block as ordinary prose (no separate carve-out earns a
    # special tag; the strict shape either matches or it is just chat text).
    block_cases = [
        ("two dots is not ONE full stop", ".."),
        ("an ellipsis is not ONE full stop", "..."),
        ("more text after the dot, same line", ". hello"),
        ("a bold-wrapped dot is not the bare token", "**.**"),
    ]
    for i, (label, text) in enumerate(block_cases):
        tp = os.path.join(tmp, "Jb%d.jsonl" % i)
        _write_transcript(tp, [_user("do the thing"), _assistant(text)])
        _check("dot: %s" % label, _run(_payload(tp), log), 2, "block:prose")

    # J7: a `.` sharing the turn with an otherwise well-formed declaration on
    # a SEPARATE line must still block -- the escape is for a turn with
    # NOTHING else to say, not a vehicle for pairing a decorative dot onto a
    # real declaration batch. Checked over ALL non-blank lines, not only the
    # ones already flagged, precisely so this case cannot slip through.
    tp = os.path.join(tmp, "Jpair.jsonl")
    _write_transcript(tp, [_user("do the thing"),
                           _assistant(".\n✅ `cscpt/clint.py`")])
    _check("dot: alongside an otherwise-clean declaration is NOT exempt",
           _run(_payload(tp), log), 2, "block:prose")

    # J8: REPO-only. The Reader session's own rule tolerates no chat text at
    # all, the dot included -- it needs no escape of its own because a
    # genuinely blank turn already clears there (see section F, case F3).
    tp = os.path.join(tmp, "Jreader.jsonl")
    _write_transcript(tp, [_user("ww it"), _assistant(".")])
    _check("dot: still blocks in READER mode (no escape there)",
           _run(_payload(tp, cwd=READER_CWD), log), 2, "block:reader")

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


def main():
    print("clint.py ALWAYS-RED regression test")
    print("target: %s" % CLINT)
    with tempfile.TemporaryDirectory(prefix="clint-red-") as tmp:
        section_always_red(tmp)
        section_loop_guard(tmp)
        section_yn(tmp)
        section_dats(tmp)
        section_api_error(tmp)
        section_reader(tmp)
        section_failsafe(tmp)
        section_redirect(tmp)
        section_dot_escape(tmp)
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
