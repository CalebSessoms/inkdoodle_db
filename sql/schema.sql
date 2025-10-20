-- Inkdoodle DB schema (aligned with Ink-Doodle app)

CREATE TABLE creators (
    id              SERIAL PRIMARY KEY,
    email           TEXT UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    display_name    TEXT NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW(),
    is_active       BOOLEAN DEFAULT TRUE
);

CREATE TABLE projects (
    id          SERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    creator_id  INTEGER REFERENCES creators(id) ON DELETE CASCADE,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE chapters (
    id          SERIAL PRIMARY KEY,
    project_id  INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    creator_id  INTEGER REFERENCES creators(id) ON DELETE CASCADE,
    number      INTEGER,
    title       TEXT NOT NULL,
    content     TEXT,
    status      TEXT DEFAULT 'draft',
    summary     TEXT,
    tags        TEXT[],
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE notes (
    id          SERIAL PRIMARY KEY,
    project_id  INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    creator_id  INTEGER REFERENCES creators(id) ON DELETE CASCADE,
    number      INTEGER,
    title       TEXT NOT NULL,
    content     TEXT,
    tags        TEXT[],
    category    TEXT,
    pinned      BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE refs (
    id          SERIAL PRIMARY KEY,
    project_id  INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    creator_id  INTEGER REFERENCES creators(id) ON DELETE CASCADE,
    number      INTEGER,
    title       TEXT NOT NULL,
    tags        TEXT[],
    type        TEXT,
    summary     TEXT,
    link        TEXT,
    content     TEXT,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);
