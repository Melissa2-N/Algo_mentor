-- Schema for the Socratic algorithm tutor
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- Curriculum knowledge base (RAG chunks)
-- ============================================================
CREATE TABLE IF NOT EXISTS kb_chunks (
    id           BIGSERIAL PRIMARY KEY,
    concept      TEXT NOT NULL,                 -- e.g. "variables", "for_loop"
    level        INT  NOT NULL CHECK (level BETWEEN 1 AND 4),
    language     TEXT NOT NULL,                 -- python | c | javascript | java | universal
    title        TEXT NOT NULL,
    content      TEXT NOT NULL,                 -- theory / analogy / example text
    metadata     JSONB NOT NULL DEFAULT '{}',   -- {"language": "python", "level": 1, "kind": "example"}
    embedding    vector(1024) NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_kb_chunks_embedding
    ON kb_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_kb_chunks_metadata
    ON kb_chunks USING gin (metadata);

-- ============================================================
-- Curriculum skill tree (universal, language-independent)
-- ============================================================
CREATE TABLE IF NOT EXISTS skills (
    id            SERIAL PRIMARY KEY,
    slug          TEXT NOT NULL UNIQUE,          -- e.g. "variables", "for_loop"
    title         TEXT NOT NULL,
    level         INT  NOT NULL CHECK (level BETWEEN 1 AND 4),
    description   TEXT NOT NULL,
    prerequisites TEXT[] NOT NULL DEFAULT '{}'   -- slugs of prerequisite skills
);

-- ============================================================
-- Student profile & tracking
-- ============================================================
CREATE TABLE IF NOT EXISTS students (
    id            SERIAL PRIMARY KEY,
    display_name  TEXT NOT NULL,
    language      TEXT NOT NULL DEFAULT 'python'
                  CHECK (language IN ('python','c','javascript','java')),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS student_skills (
    student_id   INT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    skill_slug   TEXT NOT NULL REFERENCES skills(slug),
    validated    BOOLEAN NOT NULL DEFAULT false,
    validated_at TIMESTAMPTZ,
    -- How the skill was acquired : 'validated_by_test' (sandbox tests) or
    -- 'auto_declared' (start-level shortcut, upgrades to validated_by_test
    -- once the tests pass)
    status       TEXT,
    attempts     INT NOT NULL DEFAULT 0,
    PRIMARY KEY (student_id, skill_slug)
);

-- Recurring errors ("notions fragiles"): off-by-one, infinite loops, etc.
CREATE TABLE IF NOT EXISTS error_events (
    id          BIGSERIAL PRIMARY KEY,
    student_id  INT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    skill_slug  TEXT,
    error_kind  TEXT NOT NULL,   -- off_by_one | infinite_loop | type_error | syntax_error |
                                 -- index_error | runtime_error | logic_error | compile_error | other
    detail      TEXT NOT NULL DEFAULT '',
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_error_events_student
    ON error_events (student_id, occurred_at DESC);

-- Conversation stage per (student, skill) : discovery | practicing | awaiting_confirmation
CREATE TABLE IF NOT EXISTS student_stages (
    student_id  INT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    skill_slug  TEXT NOT NULL REFERENCES skills(slug),
    stage       TEXT NOT NULL CHECK (stage IN ('discovery','practicing','awaiting_confirmation')),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (student_id, skill_slug)
);

-- Conversation history (light memory of the tutoring loop)
CREATE TABLE IF NOT EXISTS chat_messages (
    id         BIGSERIAL PRIMARY KEY,
    student_id INT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    role       TEXT NOT NULL CHECK (role IN ('user','tutor','system')),
    content    TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- Seed the universal skill tree (4 levels)
-- ============================================================
INSERT INTO skills (slug, title, level, description, prerequisites) VALUES
-- Level 1 : logic & basics
('variables',        'Variables & affectation',      1, 'Stocker et nommer une valeur', '{}'),
('types',            'Types de base',                1, 'Entiers, flottants, booléens, chaînes', '{variables}'),
('conditions',       'Conditions (si/sinon)',        1, 'Prendre des décisions selon une valeur', '{types}'),
('while_loop',       'Boucle tant que',              1, 'Répéter tant qu''une condition est vraie', '{conditions}'),
('for_loop',         'Boucle pour',                  1, 'Répéter un nombre connu de fois', '{while_loop}'),
('functions',        'Fonctions',                    1, 'Factoriser du code réutilisable', '{for_loop}'),
('scope',            'Portée des variables',         1, 'Variables locales vs globales', '{functions}'),
-- Level 2 : linear data structures
('arrays',           'Tableaux / listes',            2, 'Collections indexées', '{for_loop}'),
('strings',          'Chaînes de caractères',        2, 'Parcours et manipulation de texte', '{arrays}'),
('dictionaries',     'Dictionnaires / hash tables',  2, 'Associations clé -> valeur', '{arrays}'),
('stacks_queues',    'Piles & files',                2, 'LIFO et FIFO', '{arrays}'),
-- Level 3 : intermediate algorithms
('binary_search',    'Recherche dichotomique',       3, 'Chercher dans un tableau trié en O(log n)', '{arrays}'),
('sorting',          'Tris élémentaires',            3, 'Tri par sélection, insertion, bulles', '{arrays}'),
('recursion',        'Récursivité',                  3, 'Fonctions qui s''appellent, cas de base', '{functions}'),
('complexity',       'Notions de complexité',        3, 'O(1), O(n), O(n^2), O(log n)', '{binary_search,sorting,recursion}'),
-- Level 4 : design & autonomy
('modular_design',   'Découpage modulaire',          4, 'Découper un problème en modules', '{functions,recursion}'),
('error_handling',   'Gestion d''erreurs',           4, 'Exceptions et entrées invalides', '{modular_design}'),
('file_io',          'Lecture/écriture de fichiers', 4, 'Persistance simple de données', '{error_handling}'),
('mini_project',     'Mini-projet complet',          4, 'Assembler tout dans un vrai programme', '{file_io}')
ON CONFLICT (slug) DO NOTHING;
