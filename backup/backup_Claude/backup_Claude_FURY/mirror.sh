#!/bin/bash
#
# mirror.sh —— drift check + re-mirror for the backup_Claude_FURY snapshot.
#
# WHY THIS EXISTS
#   Every file mirrored here lives under /Volumes/FURY 2TB/.claude/, which is OUTSIDE
#   every git repo (~/.claude is a symlink to it). Nothing versions those files and
#   nothing warns when one changes. A snapshot that is never re-checked decays into a
#   configuration that was correct months ago —— which is WORSE than no backup at all,
#   because restoring it looks like it worked. This script makes that decay visible in
#   one command, so the snapshot maintains itself instead of rotting quietly.
#
# WHY A SCRIPT AND NOT A PASTE-BLOCK
#   A check that must be retyped correctly is a check that eventually gets skipped or
#   mistyped. One command, one exit code, no thinking required.
#
# WHEN TO RUN
#   `./mirror.sh sync` at the START of every CCSIM session. Also immediately after any
#   turn that edited a live file —— above all ~/.claude/settings.json, which carries the
#   ONLY registration of every lint hook.
#
# USAGE
#   ./mirror.sh                check only; one line per file; exit 1 if anything drifted
#   ./mirror.sh sync           re-mirror every drifted/absent file, then re-check
#   ./mirror.sh restore-plan   print the cp commands that copy the backups BACK into a
#                              rebuilt ~/.claude (prints only —— it never writes)
#
#   `sync` OVERWRITES the backup copy from the live file. That is intended and safe:
#   this folder is tracked by git, so the previous contents stay recoverable from
#   history. The live file is always the truth; the backup is always the follower.
#
# EXIT CODES
#   0  every mirrored pair identical, no structural problem
#   1  drift found (check mode only —— `sync` repairs drift and then returns 0)
#   2  structural problem a human must resolve: a mapped source vanished, a live file
#      has no mapping, or a backup file has no mapping. Each needs a naming or scope
#      DECISION, so the script reports it and refuses to guess.
#
# TESTING
#   CLAUDE_HOME and BACKUP_DIR may be pointed at fixtures. mirror_test.sh does exactly
#   that, so the regression test never touches the real .claude folder.

set -u

CLAUDE_HOME="${CLAUDE_HOME:-/Volumes/FURY 2TB/.claude}"
BACKUP_DIR="${BACKUP_DIR:-$(cd "$(dirname "$0")" && pwd)}"
MODE="${1:-check}"

# ---------------------------------------------------------------------------
# MAP —— the authoritative source-path <-> backup-name mapping.
# Format: <path relative to CLAUDE_HOME>|<filename in this folder>
# Naming rule (see README.md): prefix `backup_`, append `.md` if the source is not
# already .md, and insert a project tag where two projects hold same-named files.
# ---------------------------------------------------------------------------
MAP=$(cat <<'EOF'
settings.json|backup_settings.json.md
scheduled-tasks/ajap-auto-resume/SKILL.md|backup_scheduled-tasks_ajap-auto-resume_SKILL.md
projects/-Volumes-FURY-2TB-Fury-Documents-GitHub-dupbus-ceztuc-7cufVe/memory/MEMORY.md|backup_memory_dupbus_MEMORY.md
projects/-Volumes-FURY-2TB-Fury-Documents-GitHub-dupbus-ceztuc-7cufVe/memory/feedback_ajap_display_n.md|backup_memory_dupbus_feedback_ajap_display_n.md
projects/-Volumes-FURY-2TB-Fury-Documents-GitHub-dupbus-ceztuc-7cufVe/memory/feedback_application_email.md|backup_memory_dupbus_feedback_application_email.md
projects/-Volumes-FURY-2TB-Fury-Documents-GitHub-dupbus-ceztuc-7cufVe/memory/feedback_cic_mandate_on_trigger.md|backup_memory_dupbus_feedback_cic_mandate_on_trigger.md
projects/-Volumes-FURY-2TB-Fury-Documents-GitHub-dupbus-ceztuc-7cufVe/memory/feedback_declare_mahb_reread.md|backup_memory_dupbus_feedback_declare_mahb_reread.md
projects/-Volumes-FURY-2TB-Fury-Documents-GitHub-dupbus-ceztuc-7cufVe/memory/feedback_hb_reread_mahb.md|backup_memory_dupbus_feedback_hb_reread_mahb.md
projects/-Volumes-FURY-2TB-Fury-Documents-GitHub-dupbus-ceztuc-7cufVe/memory/feedback_no_chat_text.md|backup_memory_dupbus_feedback_no_chat_text.md
projects/-Volumes-FURY-2TB-Fury-Documents-GitHub-dupbus-ceztuc-7cufVe/memory/feedback_sa_brief_frontload_mandate.md|backup_memory_dupbus_feedback_sa_brief_frontload_mandate.md
projects/-Volumes-FURY-2TB-Fury-Documents-GitHub-dupbus-ceztuc-7cufVe/memory/user_chameleon_veteran.md|backup_memory_dupbus_user_chameleon_veteran.md
projects/-Volumes-FURY-2TB-Fury-Documents-GitHub-AJAP-repo/memory/MEMORY.md|backup_memory_ajap_MEMORY.md
projects/-Volumes-FURY-2TB-Fury-Documents-GitHub-AJAP-repo/memory/feedback_ajap_no_blocking_questions.md|backup_memory_ajap_feedback_ajap_no_blocking_questions.md
projects/-Volumes-FURY-2TB-Fury-Documents-GitHub-AJAP-repo/memory/feedback_ajap_no_permission_prompts.md|backup_memory_ajap_feedback_ajap_no_permission_prompts.md
EOF
)

# ---------------------------------------------------------------------------
# EXCLUDE —— live files that WATCHED_LIVE would otherwise flag as unmirrored, each
# with the reason it is deliberately out of scope. Keeping the decision here (rather
# than in prose alone) stops a future session re-litigating it or silently adding it.
# ---------------------------------------------------------------------------
EXCLUDE=$(cat <<'EOF'
scheduled-tasks/ma-heartbeat-cc-reminder/SKILL.md
EOF
)
# scheduled-tasks/ma-heartbeat-cc-reminder/SKILL.md —— its own text declares it
#   deprecated and safe to delete; mirroring it would preserve dead logic.

# WATCHED_LIVE —— the live locations that are supposed to be fully covered. These are
# DISCOVERED, not listed, because the real rot vector is a NEW file appearing (a fresh
# auto-memory entry, a new project's memory folder) that no static list would mention.
watched_live() {
  find "$CLAUDE_HOME/projects" -type f -path '*/memory/*.md' 2>/dev/null
  find "$CLAUDE_HOME/scheduled-tasks" -type f -name 'SKILL.md' 2>/dev/null
}

in_list() { printf '%s\n' "$2" | grep -Fxq "$1"; }

status=0   # 0 = clean, 1 = drift
struct=0   # 1 = needs a human decision

case "$MODE" in
  check|sync) ;;
  restore-plan)
    echo "# Restore plan —— review, then paste into a fresh terminal."
    echo "# Preconditions: the repo is back from GitHub, and ~/.claude exists (as a real"
    echo "# folder, or as a symlink to the replacement drive). Nothing below is run here."
    echo
    while IFS='|' read -r src bak; do
      [ -z "$src" ] && continue
      d="$(dirname "$src")"
      # A top-level source yields dirname "." —— emitting `mkdir -p ".../.claude/."`
      # would read like a typo in a plan meant to be pasted without hesitation.
      [ "$d" != "." ] && printf 'mkdir -p "%s"\n' "$CLAUDE_HOME/$d"
      printf 'cp "%s" "%s"\n' "$BACKUP_DIR/$bak" "$CLAUDE_HOME/$src"
    done <<EOF
$MAP
EOF
    echo
    echo "# THEN: correct every absolute path inside settings.json if the repo or the"
    echo "# volume moved, and verify the hooks actually FIRE —— a file check proves"
    echo "# nothing. Use the live probe in cp/ccsim/hook_guide.md §7.2."
    exit 0
    ;;
  *)
    echo "usage: $(basename "$0") [check|sync|restore-plan]" >&2
    exit 2
    ;;
esac

# --- 1. Mapped pairs: identical? -------------------------------------------
while IFS='|' read -r src bak; do
  [ -z "$src" ] && continue
  s="$CLAUDE_HOME/$src"
  b="$BACKUP_DIR/$bak"

  if [ ! -f "$s" ]; then
    # The live file is gone (deleted or renamed upstream). Not auto-resolvable:
    # dropping the backup could discard the last copy in existence.
    echo "MISSING    $src  (mapped source no longer exists —— keep or retire $bak?)"
    struct=1
    continue
  fi

  if [ ! -f "$b" ]; then
    if [ "$MODE" = sync ]; then
      cp "$s" "$b" && echo "SYNCED     $bak  (first copy)" || { echo "FAILED     $bak"; struct=1; }
    else
      echo "ABSENT     $bak  (live file has never been mirrored)"
      status=1
    fi
    continue
  fi

  if cmp -s "$s" "$b"; then
    echo "OK         $bak"
  elif [ "$MODE" = sync ]; then
    cp "$s" "$b" && echo "SYNCED     $bak  (was stale)" || { echo "FAILED     $bak"; struct=1; }
  else
    echo "DRIFT      $bak  <- $src"
    status=1
  fi
done <<EOF
$MAP
EOF

# --- 2. Live files nothing mirrors -----------------------------------------
while IFS= read -r live; do
  [ -z "$live" ] && continue
  rel="${live#"$CLAUDE_HOME"/}"
  in_list "$rel" "$EXCLUDE" && continue
  in_list "$rel" "$(printf '%s\n' "$MAP" | cut -d'|' -f1)" && continue
  echo "UNMIRRORED $rel"
  echo "           ^ live file with no backup. Apply the README selection test, then"
  echo "             add it to MAP + README, or to EXCLUDE with its reason."
  struct=1
done <<EOF
$(watched_live)
EOF

# --- 3. Backup files nothing explains --------------------------------------
for f in "$BACKUP_DIR"/backup_*; do
  [ -e "$f" ] || continue
  b="$(basename "$f")"
  in_list "$b" "$(printf '%s\n' "$MAP" | cut -d'|' -f2)" && continue
  echo "ORPHAN     $b  (backup file with no mapping —— its source is unknown)"
  struct=1
done

# --- Verdict ---------------------------------------------------------------
echo
if [ "$struct" -ne 0 ]; then
  echo "RESULT: needs a human decision (see the lines above). exit 2"
  exit 2
fi
if [ "$MODE" = sync ]; then
  echo "RESULT: snapshot in sync. exit 0"
  exit 0
fi
if [ "$status" -ne 0 ]; then
  echo "RESULT: drift found —— run './mirror.sh sync' to re-mirror. exit 1"
  exit 1
fi
echo "RESULT: snapshot in sync. exit 0"
exit 0
