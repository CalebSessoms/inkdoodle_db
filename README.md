# InkDoodle DB (backend-only)

This repository contains the **database management scripts** for the InkDoodle project.
The **InkDoodle app** will remain app-focused; all **database access, creation, updates,
and maintenance** are performed here via Python CLI scripts (PowerShell-friendly).

## What’s here

* **inkdb/** – small Python package with the Neon Postgres connection helper
* **cli/** – command-line scripts (create/list/update/delete)
* `.env` (ignored): contains the Neon `DATABASE_URL` with SSL

## Technology

* Postgres (hosted on **Neon**, free tier)
* Python 3.14, `pg8000`, `python-dotenv`

## Usage (from repo root)

1. Create a `.env` file in this folder with:

   ```
   DATABASE_URL=postgresql://<user>:<pass>@<host>/<db>?sslmode=require&channel_binding=require
   ```

2. Run any script, e.g.:

   ```powershell
   python .\cli\list_works.py
   python .\cli\create_work.py
   python .\cli\add_chapter.py
   python .\cli\add_note.py
   python .\cli\add_ref.py
   ```

> Note: Direct DB access is **not** exposed to app users or creators. This repo is the
> canonical place where DB schema and data are managed.
