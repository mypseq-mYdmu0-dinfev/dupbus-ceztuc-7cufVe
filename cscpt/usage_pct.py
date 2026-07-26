#!/usr/bin/env python3
"""Live Claude usage reader — ses% & wk% from the "Claude Web" usage panel.

=== NON-CCSIM —— start of all you need to RUN it ===
WHAT: prints live Claude usage —— the 5-hourly session % (`ses%`) and weekly
`wk%`. PRECONDITION: "Claude Web" open on its usage page.

    python3 cscpt/usage_pct.py --ses     # that integer alone, or "?" (--wk too)
    #  bare = human line; --json = both machine-readable; --no-dialog skips
    #  the pre-run warning

* IT DRIVES THE MAC by keystroke, only whilst "Claude Web" is frontmost ——
  tell the user not to type meanwhile.
* SLOW: up to ~1 min, waiting for the ~30–60 s window in which the numbers are
  true.
* IT NEVER GUESSES: on failure it prints "?" / `ok:false`, exit 1. Re-run.
=== NON-CCSIM —— end of all you need to RUN it ===

=== CCSIM —— only if you EDIT this file (NOT needed to run it) ===
RUN DETAIL (moved out of NON-CCSIM —— a caller needs the warning, not the
mechanism). Keystrokes only (⌘R refresh, ⌘A/⌘C grab, ⌘` next window), never a
click. The pre-run dialog gives 15 s auto-continue; Cancel exits 1 quietly;
Defer waits 1 min then asks once more; `--no-dialog` skips it for scripted
callers. The clipboard is saved and restored, and the ⌘A highlight cleared after
a successful grab. It retries for up to ~1 min waiting on "Last updated: just
now", cycling windows if the frontmost one is not the usage panel. Zero
third-party deps — only `osascript`, `pbpaste`, `pbcopy` — so any `python3` runs
it; the AJAP cockpit uses its own sibling instead (see SIBLING below).


PARSE BY LABEL, NOT PIXEL: the panel is real, SELECTABLE text, so it is grabbed
via ⌘A+⌘C and parsed by anchoring on "Current session" / "All models" — never on
a line offset, making it structurally immune to the promo/notice banner that
shifts the two integers down. Exactly two %% are accepted (the "Fable" weekly bar
is ignored), everything from "Usage credits" onward is dropped, and prose lines
(ending in a full stop) discarded.

KEYSTROKE SAFETY: System Events keystrokes land on whatever app is FRONTMOST —
if the user grabs focus mid-run, a stray ⌘R could refresh THEIR page and wipe
work. So EVERY keystroke is gated on a frontmost check; wrong app -> re-activate,
wait, re-check (up to 3); still wrong -> nothing is fired and the attempt fails
safely. A tiny check->keystroke TOCTOU window remains by physics; closing it
needs pid-targeted event posting (Quartz CGEventPostToPid, via pyobjc), which the
AJAP sibling has and this file deliberately does not.

THE GUARD MUST ASK THE APP DIRECTLY, NEVER SELF-CALIBRATE: an earlier version
sampled System Events' frontmost-process NAME ~0.4 s after its own activate and
remembered THAT as the target, because the PWA's real process name is not "Claude
Web". Live-caught flaw: a slow activation makes that sample land on whatever the
user is in at that moment, and the guard then fires keystrokes THERE (it once
⌘A-ed the user's VS Code window). Fixed by asking "Claude Web" itself for its own
`frontmost` property — nothing to guess, no window for a slow activation to
poison. Do not reintroduce a calibration step.

DESELECT VIA ⌘R: arrow keys do NOT collapse a selection in a non-editable
browser page (they scroll; the highlight stays), so a final ⌘R is the reliable
click-free deselect — the reload drops the selection and re-renders the panel.

SIBLING: `AJAP_repo/scripts/core/ajap_usage_pct.py` is the venv-bound twin (same
cycle + parser, plus OCR fallback + sampler wiring); CONSIDER mirroring any fix
either way. They stay separate BY DESIGN: this one must remain ZERO-DEP so any
session/machine runs it on bare python3, whilst the sibling gets pyobjc and must
stay prompt-free for unattended runs (hence the pre-run dialog lives here only).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time

APP_NAME = "Claude Web"
REFRESH_WAIT = 10.0         # settle after ONE ⌘R before grabbing (user 202607221929)
MAX_TRIES = 6               # refresh→wait→grab cycles, ~1 min total (user 202607221929)
MAX_WINDOWS = 4             # rare multi-window case: cycle with ⌘` this many


def _osa(*lines: str) -> bool:
    args = ["osascript"]
    for l in lines:
        args += ["-e", l]
    return subprocess.run(args, capture_output=True, text=True).returncode == 0


def _activate() -> None:
    _osa(f'tell application "{APP_NAME}" to activate')
    time.sleep(0.8)


def _frontmost_ok() -> bool:
    """Direct target query (guard fix, user 202607230551) — see module
    docstring. Ask "Claude Web" ITSELF whether it considers itself frontmost;
    no process-name guessing, no self-calibration to whatever happened to be
    in front after our own activate."""
    r = subprocess.run(
        ["osascript", "-e", f'tell application "{APP_NAME}" to get frontmost'],
        capture_output=True, text=True)
    return r.returncode == 0 and r.stdout.strip() == "true"


def _keystroke(line: str) -> bool:
    """Guarded keystroke (user 202607222309): System Events keystrokes land
    on the FRONTMOST app — a stray ⌘R on the user's own browser could wipe
    their work. So verify frontmost IS "Claude Web" before EACH keystroke;
    wrong app → re-activate + short wait + re-check (up to 3); still wrong →
    fire NOTHING and return False (the attempt fails safely). A tiny
    check→keystroke TOCTOU window remains by physics (a check can never be
    atomic with the act it gates) — closing it needs pid-targeted event
    posting (pyobjc), which the AJAP sibling has; this stays zero-dep."""
    for _ in range(3):
        if _frontmost_ok():
            return _osa(line)
        _osa(f'tell application "{APP_NAME}" to activate')
        time.sleep(0.5)
    return False


def _refresh() -> bool:
    ok = _keystroke(
        'tell application "System Events" to keystroke "r" using command down')
    if ok:
        time.sleep(REFRESH_WAIT)
    return ok


def _deselect() -> None:
    # clear the ⌘A highlight once grabbed (user 202607221929). Live find
    # 202607221947: arrow keys do NOT collapse a selection in a non-editable
    # browser page (they scroll; the blue stays) — a final ⌘R is the reliable
    # click-free deselect: the reload drops the selection and leaves the
    # panel freshly rendered. Fire-and-exit; no settle needed.
    _keystroke(
        'tell application "System Events" to keystroke "r" using command down')


def _next_window() -> None:
    # ⌘` cycles windows WITHIN the frontmost app (key code 50 = the ` key).
    _keystroke(
        'tell application "System Events" to key code 50 using command down')
    time.sleep(0.4)


def _grab_text() -> str | None:
    """⌘A+⌘C the frontmost window; save/restore the user's clipboard. Each
    keystroke is individually frontmost-guarded (the user could grab focus
    between the ⌘A and the ⌘C)."""
    try:
        prev = subprocess.run(["pbpaste"], capture_output=True, text=True).stdout
    except Exception:
        prev = None
    ok = _keystroke(
        'tell application "System Events" to keystroke "a" using command down')
    if ok:
        time.sleep(0.15)
        ok = _keystroke(
            'tell application "System Events" to keystroke "c" using command down')
    time.sleep(0.25)
    txt = None
    try:
        txt = subprocess.run(["pbpaste"], capture_output=True, text=True).stdout
    except Exception:
        pass
    if prev is not None:
        try:
            subprocess.run(["pbcopy"], input=prev, text=True)
        except Exception:
            pass
    return (txt or None) if ok else None


def parse(text: str) -> dict:
    """Label-anchored parse (user 202607212102): accept EXACTLY two %% — ses%
    ("Current session") and wk% ("All models"; the "Fable" weekly bar is
    ignored) — drop everything from "Usage credits" onward, drop prose (lines
    ending in a full stop), capture "Last updated:" for freshness only."""
    lines = [l.strip() for l in text.splitlines()]
    kept: list[str] = []
    for l in lines:                                   # cut "Usage credits" on
        if l.lower() == "usage credits":
            break
        kept.append(l)
    last_updated = None
    for l in kept:
        m = re.search(r"last updated:\s*(.+)", l, re.I)
        if m:
            last_updated = m.group(1).strip().rstrip(".")
    body = [l for l in kept if l and not l.endswith(".")]  # drop blanks + prose

    def sect(anchor: str, stops: list[str]):
        idx = next((k for k, l in enumerate(body)
                    if re.search(anchor, l, re.I)), None)
        if idx is None:
            return None, None
        reset = None
        for l in body[idx + 1:]:
            if any(re.fullmatch(s, l, re.I) for s in stops):
                break
            if reset is None:
                mr = re.search(
                    r"resets?\s+in\s*(?:(\d+)\s*hr)?\s*(?:(\d+)\s*min)?", l, re.I)
                if mr and (mr.group(1) or mr.group(2)):
                    reset = (int(mr.group(1) or 0), int(mr.group(2) or 0))
            mp = re.fullmatch(r"(\d{1,3})\s*%(?:\s*used)?", l, re.I)
            if mp:
                return int(mp.group(1)), reset
        return None, reset

    ses, ses_reset = sect(r"current session|^session$",
                          [r"weekly limits", r"all models"])
    wk, _ = sect(r"all models", [r"fable", r"last updated.*", r"usage credits"])
    return {"ses": ses, "wk": wk, "ses_reset": ses_reset,
            "last_updated": last_updated}


def read() -> dict:
    """Full cycle (user 202607221929): per attempt exactly ONE ⌘R, wait
    REFRESH_WAIT, grab, parse; retry only on failure, up to MAX_TRIES
    (~1 min); deselect the ⌘A highlight once a grab succeeds. A window whose
    FIRST grab shows no anchors is the wrong window — cycle to the next."""
    _activate()
    for _ in range(MAX_WINDOWS):
        for attempt in range(MAX_TRIES):
            if not _refresh():                  # guard aborted — nothing was
                continue                        # fired; count a failed attempt
            got = parse(_grab_text() or "")
            anchors = got["ses"] is not None or got["wk"] is not None
            if not anchors:
                if attempt == 0:
                    break                       # wrong window — next window
                continue                        # transient bad grab — retry
            fresh = "just now" in (got.get("last_updated") or "").lower()
            complete = got["ses"] is not None and got["wk"] is not None
            if (fresh and complete) or attempt == MAX_TRIES - 1:
                _deselect()
                got["ok"] = complete
                return got
        _next_window()                          # wrong window or tries spent
    return {"ses": None, "wk": None, "ses_reset": None,
            "last_updated": None, "ok": False}


def _predialog() -> None:
    """Pre-run warning (user 202607222309): the script is about to drive the
    frontmost app with keystrokes — give the user 15 s to pause typing before
    the first activate. Auto-continues after 15 s ("giving up"); "Cancel"
    exits 1 quietly; "Defer 1 min" sleeps 60 then shows the dialog once more
    (the second showing's Defer just proceeds — no unbounded deferral).
    Skipped by --no-dialog for scripted callers. STANDALONE ONLY by design:
    the AJAP sibling must stay prompt-free for unattended runs."""
    for shown in range(2):
        r = subprocess.run(
            ["osascript", "-e",
             ('display dialog "usage_pct will drive Claude Web in 15s '
              '(⌘R + ⌘A/⌘C). Pause your typing." '
              'buttons {"Defer 1 min", "Cancel", "Run now"} '
              'default button "Run now" giving up after 15')],
            capture_output=True, text=True)
        if r.returncode != 0:       # "Cancel" errors osascript (-128) — quiet
            sys.exit(1)
        if "Defer 1 min" in r.stdout and shown == 0:
            time.sleep(60)
            continue
        return


def _fmt_reset(r) -> str:
    if not r:
        return "?"
    h, m = r
    return (f"{h}h {m}m" if h else f"{m}m")


def main() -> int:
    if "--no-dialog" not in sys.argv:
        _predialog()
    got = read()
    ses = got["ses"] if got["ses"] is not None else "?"
    wk = got["wk"] if got["wk"] is not None else "?"
    if "--json" in sys.argv:
        r = got.get("ses_reset")
        print(json.dumps({
            "ses": got["ses"], "wk": got["wk"],
            "ses_reset_min": (r[0] * 60 + r[1]) if r else None,
            "last_updated": got["last_updated"], "ok": got["ok"]}))
    elif "--ses" in sys.argv:
        print(ses)
    elif "--wk" in sys.argv:
        print(wk)
    else:
        if got["ok"]:
            print(f"ses% = {ses} | wk% = {wk} | ses resets in "
                  f"{_fmt_reset(got['ses_reset'])} | Last updated: "
                  f"{got['last_updated']}")
        else:
            print(f"ses% = {ses} | wk% = {wk}  "
                  "(could not read Claude Web usage panel — is it open on the "
                  "usage page?)")
    return 0 if got["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
