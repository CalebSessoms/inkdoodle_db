# InkDoodle Database (Backend Companion)

This repository serves as the **database and backend utility layer** for the [Ink-Doodle App](https://github.com/CalebSessoms/ink-doodle) project.  
Where the main Ink-Doodle app focuses on **creative writing and worldbuilding**, this project manages the **structured data** — creators, projects, chapters, notes, and references — using a PostgreSQL database (currently hosted via **Neon**).

---

## Current Purpose

At this stage, the system is a **foundational database** intended to:
- Provide a clean, normalized backend schema.
- Allow CLI-based management of creators, projects, chapters, notes, and references.
- Serve as a **stand-alone testbed** for Ink-Doodle’s future data layer.

**What’s already wired in Postgres**
- **Code generators & triggers** for public `code` fields (e.g., `PRJ-0001-000123`).
- **`updated_at` auto-update triggers** on row change.
- Helpful **indexes** (e.g., `(project_id)`, `(project_id, number)`).
- **`prefs`** table for app prefs (JSONB).

---

## Current App Integration Status

The **Ink-Doodle desktop app** (Electron) is beginning to use this DB via IPC from its main process.

**Live endpoints used by the app right now:**
- `db:ping` — connectivity + server version (debug only).
- `prefs:getWorkspacePath` — reads `prefs.workspace_root` (`value->>'path'`).
- `prefs:setWorkspacePath` — upserts JSON `{ "path": "<abs path>" }` into `prefs(key='workspace_root')`.
- `prefs:set` / `prefs:get` for `ui_prefs` — stores current appearance settings (`mode`, `theme`, `bg`, `bgOpacity`, `bgBlur`, `editorDim`).

**Next planned IPC handlers (already specced):**
- `projects:*`, `chapters:*`, `notes:*`, `refs:*` (list/create/update/delete)

This README tracks the DB-side shape expected by those IPC calls.

---

## Schema Overview (App-Used Columns)

**creators**  
`id (PK)`, `email (unique, not null)`, `password_hash (not null)`, `display_name (not null)`,  
`is_active (bool default true)`, `created_at`, `updated_at`

**projects**  
`id (PK)`, `code (TEXT unique, auto via trigger)`, `title (not null)`, `creator_id (FK not null)`,  
`created_at`, `updated_at`  
Indexes: `(creator_id)`

**chapters**  
`id (PK)`, `code (unique, auto)`, `project_id (FK not null)`, `creator_id (FK not null)`,  
`number (int)`, `title (not null)`, `content (text)`, `status (text)`, `summary (text)`, `tags (text[])`,  
`created_at`, `updated_at`  
Indexes: `(project_id)`, `(creator_id)`, `(project_id, number)`

**notes**  
`id (PK)`, `code (unique, auto)`, `project_id (FK not null)`, `creator_id (FK not null)`,  
`number (int)`, `title (not null)`, `content (text)`, `tags (text[])`, `category (text)`,  
`pinned (bool default false)`, `created_at`, `updated_at`

**refs**  
`id (PK)`, `code (unique, auto)`, `project_id (FK not null)`, `creator_id (FK not null)`,  
`number (int)`, `title (not null)`, `tags (text[])`, `type (text)`, `summary (text)`,  
`link (text)`, `content (text)`, `created_at`, `updated_at`

**prefs** (app-level key/value store)  
`key (PK text)`, `value (jsonb)`, `updated_at (timestamp default now)`

**Code generation components**  
- Table: `id_counters (creator_id, entity, next_no)`  
- Function: `next_entity_code(entity, creator_id)` → yields `PRJ-<creator 4d>-<serial 6d>` (and `CHP-`, `NT-`, `RF-` accordingly)  
- Triggers: set `code` on insert; update `updated_at` on changes.

---

## IPC-to-SQL Reference (for App Developers)

**prefs:getWorkspacePath**
```sql
SELECT value->>'path' AS path
FROM prefs
WHERE key = 'workspace_root'
LIMIT 1;
```

**prefs:setWorkspacePath**
```sql
INSERT INTO prefs(key, value)
VALUES ('workspace_root', jsonb_build_object('path', $1))
ON CONFLICT (key)
DO UPDATE SET value = EXCLUDED.value, updated_at = now();
```

**prefs:set (ui_prefs)**
```sql
INSERT INTO prefs(key, value)
VALUES ('ui_prefs', $1::jsonb)
ON CONFLICT (key)
DO UPDATE SET value = EXCLUDED.value, updated_at = now();
```

*Project/entry endpoints (planned)* map to straight-forward `SELECT/INSERT/UPDATE/DELETE` on `projects`, `chapters`, `notes`, `refs`, with `code` set by triggers and `updated_at` managed automatically.

---

## Future Complexity — Lore & Relationship Model

Ink-Doodle’s long-term vision involves an **interconnected “lore web”**, where characters, locations, events, and items will each form graph-like relationships.  
That system will require a **hybrid model** combining relational and non-relational design:

- **Relational layer** (PostgreSQL): structured data (chapters, timelines, creators, projects, revisions).  
- **Graph/relationship layer** (likely Neo4j or pgvector): dynamic entity-to-entity connections (who met who, where, when, how).  
- **Caching / indexing layer** (SQLite or Redis): local performance layer for the desktop Ink-Doodle app.

This repo will eventually manage **entity mapping, multi-table joins**, and the **link metadata** that allows one note or reference to connect to multiple other entries dynamically.  
It will also track **version control of lore data**, so writers can branch, merge, or roll back portions of their universe history.

---

### Big Steps

1. **Local sync groundwork (offline-first prep)**
   - Extend the app’s local project file to include per-entry `rev`, `deleted_at`, and a project-level `sync` block with `device_id`, `last_sync_at`, and a persistent **change queue**.
   - Every create/update/delete in the app enqueues a compact record; entries use **soft delete** (`deleted_at`) instead of immediate removal.
   - No network calls yet—just make all changes explicit and durable for future syncing.

2. **API skeleton (local dev)**
   - Spin up a small service (FastAPI or Express) with endpoints:
     - `POST /auth/*` (login/refresh)
     - `GET /projects/{id}/bundle` (download a project snapshot)
     - `POST /sync` (upload local queued changes; return server deltas).
   - Back the service with this Postgres schema and code-generation triggers.

3. **Auth UI + secure token storage**
   - Add sign-in to the app; store tokens securely (OS keychain/Keytar).
   - Centralize authenticated HTTP via a `fetchJson` helper with auto-retry/backoff.

4. **Sync client loop**
   - Implement `syncNow()` in the app:
     - Send queued changes with `device_id` and last known `rev`s.
     - Apply server replies (upserts, soft deletes), bump `rev`, clear queue items on success.

5. **Conflict handling (MVP)**
   - Field-level last-write-wins for most fields; for chapter `body`, present a simple “Keep mine / Keep server / Compare” dialog.
   - Mark conflicted entries with a lightweight “Needs review” flag.

6. **Nice-to-haves**
   - Cloud search/export endpoints; auto-sync toggle; status indicator; structured error logs.

---

## Troubleshooting

- **SSL required (Neon):** ensure your `DATABASE_URL` includes `?sslmode=require`.  
- **Driver choice:** repo supports `pg8000` (pure Python) and `psycopg2-binary`; either works.  
- **Resetting schema:** `python .\scripts\reset_db.py` will (re)create tables, triggers, and counters.  
- **Codes not appearing:** make sure triggers are installed; re-run the reset script.  
- **Cannot connect:** test with `python .\test_connection.py` and verify env is loaded.

---

## Setup

**Requirements**
- Python 3.10+
- PostgreSQL connection (Neon used here)
- `python-dotenv`, `pg8000`, `psycopg2-binary` (installed via `requirements.txt`)

**Steps**
```bash
# clone and set up environment
git clone https://github.com/CalebSessoms/inkdoodle_db.git
cd inkdoodle_db
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# add Neon or local connection string
echo "DATABASE_URL=postgresql+pg8000://user:password@host/dbname?sslmode=require" > .env

# build or reset schema
python .\scripts\reset_db.py

# (optional) show current schema summary
python .\scripts\show_schema.py

# (optional) basic connection test
python .\test_connection.py
```

**Quick psql checks (optional)**
```sql
-- prefs workspace root
SELECT value->>'path' AS path FROM prefs WHERE key='workspace_root';

-- ui_prefs blob (renderer writes this)
SELECT value FROM prefs WHERE key='ui_prefs';

-- sample projects/chapter view
SELECT id, code, title FROM projects ORDER BY id LIMIT 10;
SELECT id, code, project_id, number, title FROM chapters ORDER BY project_id, number NULLS LAST, id LIMIT 10;
```

---

## Author
Caleb Sessoms  
Database companion for the Ink-Doodle project  
GitHub: [https://github.com/CalebSessoms/inkdoodle_db](https://github.com/CalebSessoms/inkdoodle_db)
For access/connection to the db or other requests please feel free to reach out to me at calebsessome@outlook.com

---

✅ *Status:* Database connected to live Electron app (prefs & ping verified)  
🔧 *Next:* Add project/entry synchronization IPCs and local queue integration.
