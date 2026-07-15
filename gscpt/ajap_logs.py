#!/usr/bin/env python3
"""
AJAP Logs Processor

Builds a per-timeframe CSV of job-application activity (Applied / Skipped /
Pending counts plus rule-violation tallies) by cross-referencing a timeframe
instruction file against the NEW AJAP's LEDGER (user 202607080322 §269/297:
the ledger records every job the programme processed, so file moves by #psl
sessions can never contaminate counts; old-AJAP file-scan compatibility is
deliberately dropped).

USAGE
-----
1. In THIS script's own directory, place at least one instruction file with a
   .txt or .md extension (any name except `temp.txt`; anything inside
   `parked/` is ignored). Each meaningful line must START with a 12-digit
   timestamp (YYYYMMDDHHmm) marking a timeframe's start; anything after the
   timestamp on that line is an optional free-text remark. The AJAP programme
   auto-writes these files as `ajap_logs_input_[runtime_start_TS].md`
   (`ses[nn]s`/`ses[nn]e🔴` lines) and runs this script itself on STOP.
   NOTE: macOS screenshot filenames on a line are still normalised into the
   12-digit-TS form first (legacy convenience).
2. Job data comes from the ledger
   (AJAP_repo/AJAP_code/runtime/ledger.db, read-only): every row with outcome
   Applied / Skipped / Pending, bucketed by its processed timestamp.
   Mirror*/LegacyImport/Void/AlreadyApplied rows are excluded by design
   (they are file moves or dedupe memory, not run activity).
3. Run:  python3 ajap_logs.py   (or let AJAP run it at STOP)
4. Output CSV beside this script: for an `ajap_logs_input_*` source the name
   is `ajap_logs_output_[output_TS].csv` ([output_TS] = when the CSV was
   produced); other sources keep the legacy `AJAP Logs [input_stem].csv`.

It STOPS with an alert if: no valid timeframe timestamps are found; no source
.txt/.md instruction file exists; the ledger is missing; or the target output
CSV already exists (delete/rename it first).

Input-line format: `[TS] [ses]%[wk]% ses[no.][s/e]`
"""

from pathlib import Path
from datetime import datetime
import csv
import re
import sys

# =========================================================
# CONFIG
# =========================================================

LEDGER_DB = Path(
    "/Volumes/FURY 2TB/Fury Documents/GitHub/AJAP_repo/AJAP_code/runtime/ledger.db"
)

SCRIPT_DIR = Path(__file__).resolve().parent

CATEGORIES = ("Applied", "Skipped", "Pending")

TIMESTAMP_PATTERN = re.compile(r"(\d{12})(?=\.[^.]+$)")

# macOS screenshot date/time component, e.g. "2026-06-13 at 17.01" inside
# "Screenshot 2026-06-13 at 17.01.29 (4).png". Captures YYYY,MM,DD,HH,mm;
# the seconds and anything after are ignored by the .png converter below.
SCREENSHOT_TS_PATTERN = re.compile(
    r"(\d{4})-(\d{2})-(\d{2})\s+at\s+(\d{2})[.:](\d{2})"
)

VALID_EXTENSIONS = {".md", ".txt"}

RULE_VIOLATION_SYMBOLS = ["—", "–", "+"]
EXCLUDED_FILENAME_SYMBOL = "❌"

# Every Applied file must END with EXACTLY this line (verbatim, no rephrasing,
# and no text after it). Anything else is a P.S. rule violation.
PS_REQUIRED_TAIL = (
    "P.S. I hold full work rights until 2031 and would never require visa sponsorship."
)

# Line-2 override written when AJAP resumed a file after the 5h limit, e.g.
# "(Last Modified: 10:54 on 05/06/2026)"  (HH:MM on DD/MM/YYYY)
LAST_MODIFIED_PATTERN = re.compile(
    r"Last Modified:\s*(\d{1,2}):(\d{2})\s+on\s+(\d{2})/(\d{2})/(\d{4})"
)

# =========================================================
# HELPERS
# =========================================================

def extract_timestamp(filename: str):
    """
    Extract YYYYMMDDHHmm timestamp from filename.
    Example:
    EthosBeathChapman_AutomationTester_202605202140.md
    """
    match = TIMESTAMP_PATTERN.search(filename)

    if not match:
        return None

    try:
        return datetime.strptime(match.group(1), "%Y%m%d%H%M")
    except ValueError:
        return None


def convert_png_line(line: str) -> str:
    """
    Normalise a line containing a macOS screenshot filename into one that
    starts with a 12-digit TS, so load_timeframes() can process it as usual.

    A screenshot filename looks like:
        Screenshot 2026-06-13 at 17.01.29 (4).png
    The `YYYY-MM-DD at HH.MM` component is converted to a 12-digit
    YYYYMMDDHHmm timestamp; anything between the minute and `.png` (here
    `.29 (4)`) is ignored, and the `.png` token itself is removed. Whatever
    follows `.png` on the line (e.g. ` X%X% comment`) is preserved verbatim.

    Lines without `.png`, or whose `.png` portion has no parseable screenshot
    date/time, are returned unchanged.
    """

    lower = line.lower()
    if ".png" not in lower:
        return line

    idx = lower.index(".png")
    before = line[:idx]
    after = line[idx + len(".png"):]

    m = SCREENSHOT_TS_PATTERN.search(before)
    if not m:
        return line

    yyyy, mo, dd, hh, mm = m.groups()
    ts = f"{yyyy}{mo}{dd}{hh}{mm}"

    return f"{ts}{after}"


def load_timeframes():
    """
    Scan all .txt / .md files in SCRIPT_DIR except temp.txt
    and collect valid timeframe starts.
    """

    timeframe_starts = set()
    remarks = {}  # {dt: text after the 12-digit TS on its line}

    line_pattern = re.compile(r"(\d{12})(?!\d)(.*)$")

    for file in SCRIPT_DIR.iterdir():

        if not file.is_file():
            continue

        if file.name in ("temp.txt", "blank.md", "README.md"):
            continue

        if EXCLUDED_FILENAME_SYMBOL in file.name:   # ❌_ voided = non-existent
            continue

        if file.suffix.lower() not in VALID_EXTENSIONS:
            continue

        try:
            content = file.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Failed reading: {file}")
            print(e)
            sys.exit(1)

        for line in content.splitlines():

            line = line.strip()

            if not line:            # ignore blank lines
                continue

            # Normalise any screenshot filename to a leading 12-digit TS first
            line = convert_png_line(line)

            m = line_pattern.match(line)
            if not m:               # line must start with a 12-digit TS
                continue

            try:
                dt = datetime.strptime(m.group(1), "%Y%m%d%H%M")
            except ValueError:
                continue

            remark = m.group(2).strip()   # content after the TS (ignored for processing)

            timeframe_starts.add(dt)
            if dt not in remarks or (remark and not remarks[dt]):
                remarks[dt] = remark

    if not timeframe_starts:
        print("No valid timeframe timestamps found.")
        sys.exit(1)

    return sorted(timeframe_starts), remarks


def collect_ledger_rows():
    """
    Read the AJAP ledger (read-only) and return {category: [row_dict, ...]}
    for Applied / Skipped / Pending outcomes — the ledger replaces the old
    gcl-folder filename scan entirely (user §269/297).

    processed.ts (YYYYMMDDHHmm) = creation/start timestamp
    processed.epoch (row write time) = actual latest activity timestamp
    """
    import sqlite3

    if not LEDGER_DB.exists():
        print(f"Ledger not found: {LEDGER_DB}")
        sys.exit(1)

    conn = sqlite3.connect(f"file:{LEDGER_DB}?mode=ro", uri=True)
    rows = conn.execute(
        "SELECT title, employer, outcome, ar_path, ts, epoch FROM processed "
        "WHERE outcome IN ('Applied', 'Skipped', 'Pending')"
    ).fetchall()
    conn.close()

    by_cat = {c: [] for c in CATEGORIES}

    for title, employer, outcome, ar_path, ts, epoch in rows:
        try:
            created_ts = datetime.strptime(str(ts)[:12], "%Y%m%d%H%M")
        except (ValueError, TypeError):
            continue
        try:
            modified_ts = datetime.fromtimestamp(float(epoch))
        except (ValueError, TypeError, OSError):
            modified_ts = created_ts
        path = Path(ar_path) if ar_path else None
        name = (path.name if path is not None and path.name
                else f"{employer}_{title}_{str(ts)[:12]}.md")
        by_cat[outcome].append({
            "path": path,
            "created_timestamp": created_ts,
            "modified_timestamp": modified_ts,
            "name": name,
        })

    for c in CATEGORIES:
        by_cat[c].sort(key=lambda x: x["created_timestamp"])

    return by_cat


def count_files_in_range(files, start_dt, next_start_dt, category):
    """
    Count files within timeframe.

    Timeframe membership is determined by:
    filename timestamp (creation timestamp)

    Timeframe end is determined later by:
    latest modified timestamp
    """

    matched = []

    for f in files:

        created_ts = f["created_timestamp"]

        if next_start_dt:
            valid = start_dt <= created_ts < next_start_dt
        else:
            # Last timeframe remains open until NOW
            valid = start_dt <= created_ts

        if not valid:
            continue


        matched.append(f)

    return matched


def format_parts(dt, warning=0):
    """
    warning = number of ⚠️ to append to HH/mm (0 = none, 1 = single overlap,
    2 = both the last AND the 2nd-last file overlap). Accepts a bool too
    (True -> one ⚠️).
    """

    hh = dt.strftime("%H")
    mm = dt.strftime("%M")

    if warning:
        marks = "⚠️" * int(warning)
        hh += marks
        mm += marks

    return [
        dt.strftime("%Y"),
        dt.strftime("%m"),
        dt.strftime("%d"),
        hh,
        mm,
    ]


def scan_applied_violations(applied_rows):
    """
    Return {filename: total_violation_count} for the ledger's Applied rows
    (the AR file is read via the row's ar_path; rows whose file has been
    moved/cleared are skipped — counts still come from the ledger). Total =

      1. Each occurrence of a RULE_VIOLATION_SYMBOLS symbol appearing AFTER the
         Cover Letter marker (skipped if the file has no marker).
      2. A single P.S.-ending violation (+1) if the file does NOT end with
         exactly PS_REQUIRED_TAIL —— i.e. its final line is not that exact line,
         or there is any text after it.
    """

    result = {}

    for row in applied_rows:

        item = row["path"]

        if item is None or not item.is_file():
            continue

        # Completely ignore excluded files
        if EXCLUDED_FILENAME_SYMBOL in item.name:
            continue

        try:
            content = item.read_text(
                encoding="utf-8"
            )
        except Exception:
            continue

        total = 0

        # --- Type 1: rule-violation symbols after the Cover Letter marker ---
        marker_match = re.search(
            r"##\s+\d+\.\s+Cover Letter",
            content,
        )

        if marker_match:
            scan_content = content[marker_match.start():]
            total += sum(
                scan_content.count(symbol)
                for symbol in RULE_VIOLATION_SYMBOLS
            )

        # --- Type 2: file must END with exactly PS_REQUIRED_TAIL ---
        # rstrip() tolerates an invisible trailing newline / spaces after the
        # period, but any real text after the line fails the check.
        stripped = content.rstrip()
        last_line = stripped.splitlines()[-1] if stripped else ""
        if last_line != PS_REQUIRED_TAIL:
            total += 1

        if total > 0:
            result[item.name] = total

    return result


def parse_last_modified(path):
    """
    Read the file's Line 2 for "(Last Modified: HH:MM on DD/MM/YYYY)".
    Return a datetime, or None if absent/unparseable.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except Exception:
        return None

    if len(lines) < 2:
        return None

    m = LAST_MODIFIED_PATTERN.search(lines[1])

    if not m:
        return None

    hh, mm, dd, mo, yyyy = m.groups()

    try:
        return datetime(
            int(yyyy), int(mo), int(dd), int(hh), int(mm)
        )
    except ValueError:
        return None


# =========================================================
# MAIN
# =========================================================

def main():

    timeframe_starts, remarks_by_dt = load_timeframes()

    files_by_category = collect_ledger_rows()

    rows = []

    overlap_warnings = 0

    applied_violations = scan_applied_violations(files_by_category["Applied"])

    for i, start_dt in enumerate(timeframe_starts):

        next_start_dt = (
            timeframe_starts[i + 1]
            if i + 1 < len(timeframe_starts)
            else None
        )

        applied_matches = count_files_in_range(
            files_by_category["Applied"],
            start_dt,
            next_start_dt,
            "Applied",
        )

        skipped_matches = count_files_in_range(
            files_by_category["Skipped"],
            start_dt,
            next_start_dt,
            "Skipped",
        )

        pending_matches = count_files_in_range(
            files_by_category["Pending"],
            start_dt,
            next_start_dt,
            "Pending",
        )

        all_matches = (
            applied_matches
            + skipped_matches
            + pending_matches
        )

        # Files in this timeframe, newest-first by filename (creation) TS.
        # Last AR = by_created[0]; 2nd-last AR = by_created[1].
        by_created = sorted(
            all_matches,
            key=lambda x: x["created_timestamp"],
            reverse=True,
        )

        last_ar = by_created[0] if by_created else None
        end_dt = last_ar["modified_timestamp"] if last_ar else start_dt

        # warning_count = number of ⚠️ to stamp on HH_e/mm_e (0/1/2);
        # overlap_filenames = overlapping file name(s) to surface in Remarks.
        warning_count = 0
        overlap_filenames = []

        overlap_warning = (
            next_start_dt is not None
            and end_dt > next_start_dt
        )

        if overlap_warning and last_ar is not None:
            # On overlap (AJAP resumed the last AR after the 5h limit, inflating
            # its filesystem mod time): prefer the real end remarked on Line 2.
            remarked_end = parse_last_modified(last_ar["path"])

            if remarked_end is not None:
                end_dt = remarked_end
                # The Line-2 remark may still overlap; if so, keep a single ⚠️.
                if next_start_dt is not None and end_dt > next_start_dt:
                    warning_count = 1
            else:
                # No Line-2 remark: the last AR's mod time is unreliable, so fall
                # back to the 2nd-last file's mod time. Keep ⚠️ + name the last
                # (overlapping) file so the overlap is still flagged.
                warning_count = 1
                overlap_filenames.append(last_ar["name"])

                second_last = by_created[1] if len(by_created) > 1 else None
                if second_last is not None:
                    end_dt = second_last["modified_timestamp"]

                    # Very rare: the 2nd-last file ALSO overlaps. Stamp 2× ⚠️ and
                    # name it too, but do NOT cascade to the 3rd-last file.
                    if (
                        next_start_dt is not None
                        and end_dt > next_start_dt
                    ):
                        warning_count = 2
                        overlap_filenames.append(second_last["name"])
                # else: only one file in timeframe; keep last AR mod time + 1 ⚠️.

        if warning_count > 0:
            overlap_warnings += 1

        a = len(applied_matches)

        # Rule-violation tallies for THIS timeframe's Applied files
        V = sum(
            applied_violations.get(f["name"], 0)
            for f in applied_matches
        )
        VF = sum(
            1 for f in applied_matches
            if applied_violations.get(f["name"], 0) > 0
        )
        v_a = f"{V / a:.2f}" if a else ""           # avg violations per Applied job (plain number, 2 dp)
        vf_a = f"{VF / a * 100:.0f}%" if a else ""  # % of Applied jobs with any violation (0 dp)

        # Remarks = [overlapping file name(s)] [; personal remark]
        personal_remark = remarks_by_dt.get(start_dt, "")
        overlap_prefix = "; ".join(overlap_filenames)
        if overlap_prefix:
            remark_out = (
                f"{overlap_prefix}; {personal_remark}"
                if personal_remark else overlap_prefix
            )
        else:
            remark_out = personal_remark

        row = (
            format_parts(start_dt)
            + format_parts(
                end_dt,
                warning=warning_count
            )
            + [
                a,
                len(skipped_matches),
                len(pending_matches),
                V,
                VF,
                v_a,
                vf_a,
                remark_out,
            ]
        )

        rows.append(row)

    # =====================================================
    # OUTPUT CSV
    # =====================================================

    source_files = sorted([
        f for f in SCRIPT_DIR.iterdir()
        if (
            f.is_file()
            and f.name not in ("temp.txt", "blank.md", "README.md")
            and f.suffix.lower() in VALID_EXTENSIONS
            and EXCLUDED_FILENAME_SYMBOL not in f.name
        )
    ])

    if not source_files:
        print("No source .txt/.md files found.")
        sys.exit(1)

    # Use first valid source filename
    source_file = source_files[0]

    # Naming (user §286): an AJAP-written input (`ajap_logs_input_*`) yields
    # `ajap_logs_output_[output_TS].csv` ([output_TS] = now); any other source
    # keeps the legacy "AJAP Logs [input_stem].csv" convention.
    if source_file.stem.startswith("ajap_logs_input"):
        out_ts = datetime.now().strftime("%Y%m%d%H%M")
        output_file = source_file.with_name(f"ajap_logs_output_{out_ts}.csv")
    else:
        output_file = source_file.with_name(
            f"AJAP Logs {source_file.stem}.csv")

    if output_file.exists():
        print("")
        print("ERROR: CSV already exists.")
        print(output_file)
        print("")
        print("Delete/rename existing CSV first.")
        sys.exit(1)

    headers = [
        "YYYY_s",
        "MM_s",
        "DD_s",
        "HH_s",
        "mm_s",
        "YYYY_e",
        "MM_e",
        "DD_e",
        "HH_e",
        "mm_e",
        "Applied",
        "Skipped",
        "Pending",
        "V",
        "VF",
        "V/A",
        "VF/A",
        "Remarks",
    ]

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow(headers)

        writer.writerows(rows)

    total_files = sum(
        row[10] + row[11] + row[12]
        for row in rows
    )

    print("")
    print(f"✅ Total files counted: {total_files}")

    if overlap_warnings > 0:
        print("")
        print(
            f"⚠️ Timeframe overlap(s): "
            f"{overlap_warnings}"
        )

    # Rule violations are now reported in the CSV columns V / VF / V/A / VF/A,
    # not in the terminal.

    print("")
    print("CSV generated:")
    print(output_file)


if __name__ == "__main__":
    main()