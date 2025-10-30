-- Inkdoodle DB schema (aligned with Neon DB structure)

-- Trigger function for updating timestamps
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Helper function to generate random code
CREATE OR REPLACE FUNCTION generate_random_code(prefix text, length integer DEFAULT 8)
RETURNS text AS $$
DECLARE
    chars text := 'abcdefghijklmnopqrstuvwxyz0123456789';
    result text := prefix;
    i integer;
BEGIN
    FOR i IN 1..length LOOP
        result := result || substr(chars, floor(random() * length(chars) + 1)::integer, 1);
    END LOOP;
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Trigger function for projects code assignment
CREATE OR REPLACE FUNCTION projects_assign_code()
RETURNS TRIGGER AS $$
DECLARE
    new_code text;
    retry_count integer := 0;
    max_retries integer := 5;
BEGIN
    WHILE retry_count < max_retries LOOP
        new_code := generate_random_code('pr_');
        BEGIN
            NEW.code := new_code;
            RETURN NEW;
        EXCEPTION WHEN unique_violation THEN
            retry_count := retry_count + 1;
        END;
    END LOOP;
    RAISE EXCEPTION 'Failed to generate unique project code after % attempts', max_retries;
END;
$$ LANGUAGE plpgsql;

-- Trigger function for chapters code assignment
CREATE OR REPLACE FUNCTION chapters_assign_code()
RETURNS TRIGGER AS $$
DECLARE
    new_code text;
    retry_count integer := 0;
    max_retries integer := 5;
BEGIN
    WHILE retry_count < max_retries LOOP
        new_code := generate_random_code('ch_');
        BEGIN
            NEW.code := new_code;
            -- Auto-assign number if not provided
            IF NEW.number IS NULL THEN
                SELECT COALESCE(MAX(number), 0) + 1
                INTO NEW.number
                FROM chapters
                WHERE project_id = NEW.project_id;
            END IF;
            RETURN NEW;
        EXCEPTION WHEN unique_violation THEN
            retry_count := retry_count + 1;
        END;
    END LOOP;
    RAISE EXCEPTION 'Failed to generate unique chapter code after % attempts', max_retries;
END;
$$ LANGUAGE plpgsql;

-- Trigger function for notes code assignment
CREATE OR REPLACE FUNCTION notes_assign_code()
RETURNS TRIGGER AS $$
DECLARE
    new_code text;
    retry_count integer := 0;
    max_retries integer := 5;
BEGIN
    WHILE retry_count < max_retries LOOP
        new_code := generate_random_code('no_');
        BEGIN
            NEW.code := new_code;
            -- Auto-assign number if not provided
            IF NEW.number IS NULL THEN
                SELECT COALESCE(MAX(number), 0) + 1
                INTO NEW.number
                FROM notes
                WHERE project_id = NEW.project_id;
            END IF;
            RETURN NEW;
        EXCEPTION WHEN unique_violation THEN
            retry_count := retry_count + 1;
        END;
    END LOOP;
    RAISE EXCEPTION 'Failed to generate unique note code after % attempts', max_retries;
END;
$$ LANGUAGE plpgsql;

-- Trigger function for refs code assignment
CREATE OR REPLACE FUNCTION refs_assign_code()
RETURNS TRIGGER AS $$
DECLARE
    new_code text;
    retry_count integer := 0;
    max_retries integer := 5;
BEGIN
    WHILE retry_count < max_retries LOOP
        new_code := generate_random_code('rf_');
        BEGIN
            NEW.code := new_code;
            -- Auto-assign number if not provided
            IF NEW.number IS NULL THEN
                SELECT COALESCE(MAX(number), 0) + 1
                INTO NEW.number
                FROM refs
                WHERE project_id = NEW.project_id;
            END IF;
            RETURN NEW;
        EXCEPTION WHEN unique_violation THEN
            retry_count := retry_count + 1;
        END;
    END LOOP;
    RAISE EXCEPTION 'Failed to generate unique reference code after % attempts', max_retries;
END;
$$ LANGUAGE plpgsql;

-- Creators table
CREATE TABLE creators (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email TEXT NOT NULL,
    display_name TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITHOUT TIME ZONE
);

CREATE UNIQUE INDEX creators_email_ci_idx ON creators (LOWER(email));
CREATE UNIQUE INDEX creators_email_key ON creators (email);

CREATE TRIGGER trg_creators_updated_at
    BEFORE UPDATE ON creators
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();

-- Projects table
CREATE TABLE projects (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title TEXT NOT NULL,
    creator_id INTEGER NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    code TEXT,
    FOREIGN KEY (creator_id) REFERENCES creators(id) ON DELETE CASCADE
);

CREATE INDEX idx_projects_created_at ON projects(created_at);
CREATE INDEX idx_projects_creator_id ON projects(creator_id);
CREATE UNIQUE INDEX projects_code_key ON projects(code);

CREATE TRIGGER trg_projects_assign_code
    BEFORE INSERT ON projects
    FOR EACH ROW
    EXECUTE FUNCTION projects_assign_code();

CREATE TRIGGER trg_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();

-- Chapters table
CREATE TABLE chapters (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id INTEGER NOT NULL,
    creator_id INTEGER NOT NULL,
    number INTEGER,
    title TEXT NOT NULL,
    content TEXT,
    status TEXT DEFAULT 'draft',
    summary TEXT,
    tags TEXT[],
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    code TEXT,
    word_goal INTEGER DEFAULT 0,
    FOREIGN KEY (creator_id) REFERENCES creators(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE(project_id, number)
);

CREATE INDEX idx_chapters_creator_id ON chapters(creator_id);
CREATE INDEX idx_chapters_project_id ON chapters(project_id);
CREATE INDEX idx_chapters_project_number ON chapters(project_id, number);
CREATE UNIQUE INDEX chapters_code_key ON chapters(code);

CREATE TRIGGER trg_chapters_assign_code
    BEFORE INSERT ON chapters
    FOR EACH ROW
    EXECUTE FUNCTION chapters_assign_code();

CREATE TRIGGER trg_chapters_updated_at
    BEFORE UPDATE ON chapters
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();

-- Notes table
CREATE TABLE notes (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id INTEGER NOT NULL,
    creator_id INTEGER NOT NULL,
    number INTEGER,
    title TEXT NOT NULL,
    content TEXT,
    tags TEXT[],
    category TEXT,
    pinned BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    code TEXT,
    FOREIGN KEY (creator_id) REFERENCES creators(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE(project_id, number)
);

CREATE INDEX idx_notes_creator_id ON notes(creator_id);
CREATE INDEX idx_notes_project_id ON notes(project_id);
CREATE INDEX idx_notes_project_number ON notes(project_id, number);
CREATE UNIQUE INDEX notes_code_key ON notes(code);

CREATE TRIGGER trg_notes_assign_code
    BEFORE INSERT ON notes
    FOR EACH ROW
    EXECUTE FUNCTION notes_assign_code();

CREATE TRIGGER trg_notes_updated_at
    BEFORE UPDATE ON notes
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();

-- References table
CREATE TABLE refs (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id INTEGER NOT NULL,
    creator_id INTEGER NOT NULL,
    number INTEGER,
    title TEXT NOT NULL,
    tags TEXT[],
    reference_type TEXT,
    summary TEXT,
    source_link TEXT,
    content TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    code TEXT,
    FOREIGN KEY (creator_id) REFERENCES creators(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE(project_id, number)
);

CREATE INDEX idx_refs_creator_id ON refs(creator_id);
CREATE INDEX idx_refs_project_id ON refs(project_id);
CREATE INDEX idx_refs_project_number ON refs(project_id, number);
CREATE UNIQUE INDEX refs_code_key ON refs(code);

CREATE TRIGGER trg_refs_assign_code
    BEFORE INSERT ON refs
    FOR EACH ROW
    EXECUTE FUNCTION refs_assign_code();

CREATE TRIGGER trg_refs_updated_at
    BEFORE UPDATE ON refs
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();

-- Preferences table
CREATE TABLE prefs (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TRIGGER prefs_set_updated_at
    BEFORE UPDATE ON prefs
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_at();

-- ID Counters table
CREATE TABLE id_counters (
    creator_id INTEGER NOT NULL,
    entity TEXT NOT NULL,
    next_no INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (creator_id, entity),
    FOREIGN KEY (creator_id) REFERENCES creators(id) ON DELETE CASCADE
);
