#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime
import csv
import re
import sys

# =========================================================
# CONFIG
# =========================================================

BASE_DIR = Path(
    "/Volumes/FURY 2TB/Fury Documents/GitHub/dupbus-ceztuc-7cufVe/seek/gcl"
)

SCRIPT_DIR = Path(__file__).resolve().parent

DIRS = {
    "Applied": BASE_DIR / "applied",
    "Skipped": BASE_DIR / "skipped",
    "Pending": BASE_DIR / "pending",
}

TIMESTAMP_PATTERN = re.compile(r"(\d{12})(?=\.[^.]+$)")

VALID_EXTENSIONS = {".md", ".txt"}

RULE_VIOLATION_SYMBOLS = ["—", "–", "+"]
EXCLUDED_FILENAME_SYMBOL = "❌"

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

        if file.name == "temp.txt":
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


def collect_files(directory: Path):
    """
    Collect only files directly inside directory
    (excluding subfolders).

    Filename timestamp = creation/start timestamp
    File modified time = actual latest activity timestamp
    """

    collected = []

    for item in directory.iterdir():

        if not item.is_file():
            continue

        if item.suffix.lower() not in VALID_EXTENSIONS:
            continue

        # Completely ignore excluded files
        if EXCLUDED_FILENAME_SYMBOL in item.name:
            continue

        created_ts = extract_timestamp(item.name)

        if not created_ts:
            continue

        modified_ts = datetime.fromtimestamp(
            item.stat().st_mtime
        )

        collected.append({
            "path": item,
            "created_timestamp": created_ts,
            "modified_timestamp": modified_ts,
            "name": item.name,
        })

    return sorted(
        collected,
        key=lambda x: x["created_timestamp"]
    )


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


def format_parts(dt, warning=False):

    hh = dt.strftime("%H")
    mm = dt.strftime("%M")

    if warning:
        hh += "⚠️"
        mm += "⚠️"

    return [
        dt.strftime("%Y"),
        dt.strftime("%m"),
        dt.strftime("%d"),
        hh,
        mm,
    ]


def scan_applied_violations():
    """
    Return {filename: total_violation_symbol_count} for Applied files,
    counting RULE_VIOLATION_SYMBOLS that appear AFTER the Cover Letter marker.
    """

    applied_dir = DIRS["Applied"]

    result = {}

    for item in applied_dir.iterdir():

        if not item.is_file():
            continue

        if item.suffix.lower() not in VALID_EXTENSIONS:
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

        marker_match = re.search(
            r"##\s+\d+\.\s+Cover Letter",
            content,
        )

        if not marker_match:
            continue

        scan_content = content[
            marker_match.start():
        ]

        total = sum(
            scan_content.count(symbol)
            for symbol in RULE_VIOLATION_SYMBOLS
        )

        if total > 0:
            result[item.name] = total

    return result


# =========================================================
# MAIN
# =========================================================

def main():

    timeframe_starts, remarks_by_dt = load_timeframes()

    files_by_category = {
        category: collect_files(path)
        for category, path in DIRS.items()
    }

    rows = []

    overlap_warnings = 0

    applied_violations = scan_applied_violations()

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

        # Determine timeframe end
        # Based on latest FILE MODIFIED time

        if all_matches:
            end_dt = max(
                x["modified_timestamp"]
                for x in all_matches
            )

        else:
            # No files found in timeframe
            end_dt = start_dt

        overlap_warning = (
            next_start_dt is not None
            and end_dt > next_start_dt
        )

        if overlap_warning:
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

        row = (
            format_parts(start_dt)
            + format_parts(
                end_dt,
                warning=overlap_warning
            )
            + [
                a,
                len(skipped_matches),
                len(pending_matches),
                V,
                VF,
                v_a,
                vf_a,
                remarks_by_dt.get(start_dt, ""),
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
            and f.name != "temp.txt"
            and f.suffix.lower() in VALID_EXTENSIONS
            and EXCLUDED_FILENAME_SYMBOL not in f.name
        )
    ])

    if not source_files:
        print("No source .txt/.md files found.")
        sys.exit(1)

    # Use first valid source filename
    source_file = source_files[0]

    output_file = source_file.with_suffix(".csv")

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