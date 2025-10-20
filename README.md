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
