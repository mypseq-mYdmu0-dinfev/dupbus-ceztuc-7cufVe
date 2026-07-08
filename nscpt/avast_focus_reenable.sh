#!/bin/zsh
# ============================================================
# avast_focus_reenable.sh
# Re-enables the "decoy" macOS Focus mode that tricks Avast.app
# into thinking Focus is on (so it self-silences its own custom
# popups) whilst NOT silencing anything else (see response_
# 202607082153.md for the full explanation + one-time setup).
#
# PREREQUISITE (one-time, manual, GUI --- cannot be scripted):
#   1. System Settings > Focus > + > Custom > name it (match
#      SHORTCUT_NAME's Focus target below, e.g. "Avast Decoy").
#   2. In it: Apps row + People row --- both set to "Silence
#      Notifications From" and add NOBODY/NOTHING to either list
#      (leaving both empty = nothing is actually silenced).
#   3. Turn it on once manually; approve Avast's Focus-status
#      permission prompt (or grant it via System Settings >
#      Privacy & Security > Focus > Avast).
#   4. In Shortcuts.app, create a shortcut named exactly
#      SHORTCUT_NAME below, containing ONE action: "Set Focus"
#      -> your Focus (e.g. "Avast Decoy") -> On -> Until Turned Off.
#
# THIS SCRIPT just re-runs that Shortcut (i.e. re-toggles the
# Focus back on) --- e.g. if you ever turn it off by mistake. It
# does NOT create/configure the Focus itself (not scriptable).
# ============================================================

SHORTCUT_NAME="Avast Decoy Focus On"   # must match your Shortcuts.app shortcut's name exactly

shortcuts run "$SHORTCUT_NAME"
