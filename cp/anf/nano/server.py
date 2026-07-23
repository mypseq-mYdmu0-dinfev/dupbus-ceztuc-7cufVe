#!/usr/bin/env python3
"""
ANF Nano — a deliberately tiny personal-finance / expense tracker.

WHY THIS SHAPE (baked in so the file explains itself, no outside docs needed):

- Standard library ONLY (http.server, sqlite3, json, csv, io, urllib, os,
  datetime). There is NOTHING to install: `python3 server.py` runs on a bare
  system Python. That makes the tool trivially portable and future-proof — no
  framework that can rot, no pip resolver that can break years from now.

- Data lives in ONE SQLite file (anf_nano.db) sitting right next to this
  script. The user OWNS that file outright: it can be copied, backed up, opened
  in any SQLite tool, or exported to CSV at any moment. This directly answers
  the top fear behind the whole project — a cloud vendor folding and taking
  years of financial history with it. Here, the vendor is a single local file.

- The interface is a plain JSON REST API. That is already the correct shape to
  later wrap in an MCP server so an AI agent can do bulk edits/imports on the
  same data — the batch-rename endpoint below is a first concrete taste of that.

So this "nano" build is not a throwaway: it is a faithful, working miniature of
the full vision, small enough to read end-to-end in one sitting.

NON-SCALABLE BY DESIGN: it loads every record at once, has no pagination, no
auth, no migrations, and seeds ~24 demo rows. That is intentional — it exists to
be evaluated, not to serve production traffic.

Run:  python3 server.py            (defaults to http://localhost:8731)
      python3 server.py --port 9000
"""

import argparse
import csv
import io
import json
import math
import os
import re
import sqlite3
from datetime import date, datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "anf_nano.db")
INDEX_PATH = os.path.join(HERE, "index.html")

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# Only these two columns may be batch-renamed. An allow-list (not a block-list)
# is used so an unexpected field name can NEVER reach the SQL layer.
RENAMABLE_FIELDS = ("category", "label")


# --------------------------------------------------------------------------- #
# Database
# --------------------------------------------------------------------------- #

def connect():
    """A fresh connection per request — ThreadingHTTPServer runs handlers on
    separate threads, and a single sqlite3 connection/cursor is NOT safe to
    share across them. Each request opens, uses, and closes its own."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = connect()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date        TEXT NOT NULL,
                payee       TEXT NOT NULL,
                note        TEXT,
                amount      REAL NOT NULL,
                label       TEXT,
                category    TEXT,
                created_at  TEXT NOT NULL
            )
            """
        )
        conn.commit()
        seed_if_empty(conn)
    finally:
        conn.close()


def seed_if_empty(conn):
    """Populate ~24 realistic AUD rows on first run so 'just run it' yields a
    live, populated app. Dates are computed relative to today, spread across the
    last ~6 weeks, so the demo always looks current."""
    count = conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
    if count:
        return

    today = date.today()

    def d(days_ago):
        return (today - timedelta(days=days_ago)).isoformat()

    # (days_ago, payee, note, amount, label, category)
    seed = [
        (1,  "Woolworths",          "Weekly groceries",           -142.85, "Groceries",  "Essentials"),
        (2,  "NSW Transport",       "Opal bus fare",                -4.40,  "Transport",  "Essentials"),
        (2,  "Campos Coffee",       "Flat white",                   -5.50,  "Dining",     "Discretionary"),
        (3,  "NSW Transport",       "Opal train fare",              -3.79,  "Transport",  "Essentials"),
        (4,  "Ampol",               "Fuel top-up",                 -78.20,  "Transport",  "Essentials"),
        (5,  "Chemist Warehouse",   "Vitamins and painkillers",    -32.15,  "Health",     "Essentials"),
        (6,  "Employer Pty Ltd",    "Fortnightly salary",         3120.00,  "Income",     "Salary"),
        (7,  "Woolworths",          "Groceries top-up",            -46.30,  "Groceries",  "Essentials"),
        (8,  "NSW Transport",       "Opal bus fare",                -4.40,  "Transport",  "Essentials"),
        (9,  "Netflix",             "Monthly subscription",        -25.99,  "Utilities",  "Bills"),
        (10, "AGL Energy",          "Electricity bill",           -184.60,  "Utilities",  "Bills"),
        (12, "The Local Cafe",      "Brunch with friends",         -38.00,  "Dining",     "Discretionary"),
        (13, "NSW Transport",       "Opal train fare",              -3.79,  "Transport",  "Essentials"),
        (14, "Coles",              "Groceries",                    -89.75,  "Groceries",  "Essentials"),
        (16, "Priceline Pharmacy",  "Prescription",                -18.90,  "Health",     "Essentials"),
        (18, "Employer Pty Ltd",    "Fortnightly salary",         3120.00,  "Income",     "Salary"),
        (19, "BP",                  "Fuel",                        -71.40,  "Transport",  "Essentials"),
        (21, "Woolworths",          "Weekly groceries",           -131.20,  "Groceries",  "Essentials"),
        (23, "NSW Transport",       "Opal bus fare",                -4.40,  "Transport",  "Essentials"),
        (26, "Optus",               "Mobile plan",                 -49.00,  "Utilities",  "Bills"),
        (29, "Guzman y Gomez",      "Dinner takeaway",             -21.50,  "Dining",     "Discretionary"),
        (33, "Sydney Water",        "Quarterly water bill",       -142.30,  "Utilities",  "Bills"),
        (37, "Freelance Client",    "Side project invoice",        640.00,  "Income",     "Salary"),
        (40, "Woolworths",          "Groceries",                   -97.65,  "Groceries",  "Essentials"),
        (42, "Kmart",              "Household items",              -54.80,  "Shopping",   "Discretionary"),
    ]

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    conn.executemany(
        "INSERT INTO records (date, payee, note, amount, label, category, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        [(d(days), payee, note, amount, label, cat, now)
         for (days, payee, note, amount, label, cat) in seed],
    )
    conn.commit()


def _csv_safe(value):
    """Neutralise CSV/formula injection: a text cell beginning with = + - @ (or a
    leading tab/CR) is treated as an active formula by Excel/Numbers on open. A
    single-user local tool still exports the headline 'own your data' file, and a
    payee/note pasted or bulk-imported later is untrusted, so prefix such cells
    with an apostrophe to force them to stay literal text."""
    s = "" if value is None else str(value)
    if s[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + s
    return s


def row_to_dict(row):
    return {
        "id": row["id"],
        "date": row["date"],
        "payee": row["payee"],
        "note": row["note"],
        "amount": row["amount"],
        "label": row["label"],
        "category": row["category"],
        "created_at": row["created_at"],
    }


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #

class BadRequest(Exception):
    """Raised for any invalid user input; the handler turns it into HTTP 400.
    Bad input must NEVER surface as a 500."""


def validate_record(body):
    """Validate + normalise an incoming record dict. Returns a clean tuple of
    (date, payee, note, amount, label, category). Raises BadRequest on anything
    invalid so the caller can return a 400 with a helpful message."""
    if not isinstance(body, dict):
        raise BadRequest("Request body must be a JSON object.")

    d = str(body.get("date", "")).strip()
    if not DATE_RE.match(d):
        raise BadRequest("Field 'date' must be in YYYY-MM-DD format.")
    try:
        datetime.strptime(d, "%Y-%m-%d")
    except ValueError:
        raise BadRequest("Field 'date' is not a valid calendar date.")

    payee = str(body.get("payee", "")).strip()
    if not payee:
        raise BadRequest("Field 'payee' is required.")

    amount_raw = body.get("amount", "")
    if isinstance(amount_raw, bool):  # bool is a subclass of int — reject it
        raise BadRequest("Field 'amount' must be a number.")
    try:
        amount = float(amount_raw)
    except (TypeError, ValueError):
        raise BadRequest("Field 'amount' must be a number.")
    # NaN/inf pass float() but cannot be stored (NOT NULL breaks on NaN) nor
    # serialised as valid JSON — reject them here so they surface as a clean 400,
    # never a 500 or an 'Infinity' token that poisons every JSON/CSV consumer.
    if not math.isfinite(amount):
        raise BadRequest("Field 'amount' must be a finite number.")

    note = str(body.get("note", "") or "").strip()
    label = str(body.get("label", "") or "").strip()
    category = str(body.get("category", "") or "").strip()

    return (d, payee, note, amount, label, category)


# --------------------------------------------------------------------------- #
# HTTP handler
# --------------------------------------------------------------------------- #

class Handler(BaseHTTPRequestHandler):
    server_version = "ANFNano/1.0"

    # -- low-level response helpers --------------------------------------- #

    def _send_json(self, obj, status=200):
        # allow_nan=False so a stray non-finite value can never leave the server
        # as the invalid-JSON token 'Infinity'/'NaN' (defence-in-depth; validation
        # already rejects these on the way in).
        payload = json.dumps(obj, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _send_400(self, message):
        self._send_json({"error": message}, status=400)

    def _send_404(self):
        self._send_json({"error": "Not found."}, status=404)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        if not raw:
            raise BadRequest("Request body is empty; expected JSON.")
        try:
            return json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            raise BadRequest("Request body is not valid JSON.")

    def log_message(self, fmt, *args):
        # Compact one-line request log.
        print("  %s - %s" % (self.address_string(), fmt % args))

    # -- routing ---------------------------------------------------------- #

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            return self._serve_index()
        if path == "/api/records":
            return self._get_records(parse_qs(parsed.query))
        if path == "/api/summary":
            return self._get_summary()
        if path == "/api/export.csv":
            return self._export_csv()
        if path.startswith("/api/"):
            return self._send_404()
        return self._send_404()

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            if path == "/api/records":
                return self._create_record()
            if path == "/api/batch-rename":
                return self._batch_rename()
        except BadRequest as exc:
            return self._send_400(str(exc))
        if path.startswith("/api/"):
            return self._send_404()
        return self._send_404()

    def do_PUT(self):
        path = urlparse(self.path).path
        rec_id = self._record_id_from_path(path)
        if rec_id is None:
            return self._send_404()
        try:
            return self._update_record(rec_id)
        except BadRequest as exc:
            return self._send_400(str(exc))

    def do_DELETE(self):
        path = urlparse(self.path).path
        rec_id = self._record_id_from_path(path)
        if rec_id is None:
            return self._send_404()
        return self._delete_record(rec_id)

    @staticmethod
    def _record_id_from_path(path):
        m = re.match(r"^/api/records/(\d+)$", path)
        return int(m.group(1)) if m else None

    # -- endpoints -------------------------------------------------------- #

    def _serve_index(self):
        try:
            with open(INDEX_PATH, "rb") as f:
                body = f.read()
        except OSError:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"index.html not found")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _get_records(self, query):
        q_values = query.get("q") or []
        q = (q_values[0] if q_values else "").strip()
        conn = connect()
        try:
            if q:
                # Parameterised LIKE — the search term is a bound '?' value,
                # never string-interpolated into the SQL. '%' wraps the bound
                # value in Python, not in the query text.
                like = "%" + q + "%"
                rows = conn.execute(
                    "SELECT * FROM records "
                    "WHERE payee LIKE ? OR note LIKE ? OR label LIKE ? OR category LIKE ? "
                    "ORDER BY date DESC, id DESC",
                    (like, like, like, like),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM records ORDER BY date DESC, id DESC"
                ).fetchall()
            self._send_json([row_to_dict(r) for r in rows])
        finally:
            conn.close()

    def _create_record(self):
        body = self._read_json_body()
        d, payee, note, amount, label, category = validate_record(body)
        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        conn = connect()
        try:
            cur = conn.execute(
                "INSERT INTO records (date, payee, note, amount, label, category, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (d, payee, note, amount, label, category, now),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM records WHERE id = ?", (cur.lastrowid,)
            ).fetchone()
            self._send_json(row_to_dict(row), status=201)
        finally:
            conn.close()

    def _update_record(self, rec_id):
        body = self._read_json_body()
        d, payee, note, amount, label, category = validate_record(body)
        conn = connect()
        try:
            exists = conn.execute(
                "SELECT id FROM records WHERE id = ?", (rec_id,)
            ).fetchone()
            if not exists:
                return self._send_404()
            conn.execute(
                "UPDATE records SET date = ?, payee = ?, note = ?, amount = ?, "
                "label = ?, category = ? WHERE id = ?",
                (d, payee, note, amount, label, category, rec_id),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM records WHERE id = ?", (rec_id,)
            ).fetchone()
            self._send_json(row_to_dict(row))
        finally:
            conn.close()

    def _delete_record(self, rec_id):
        conn = connect()
        try:
            cur = conn.execute("DELETE FROM records WHERE id = ?", (rec_id,))
            conn.commit()
            if cur.rowcount == 0:
                return self._send_404()
            self._send_json({"ok": True})
        finally:
            conn.close()

    def _batch_rename(self):
        body = self._read_json_body()
        if not isinstance(body, dict):
            raise BadRequest("Request body must be a JSON object.")
        field = str(body.get("field", "")).strip()
        # Allow-list gate: reject anything that is not exactly 'category' or
        # 'label' BEFORE the value ever touches SQL. The column name is then one
        # of two trusted literals, never user text.
        if field not in RENAMABLE_FIELDS:
            raise BadRequest("Field must be exactly 'category' or 'label'.")
        from_val = str(body.get("from", "")).strip()
        to_val = str(body.get("to", "")).strip()
        if not from_val:
            raise BadRequest("Field 'from' is required.")
        if not to_val:
            raise BadRequest("Field 'to' is required.")

        # `field` is a validated literal from RENAMABLE_FIELDS, so this f-string
        # only ever inserts 'category' or 'label'. The user-supplied values stay
        # bound as '?' parameters.
        sql = f"UPDATE records SET {field} = ? WHERE {field} = ?"
        conn = connect()
        try:
            cur = conn.execute(sql, (to_val, from_val))
            conn.commit()
            self._send_json({"updated": cur.rowcount})
        finally:
            conn.close()

    def _get_summary(self):
        conn = connect()
        try:
            row = conn.execute(
                "SELECT "
                "  COUNT(*) AS count, "
                "  COALESCE(SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END), 0) AS income, "
                "  COALESCE(SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END), 0) AS expense, "
                "  COALESCE(SUM(amount), 0) AS net "
                "FROM records"
            ).fetchone()
            self._send_json({
                "count": row["count"],
                "income": round(row["income"], 2),
                "expense": round(row["expense"], 2),
                "net": round(row["net"], 2),
            })
        finally:
            conn.close()

    def _export_csv(self):
        conn = connect()
        try:
            rows = conn.execute(
                "SELECT * FROM records ORDER BY date DESC, id DESC"
            ).fetchall()
        finally:
            conn.close()

        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["Date", "Payee", "Note", "Amount", "Label", "Category"])
        for r in rows:
            # Amount is a server-formatted numeric literal (safe); the four free-text
            # fields are user-supplied, so pass them through _csv_safe.
            writer.writerow([_csv_safe(r["date"]), _csv_safe(r["payee"]),
                             _csv_safe(r["note"]), f"{r['amount']:.2f}",
                             _csv_safe(r["label"]), _csv_safe(r["category"])])
        payload = buf.getvalue().encode("utf-8")

        stamp = date.today().isoformat()
        self.send_response(200)
        self.send_header("Content-Type", "text/csv; charset=utf-8")
        self.send_header("Content-Disposition",
                         f'attachment; filename="anf_nano_export_{stamp}.csv"')
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

def main():
    parser = argparse.ArgumentParser(description="ANF Nano expense tracker (stdlib-only).")
    parser.add_argument("--port", type=int, default=8731,
                        help="Port to serve on (default: 8731).")
    args = parser.parse_args()

    init_db()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = f"http://localhost:{args.port}"
    print("ANF Nano is running.")
    print(f"  Open:     {url}")
    print(f"  Database: {DB_PATH}")
    print("  Stop:     Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down. Your data is safe in anf_nano.db.")
        server.server_close()


if __name__ == "__main__":
    main()
