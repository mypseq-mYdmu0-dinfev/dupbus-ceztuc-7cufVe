# ANF Nano

A deliberately tiny personal-finance / expense tracker — a concrete, working miniature you can run, click, and evaluate in one sitting.

## What It Is

A single-user expense log: a table of transactions (date, payee, note, amount, label, category) with live search, add / edit / delete, a batch-rename tool, a CSV export, and a running income / expense / net summary. It ships pre-seeded with about two dozen realistic AUD records so it is populated the moment you open it.

## How to Run

You need only a system Python 3 — nothing to install.

```
python3 server.py
```

Then open:

```
http://localhost:8731
```

To use a different port:

```
python3 server.py --port 9000
```

Stop the server with `Ctrl+C`. On first run it creates and seeds `anf_nano.db` automatically; on later runs it reuses whatever is already there.

## Features

- **Records table** — date, payee, note, amount (expenses in the Arancio Xanto red, income in teal), label, and category, with per-row Edit and Delete.
- **Live search** — filter as you type across payee, note, label, and category.
- **Add a record** — a simple form; expenses are negative, income positive.
- **Edit a record** — a small modal for quick corrections.
- **Batch rename** — pick Category or Label, type a From and a To, and rename every matching record in one action. This is the concrete answer to re-editing the same label or category on every imported row one at a time.
- **Export CSV** — download every record as a spreadsheet-ready file. This is the concrete answer to "own your data, leave anytime".
- **Summary strip** — count, total income, total expense, and net, in AUD.
- **Dark mode** — a toggle that follows your system theme and remembers your choice.

## Stack and Rationale

- **Backend** — one file, `server.py`, using only the Python 3 standard library (`http.server`, `sqlite3`, `json`, `csv`, and friends). Standard-library-only means there is nothing to install and nothing that can rot: it runs anywhere a bare Python does. Every database call uses parameterised SQL, so user input is never spliced into a query.
- **Data** — one SQLite file, `anf_nano.db`, sitting next to the server. You own that file outright: copy it, back it up, open it in any SQLite tool, or export it to CSV whenever you like. This directly answers the top fear behind the whole project — a cloud vendor folding and taking years of financial history with it. Here, the "vendor" is a single local file you control. (The `.db` is git-ignored and never committed.)
- **Frontend** — one file, `index.html`, with all CSS and JavaScript inlined and zero external requests, so it runs fully offline. It talks to the backend over a plain JSON REST API.
- **Why a REST API** — a JSON REST interface is already the right shape to later wrap in an MCP server, so an AI agent can do bulk edits and imports on the same data. The batch-rename endpoint is a first taste of that direction.

So this nano build is not a throwaway: it is a faithful, working miniature of the full vision.

## API Reference

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Serves the app |
| GET | `/api/records?q=TEXT` | List records (newest first); `q` filters across payee / note / label / category |
| POST | `/api/records` | Create a record from a JSON body |
| PUT | `/api/records/{id}` | Update a record |
| DELETE | `/api/records/{id}` | Delete a record |
| POST | `/api/batch-rename` | Body `{field, from, to}` — rename across all matching records (`field` must be `category` or `label`) |
| GET | `/api/summary` | `{count, income, expense, net}` |
| GET | `/api/export.csv` | Download all records as CSV |

## This Is a Nano Prototype — Non-Scalable by Design

This build loads every record at once, has no pagination, no accounts, no authentication, and no migrations, and it seeds about two dozen demo rows. That is intentional. It exists to be a small, honest, end-to-end demonstration of the core idea — not to serve production traffic or large datasets. Its job is to make the direction tangible enough to judge.
