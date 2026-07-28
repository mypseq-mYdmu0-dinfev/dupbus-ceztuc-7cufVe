#!/bin/bash
# ============================================================================
# syntax_check_nscpt.sh  —  regression guard for every *.sh in this folder.
# ============================================================================
# WHY THIS EXISTS: several scripts here began life as the owner's Apple Notes,
#   so explanatory PROSE (emoji section headings, "Sample Result (Vocus):",
#   pasted sample command output) once sat at shell top level, uncommented.
#   Two distinct failure modes follow, and this guard pins BOTH:
#
#     1. SYNTAX — prose carrying shell metacharacters (e.g. the "(" in
#        "Sample Result (Vocus):") makes the file unparseable, so it cannot be
#        run at all. network_diagnostics.sh failed exactly this way.
#
#     2. SILENT EXECUTION — the worse case, because nothing complains: prose
#        that happens to PARSE gets EXECUTED. A traceroute timeout line
#        " 3  * * *" glob-expands each "*" to every name in the current
#        directory and tries to RUN the first one. "Safari: http://..." runs a
#        command called "Safari:". Neither is caught by a syntax check, which
#        is why check 2 below exists alongside check 1.
#
#   The prose is deliberately KEPT rather than deleted — the owner reads it as
#   documentation. It simply has to stay behind a "#". This guard asserts that
#   it still does, so a future edit cannot quietly un-comment it again.
#
#   NOTE: check 2 is a fixed sentinel list, not a prose detector. Prose in a
#   NEWLY added note-style script still has to be commented by hand; add its
#   distinctive fragments to PROSE below so they are pinned from then on.
#
# HOW TO RUN, in a plain Terminal:
#   bash "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/nscpt/syntax_check_nscpt.sh"
# Exit 0 = everything clean. Exit 1 = at least one failure, named with its line.
# ----------------------------------------------------------------------------
set -uo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
rc=0

# --- Check 1: every *.sh parses under the shell its own shebang names -------
# Parsing a zsh script with bash (or vice versa) can both miss real errors and
# invent fake ones, so the interpreter is taken from the file itself.
echo "== Check 1: parse every *.sh =="
for f in "$DIR"/*.sh; do
  case "$(head -1 "$f")" in
    '#!'*zsh) shell=zsh ;;
    *)        shell=bash ;;   # no shebang -> bash, matching /bin/sh fallback
  esac
  if err="$("$shell" -n "$f" 2>&1)"; then
    printf '  PARSE OK    %s (%s)\n' "$(basename "$f")" "$shell"
  else
    printf '  PARSE FAIL  %s (%s)\n' "$(basename "$f")" "$shell"
    printf '%s\n' "$err" | sed 's/^/                /'
    rc=1
  fi
done

# --- Check 2: known prose must remain commented -----------------------------
# Format: filename|verbatim fragment. Each fragment is EXPLANATORY text, never
# a command, so every line it appears on must begin with "#". These are the
# exact strings that were found bare and were commented out; listing them here
# is what turns that one-off fix into a standing invariant.
echo "== Check 2: known prose stays commented =="
PROSE=(
  "network_diagnostics.sh|🛜 Ping Google:"
  "network_diagnostics.sh|Sample Result:"
  "network_diagnostics.sh|ping statistics"
  "network_diagnostics.sh|packets transmitted"
  "network_diagnostics.sh|round-trip min/avg/max/stddev"
  "network_diagnostics.sh|🗺️ Trace Route:"
  "network_diagnostics.sh|Sample Result (Vocus):"
  "network_diagnostics.sh|traceroute to 8.8.8.8"
  "network_diagnostics.sh|192.168.0.1"
  "network_diagnostics.sh|vocus.network"
  "network_diagnostics.sh|* * *"
  "coding_basics.sh|🌱 Create venv:"
  "coding_basics.sh|🌿 Activate the venv:"
  "coding_basics.sh|🌐 Run PHP Server:"
  "coding_basics.sh|Safari: http://localhost:8000"
  "coding_basics.sh|Terminal Run Python:"
  "12digit_timestamp.sh|---"
)

for entry in "${PROSE[@]}"; do
  file="${entry%%|*}"
  frag="${entry#*|}"
  path="$DIR/$file"
  if [ ! -f "$path" ]; then
    printf '  MISSING     %s (expected to exist)\n' "$file"
    rc=1
    continue
  fi
  hits="$(grep -Fn -- "$frag" "$path" || true)"
  if [ -z "$hits" ]; then
    # Deleting the prose is also a regression: the owner wants it kept visible.
    printf '  PROSE GONE  %s: "%s" no longer present\n' "$file" "$frag"
    rc=1
    continue
  fi
  while IFS= read -r hit; do
    n="${hit%%:*}"
    body="${hit#*:}"
    case "$(printf '%s' "$body" | sed 's/^[[:space:]]*//')" in
      '#'*) printf '  COMMENTED   %s:%s\n' "$file" "$n" ;;
      *)    printf '  BARE PROSE  %s:%s  ->  %s\n' "$file" "$n" "$body"; rc=1 ;;
    esac
  done <<< "$hits"
done

echo "----------------------------------------------------------------------"
if [ "$rc" -eq 0 ]; then
  echo "PASS — every script parses and all known prose is commented."
else
  echo "FAIL — see the lines flagged above."
fi
exit "$rc"
