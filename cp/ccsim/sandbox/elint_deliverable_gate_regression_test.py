#!/usr/bin/env python3
"""Regression test for `cscpt/elint.py` —— the deliverable-escape gate.

WHY THIS EXISTS (coding.md: "a fix without its test is unfinished").
Root CLAUDE.md §3.7.3 requires FULL `dlint.py` on ANY deliverable before it
reaches the user, and until elint that rule had NO mechanical backstop outside
comms files: `dlint_quick.py` fires only on a basename containing
`response_`/`close_`/`wrap_`. A genuine interview cheat sheet was therefore
drafted, debated twice, and delivered un-linted; a retroactive FULL run found
18 RED and 22 YELLOW. That exact pre-lint text is the fixture beside this file
(`elint_fixture_cheatsheet_prelint.md`), so the suite proves the fix against
the case that motivated it rather than a synthetic stand-in.

HOW IT DRIVES THE REAL CODE. `elint.py` derives the repo root from its own
`__file__`, so every check runs inside a SYNTHETIC repo built in a temp dir
whose `cscpt/` holds SYMLINKS to the real `elint.py`, `elint_hook.sh` and
`dlint.py`. Symlinks, not copies: `os.path.abspath(__file__)` does not resolve
them, so the scripts anchor on the synthetic repo whilst the bytes executed are
the LIVE ones —— a copy could drift from the file it claims to pin. Nothing in
the user's real tree is read or written, and no live `.md` is touched.

WHAT IT CANNOT PROVE. Exactly what `cp/ccsim/hook_guide.md` §7.1 warns about:
this drives the scripts with synthesised payloads, which tests the SCRIPT. It
says NOTHING about whether the harness invokes them. That claim needs the live
probe in the hook guide, run after the registration exists in
`~/.claude/settings.json`, and must never be inferred from a green run here.

COVERAGE:
  A. CLASSIFIER —— extension, repo containment, protocol territory, protocol
     names, comms/machinery roles, the substance floor.
  B. OVERRIDES —— `<!-- dlint: internal -->` beats a deliverable verdict and
     `<!-- dlint: deliverable -->` beats territory, in both directions, since
     a one-line permanent dismissal is the whole reason a false positive here
     costs less than plint's did.
  C. TIER A —— advises once per (session, file), never twice, and stays silent
     once a clean receipt covers the current content.
  D. TIER B —— exit 2 on a delivery-named comms write whilst something is
     owed; the loop guard degrades the SECOND block to an advisory; `query_`
     is never a delivery; nothing owed means silence.
  E. TIER C —— Stop warns at exit 0 and NEVER blocks, because a Stop block
     lands after root §3.1.6's turn-end actions.
  F. RECEIPTS —— FULL writes one, `--quick` and `--text` write none, the RED
     count is recorded so a FAILED lint cannot pass as a clean one, and an
     edit after a clean lint correctly lapses the receipt.
  G. SCOPE GUARD —— in scope, out of scope, and FAIL-OPEN on an unreadable
     payload.
  H. FAIL-SAFE —— malformed stdin, missing keys, deleted target, unknown mode.
  I. THE SHIM —— skips a payload with no prose extension, passes exit codes
     through unchanged, and forwards the load-bearing `post` argument.
  J. THE REPLAY —— the real pre-lint cheat sheet is classified as a
     deliverable, advised on, and BLOCKS the comms write that would have
     delivered it.
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
ELINT = os.path.join(CSCPT, "elint.py")
SHIM = os.path.join(CSCPT, "elint_hook.sh")
DLINT = os.path.join(CSCPT, "dlint.py")
FIXTURE = os.path.join(HERE, "elint_fixture_cheatsheet_prelint.md")

PASS = 0
FAIL = []

# Long enough to clear elint's substance floor without being a real document.
FILLER = ("This paragraph exists so the fixture clears the substance floor "
          "that keeps stubs, placeholders and index fragments out of scope. "
          "It is ordinary prose, it says nothing of consequence, and it is "
          "repeated only to reach a plausible length for a short one-pager "
          "that somebody might actually hand over to a third party. ") * 2


def check(name, cond, detail=""):
    global PASS
    if cond:
        PASS += 1
    else:
        FAIL.append("%s%s" % (name, (" —— " + str(detail)) if detail else ""))


class Repo(object):
    """A synthetic repo whose `cscpt/` symlinks the LIVE scripts."""

    def __init__(self):
        self.root = os.path.realpath(tempfile.mkdtemp(prefix="elint_rt_"))
        os.makedirs(os.path.join(self.root, "cscpt"))
        for src in (ELINT, SHIM, DLINT):
            os.symlink(src, os.path.join(self.root, "cscpt",
                                         os.path.basename(src)))
        self.elint = os.path.join(self.root, "cscpt", "elint.py")
        self.shim = os.path.join(self.root, "cscpt", "elint_hook.sh")
        self.dlint = os.path.join(self.root, "cscpt", "dlint.py")
        self._mod = None

    def mod(self):
        """The LIVE elint module, imported through this repo's symlink so its
        `__file__`-derived anchors point HERE rather than at the real repo.

        Load-bearing, not a convenience: a plain `import elint` resolves the
        real `cscpt/`, and every synthetic path then classifies as
        `outside_repo` —— which makes an "is excluded" assertion pass for the
        wrong reason and prove nothing. That is exactly how 26 of this suite's
        checks were vacuous on their first run."""
        if self._mod is None:
            name = "elint_rt_%s" % os.path.basename(self.root)
            spec = importlib.util.spec_from_file_location(name, self.elint)
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

    def payload(self, session, path, event="PostToolUse", tool="Write",
                cwd=True):
        d = {"session_id": session, "hook_event_name": event}
        if cwd:
            d["cwd"] = self.root
        if path is not None:
            d["tool_name"] = tool
            d["tool_input"] = {"file_path": path}
        return json.dumps(d)

    def post(self, session, path, tool="Write", cwd=True, via_shim=False):
        body = self.payload(session, path, "PostToolUse", tool, cwd)
        return self.run(body, shim=via_shim, mode="post")

    def stop(self, session, cwd=True):
        body = self.payload(session, None, "Stop", cwd=cwd)
        return self.run(body, mode="stop")

    def run(self, body, shim=False, mode="post", raw=None):
        cmd = (["bash", self.shim] if shim
               else [sys.executable, self.elint, mode])
        r = subprocess.run(cmd, input=(raw if raw is not None else body),
                           capture_output=True, text=True, timeout=60)
        return r

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
        p = os.path.join(self.root, "cscpt", ".elint.log")
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


DELIV = "temp/temp_misc/20260801_probe/output/ONEPAGER_Client.md"


# ---------------------------------------------------------------------------
# A. CLASSIFIER
# ---------------------------------------------------------------------------
def test_classifier():
    rt = Repo()
    elint = rt.mod()
    try:
        body = "# Title\n\n" + FILLER

        # Guard the guard: if the module ever anchors on the real repo again,
        # every exclusion below would pass as `outside_repo` and this suite
        # would go quietly green whilst testing nothing.
        canary = rt.write("temp/temp_misc/canary/output/CANARY_Doc.md", body)
        ok, reason = elint.classify(canary)
        check("A/HARNESS canary: the synthetic repo is the anchor",
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
            ok, reason = elint.classify(p)
            check("A/excluded %s (%s)" % (rel, why), not ok,
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
            # suffix, must NOT be read as a comms file. Letting the comms
            # regex skip two prefix segments made exactly this a false
            # negative, which is the failure the whole lint exists to stop.
            "temp/temp_misc/20260801_x/output/Client_Project_Response_Plan.md",
            "temp/temp_misc/20260801_x/output/Acme_Board_Briefing_Pack.md",
            # Hand-named deliverable that DOES carry a timestamp (root §3.3.7)
            # but no role word —— the timestamp alone must not exclude it.
            "temp/temp_misc/20260801_x/output/Acme_Onboarding_202607021219.md",
        ]
        for rel in cases_in:
            p = rt.write(rel, body)
            ok, reason = elint.classify(p)
            check("A/included %s" % rel, ok,
                  "not classified, reason=%s" % reason)

        thin = rt.write("temp/temp_misc/20260801_x/output/stub.md", "# Hi\n")
        ok, reason = elint.classify(thin)
        check("A/substance floor drops a stub", not ok and reason == "thin",
              reason)

        outside = os.path.join(tempfile.gettempdir(), "elint_outside_probe.md")
        with open(outside, "w", encoding="utf-8") as fh:
            fh.write(body)
        ok, reason = elint.classify(outside)
        check("A/outside the repo is never classified",
              not ok and reason == "outside_repo", reason)
        os.remove(outside)

        # ---- B. OVERRIDES ----
        p = rt.write("temp/temp_misc/20260801_x/output/transcript.md",
                     "# Transcript\n\n<!-- dlint: internal -->\n\n" + FILLER)
        ok, reason = elint.classify(p)
        check("B/opt-out beats a deliverable verdict",
              not ok and reason == "marked_internal", reason)

        p = rt.write("temp/temp_misc/20260801_x/output/skip.md",
                     "# X\n\n# dlint: skip\n\n" + FILLER)
        ok, _ = elint.classify(p)
        check("B/opt-out works in any comment syntax", not ok)

        p = rt.write("cp/career/culous_yu_resume_full.md",
                     "# CV\n\n<!-- dlint: deliverable -->\n\n" + FILLER)
        ok, reason = elint.classify(p)
        check("B/opt-in beats protocol territory",
              ok and reason == "marked_deliverable", reason)

        p = rt.write("cp/career/CP_notes.md",
                     "# Notes\n\n<!-- dlint: internal -->\n\n" + FILLER)
        ok, _ = elint.classify(p)
        check("B/opt-out and territory agree (no contradiction)", not ok)

        p = rt.write("temp/temp_misc/20260801_x/output/both.md",
                     "<!-- dlint: internal -->\n<!-- dlint: deliverable -->\n"
                     + FILLER)
        ok, _ = elint.classify(p)
        check("B/opt-out wins when both markers are present", not ok,
              "the safe direction: never rewrite a file marked internal")
    finally:
        rt.close()


# ---------------------------------------------------------------------------
# C/D/E. THE TIERS
# ---------------------------------------------------------------------------
def test_tiers():
    rt = Repo()
    try:
        d = rt.write(DELIV, "# One-pager\n\n" + FILLER)
        resp = rt.write("sessions/2026/202608/response_202608012100.md",
                        "# Response\n")

        r = rt.post("S1", d)
        check("C/tier A advises on the deliverable write", advises(r),
              r.stdout[:200])
        check("C/tier A never blocks", r.returncode == 0, r.returncode)
        check("C/advice names the file", "ONEPAGER_Client.md" in r.stdout)
        check("C/advice names the FULL dlint command",
              "cscpt/dlint.py" in r.stdout)
        check("C/advice offers the permanent dismissal",
              "dlint: internal" in r.stdout)

        r = rt.post("S1", d)
        check("C/tier A is silent on a redraft in the same session",
              not advises(r) and r.returncode == 0, r.stdout[:200])

        r = rt.post("S2", d)
        check("C/a NEW session gets its own single advisory", advises(r))

        # --- D. TIER B ---
        r = rt.post("S1", resp)
        check("D/tier B BLOCKS the comms write", r.returncode == 2,
              "rc=%s out=%s err=%s" % (r.returncode, r.stdout[:120],
                                       r.stderr[:120]))
        check("D/tier B writes to stderr (exit 2 discards stdout)",
              "ONEPAGER_Client.md" in r.stderr, r.stderr[:200])

        r = rt.post("S1", resp)
        check("D/tier B loop guard: the second block degrades",
              r.returncode == 0 and advises(r),
              "rc=%s" % r.returncode)

        q = rt.write("sessions/2026/202608/query_202608012100.md", "# Q\n")
        r = rt.post("S3", q)
        check("D/a query_ write is never a delivery", r.returncode == 0)

        for role in ("close_202608012100.md", "wrap_202608012100.md",
                     "career_response_202608012100.md"):
            p = rt.write("sessions/2026/202608/" + role, "# X\n")
            rt.post("S_" + role, d)
            r = rt.post("S_" + role, p)
            check("D/%s is a delivery and blocks" % role, r.returncode == 2,
                  r.returncode)

        r = rt.post("S_none", resp)
        check("D/nothing owed means silence",
              r.returncode == 0 and not advises(r), r.stdout[:120])

        # The dlint live probe is named `hook_probe_response_.md`. A looser
        # delivery prefix would read it as a comms file and make elint block
        # during an unrelated probe run, so pin that it does not.
        probe = rt.write("cp/ccsim/sandbox/hook_probe_response_.md", "# P\n")
        rt.post("S_probe", d)
        r = rt.post("S_probe", probe)
        check("D/the dlint probe file is NOT read as a delivery",
              r.returncode == 0, r.returncode)

        # --- E. TIER C ---
        r = rt.stop("S1")
        check("E/tier C warns", "ONEPAGER_Client.md" in r.stdout,
              r.stdout[:200])
        check("E/tier C NEVER blocks (a Stop block lands after the TEAs)",
              r.returncode == 0, r.returncode)
        check("E/tier C speaks to the user via systemMessage",
              "systemMessage" in r.stdout)
        r = rt.stop("S_none")
        check("E/tier C is silent with nothing owed",
              r.returncode == 0 and not r.stdout.strip(), r.stdout[:120])

        # --- F. RECEIPTS ---
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

        r = rt.post("S4", resp)
        check("F/a receipt with RED>0 does NOT satisfy the gate",
              r.returncode in (0, 2), r.returncode)
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
        r = rt.stop("S6")
        check("F/a CLEAN receipt clears tier C too", not r.stdout.strip(),
              r.stdout[:200])

        with open(d, "a", encoding="utf-8") as fh:
            fh.write("\nAn extra line the clean receipt cannot vouch for.\n")
        r = rt.post("S7", d)
        check("F/an edit after a clean lint lapses the receipt", advises(r),
              "content-addressed receipts must not survive an edit")

        acts = set(x.split("\t")[1] for x in rt.log() if "\t" in x)
        check("G/every invocation is logged (never-fired stays detectable)",
              "post:advise" in acts and "post:block" in acts
              and "stop:clean" in acts, sorted(acts))
    finally:
        rt.close()


# ---------------------------------------------------------------------------
# G/H/I. GUARDS, FAIL-SAFES, SHIM
# ---------------------------------------------------------------------------
def test_guards():
    rt = Repo()
    try:
        d = rt.write(DELIV, "# One-pager\n\n" + FILLER)

        body = json.dumps({
            "session_id": "OUT", "hook_event_name": "PostToolUse",
            "cwd": "/Users/nobody/some-other-project",
            "tool_name": "Write", "tool_input": {"file_path": d}})
        r = rt.run(body, mode="post")
        check("G/out-of-scope cwd is silent",
              r.returncode == 0 and not r.stdout.strip(), r.stdout[:120])

        body = json.dumps({
            "session_id": "SIB", "hook_event_name": "PostToolUse",
            "cwd": rt.root + "-sibling",
            "tool_name": "Write", "tool_input": {"file_path": d}})
        r = rt.run(body, mode="post")
        check("G/a `-sibling` path is not a sub-path (separator-bounded)",
              r.returncode == 0 and not r.stdout.strip(), r.stdout[:120])

        body = json.dumps({
            "session_id": "FO", "hook_event_name": "PostToolUse",
            "tool_name": "Write", "tool_input": {"file_path": d}})
        r = rt.run(body, mode="post")
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
            r = rt.run("", mode="post", raw=raw)
            check("H/fail-safe exit 0 on %s" % label, r.returncode == 0,
                  "rc=%s err=%s" % (r.returncode, r.stderr[:120]))
            r = rt.run("", mode="stop", raw=raw)
            check("H/fail-safe exit 0 on %s (stop)" % label,
                  r.returncode == 0, r.returncode)

        r = subprocess.run([sys.executable, rt.elint, "nonsense"],
                           input=json.dumps({"session_id": "X",
                                             "cwd": rt.root}),
                           capture_output=True, text=True, timeout=60)
        check("H/an unknown mode with no hook_event_name exits 0 silently",
              r.returncode == 0 and not r.stdout.strip(), r.stdout[:120])

        r = subprocess.run([sys.executable, rt.elint],
                           input=rt.payload("MODE", d, "PostToolUse"),
                           capture_output=True, text=True, timeout=60)
        check("H/hook_event_name is a working fallback for a missing argv",
              advises(r), r.stdout[:120])

        # A RELATIVE file_path must resolve against the PAYLOAD's cwd, not the
        # hook process's own —— the harness launches hooks from anywhere, and
        # resolving against the wrong tree makes every territory verdict
        # meaningless. Run from `/` so a cwd-relative resolution cannot
        # accidentally land on the right file.
        r = subprocess.run(
            [sys.executable, rt.elint, "post"],
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
            [sys.executable, rt.elint, "post"], stdin=subprocess.PIPE,
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

        # --- I. SHIM ---
        rt2 = Repo()
        try:
            d2 = rt2.write(DELIV, "# One-pager\n\n" + FILLER)
            code = rt2.write("cscpt/thing.py", "print(1)\n")
            r = rt2.post("SH", code, via_shim=True)
            check("I/the shim skips a payload with no prose extension",
                  r.returncode == 0 and not r.stdout.strip(), r.stdout[:120])
            r = rt2.post("SH", d2, via_shim=True)
            check("I/the shim forwards `post` and returns the advisory",
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

        r = rt.post("REPLAY", p)
        check("J/tier A would have advised at its write", advises(r),
              r.stdout[:200])

        resp = rt.write("sessions/2026/202607/career_response_202607310730.md",
                        "# Response\n")
        r = rt.post("REPLAY", resp)
        check("J/tier B would have BLOCKED the delivering comms write",
              r.returncode == 2, "rc=%s" % r.returncode)
        check("J/the block names the cheat sheet",
              "CHEATSHEET_Stage3.md" in r.stderr, r.stderr[:200])

        r = rt.stop("REPLAY")
        check("J/tier C would have warned the user at turn end",
              "CHEATSHEET_Stage3.md" in r.stdout, r.stdout[:200])

        out = rt.lint(p)
        m_red = re.search(r"RED FLAGS \((\d+)\)", out.stdout)
        m_yel = re.search(r"YELLOW FLAGS \((\d+)\)", out.stdout)
        check("J/FULL dlint still finds the 18 RED flags on this text",
              m_red and m_red.group(1) == "18",
              m_red.group(1) if m_red else out.stdout[-200:])
        check("J/and the 22 YELLOW flags",
              m_yel and m_yel.group(1) == "22",
              m_yel.group(1) if m_yel else "")

        recs = [x for x in rt.receipts() if x.get("p") == os.path.realpath(p)]
        check("J/the failed lint leaves a receipt recording RED>0",
              recs and recs[-1].get("r") == 18, recs[-1] if recs else None)

        rt.post("REPLAY2", p)
        r = rt.post("REPLAY2", resp)
        check("J/a FAILED lint does not unlock delivery", r.returncode == 2,
              "18 RED must not read as linted")
    finally:
        rt.close()


def test_live_probe_intact():
    """The live probe in `cp/ccsim/hook_guide.md` is only a valid liveness
    test whilst the probe FILE still classifies as a deliverable. It sits
    under `cp/` —— protocol territory —— so it depends entirely on its opt-in
    marker, and removing that line would leave a probe that passes for a
    second reason and proves nothing. Pin it here, since a rotted probe is
    how dead wiring survives unnoticed (hook_guide §2)."""
    probe = os.path.join(HERE, "elint_probe_deliverable.md")
    if not os.path.isfile(probe):
        FAIL.append("K/live probe file is missing: %s" % probe)
        return
    sys.path.insert(0, CSCPT)
    try:
        import elint                                             # noqa: E402
        ok, reason = elint.classify(probe)
    finally:
        sys.path.remove(CSCPT)
    check("K/the live probe still classifies as a deliverable", ok,
          "reason=%s —— the probe is inert; restore its "
          "`<!-- dlint: deliverable -->` marker" % reason)
    check("K/and it does so via the opt-in marker, not by accident",
          reason == "marked_deliverable", reason)


def test_scratch_never_owed():
    """REGRESSION —— the exact defect the live wiring caught on 202608012141.

    The probe's opt-in marker made it a permanently OUTSTANDING deliverable,
    so TIER B blocked the first `response_` write of the session, and the
    only way to clear it was to lint the probe —— which writes a clean
    receipt and silences the probe for ever. Scratch must therefore be
    TIER-A-visible (so the probe still proves the wiring) yet never TIER-B
    owed (so the gate's own fixture cannot disarm the gate).

    Encoded as the failing scenario, not as a restatement of the fix: the
    probe classifies as a deliverable AND is excluded from `outstanding()`."""
    probe = os.path.join(HERE, "elint_probe_deliverable.md")
    if not os.path.isfile(probe):
        FAIL.append("L/live probe file is missing: %s" % probe)
        return
    sys.path.insert(0, CSCPT)
    try:
        import elint                                             # noqa: E402
        ok, _reason = elint.classify(probe)
        scratch = elint._is_scratch(probe)
        outside = elint._is_scratch(os.path.join(
            REPO, "sessions", "2026", "202608", "some_deliverable.md"))
    finally:
        sys.path.remove(CSCPT)
    check("L/the probe is still a TIER A subject", ok,
          "TIER A must keep firing or the probe proves nothing")
    check("L/but scratch is never a TIER B obligation", scratch,
          "cp/ccsim/sandbox/ must be excluded from outstanding()")
    check("L/and the exclusion does not leak outside the sandbox",
          not outside, "a real deliverable must still be owed")


def main():
    for fn in (test_classifier, test_tiers, test_guards, test_replay,
               test_live_probe_intact, test_scratch_never_owed):
        try:
            fn()
        except Exception as exc:                                # noqa: BLE001
            FAIL.append("%s raised %r" % (fn.__name__, exc))
    total = PASS + len(FAIL)
    print("elint deliverable-gate suite: %d/%d passed" % (PASS, total))
    for f in FAIL:
        print("  FAIL: %s" % f)
    print("\nNOTE: this proves the SCRIPTS. It proves NOTHING about whether "
          "the harness invokes them —— for that, run the live probe in "
          "cp/ccsim/hook_guide.md after registering the hooks.")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
