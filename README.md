# InkDoodle Database (Backend Companion)

This repository serves as the **database and backend utility layer** for the [Ink-Doodle App](https://github.com/CalebSessoms/ink-doodle) project.  
Where the main Ink-Doodle app focuses on **creative writing and worldbuilding**, this project manages the **structured data** — creators, projects, chapters, notes, and references — using a PostgreSQL database (currently hosted via **Neon**).

---

## Current Purpose

At this stage, the system is a **foundational database** intended to:
- Provide a clean, normalized backend schema.
- Allow CLI-based management of creators, projects, chapters, notes, and references.
- Serve as a **stand-alone testbed** for Ink-Doodle’s future data layer.

You can create, read, update, and delete every major entity through Python CLI scripts found under the `cli/` directory.

> **Note:** This database is intentionally kept simple for now — relational depth, version history, and multi-link entity structures will come later once the Ink-Doodle app evolves beyond local storage.

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

### Step 1: Local Sync Groundwork (brief)

**Why:** prepares the desktop app to sync later without redesigning the data model.

**App-side additions (saved in the project JSON):**
- Per entry: `rev` (monotonic integer), `deleted_at` (ISO string or `null`).
- Project-level `sync` block:
  ```json
  {
    "sync": {
      "device_id": "dev_xxx",
      "last_sync_at": null,
      "queue": []
    }
  }
Change queue items (example shape):

json
Copy code
{
  "id": "uuid",
  "ts": "2025-10-13T15:40:00Z",
  "op": "create|update|delete",
  "entity": "chapter|note|reference",
  "local_id": "entry-local-id",
  "rev": 4,
  "payload": { "title": "New title" }
}
Semantics:

create: set rev = 1, enqueue minimal payload.

update: increment rev, enqueue only changed fields (or full object if simpler to start).

delete: increment rev, set deleted_at, enqueue a delete op.

Persist the queue inside the project file so it survives restarts.

Step 2 will introduce the API (/bundle, /sync) that consumes these queue items and returns authoritative deltas sourced from this Postgres schema.

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
