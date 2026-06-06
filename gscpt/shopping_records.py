#!/usr/bin/env python3
"""
Shopping Records Processor

Process all *.txt receipt files (except temp.txt) into standardised csv files.
Input:  this script's own directory (inside the repo)
Output: this script's own directory (inputs are .txt, outputs are .csv — no clash)
No external libraries required.

USAGE
-----
1. In THIS script's own directory, place one or more receipt .txt files (any
   name except `temp.txt`). Each file is a raw receipt: description lines
   accumulate until a standalone price line (e.g. `5.47`) closes a record;
   prices glued onto the end of a line are split automatically.
2. Run:  python3 shopping_records.py
3. For each input, an output CSV is written beside this script as
   `Shopping Records [input_stem].csv` (columns: Note, Amount), where
   [input_stem] is that receipt's filename without its extension.

A given output is SKIPPED (with an alert) if its CSV already exists — remove
it and rerun.
"""

import os
import re
import glob

INPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = INPUT_DIR
EXCLUDE   = 'temp.txt'


# ── Text Transformations ──────────────────────────────────────────────────────

def remove_special_chars(text):
    """Remove ^, #, and * characters anywhere in the text."""
    return re.sub(r'[\^#*]', '', text)


def split_camel_case(text):
    """Insert a space between a lowercase letter directly followed by an uppercase letter."""
    return re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)


def remove_net(text):
    return re.sub(r'\bNET\b', '', text)


def handle_packs_and_qty(text):
    """
    Apply pack/quantity transformations in strict order so that pack-related
    Qty values are consumed before standalone Qty conversion.

      1. NxWunit Pack  →  Npk       e.g. "5x120g Pack" → "5pk"
      2. Npk Qty M     →  xN xMpk   e.g. "12pk Qty 2"  → "x12 x2pk"
      3. Npk            →  xN x1pk   e.g. "12pk"         → "x12 x1pk"
      4. Qty M          →  xM         e.g. "Qty 2"        → "x2"
    """
    # 1. "5x120g Pack" → "5pk"  (requires digit immediately after x)
    text = re.sub(
        r'(\d+)[xX](\d+\.?\d*)\w*\s+(?:Pack|Pks?)\b',
        lambda m: m.group(1) + 'pk',
        text,
        flags=re.IGNORECASE
    )
    # 2. "12pk Qty 2" → "x12 x2pk"
    text = re.sub(
        r'(\d+)\s*[Pp][Kk]\s+Qty\s+(\d+)',
        lambda m: f'x{m.group(1)} x{m.group(2)}pk',
        text,
        flags=re.IGNORECASE
    )
    # 3. remaining "12pk" → "x12 x1pk"
    text = re.sub(
        r'(\d+)\s*[Pp][Kk]\b',
        lambda m: f'x{m.group(1)} x1pk',
        text
    )
    # 3b. "Pk 4" or "Pack 4" → "x4 x1pk"  (pack word before count)
    text = re.sub(
        r'(?<!\d)[Pp][Kk]\s+(\d+)',
        lambda m: f'x{m.group(1)} x1pk',
        text
    )
    # 4. remaining "Qty 2" → "x2"
    text = re.sub(
        r'\bQty\s+(\d+)',
        lambda m: f'x{m.group(1)}',
        text,
        flags=re.IGNORECASE
    )
    return text


def normalise_at_price(text):
    """Remove any whitespace between @ and $."""
    return re.sub(r'@\s*\$', '@$', text)


def normalise_unit_spacing(text):
    """
    Remove whitespace between a number and its unit (g, kg, ml, l, L).
    Also normalises bare 'l' → 'L' (both spaced and unspaced forms).
    """
    def _repl(m):
        unit = 'L' if m.group(2) == 'l' else m.group(2)
        return m.group(1) + unit

    # Spaced: "0.832 kg" → "0.832kg", "1 l" → "1L"
    text = re.sub(r'(\d+\.?\d*)\s+(ml|kg|g|l|L)\b', _repl, text)
    # Unspaced bare l: "1l" → "1L"  (ml is safe: digit precedes m, not l directly)
    text = re.sub(r'(\d+\.?\d*)(l)\b', lambda m: m.group(1) + 'L', text)
    return text


def normalise_each(text):
    """Strip any preceding whitespace and replace word 'each' with 'ea'."""
    return re.sub(r'\s*\beach\b', 'ea', text, flags=re.IGNORECASE)


def smart_title_case(text):
    """
    Title-case each token with three exceptions (left untouched):
      - Tokens containing digits, @, $, or /  →  qty/price notation (x2, @$6.10ea, etc.)
      - All-uppercase tokens of 1–2 chars      →  abbreviations (WW, JW, OK, etc.)
    Everything else: first letter upper, remainder lower.
    """
    def _word(w):
        if re.search(r'[\d@$/]', w):
            return w
        if w.isupper() and 1 <= len(w) <= 2:
            return w
        return (w[0].upper() + w[1:].lower()) if w else w

    return ' '.join(_word(w) for w in text.split())


def process_note(desc_lines):
    """
    Consolidate a list of raw description lines into a single, fully
    transformed note string.
    """
    text = ' '.join(line.strip() for line in desc_lines)
    text = remove_special_chars(text)
    text = split_camel_case(text)
    text = remove_net(text)
    text = handle_packs_and_qty(text)
    text = normalise_at_price(text)
    text = normalise_unit_spacing(text)
    text = normalise_each(text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = smart_title_case(text)
    return text


# ── Record Parsing ────────────────────────────────────────────────────────────

def split_trailing_price(line):
    """
    Split a line where a price is concatenated onto the end, with or without space.
    Handles 1- or 2-decimal prices. Two patterns tried in order:
      A. "...Pk <digit><price>" — single-digit pack size glued to price start
         e.g. "Brioche Buns Pk 46.50" → ["Brioche Buns Pk 4", "6.50"]
      B. General concat (no space between description and price)
         e.g. "@$10.90/kg5.47" → ["@$10.90/kg", "5.47"]
         e.g. "each10.0"       → ["each", "10.00"]
    """
    s = line.strip()
    m_pk = re.match(r'^(.*[Pp][Kk])\s+(\d)(\d+\.\d{1,2})$', s)
    if m_pk:
        return [f'{m_pk.group(1)} {m_pk.group(2)}', f'{float(m_pk.group(3)):.2f}']
    m = re.match(r'^(.*\D)(\d+\.\d{1,2})$', s)
    if m:
        return [m.group(1).strip(), f'{float(m.group(2)):.2f}']
    return [s]


def is_price_line(s):
    """True when the stripped string is a standalone price (1 or 2 decimal places)."""
    return bool(re.fullmatch(r'-?\d+\.\d{1,2}', s.strip()))


def parse_records(lines):
    """
    Segment raw lines into records. Non-price lines accumulate as the
    description; a price line closes the record.
    Returns a list of (desc_lines, price_str) tuples.
    """
    records, current = [], []
    for raw in lines:
        for s in split_trailing_price(raw):
            if not s:
                continue
            if is_price_line(s):
                if current:
                    records.append((current[:], f'{float(s):.2f}'))
                current = []
            else:
                current.append(s)
    return records


def merge_discounts(records):
    """
    Records with a negative amount are treated as a discount applied to the
    immediately preceding record. Recalculates per-unit price when an
    'xN @$Yea' pattern is present in that record.
    """
    result = []
    for note, amt_str in records:
        amt = float(amt_str)
        if amt < 0 and result:
            prev_note, prev_amt_str = result[-1]
            new_total = float(prev_amt_str) + amt
            m = re.search(r'x(\d+)\s+@\$([\d.]+)ea', prev_note)
            if m:
                qty      = int(m.group(1))
                new_unit = new_total / qty
                new_note = re.sub(
                    r'x(\d+)\s+@\$[\d.]+ea',
                    f'x{qty} @${new_unit:.2f}ea',
                    prev_note
                )
                result[-1] = (new_note, f'{new_total:.2f}')
            else:
                result[-1] = (prev_note, f'{new_total:.2f}')
        else:
            result.append((note, amt_str))
    return result


def combine_duplicates(records):
    """
    Combine consecutive records with identical notes into one line,
    annotated with combined quantity and per-unit price.
    """
    result, i = [], 0
    while i < len(records):
        note, amt_str = records[i]
        unit_price = float(amt_str)
        count = 1
        while i + count < len(records) and records[i + count][0] == note:
            count += 1
        if count > 1:
            total    = unit_price * count
            new_note = f'{note} x{count} @${unit_price:.2f}ea'
            result.append((new_note, f'{total:.2f}'))
        else:
            result.append((note, amt_str))
        i += count
    return result


# ── Output Formatting ─────────────────────────────────────────────────────────

def to_csv(records):
    rows = ['Note,Amount']
    rows += [f'"{note}",{amt}' for note, amt in records]
    return '\n'.join(rows) + '\n'


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    files = sorted(
        f for f in glob.glob(os.path.join(INPUT_DIR, '*.txt'))
        if os.path.basename(f).lower() != EXCLUDE.lower()
    )
    multi = len(files) > 1

    for input_path in files:
        fname       = os.path.basename(input_path)
        # Prefix output CSV with "Shopping Records " (mirrors battery_logs.py's
        # "Battery Logs ..." convention); [input_stem] = filename w/o ext.
        csv_name    = f'Shopping Records {os.path.splitext(fname)[0]}.csv'
        output_path = os.path.join(OUTPUT_DIR, csv_name)
        prefix      = f'[{fname}] ' if multi else ''

        if os.path.exists(output_path):
            print(f'{prefix}⛔STOPPED: "{csv_name}" already exists in output folder. Remove it and rerun.')
            continue

        with open(input_path, encoding='utf-8') as fh:
            raw_lines = fh.readlines()

        n       = len(raw_lines)
        records = parse_records(raw_lines)
        records = [(process_note(d), a) for d, a in records]
        records = merge_discounts(records)
        records = combine_duplicates(records)

        with open(output_path, 'w', encoding='utf-8') as fh:
            fh.write(to_csv(records))

        print(f'{prefix}Done. {n} records processed.')


if __name__ == '__main__':
    main()