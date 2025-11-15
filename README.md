# InkDoodle Database (Backend Companion)

This repository holds the PostgreSQL schema, trigger/functions, and backend utilities that power the Ink‑Doodle desktop app's data model. It is both a standalone toolset for managing creators/projects/entries and the authoritative reference for the Electron app's IPC→SQL contract.

Short version:
- The DB contains creators, projects, chapters, notes, refs, lore, and a small `prefs` store (JSONB).
- The desktop app talks to the DB via IPC handlers in `src/main/*` (main process). The integration is currently "local-first":
  - Local JSON files are authoritative on the desktop. The app only writes to the remote DB when an explicit uploader runs (logout/upload or manual triggers).
  - Automatic DB→local imports are disabled by default; imports are handled explicitly via `db.load.fullLoad()` if desired.

---

## What’s in this repo

- SQL schema, triggers, and helper scripts (in `sql/` and `scripts/`).
- CLI utilities for creating/updating records and resetting schema (`scripts/`).
- A small set of tests / helpers for local development (`test_connection.py`).

## Key design decisions

- Local-first (desktop): local project JSON files are canonical. Remote DB writes are explicit and controlled.
- Deterministic public `code` fields are generated server-side by triggers (e.g., `PRJ-0001-000001`).
- Soft- and hard- delete behaviors are tracked and will be coordinated with the sync queue in a later iteration.

---

## App ↔ DB integration (current IPC surface)

The Electron app uses a thin IPC bridge implemented in the desktop repository. The important handlers the app currently uses or exposes are:

- `db:ping` — quick connectivity + server version check.
- `prefs:getWorkspacePath` — returns the workspace/projects root stored in `prefs`.
- `prefs:setWorkspacePath` — upserts `{ path }` into `prefs(key='workspace_root')`.
- `prefs:get` / `prefs:set` — generic key/value store used for `ui_prefs`, `auth_user`, and similar blobs.
- `auth:login` — login by email (returns `ok` and schedules a background `fullLoad()` to optionally create local project files).
- `auth:logout` — performs local->DB upload (uploader) and clears local project/workspace files; the app now also calls this automatically on quit when a user is logged in.

- Backend helpers (TypeScript/main): recent updates added basic lore support into the main-process helpers used by IPC flows:
  - `src/main/db.query.ts` exposes a `getProjectLore(projectCode)` helper to fetch lore rows for a given project.
  - `src/main/db.format.ts` includes local lore field constants and logic to map DB payloads into local on-disk lore shapes used by the renderer/uploader.
  - `src/main/db.load.ts` was extended to write per-item `lore/` JSON files during `fullLoad()` so DB→local imports emit canonical per-item lore files.
  - Per-field debug logging was added to assist tracing missing or mismatched lore fields across DB→local→renderer flows.

Notes on behavior and safety:
- DB→local automatic writes are intentionally disabled to keep the user's local files safe. `fullLoad()` exists as an explicit operation that will create local project folders when invoked (and is used at login only when desired).
- The uploader is implemented in `src/main/db.upload.ts`. It reads local projects, upserts project rows, streams child rows (chapters/notes/refs,lore) using mutating iterators (getNextChapter/getNextNote/getNextRef/getNextLore), and performs a verification pass to compare local vs DB counts. Lore upload support and mapping conventions were added to the uploader and format helpers; runtime verification in some environments is pending due to ESM/module resolution issues encountered during dry-runs.
- `performLogout()` (exposed by the main IPC module) is invoked during `auth:logout` and by the main process before quit to ensure users are logged out and local files cleaned up.

---

## Schema summary (as used by the app)

The production schema used by the app includes the following tables (high level):

- `creators` — id, email, display_name, password_hash, is_active, created_at, updated_at
- `projects` — id, code, title, creator_id, created_at, updated_at
- `chapters` — id, code, project_id, creator_id, number, title, content, status, summary, tags, created_at, updated_at
- `notes` — id, code, project_id, creator_id, number, title, content, tags, category, pinned, created_at, updated_at
- `refs` — id, code, project_id, creator_id, number, title, tags, type, summary, link, content, created_at, updated_at
- `lore` — id, code, project_id, creator_id, number, title, content, summary, tags, lore_kind, entry1name, entry1content, entry2name, entry2content, entry3name, entry3content, entry4name, entry4content, created_at, updated_at
- `prefs` — key (PK), value (jsonb), updated_at

There are helper objects/functions for generating stable public `code` values and for maintaining `updated_at` timestamps via triggers.

---

## Useful SQL snippets

Prefs (workspace root):
```sql
SELECT value->>'path' AS path FROM prefs WHERE key='workspace_root';
```

Basic prefs upsert:
```sql
INSERT INTO prefs(key, value)
VALUES ('workspace_root', jsonb_build_object('path', $1))
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = now();
```

Simple project / chapter queries (read-only examples):
```sql
SELECT id, code, title FROM projects ORDER BY id LIMIT 10;
SELECT id, code, project_id, number, title FROM chapters ORDER BY project_id, number NULLS LAST, id LIMIT 20;
```

---

## Running locally / dev setup

Requirements

- Python 3.10+
- PostgreSQL connection (Neon or local Postgres)
- `python-dotenv`, `pg8000` or `psycopg2-binary` (see `requirements.txt`)

Quick start

```powershell
# clone and set up environment
git clone https://github.com/CalebSessoms/inkdoodle_db.git
cd inkdoodle_db
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# add a DATABASE_URL (example using pg8000 + sslmode)
$env:DATABASE_URL = 'postgresql+pg8000://user:password@host/dbname?sslmode=require'

# create/reset schema
python .\scripts\reset_db.py

# quick connection test
python .\test_connection.py
```

If you want the desktop app to talk to your local DB instances, set the same `DATABASE_URL` for the app's environment and run the Electron app from the repo root (use the app's README for start instructions).

---

## Troubleshooting & notes

- SSL required (Neon): include `?sslmode=require` in `DATABASE_URL`.
- If codes are missing on insert, re-run `reset_db.py` to ensure triggers/functions are installed.
- Use `python .\scripts\show_schema.py` to inspect the installed schema.

Runtime integration notes (desktop app):
- The desktop app writes a global debug log (workspace debug.log) which is invaluable when troubleshooting upload/save/load flows. Watch for `auth:login`, `db.load:fullLoad`, `db.format:translateDbToLocal` (per-field logs for lore mapping), `db.upload`, and `performLogout` messages.
- The uploader performs verification checks (local vs DB counts) and emits `conflicts` in the summary; use that to detect silent mismatches.

---

## Next steps (roadmap) Same as the app roadmap

1. Getting the ui setup for the lore and world building elements
2. Planning out the formatting (local and db) for the lore elements including mapping between the two
3. Getting the local opperations fully hooked up to handle the new lore fields
4. Hooking up the db for lore elements
5. Adding in links between different lore elements. Links are going to be limitless, cascading, and double sided. eg there are going to be no limits for number of links, deleting a linked element will removing any links other elements had with it, and links are two sided linking x with y will also link y with x.
6. Adding a visualization of these lore/world building elements. Would consist of a relationship web with drag drop editting. Editting the elements and their respective links could theoretically happen in this new view mod. Possibility of a slider so it would act like a timeline for characters, worlds, etc etc possibly tied to chapters. eg move the slider to chapter one oh these characcters are the ones present move the slider to chapter 5 oh this character has died these other characters have gotten married and so are linked etc etc. Honestly so many features that could be implemented might remain a ongoing project for some time to come.
7. Timeline visualization save/load to database integration. The timeline system currently saves local JSON files (`timeline.json`) and will be extended to support database persistence for cross-device synchronization and backup.

---

## Author

Caleb Sessoms — Database companion for the Ink‑Doodle project
GitHub: https://github.com/CalebSessoms/inkdoodle_db
Email: calebsessoms@outlook.com

---

✅ Status: DB & IPC plumbing tested locally with prefs/ping and uploader flows.  
🔧 Next: Add IPC CRUD endpoints and local sync queue support.