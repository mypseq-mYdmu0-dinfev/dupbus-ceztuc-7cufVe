#!/usr/bin/env python3
"""Regression test for the dlint family —— `cscpt/dlint.py`, `dlint_quick.py`
and `dlint_hook.sh`.

WHY THIS EXISTS (coding.md: "a fix without its test is unfinished"). It pins
three changes that landed together, each encoded as the failing scenario rather
than as a restatement of the fix:

  1. HART'S QUOTATION HAS NO EXEMPTION. `."` was YELLOW on the theory that the
     full stop might be original to the quote. The owner's ruling is that it is
     RED regardless, because the rule serves the reader's comfort and moving
     the stop out costs two clicks —— with ONE relief valve: past
     `HART_RED_MAX` hits in a single file the class demotes to YELLOW, since at
     that point it is no longer two clicks. The owner LATER extended the same
     treatment to `,"`, so both classes now carry the relief valve —— but with
     INDEPENDENT counters, so neither class can soften the other on evidence
     drawn from the other. Both directions of that are pinned below.

  2. `dlint_quick.py` COVERS EVERY `.md`, not three filename roles. Anything CC
     wrote outside `response_`/`close_`/`wrap_` was mechanically unchecked. The
     widening carries three named carve-outs (`query_` skipped outright; a
     non-comms verdict scoped to the text the write produced; a permanent
     `<!-- dlint: skip -->` dismissal), and NONE of them may reach a comms file
     —— whatever was enforced before must still be enforced now.

  3. THE DELIVERABLE GATE MOVED IN. It was `elint.py`, three tiers on two
     registrations. Tier A became redundant once `dlint_quick` fired on the
     deliverable's own write with the same reminder, and Tier C only ever
     reached the user. What survives is the middle tier: a comms write BLOCKS
     whilst a deliverable is still un-linted by FULL `dlint.py`. It earned its
     place —— a real interview cheat sheet was drafted, debated twice, and
     delivered un-linted, and a retroactive FULL run found 18 RED. That exact
     pre-lint text is the fixture beside this file
     (`elint_fixture_cheatsheet_prelint.md`), so the suite proves the gate
     against the case that motivated it rather than a synthetic stand-in.

HOW IT DRIVES THE REAL CODE. `dlint_quick.py` derives the repo root from its
own `__file__`, so every check runs inside a SYNTHETIC repo built in a temp dir
whose `cscpt/` holds SYMLINKS to the real `dlint_quick.py`, `dlint_hook.sh` and
`dlint.py`. Symlinks, not copies: `os.path.abspath(__file__)` does not resolve
them, so the scripts anchor on the synthetic repo whilst the bytes executed are
the LIVE ones —— a copy could drift from the file it claims to pin. Nothing in
the user's real tree is read or written, and no live `.md` is touched.

WHAT IT CANNOT PROVE. Exactly what `cp/ccsim/hook_guide.md` §7.1 warns about:
this drives the scripts with synthesised payloads, which tests the SCRIPT. It
says NOTHING about whether the harness invokes them. That claim needs the live
probe in the hook guide, run after the registration exists in
`~/.claude/settings.json`, and must never be inferred from a green run here.
"""

import os
import re
import sys
import json
import shutil
import tempfile
import importlib.util
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CSCPT = os.path.join(REPO, "cscpt")
QUICK = os.path.join(CSCPT, "dlint_quick.py")
SHIM = os.path.join(CSCPT, "dlint_hook.sh")
DLINT = os.path.join(CSCPT, "dlint.py")
FIXTURE = os.path.join(HERE, "elint_fixture_cheatsheet_prelint.md")

PASS = 0
FAIL = []

# Long enough to clear the substance floor without being a real document, and
# deliberately free of every quick-mode RED so it can stand in for "clean
# prose" throughout.
FILLER = ("This paragraph exists so the fixture clears the substance floor "
          "that keeps stubs, placeholders and index fragments out of scope. "
          "It is ordinary prose, it says nothing of consequence, and it is "
          "repeated only to reach a plausible length for a short one-pager "
          "that somebody might actually hand over to a third party. ") * 2

DELIV = "temp/temp_misc/20260801_probe/output/ONEPAGER_Client.md"


def check(name, cond, detail=""):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append("%s%s" % (name, (" —— " + str(detail)) if detail else ""))


class Repo(object):
    """A synthetic repo whose `cscpt/` symlinks the LIVE scripts."""

    def __init__(self):
        self.root = os.path.realpath(tempfile.mkdtemp(prefix="dlint_rt_"))
        os.makedirs(os.path.join(self.root, "cscpt"))
        for src in (QUICK, SHIM, DLINT):
            os.symlink(src, os.path.join(self.root, "cscpt",
                                         os.path.basename(src)))
        self.quick = os.path.join(self.root, "cscpt", "dlint_quick.py")
        self.shim = os.path.join(self.root, "cscpt", "dlint_hook.sh")
        self.dlint = os.path.join(self.root, "cscpt", "dlint.py")
        self._mod = None

    def mod(self):
        """The LIVE module, imported through this repo's symlink so its
        `__file__`-derived anchors point HERE rather than at the real repo.

        Load-bearing, not a convenience: a plain `import dlint_quick` resolves
        the real `cscpt/`, and every synthetic path then classifies as
        `outside_repo` —— which makes an "is excluded" assertion pass for the
        wrong reason and prove nothing. The canary in `test_classifier` guards
        exactly that."""
        if self._mod is None:
            name = "dlint_quick_rt_%s" % os.path.basename(self.root)
            spec = importlib.util.spec_from_file_location(name, self.quick)
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            self._mod = m
        return self._mod

    def write(self, rel, text):
        p = os.path.join(self.root, rel)
        d = os.path.dirname(p)
        if d and not os.path.isdir(d):
            os.makedirs(d)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        return p

    def payload(self, session, path, tool="Write", cwd=True, ti_extra=None):
        d = {"session_id": session, "hook_event_name": "PostToolUse"}
        if cwd:
            d["cwd"] = self.root
        if path is not None:
            d["tool_name"] = tool
            ti = {"file_path": path}
            if ti_extra:
                ti.update(ti_extra)
            d["tool_input"] = ti
        return json.dumps(d)

    def post(self, session, path, tool="Write", cwd=True, via_shim=False,
             ti_extra=None):
        body = self.payload(session, path, tool, cwd, ti_extra)
        return self.run(body, shim=via_shim)

    def run(self, body, shim=False, raw=None):
        cmd = ["bash", self.shim] if shim else [sys.executable, self.quick]
        return subprocess.run(cmd, input=(raw if raw is not None else body),
                              capture_output=True, text=True, timeout=60)

    def lint(self, path, *flags):
        return subprocess.run(
            [sys.executable, self.dlint] + list(flags) + [path],
            capture_output=True, text=True, timeout=60)

    def receipts(self):
        p = os.path.join(self.root, "cscpt", ".dlint_receipts.jsonl")
        if not os.path.isfile(p):
            return []
        with open(p, "r", encoding="utf-8") as fh:
            return [json.loads(x) for x in fh if x.strip()]

    def log(self):
        p = os.path.join(self.root, "cscpt", ".dlint.log")
        if not os.path.isfile(p):
            return []
        with open(p, "r", encoding="utf-8") as fh:
            return [x.rstrip("\n") for x in fh if x.strip()]

    def close(self):
        shutil.rmtree(self.root, ignore_errors=True)


def advises(r):
    """True if this result carries a model-visible PostToolUse advisory."""
    if r.returncode != 0 or not r.stdout.strip():
        return False
    try:
        d = json.loads(r.stdout)
    except Exception:
        return False
    return bool((d.get("hookSpecificOutput") or {}).get("additionalContext"))


def ctx(r):
    try:
        return (json.loads(r.stdout).get("hookSpecificOutput")
                or {}).get("additionalContext") or ""
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# A. HART'S QUOTATION —— the rule the owner rewrote
# ---------------------------------------------------------------------------
def test_hart():
    sys.path.insert(0, CSCPT)
    try:
        import dlint                                            # noqa: E402
    finally:
        sys.path.remove(CSCPT)

    def quick(t):
        return dlint.run_checks(t, quick=True)

    def hart_msgs(flags):
        return [m for _, m in flags if "closing quote" in m]

    red, yellow = quick('He said "I am leaving".')
    check("A/punctuation outside the quote is clean", not red and not yellow)

    red, yellow = quick('He said "I am leaving."')
    check("A/a single `.”` is RED, with no `might be original` escape",
          len(hart_msgs(red)) == 1 and not hart_msgs(yellow),
          "red=%s yellow=%s" % (red, yellow))
    check("A/and the flag says to move it out ALWAYS",
          red and "even if the mark is original" in red[0][1], red)

    five = " ".join('X "q%d."' % i for i in range(5))
    red, yellow = quick(five)
    check("A/exactly %d hits stay RED" % dlint.HART_RED_MAX,
          len(hart_msgs(red)) == 5 and not hart_msgs(yellow),
          "red=%d yellow=%d" % (len(red), len(yellow)))

    six = " ".join('X "q%d."' % i for i in range(6))
    red, yellow = quick(six)
    check("A/more than %d demotes the WHOLE class to YELLOW"
          % dlint.HART_RED_MAX,
          not hart_msgs(red) and len(hart_msgs(yellow)) == 6,
          "red=%d yellow=%d" % (len(red), len(yellow)))
    check("A/the demotion warns rather than silently passing",
          yellow and "does the mark truly belong INSIDE" in yellow[0][1],
          yellow[:1])

    # THE COMMA CLASS NOW GETS THE SAME TREATMENT, and nothing less: a single
    # `,"` is RED with no exemption, exactly as `."` is.
    red, yellow = quick('He said "I am leaving," then left.')
    check("A/a single `,”` is RED, with no exemption",
          len(hart_msgs(red)) == 1 and not hart_msgs(yellow),
          "red=%s yellow=%s" % (red, yellow))
    check("A/and the comma flag says to move it out ALWAYS",
          red and "even if the mark is original" in red[0][1], red)

    five_c = " ".join('X "c%d,"' % i for i in range(5))
    red, yellow = quick(five_c)
    check("A/exactly %d commas stay RED" % dlint.HART_RED_MAX,
          len(hart_msgs(red)) == 5 and not hart_msgs(yellow),
          "red=%d yellow=%d" % (len(red), len(yellow)))

    six_c = " ".join('X "c%d,"' % i for i in range(6))
    red, yellow = quick(six_c)
    check("A/more than %d commas demote the comma class to YELLOW"
          % dlint.HART_RED_MAX,
          not hart_msgs(red) and len(hart_msgs(yellow)) == 6,
          "red=%d yellow=%d" % (len(red), len(yellow)))

    # THE CROSS-CONTAMINATION GUARD, and the reason the counters are INDEPENDENT
    # rather than shared. Clearing six commas is not clearing the one period, so
    # a comma-heavy file must not buy the period rule out (nor the reverse).
    red, yellow = quick(" ".join('X "c%d,"' % i for i in range(6))
                        + ' and Y "p."')
    check("A/6 commas demote themselves but NOT a lone period",
          len(red) == 1 and "period" in red[0][1] and len(yellow) == 6,
          "red=%s yellow=%d" % (red, len(yellow)))
    red, yellow = quick(" ".join('X "p%d."' % i for i in range(6))
                        + ' and Y "c,"')
    check("A/6 periods demote themselves but NOT a lone comma",
          len(red) == 1 and "comma" in red[0][1] and len(yellow) == 6,
          "red=%s yellow=%d" % (red, len(yellow)))

    red, yellow = quick('He trailed off "like this..." and stopped.')
    check("A/an ellipsis is not a full stop and stays exempt",
          not hart_msgs(red) and not hart_msgs(yellow), "%s %s" % (red, yellow))

    red, _ = quick('Ask "why."\n\n```\nprint("done.")\n```\n')
    check("A/the rule never fires inside a code fence", len(hart_msgs(red)) == 1,
          hart_msgs(red))

    # The threshold is per FILE, so two separate files each under it both stay
    # RED —— it must never become a per-run budget.
    rt = Repo()
    try:
        a = rt.write("a.md", 'One "x." two "y."')
        b = rt.write("b.md", 'One "x." two "y."')
        out = rt.lint(a, "--quick")
        out2 = rt.lint(b, "--quick")
        check("A/the threshold is per file, not per run",
              "RED FLAGS (2)" in out.stdout and "RED FLAGS (2)" in out2.stdout,
              out.stdout[:120])
    finally:
        rt.close()


# ---------------------------------------------------------------------------
# B. QUICK-LINT SCOPE —— the widening, and the three carve-outs
# ---------------------------------------------------------------------------
def test_scope():
    rt = Repo()
    try:
        clean = "# Doc\n\n" + FILLER
        dirty = "# Doc\n\nThe colors are wrong and the center is off.\n" + FILLER

        # THE WIDENING: a plain `.md` that no old filename rule would match.
        p = rt.write("temp/temp_misc/notes/random_thoughts.md", dirty)
        r = rt.post("W1", p)
        check("B/a non-comms .md now BLOCKS on RED", r.returncode == 2,
              "rc=%s" % r.returncode)
        check("B/and the block names the escape for captured text",
              "dlint: skip" in r.stderr, r.stderr[:200])

        p = rt.write("temp/temp_misc/notes/clean_thoughts.md", clean)
        r = rt.post("W1", p)
        check("B/a clean non-comms .md does not block", r.returncode == 0,
              r.stderr[:200])

        # Unchanged behaviour for the roles that were always in scope.
        c = rt.write("sessions/2026/202608/response_202608012100.md", dirty)
        r = rt.post("W2", c)
        check("B/a comms file still blocks on RED (unchanged)",
              r.returncode == 2, r.returncode)

        # CARVE-OUT 1 —— `query_` carries the USER's words.
        q = rt.write("sessions/2026/202608/query_202608012100.md", dirty)
        r = rt.post("W3", q)
        check("B/CARVE-OUT 1: a query_ is skipped entirely",
              r.returncode == 0 and not r.stdout.strip(), r.stdout[:120])
        q = rt.write("sessions/2026/202608/career_query_202608012100.md", dirty)
        r = rt.post("W3", q)
        check("B/CARVE-OUT 1 covers a CP-prefixed query_", r.returncode == 0,
              r.returncode)

        # CARVE-OUT 2 —— the verdict is scoped to the text this write produced.
        big = rt.write("temp/temp_misc/lectures/transcript.md", dirty)
        r = rt.post("W4", big, tool="Edit",
                    ti_extra={"old_string": "Nothing",
                              "new_string": "An ordinary British sentence."})
        check("B/CARVE-OUT 2: an Edit is judged on its OWN new text",
              r.returncode == 0,
              "a pre-existing RED elsewhere in the file must not block")
        r = rt.post("W4", big, tool="Edit",
                    ti_extra={"old_string": "x",
                              "new_string": "The colors are still wrong."})
        check("B/CARVE-OUT 2 still blocks when the NEW text is the breach",
              r.returncode == 2, r.returncode)
        r = rt.post("W4", big, tool="MultiEdit", ti_extra={"edits": [
            {"old_string": "a", "new_string": "Fine prose."},
            {"old_string": "b", "new_string": "The center is off."}]})
        check("B/CARVE-OUT 2 reads every MultiEdit new_string",
              r.returncode == 2, r.returncode)
        r = rt.post("W4", big, tool="Write", ti_extra={"content": dirty})
        check("B/CARVE-OUT 2 gives no cover to a Write (all of it is new)",
              r.returncode == 2, r.returncode)

        # CARVE-OUT 2 MUST NOT REACH COMMS —— the whole file, every time.
        c2 = rt.write("sessions/2026/202608/close_202608012100.md", dirty)
        r = rt.post("W5", c2, tool="Edit",
                    ti_extra={"old_string": "Nothing",
                              "new_string": "An ordinary British sentence."})
        check("B/CARVE-OUT 2 does NOT apply to a comms file",
              r.returncode == 2,
              "a comms file is CC's own work end to end; no write-scoping")

        # CARVE-OUT 3 —— the permanent per-file dismissal.
        m = rt.write("temp/temp_misc/lectures/lecture_w1.md",
                     "<!-- dlint: skip -->\n" + dirty)
        r = rt.post("W6", m, tool="Write", ti_extra={"content": dirty})
        check("B/CARVE-OUT 3: a marked file is skipped outright",
              r.returncode == 0 and not r.stdout.strip(), r.stdout[:120])
        m2 = rt.write("sessions/2026/202608/wrap_202608012100.md",
                      "<!-- dlint: skip -->\n" + dirty)
        r = rt.post("W6", m2)
        check("B/CARVE-OUT 3 does NOT work on a comms file", r.returncode == 2,
              "a marker must never buy a comms file out of the lint")

        # Extension and containment.
        code = rt.write("cscpt/thing.py", "x = 'colors'\n")
        r = rt.post("W7", code)
        check("B/a .py write is never linted", r.returncode == 0)
        outside = os.path.join(tempfile.gettempdir(),
                               "dlint_outside_probe_response_.md")
        with open(outside, "w", encoding="utf-8") as fh:
            fh.write(dirty)
        r = rt.post("W7", outside)
        check("B/a target outside the repo is never linted",
              r.returncode == 0 and not r.stdout.strip(),
              "a lint that BLOCKS must not roam (hook_guide §4.7)")
        os.remove(outside)

        # The dlint liveness probe (hook_guide §7.2) must still be in scope and
        # must still block —— it is the only evidence the wiring is alive.
        probe = rt.write("cp/ccsim/sandbox/hook_probe_response_.md",
                         "The colors, the center, the theater.\n")
        r = rt.post("W8", probe)
        check("B/the live probe still blocks (hook_guide §7.2)",
              r.returncode == 2, r.returncode)
    finally:
        rt.close()


# ---------------------------------------------------------------------------
# C. THE REMINDER
# ---------------------------------------------------------------------------
def test_reminder():
    rt = Repo()
    try:
        p = rt.write("temp/temp_misc/notes/plain.md", "# Doc\n\n" + FILLER)
        r = rt.post("R1", p)
        check("C/a clean run emits a model-visible reminder", advises(r),
              r.stdout[:200])
        check("C/the reminder asks whether FULL dlint is warranted",
              "FULL `dlint.py`" in ctx(r), ctx(r)[:200])
        check("C/and names the EXTRACT case explicitly",
              "EXTRACT" in ctx(r), ctx(r)[:200])
        check("C/the reminder never blocks", r.returncode == 0)

        r = rt.post("R1", p)
        check("C/it is silent on a redraft in the same session",
              not advises(r) and r.returncode == 0, r.stdout[:160])
        r = rt.post("R2", p)
        check("C/a NEW session gets its own single reminder", advises(r))

        d = rt.write(DELIV, "# One-pager\n\n" + FILLER)
        r = rt.post("R3", d)
        check("C/a deliverable-shaped file gets the STRONGER reminder",
              "DELIVERABLE" in ctx(r) and "3.7.3" in ctx(r), ctx(r)[:200])
        scratch = rt.write("temp/temp_misc/20260801_x/build/notes.md",
                           "# Doc\n\n" + FILLER)
        r = rt.post("R3", scratch)
        check("C/an internal file is reminded WITHOUT the deliverable claim",
              advises(r) and "DELIVERABLE" not in ctx(r), ctx(r)[:160])
    finally:
        rt.close()


# ---------------------------------------------------------------------------
# D. THE CLASSIFIER (the gate's only question)
# ---------------------------------------------------------------------------
def test_classifier():
    rt = Repo()
    m = rt.mod()
    try:
        body = "# Title\n\n" + FILLER

        # Guard the guard: if the module ever anchors on the real repo again,
        # every exclusion below would pass as `outside_repo` and this suite
        # would go quietly green whilst testing nothing.
        canary = rt.write("temp/temp_misc/canary/output/CANARY_Doc.md", body)
        _ok, reason = m.classify(canary)
        check("D/HARNESS canary: the synthetic repo is the anchor",
              reason != "outside_repo",
              "module anchored on the real repo; all exclusions are vacuous")

        cases_out = [
            ("universal/newpcmd.md", "protocol tree"),
            ("cscpt/notes.md", "tooling tree"),
            ("gscpt/notes.md", "tooling tree"),
            ("nscpt/notes.md", "tooling tree"),
            ("backup/thing.md", "backup mirror"),
            (".claude/thing.md", "config tree"),
            ("cp/career/anything.md", "CP protocol territory"),
            ("cp/ccsim/sandbox/scratch.md", "sandbox sits under cp/"),
            ("temp/temp_archive/old.md", "archive, never touch"),
            ("sessions/queued_queries/thing.md", "queued query"),
            ("temp/t/20260801_x/input/brief.md", "provided material"),
            ("temp/t/20260801_x/resource/research.md", "retrieved material"),
            ("temp/t/20260801_x/build/scratch.md", "scratch"),
            ("TOPLEVEL.md", "repo-root furniture"),
            ("temp/t/20260801_x/output/README.md", "README"),
            ("temp/t/20260801_x/output/CLAUDE.md", "CLAUDE.md"),
            ("temp/t/20260801_x/output/placeholder.md", "protocol basename"),
            ("temp/t/20260801_x/output/temp_draft.md", "temp_ prefix §8.3.2"),
            ("temp/t/20260801_x/output/my_user_notes.md", "private §8.3.1"),
            ("temp/t/20260801_x/output/brief_otg.md", "OTG variant §8.3.3"),
            ("temp/t/20260801_x/output/❌_dead.md", "voided §8.2"),
            ("temp/t/20260801_x/output/response_202608010101.md", "comms"),
            ("temp/t/20260801_x/output/career_close_202608010101.md", "comms"),
            ("temp/t/20260801_x/output/debate_board_202608010101.md",
             "machinery role + TS"),
            ("sessions/2026/202606/dissertation_A1Rv2_debate_s_202606221648.md",
             "role at depth, TS-anchored"),
            ("sessions/2026/202607/ccsim_migration_revertlog_202607241459.md",
             "role at depth, TS-anchored"),
            ("sessions/2026/202606/career_handoff_202606252017.md",
             "machinery role + TS"),
            ("temp/t/20260801_x/output/thing.py", "not prose"),
            ("temp/t/20260801_x/output/thing.html", "not lintable prose"),
        ]
        for rel, why in cases_out:
            p = rt.write(rel, body)
            ok, reason = m.classify(p)
            check("D/excluded %s (%s)" % (rel, why), not ok,
                  "classified as deliverable, reason=%s" % reason)

        cases_in = [
            "temp/temp_misc/20260801_x/output/CHEATSHEET_Thing.md",
            "temp/temp_misc/20260801_x/output/SPEECH_Thing.md",
            "temp/temp_misc/20260801_x/output/mini_SPEECH_Thing.md",
            "temp/temp_misc/20260801_x/output/Client_Report_Name_Surname.md",
            "temp/temp_misc/20260801_x/output/notes.txt",
            # No allow-list would hold these; the deny-list does, which is the
            # whole argument for inverting the rule.
            "deliverables/anything_at_all.md",
            "client_x/2026/handover_pack.md",
            "sessions/2026/202608/onepager_for_client.md",
            # A role WORD in an ordinary deliverable name, with no timestamp
            # suffix, must NOT read as a comms file. Letting the comms regex
            # skip two prefix segments made exactly this a false negative,
            # which is the failure the gate exists to stop.
            "temp/temp_misc/20260801_x/output/Client_Project_Response_Plan.md",
            "temp/temp_misc/20260801_x/output/Acme_Board_Briefing_Pack.md",
            # Hand-named deliverable that DOES carry a timestamp (root §3.3.7)
            # but no role word —— the timestamp alone must not exclude it.
            "temp/temp_misc/20260801_x/output/Acme_Onboarding_202607021219.md",
        ]
        for rel in cases_in:
            p = rt.write(rel, body)
            ok, reason = m.classify(p)
            check("D/included %s" % rel, ok,
                  "not classified, reason=%s" % reason)

        thin = rt.write("temp/temp_misc/20260801_x/output/stub.md", "# T\n")
        ok, reason = m.classify(thin)
        check("D/the substance floor drops a stub",
              not ok and reason == "thin", reason)

        outside = os.path.join(tempfile.gettempdir(), "dlint_outside_cls.md")
        with open(outside, "w", encoding="utf-8") as fh:
            fh.write(body)
        ok, reason = m.classify(outside)
        check("D/outside the repo is never classified",
              not ok and reason == "outside_repo", reason)
        os.remove(outside)

        # ---- OVERRIDES ----
        p = rt.write("temp/temp_misc/20260801_x/output/transcript.md",
                     "# T\n\n<!-- dlint: internal -->\n\n" + FILLER)
        ok, reason = m.classify(p)
        check("D/opt-out beats a deliverable verdict",
              not ok and reason == "marked_internal", reason)

        p = rt.write("temp/temp_misc/20260801_x/output/skip.md",
                     "# X\n\n# dlint: skip\n\n" + FILLER)
        ok, _ = m.classify(p)
        check("D/opt-out works in any comment syntax", not ok)

        p = rt.write("cp/career/culous_yu_resume_full.md",
                     "# CV\n\n<!-- dlint: deliverable -->\n\n" + FILLER)
        ok, reason = m.classify(p)
        check("D/opt-in beats protocol territory",
              ok and reason == "marked_deliverable", reason)

        p = rt.write("temp/temp_misc/20260801_x/output/both.md",
                     "<!-- dlint: internal -->\n<!-- dlint: deliverable -->\n"
                     + FILLER)
        ok, _ = m.classify(p)
        check("D/opt-out wins when both markers are present", not ok,
              "the safe direction: never rewrite a file marked internal")
    finally:
        rt.close()


# ---------------------------------------------------------------------------
# E. THE GATE + F. RECEIPTS
# ---------------------------------------------------------------------------
def test_gate():
    rt = Repo()
    try:
        d = rt.write(DELIV, "# One-pager\n\n" + FILLER)
        resp = rt.write("sessions/2026/202608/response_202608012100.md",
                        "# Response\n")

        r = rt.post("S_none", resp)
        check("E/nothing owed means no block", r.returncode == 0, r.returncode)

        rt.post("S1", d)
        r = rt.post("S1", resp)
        check("E/the gate BLOCKS the comms write", r.returncode == 2,
              "rc=%s out=%s err=%s" % (r.returncode, r.stdout[:120],
                                       r.stderr[:120]))
        check("E/it writes to stderr (exit 2 discards stdout)",
              "ONEPAGER_Client.md" in r.stderr, r.stderr[:200])
        check("E/it names the FULL dlint command",
              "cscpt/dlint.py" in r.stderr, r.stderr[:200])

        r = rt.post("S1", resp)
        check("E/the loop guard degrades the SECOND block to an advisory",
              r.returncode == 0 and advises(r), "rc=%s" % r.returncode)

        q = rt.write("sessions/2026/202608/query_202608012100.md", "# Q\n")
        rt.post("S2", d)
        r = rt.post("S2", q)
        check("E/a query_ write is never a delivery", r.returncode == 0,
              r.returncode)

        for role in ("close_202608012100.md", "wrap_202608012100.md",
                     "career_response_202608012100.md",
                     "artefact_202608012100.md"):
            p = rt.write("sessions/2026/202608/" + role, "# X\n")
            rt.post("S_" + role, d)
            r = rt.post("S_" + role, p)
            check("E/%s is a delivery and blocks" % role, r.returncode == 2,
                  r.returncode)

        # The dlint live probe is named `hook_probe_response_.md`. A looser
        # delivery prefix would read it as a comms file and make the gate fire
        # during an unrelated probe run, so pin that it does not.
        probe = rt.write("cp/ccsim/sandbox/hook_probe_response_.md", "# P\n")
        rt.post("S_probe", d)
        r = rt.post("S_probe", probe)
        check("E/the dlint probe file is NOT read as a delivery",
              r.returncode == 0, r.returncode)

        # A deliverable that fails the QUICK lint must still be RECORDED, or
        # walking away from that block would leave it un-gated at delivery.
        bad = rt.write("temp/temp_misc/20260801_x/output/BAD_Doc.md",
                       "# Doc\n\nThe colors are wrong.\n" + FILLER)
        r = rt.post("S_rec", bad)
        check("E/a RED deliverable blocks at its own write", r.returncode == 2,
              r.returncode)
        r = rt.post("S_rec", resp)
        check("E/and is still owed at delivery despite that block",
              r.returncode == 2,
              "recording must happen BEFORE the quick-lint verdict")

        # --- RECEIPTS ---
        n_before = len(rt.receipts())
        rt.lint(d, "--quick")
        check("F/--quick writes NO receipt", len(rt.receipts()) == n_before,
              "quick mode must never vouch for a file")
        subprocess.run([sys.executable, rt.dlint, "--text", "hello there"],
                       capture_output=True, text=True, timeout=60)
        check("F/--text writes NO receipt", len(rt.receipts()) == n_before)

        rt.write(DELIV, "# One-pager\n\nThe colors are wrong. " + FILLER)
        rt.lint(d)
        recs = [x for x in rt.receipts() if x.get("p") == os.path.realpath(d)]
        check("F/FULL mode writes a receipt", len(recs) == 1, recs)
        check("F/a FAILED lint records its RED count",
              recs and recs[-1].get("r", 0) > 0, recs[-1] if recs else None)

        rt.post("S5", d)
        r = rt.post("S5", resp)
        check("F/a failed lint still blocks delivery", r.returncode == 2,
              r.returncode)

        rt.write(DELIV, "# One-pager\n\nThe colours are right. " + FILLER)
        out = rt.lint(d)
        check("F/the corrected file lints clean", "RED=0" in out.stdout,
              out.stdout[-200:])
        rt.post("S6", d)
        r = rt.post("S6", resp)
        check("F/a CLEAN receipt clears the gate", r.returncode == 0,
              "rc=%s err=%s" % (r.returncode, r.stderr[:200]))

        with open(d, "a", encoding="utf-8") as fh:
            fh.write("\nAn extra line the clean receipt cannot vouch for.\n")
        rt.post("S7", d)
        r = rt.post("S7", resp)
        check("F/an edit after a clean lint lapses the receipt",
              r.returncode == 2,
              "content-addressed receipts must not survive an edit")

        # THE CAP. A long session must not grow state without bound, but the
        # cheap way to bound it —— refuse every new marker —— would silently
        # un-gate a deliverable written late in the turn. Reminders yield;
        # the gate does not.
        m = rt.mod()
        sdir = m._session_dir("CAP")
        os.makedirs(sdir, exist_ok=True)
        for i in range(m._MAX_PENDING_PER_SESSION):
            with open(os.path.join(sdir, "pad%04d.json" % i), "w",
                      encoding="utf-8") as fh:
                json.dump({"p": "/nowhere/%d.md" % i}, fh)
        late = rt.write("temp/temp_misc/late/output/LATE_Doc.md",
                        "# Late\n\n" + FILLER)
        check("F/past the cap a REMINDER marker is refused",
              m.marker_put("CAP", late, "h", reminded=1) is None,
              "unbounded state is the worse failure")
        check("F/but a GATE marker is still recorded",
              (m.marker_put("CAP", late, "h", owed=1) or {}).get("owed") == 1,
              "dropping one would silently un-gate a real deliverable")

        acts = set(x.split("\t")[1] for x in rt.log() if "\t" in x)
        check("F/every invocation is logged (never-fired stays detectable)",
              any(a.startswith("gate:") for a in acts)
              and any(a.startswith("red:") for a in acts)
              and any(a.startswith("clean:") for a in acts), sorted(acts))
    finally:
        rt.close()


# ---------------------------------------------------------------------------
# G/H/I. SCOPE GUARD, FAIL-SAFES, SHIM
# ---------------------------------------------------------------------------
def test_guards():
    rt = Repo()
    try:
        d = rt.write(DELIV, "# One-pager\n\n" + FILLER)

        body = json.dumps({
            "session_id": "OUT", "hook_event_name": "PostToolUse",
            "cwd": "/Users/nobody/some-other-project",
            "tool_name": "Write", "tool_input": {"file_path": d}})
        r = rt.run(body)
        check("G/out-of-scope cwd is silent",
              r.returncode == 0 and not r.stdout.strip(), r.stdout[:120])

        body = json.dumps({
            "session_id": "SIB", "hook_event_name": "PostToolUse",
            "cwd": rt.root + "-sibling",
            "tool_name": "Write", "tool_input": {"file_path": d}})
        r = rt.run(body)
        check("G/a `-sibling` path is not a sub-path (separator-bounded)",
              r.returncode == 0 and not r.stdout.strip(), r.stdout[:120])

        body = json.dumps({
            "session_id": "FO", "hook_event_name": "PostToolUse",
            "tool_name": "Write", "tool_input": {"file_path": d}})
        r = rt.run(body)
        check("G/FAILS OPEN when scope is undeterminable", advises(r),
              "an unreadable shape is not evidence of another project")

        for label, raw in (
                ("malformed stdin", "{not json"),
                ("empty stdin", ""),
                ("a JSON array", "[]"),
                ("no tool_input", json.dumps(
                    {"session_id": "X", "cwd": rt.root})),
                ("no session_id", json.dumps(
                    {"cwd": rt.root, "tool_name": "Write",
                     "tool_input": {"file_path": d}})),
                ("a missing target", json.dumps(
                    {"session_id": "X", "cwd": rt.root, "tool_name": "Write",
                     "tool_input": {"file_path": d + ".nope"}}))):
            r = rt.run("", raw=raw)
            check("H/fail-safe exit 0 on %s" % label, r.returncode == 0,
                  "rc=%s err=%s" % (r.returncode, r.stderr[:120]))

        # A RELATIVE file_path must resolve against the PAYLOAD's cwd, not the
        # hook process's own —— the harness launches hooks from anywhere, and
        # resolving against the wrong tree makes every verdict meaningless.
        # Run from `/` so a cwd-relative resolution cannot land on the file.
        r = subprocess.run(
            [sys.executable, rt.quick],
            input=json.dumps({"session_id": "REL", "cwd": rt.root,
                              "hook_event_name": "PostToolUse",
                              "tool_name": "Write",
                              "tool_input": {"file_path": DELIV}}),
            capture_output=True, text=True, timeout=60, cwd="/")
        check("H/a relative file_path resolves against the payload cwd",
              advises(r), r.stdout[:160])

        # Parallel writes in one turn must not lose the ledger or crash: the
        # pending state is a directory of independent markers precisely so
        # there is no read-modify-write race (coding.md § Concurrency).
        procs = [subprocess.Popen(
            [sys.executable, rt.quick], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for _ in range(6)]
        for pr in procs:
            pr.communicate(rt.payload("PAR", d), timeout=60)
        rcs = [pr.returncode for pr in procs]
        check("H/six concurrent writes all exit 0", set(rcs) == {0}, rcs)
        r = rt.post("PAR", rt.write("sessions/2026/202608/response_p.md",
                                    "# R\n"))
        check("H/and the pending ledger survived the race",
              r.returncode == 2, r.returncode)

        # --- THE SHIM ---
        rt2 = Repo()
        try:
            d2 = rt2.write(DELIV, "# One-pager\n\n" + FILLER)
            code = rt2.write("cscpt/thing.py", "print(1)\n")
            r = rt2.post("SH", code, via_shim=True)
            check("I/the shim skips a payload with no prose extension",
                  r.returncode == 0 and not r.stdout.strip(), r.stdout[:120])
            r = rt2.post("SH", d2, via_shim=True)
            check("I/the shim forwards a .md payload and returns the reminder",
                  advises(r), r.stdout[:160])
            resp2 = rt2.write("sessions/2026/202608/response_1.md", "# R\n")
            r = rt2.post("SH", resp2, via_shim=True)
            check("I/the shim passes exit 2 through unchanged",
                  r.returncode == 2, r.returncode)
        finally:
            rt2.close()
    finally:
        rt.close()


# ---------------------------------------------------------------------------
# J. THE REPLAY —— the real case, end to end
# ---------------------------------------------------------------------------
def test_replay():
    if not os.path.isfile(FIXTURE):
        FAIL.append("J/fixture missing: %s" % FIXTURE)
        return
    with open(FIXTURE, "r", encoding="utf-8") as fh:
        text = fh.read()

    rt = Repo()
    try:
        rel = "temp/temp_int/20260625_Alltech/output/CHEATSHEET_Stage3.md"
        p = rt.write(rel, text)

        ok, reason = rt.mod().classify(p)
        check("J/the real cheat sheet classifies as a deliverable", ok, reason)

        r = rt.post("REPLAY", p, tool="Write", ti_extra={"content": text})
        check("J/it would now be BLOCKED at its own write", r.returncode == 2,
              "rc=%s" % r.returncode)

        resp = rt.write("sessions/2026/202607/career_response_202607310730.md",
                        "# Response\n")
        r = rt.post("REPLAY", resp)
        check("J/and the delivering comms write is BLOCKED too",
              r.returncode == 2, "rc=%s" % r.returncode)
        check("J/the block names the cheat sheet",
              "CHEATSHEET_Stage3.md" in r.stderr, r.stderr[:200])

        out = rt.lint(p)
        m_red = re.search(r"RED FLAGS \((\d+)\)", out.stdout)
        m_yel = re.search(r"YELLOW FLAGS \((\d+)\)", out.stdout)
        n_red = int(m_red.group(1)) if m_red else -1
        n_yel = int(m_yel.group(1)) if m_yel else -1
        # 18 RED / 22 YELLOW before Hart's rule was hardened. The fixture holds
        # 2 periods inside closing quotes, which moved from YELLOW to RED, so
        # the split is now 20/20 whilst the TOTAL is unchanged —— pinning both
        # halves and the total is what catches a rule change that quietly loses
        # a flag instead of reclassifying it.
        check("J/FULL dlint finds 20 RED on this text (18 + 2 re-tiered)",
              n_red == 20, n_red)
        check("J/and 20 YELLOW (22 - 2)", n_yel == 20, n_yel)
        check("J/the historical total of 40 flags is unchanged",
              n_red + n_yel == 40, "%s + %s" % (n_red, n_yel))

        recs = [x for x in rt.receipts() if x.get("p") == os.path.realpath(p)]
        check("J/the failed lint leaves a receipt recording RED>0",
              recs and recs[-1].get("r") == n_red,
              recs[-1] if recs else None)

        rt.post("REPLAY2", p)
        r = rt.post("REPLAY2", resp)
        check("J/a FAILED lint does not unlock delivery", r.returncode == 2,
              "20 RED must not read as linted")
    finally:
        rt.close()


# ---------------------------------------------------------------------------
# K. THE FOLD —— elint is gone, and nothing may quietly resurrect it
# ---------------------------------------------------------------------------
def test_fold():
    """The gate used to be `cscpt/elint.py` on TWO registrations with THREE
    tiers. Folding it into `dlint_quick.py` is only real if the old wiring is
    actually gone —— a stale registration or a live script left beside the new
    one is exactly the half-done change hook_guide §8 describes.

    Per the standing rule, this asserts only that no LIVE copy exists. It never
    asserts the voided `❌_` file is present: a voided file is awaiting the
    user's manual delete, so its absence is the expected end state, and a test
    demanding it would fail the moment he does what the Void Rule asks."""
    for gone in ("elint.py", "elint_hook.sh"):
        check("K/no live cscpt/%s remains" % gone,
              not os.path.isfile(os.path.join(CSCPT, gone)),
              "the fold is not done whilst the old script is still runnable")
    check("K/the Tier A probe file is gone with its tier",
          not os.path.isfile(os.path.join(HERE, "elint_probe_deliverable.md")),
          "a dead probe is worse than none —— it reads as live coverage")

    ref = os.path.join(REPO, ".claude", "hooks_user_settings.reference.json")
    if os.path.isfile(ref):
        with open(ref, "r", encoding="utf-8") as fh:
            body = fh.read()
        check("K/the restore-of-record no longer registers elint",
              "elint" not in body,
              "a stale reference silently restores dead wiring "
              "(hook_guide §9.4)")
    else:
        FAIL.append("K/restore-of-record missing: %s" % ref)

    live = os.path.expanduser("~/.claude/settings.json")
    if os.path.isfile(live):
        with open(live, "r", encoding="utf-8") as fh:
            body = fh.read()
        check("K/the LIVE registrations no longer name elint",
              "elint" not in body,
              "hooks fire from ~/.claude/settings.json, not the repo")
        try:
            hooks = json.loads(body).get("hooks", {})
            cmds = [h.get("command", "") for grp in hooks.values()
                    for g in grp for h in (g.get("hooks") or [g])]
            check("K/dlint_hook.sh is still registered",
                  any("dlint_hook.sh" in c for c in cmds), cmds)
        except Exception as exc:                                # noqa: BLE001
            FAIL.append("K/live settings unparseable: %r" % exc)
    else:
        FAIL.append("K/live settings missing: %s" % live)



def _dlint():
    sys.path.insert(0, CSCPT)
    try:
        import dlint
        return dlint
    finally:
        sys.path.remove(CSCPT)


def _rt(dlint, text):
    """The `read`/`#r` advisory messages produced by QUICK mode on `text`."""
    _r, y = dlint.run_checks(text, quick=True)
    return [m for _, m in y if 'bare "read"' in m]


def test_read_tense_quick_only():
    """REGRESSION —— the `#r` tense advisory must fire in QUICK and NEVER in FULL.

    `glossary.md` reserves `#r` for the past tense of "read". The advisory is
    house shorthand, so pushing it into FULL mode would nudge deliverables ——
    sent to third parties who have never seen this glossary —— towards an
    abbreviation they cannot parse. The quick/full split IS the rule, not an
    implementation detail, so it is pinned in both directions."""
    dlint = _dlint()
    sample = "Having already read A, I also read B and will read C."
    qhits = _rt(dlint, sample)
    _fr, fy = dlint.run_checks(sample, quick=False)
    fhits = [m for _, m in fy if 'bare "read"' in m]

    check("M/quick mode raises the advisory", len(qhits) == 1, len(qhits))
    check("M/FULL mode never raises it", not fhits, fhits[:1])
    check("M/the advisory names glossary.md",
          qhits and "glossary.md" in qhits[0], qhits[:1])
    check("M/and tells CC to fix silently",
          qhits and "Silently" in qhits[0], qhits[:1])
    check("M/a context window is quoted for locating the instance",
          qhits and 'first is "' in qhits[0], qhits[:1])
    check("M/`will read` is excluded, so only 2 candidates survive",
          qhits and qhits[0].startswith("2 bare"), qhits[:1])
    check("M/silent when the word is absent",
          not _rt(dlint, "Nothing here mentions it at all."))


def test_read_tense_noise():
    """REGRESSION —— the advisory must not fire on correct writing.

    THE FAILING SCENARIO, measured rather than asserted: `\\b[Rr]ead\\b` over one
    real `response_` produced 21 flags, of which one was an actual past tense.
    The owner's expectation is that a correctly-written file fires ZERO times.
    That is not reachable by tense detection —— "you read it" is past or present
    and only a reader can say —— so what IS pinned here is the four mechanical
    classes that were never tense errors at all, plus the one-flag-per-file
    reporting that stops a genuine ambiguity being served twenty times over.

    The residual is pinned too, deliberately: a bare "You read X" STILL fires,
    and a test asserting otherwise would be encoding a promise the check cannot
    keep."""
    dlint = _dlint()

    silent = [
        ("re-read the file", "class 1: hyphenated compound"),
        ("read-only mode", "class 1: hyphenated compound"),
        ("another read-reminder fired", "class 1: hyphenated compound"),
        ("she over-read the situation", "class 1: hyphenated compound"),
        ("a must-read guide", "class 1: hyphenated compound"),
        ("edit it with the Read tool", "class 2: the tool name"),
        ("Read/Write payloads", "class 2: the tool name"),
        ("the miss was not a missing read.", "class 3: a noun"),
        ("this does not discharge the read", "class 3: a noun"),
        ("a read via Bash is invisible", "class 3: a noun"),
        ("you had to read past it", "class 4: infinitive"),
        ("it will read as questions", "class 4: future"),
        ("the file is only read when editing", "class 4: present passive"),
        ("the file is not yet read", "class 4: present passive"),
        ("CC must read it first", "class 4: modal"),
        ("reading the file", "never matched: not the whole word"),
        ("`#r` and #r are shorthand", "never matched: not the word"),
    ]
    for text, why in silent:
        check("N/silent on %r (%s)" % (text, why), not _rt(dlint, text),
              _rt(dlint, text)[:1])

    fires = [
        "You read the originals, then discovered they had moved.",
        "The files were already read this session.",
    ]
    for text in fires:
        check("N/still fires on %r" % text, _rt(dlint, text), "a real past "
              "tense must survive the narrowing —— hiding it is worse than "
              "the noise")

    # ONE FLAG PER FILE. Twenty repetitions of one reminder is the noise; the
    # line numbers carry the same information at a twentieth of the volume.
    many = "\n".join("You read item %d there." % i for i in range(20))
    hits = _rt(dlint, many)
    check("N/twenty candidates produce ONE flag", len(hits) == 1, len(hits))
    check("N/and that flag reports the count", hits and "20 bare" in hits[0],
          hits[:1])
    check("N/and names line numbers to jump to",
          hits and "L1, L2" in hits[0], hits[:1])

    # `--rt-quiet` suppresses THIS advisory and nothing else. `dlint_quick.py`
    # passes it once a (session, file) has already been shown the report.
    red, yellow = dlint.run_checks("You read it. The colors are wrong.",
                                   quick=True, rt_quiet=True)
    check("N/--rt-quiet silences the advisory",
          not [m for _, m in yellow if 'bare "read"' in m], yellow[:1])
    check("N/but never silences a RED", len(red) == 1, red)


def test_americanisms():
    """REGRESSION —— the `-our`/`-or` class, and the words that only LOOK like it.

    THE FAILING SCENARIO: a `response_` shipped the word `rigor` after a clean
    `--quick` run. The check itself was sound (RED, quick-mode, word-boundary,
    code-masked); `rigor` was simply not in the list, and neither was the whole
    `-our` class around it.

    The other half of the fix matters just as much and is pinned harder: an
    ending-based rule would have caught `rigor` and ALSO fired on `tremor`,
    `error`, `senator`, `separator`, `junior` and `rigorous` —— ordinary correct
    English —— and a RED that cries wolf gets switched off. Every one of those
    is asserted SILENT below, so nobody can "simplify" the word list into a
    pattern without this suite going red."""
    dlint = _dlint()

    def red_words(text):
        red, _y = dlint.run_checks(text, quick=True)
        return [m.split("`")[1] for _ln, m in red if m.startswith("Americanism")]

    check("L/`rigor` is RED (the exact miss that motivated this)",
          red_words("This deserves the same rigor.") == ["rigor"],
          red_words("This deserves the same rigor."))

    for w in ("ardor", "armor", "candor", "clamor", "demeanor", "endeavor",
              "fervor", "glamor", "harbor", "humor", "odor", "rancor", "rigor",
              "rumor", "savior", "savor", "splendor", "succor", "tumor",
              "valor", "vapor", "vigor", "misdemeanor", "behavioral",
              "neighborhood", "favorable", "honorable", "humorless",
              "colorful", "laborer"):
        check("L/`%s` is RED" % w, red_words("A sentence with %s in it." % w),
              "the -our class must be covered, not just the seed words")

    # THE MISFIRE CLASS. Correct English that an `-or` pattern would destroy.
    for w in ("tremor", "error", "mirror", "horror", "terror", "major",
              "minor", "donor", "motor", "doctor", "senator", "metaphor",
              "anchor", "pallor", "junior", "senior", "superior", "separator",
              "elevator", "translator", "animator", "devour", "contour",
              "flour", "hour", "paramour", "tour", "velour"):
        check("L/`%s` is NOT flagged" % w,
              not red_words("A sentence with %s in it." % w),
              "%s is correct in British English; an ending rule would fire"
              % w)

    # BRITISH DERIVATIVES LEGITIMATELY DROP THE `u`, and word-boundary matching
    # is what spares them —— `\\brigor\\b` cannot reach inside `rigorous`.
    for w in ("rigorous", "vigorous", "humorous", "laborious", "honorary",
              "honorific", "humorist", "glamorous", "invigorate",
              "thermometer", "kilometre", "colouration"):
        check("L/`%s` is NOT flagged" % w,
              not red_words("A sentence with %s in it." % w),
              "British drops the u before these Latin suffixes")

    # THE CONTEXT EXEMPTIONS, each a place the listed spelling is correct.
    for text, w in (("rigor mortis had set in", "rigor"),
                    ("the Australian Labor Party won", "labor"),
                    ("a Labor MP said so", "labor"),
                    ("Pearl Harbor was bombed", "harbor"),
                    ("a parking meter costs money", "meter"),
                    ("the meter reading was wrong", "meter")):
        check("L/%r does not fire" % text, not red_words(text),
              "a source-named correct usage must not be a hard block")
    # …and the exemption is offset-precise: the same word elsewhere still fires.
    check("L/the exemption does not cover the whole line",
          red_words("rigor mortis, and the rigor of the argument")
          == ["rigor"],
          red_words("rigor mortis, and the rigor of the argument"))

    # OTHER CLASSES AUDITED IN THE SAME PASS (each Wiktionary-confirmed).
    for w in ("analyze", "specter", "maneuver", "pretense", "traveler",
              "counselor", "modeled", "signaled", "enrollment", "skillful",
              "willful", "installment", "aluminum", "pajamas", "skeptic",
              "mold", "jewelry", "plow", "mustache", "esthetic"):
        check("L/`%s` is RED" % w, red_words("A sentence with %s in it." % w),
              "audited gap outside the -our class")

    # `#distil`/`#distill` are interchangeable TRIGGER names in
    # `universal/shrink.md`, so the American-looking one must not hard-block a
    # house command.
    check("L/`distill` is NOT flagged (it is a house trigger alias)",
          not red_words("Use #distill on that file."), "shrink.md names it")

    # And it still never fires inside code —— the masking predates this change
    # and must survive it.
    red, _y = dlint.run_checks("Use `color` here.\n```\nrigor = 1\n```\n",
                               quick=True)
    check("L/masked code is still exempt",
          not [m for _ln, m in red if m.startswith("Americanism")], red[:1])

    # THE FAST PATH IS THE SAME VERDICT. Growing the list past ~200 words made
    # one-regex-per-word-per-line cost `~`1.5 s on the repo's largest `.md`,
    # over hook_guide §12.4's 1 s ceiling for a hook that fires on every write,
    # so the lookup became a `\\w+` tokenise plus a set intersection. A rewrite
    # for speed is only safe if it is verifiably the SAME rule (coding.md:
    # verify equivalence, never trust the transform), so pin that here rather
    # than trusting the reasoning about `\\b`.
    probe = [
        "color's edge", "colorful", "color2 rows", "re-color it",
        "COLOR and Color and color", "rigor.", "rigorous", "a meter,",
        "thermometer", "kilometer", "(honor)", "honor-bound", "x=color",
        "no americanism at all here",
    ]
    keys = set(dlint.AMERICANISMS)
    for line in probe:
        low = line.lower()
        slow = {w for w in keys if re.search(r"\b%s\b" % re.escape(w), low)}
        fast = set(dlint._WORD_RE.findall(low)) & keys
        check("L/fast lookup equals the word-boundary regex on %r" % line,
              slow == fast, "differ by %s" % (slow ^ fast))


def test_write_scope_is_one_file():
    """REGRESSION —— a write is judged on ITSELF, never on the repo's history.

    The owner's objection, verbatim in intent: the lint should apply to the file
    being created or edited, not to historic ones. This pins that the hook opens
    exactly the file the payload names —— a repo full of RED-laden `.md` cannot
    make a clean write fail, and an Edit to a non-comms file is judged on the
    text it introduced rather than on prose it merely sat next to."""
    rt = Repo()
    try:
        legacy = "# Old\n\nThe colors are wrong, the center is off.\n" + FILLER
        for rel in ("temp/temp_misc/old/a.md", "temp/temp_misc/old/b.md",
                    "sessions/2026/202601/response_202601010101.md"):
            rt.write(rel, legacy)

        clean = rt.write("temp/temp_misc/new/fresh.md", "# New\n\n" + FILLER)
        r = rt.post("HIST", clean, tool="Write",
                    ti_extra={"content": "# New\n\n" + FILLER})
        check("O/a clean write passes with 3 RED files sitting in the repo",
              r.returncode == 0, r.stderr[:200])
        check("O/and no other file is ever named", "a.md" not in r.stderr
              and "b.md" not in r.stderr, r.stderr[:200])

        # Even a comms write, which IS whole-file, only ever sees its own file.
        # A FRESH session id, deliberately: the gate is a separate mechanism and
        # `fresh.md` above is deliverable-shaped, so reusing "HIST" would fail
        # this for a reason that has nothing to do with historic linting.
        resp = rt.write("sessions/2026/202608/response_202608012100.md",
                        "# Response\n\n" + FILLER)
        r = rt.post("HIST_COMMS", resp)
        check("O/a clean comms write is not held to account for older comms",
              r.returncode == 0, r.stderr[:200])

        # The one-line edit to a captured transcript: judged on the line.
        big = rt.write("temp/temp_misc/lectures/transcript.md", legacy)
        r = rt.post("HIST", big, tool="Edit",
                    ti_extra={"old_string": "x",
                              "new_string": "One ordinary British sentence."})
        check("O/an edit is judged on its own new text", r.returncode == 0,
              "history CC did not touch must not block her edit")
    finally:
        rt.close()


def test_read_tense_once_per_session():
    """REGRESSION —— told once is told.

    The whole dlint report reaches CC only on a BLOCK, so a RED loop re-serves
    the same `read`/`#r` advisory on every pass. The owner's second sentence was
    that it must not repeat within a session once CC has been told. Reuses the
    existing (session, file) marker directory rather than a second mechanism."""
    rt = Repo()
    try:
        body = ("# Response\n\nYou read the originals yesterday.\n"
                "The colors are wrong.\n" + FILLER)
        p = rt.write("sessions/2026/202608/response_202608019999.md", body)

        r = rt.post("RT1", p)
        check("P/the first block carries the advisory",
              r.returncode == 2 and 'bare "read"' in r.stderr, r.stderr[:300])

        r = rt.post("RT1", p)
        check("P/the second block in the SAME session does not repeat it",
              r.returncode == 2 and 'bare "read"' not in r.stderr,
              r.stderr[:300])
        check("P/but the RED itself is still reported",
              "Americanism" in r.stderr, r.stderr[:300])

        r = rt.post("RT2", p)
        check("P/a NEW session is told once of its own",
              r.returncode == 2 and 'bare "read"' in r.stderr, r.stderr[:300])
    finally:
        rt.close()


def main():
    for fn in (test_read_tense_quick_only, test_read_tense_noise,
               test_americanisms, test_write_scope_is_one_file,
               test_read_tense_once_per_session,
               test_hart, test_scope, test_reminder, test_classifier,
               test_gate, test_guards, test_replay, test_fold):
        try:
            fn()
        except Exception as exc:                                # noqa: BLE001
            FAIL.append("%s raised %r" % (fn.__name__, exc))
    total = PASS + len(FAIL)
    print("dlint family suite: %d/%d passed" % (PASS, total))
    for f in FAIL:
        print("  FAIL: %s" % f)
    print("\nNOTE: this proves the SCRIPTS. It proves NOTHING about whether "
          "the harness invokes them —— for that, run the live probe in "
          "cp/ccsim/hook_guide.md after registering the hooks.")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
