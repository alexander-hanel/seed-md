-- Public WinAPIDB schema, combined for this SEED package; schema version 4.
-- Adapted from the reference project's schema assets; reusable specification material.
-- The importer must maintain FTS rows in the same transaction as source rows.
PRAGMA foreign_keys = ON;

CREATE TABLE build_info (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    source_path TEXT NOT NULL UNIQUE,
    source_sha256 TEXT NOT NULL,
    uid TEXT,                           -- Deliberately not UNIQUE: duplicates exist.
    title TEXT,
    kind TEXT,                          -- Preserve unknown/ambiguous kinds.
    primary_name TEXT,
    header TEXT,
    include_header TEXT,
    technology TEXT,
    library TEXT,
    dll TEXT,
    description TEXT,
    source_date TEXT,                   -- Documentary date, not import timestamp.
    published_url TEXT,                 -- Derived URL; not necessarily verified live.
    metadata_json TEXT NOT NULL,
    raw_markdown TEXT NOT NULL          -- Entire original document including YAML.
);
CREATE INDEX documents_uid ON documents(uid);
CREATE INDEX documents_header ON documents(header COLLATE NOCASE);
CREATE INDEX documents_technology_kind ON documents(technology COLLATE NOCASE, kind);
CREATE INDEX documents_kind ON documents(kind);

CREATE TABLE requirements (
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    value TEXT,                         -- NULL means unspecified, not unsupported.
    PRIMARY KEY (document_id, name)
);

CREATE TABLE aliases (
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    origin TEXT NOT NULL,               -- primary, api_name, f1_keywords, derived, etc.
    PRIMARY KEY (document_id, name, origin)
);
CREATE INDEX aliases_lookup ON aliases(normalized_name, document_id);

CREATE TABLE sections (
    id INTEGER PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    ordinal INTEGER NOT NULL,
    parent_id INTEGER REFERENCES sections(id) ON DELETE CASCADE,
    kind TEXT NOT NULL,                 -- description, parameter, field, remarks, etc.
    heading TEXT NOT NULL,
    line_start INTEGER NOT NULL,
    line_end INTEGER NOT NULL,
    markdown TEXT NOT NULL,
    plain_text TEXT NOT NULL,
    UNIQUE (document_id, ordinal)
);
CREATE INDEX sections_lookup ON sections(document_id, kind, ordinal);

CREATE TABLE members (
    id INTEGER PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    section_id INTEGER NOT NULL UNIQUE REFERENCES sections(id) ON DELETE CASCADE,
    kind TEXT NOT NULL CHECK (kind IN ('parameter', 'field', 'enum_constant')),
    name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    position INTEGER NOT NULL,          -- Documentation order, not verified ABI order.
    direction TEXT,
    optional INTEGER CHECK (optional IN (0, 1)), -- NULL = not explicitly documented.
    declared_type TEXT,                 -- Extract only an explicit 'Type:' line.
    value_text TEXT                     -- Only explicit enum values; never inferred.
);
CREATE INDEX members_lookup ON members(document_id, normalized_name);
CREATE INDEX members_name ON members(normalized_name);
CREATE INDEX members_order ON members(document_id, kind, position);

CREATE TABLE links (
    id INTEGER PRIMARY KEY,
    source_document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    source_section_id INTEGER REFERENCES sections(id) ON DELETE SET NULL,
    source_line INTEGER,
    label TEXT,
    raw_target TEXT NOT NULL,
    normalized_target TEXT,
    fragment TEXT,
    target_document_id INTEGER REFERENCES documents(id) ON DELETE SET NULL,
    relation TEXT NOT NULL DEFAULT 'reference',
    resolution_status TEXT NOT NULL    -- local, external, missing, ambiguous, etc.
);
CREATE INDEX links_outgoing ON links(source_document_id, relation);
CREATE INDEX links_incoming ON links(target_document_id);
CREATE INDEX links_unresolved ON links(resolution_status);

CREATE TABLE diagnostics (
    id INTEGER PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    source_line INTEGER,
    code TEXT NOT NULL,
    detail TEXT NOT NULL
);

-- One search row per section/chunk. Keep exact symbol lookup in aliases.
-- Identifiers retain underscores; add spaced CamelCase aliases at ingestion.
CREATE VIRTUAL TABLE section_search USING fts5(
    document_id UNINDEXED,
    section_id UNINDEXED,
    symbol,
    title,
    heading,
    body,
    tokenize = 'unicode61 tokenchars ''_'''
);

CREATE TRIGGER sections_delete_search AFTER DELETE ON sections BEGIN
    DELETE FROM section_search WHERE section_id = old.id;
END;

-- Example exact lookup (:name is normalized by the application).
-- SELECT DISTINCT d.id, d.uid, d.title, d.source_path
-- FROM aliases AS a JOIN documents AS d ON d.id = a.document_id
-- WHERE a.normalized_name = :name;

-- Example prose search (:query is a safely constructed FTS expression).
-- SELECT document_id, section_id, snippet(section_search, 5, '', '', ' … ', 32)
-- FROM section_search
-- WHERE section_search MATCH :query
-- ORDER BY bm25(section_search, 0, 0, 8, 5, 3, 1)
-- LIMIT :limit;

CREATE TABLE corpora(id INTEGER PRIMARY KEY, key TEXT UNIQUE NOT NULL, kind TEXT NOT NULL, source_root TEXT NOT NULL, revision TEXT, metadata_json TEXT NOT NULL);
CREATE TABLE source_files(id INTEGER PRIMARY KEY, corpus_id INTEGER NOT NULL REFERENCES corpora(id), path TEXT NOT NULL, sha256 TEXT NOT NULL, encoding TEXT NOT NULL, raw BLOB NOT NULL, status TEXT NOT NULL DEFAULT 'pending', UNIQUE(corpus_id,path));
CREATE INDEX source_files_hash ON source_files(sha256);
CREATE TABLE extraction_diagnostics(id INTEGER PRIMARY KEY,file_id INTEGER REFERENCES source_files(id),line INTEGER,code TEXT NOT NULL,detail TEXT NOT NULL);
CREATE TABLE source_includes(file_id INTEGER REFERENCES source_files(id),target_file_id INTEGER REFERENCES source_files(id),line INTEGER,raw_target TEXT,status TEXT NOT NULL);
ALTER TABLE documents ADD COLUMN corpus_id INTEGER REFERENCES corpora(id);
ALTER TABLE documents ADD COLUMN file_id INTEGER REFERENCES source_files(id);
ALTER TABLE documents ADD COLUMN source_map_json TEXT;
ALTER TABLE documents ADD COLUMN expanded_markdown TEXT;
CREATE INDEX documents_corpus ON documents(corpus_id);
CREATE TABLE link_candidates(link_id INTEGER REFERENCES links(id),document_id INTEGER REFERENCES documents(id),PRIMARY KEY(link_id,document_id));
CREATE TABLE declarations(id INTEGER PRIMARY KEY,file_id INTEGER NOT NULL REFERENCES source_files(id),name TEXT NOT NULL,qualified_name TEXT NOT NULL,normalized_name TEXT NOT NULL,kind TEXT NOT NULL,language TEXT NOT NULL,line_start INTEGER NOT NULL,line_end INTEGER NOT NULL,byte_start INTEGER NOT NULL,byte_end INTEGER NOT NULL,signature TEXT NOT NULL,details_json TEXT NOT NULL,conditions_json TEXT NOT NULL,method TEXT NOT NULL,status TEXT NOT NULL);
CREATE INDEX declarations_name ON declarations(normalized_name);
CREATE INDEX declarations_file ON declarations(file_id);
CREATE TABLE document_declarations(document_id INTEGER REFERENCES documents(id),declaration_id INTEGER REFERENCES declarations(id),status TEXT NOT NULL,evidence_json TEXT NOT NULL,PRIMARY KEY(document_id,declaration_id));
CREATE INDEX document_declarations_reverse ON document_declarations(declaration_id);
CREATE TABLE sample_regions(id INTEGER PRIMARY KEY,file_id INTEGER NOT NULL REFERENCES source_files(id),name TEXT NOT NULL,line_start INTEGER NOT NULL,line_end INTEGER NOT NULL,byte_start INTEGER NOT NULL,byte_end INTEGER NOT NULL,language TEXT NOT NULL);
CREATE INDEX sample_regions_file ON sample_regions(file_id);
CREATE TABLE sample_projects(id INTEGER PRIMARY KEY,file_id INTEGER NOT NULL REFERENCES source_files(id),details_json TEXT NOT NULL);
CREATE TABLE usages(id INTEGER PRIMARY KEY,file_id INTEGER NOT NULL REFERENCES source_files(id),region_id INTEGER REFERENCES sample_regions(id),name TEXT NOT NULL,qualified_name TEXT,kind TEXT NOT NULL,line INTEGER NOT NULL,column_number INTEGER NOT NULL,conditions_json TEXT NOT NULL,status TEXT NOT NULL,evidence_json TEXT NOT NULL,candidate_set_id INTEGER NOT NULL REFERENCES candidate_sets(id));
CREATE INDEX usages_name ON usages(name);
CREATE INDEX usages_region ON usages(region_id);
CREATE VIRTUAL TABLE source_search USING fts5(file_id UNINDEXED,region_id UNINDEXED,kind UNINDEXED,name,body,tokenize='unicode61 tokenchars ''_''');

CREATE INDEX links_section ON links(source_section_id);
CREATE TABLE sample_project_files(project_id INTEGER REFERENCES sample_projects(id),file_id INTEGER REFERENCES source_files(id),evidence TEXT NOT NULL,PRIMARY KEY(project_id,file_id));
CREATE INDEX sample_project_files_source ON sample_project_files(file_id);

CREATE TABLE document_assets(document_id INTEGER NOT NULL REFERENCES documents(id),file_id INTEGER NOT NULL REFERENCES source_files(id),role TEXT NOT NULL,PRIMARY KEY(document_id,file_id));
CREATE INDEX document_assets_file ON document_assets(file_id);
ALTER TABLE sample_regions ADD COLUMN kind TEXT NOT NULL DEFAULT 'routine';
CREATE TABLE document_redirects(corpus_id INTEGER NOT NULL REFERENCES corpora(id),source_path TEXT NOT NULL,target TEXT NOT NULL,file_id INTEGER NOT NULL REFERENCES source_files(id),PRIMARY KEY(corpus_id,source_path));

-- Identical evidence-based target sets are stored once, then shared by occurrences.
CREATE TABLE candidate_sets(id INTEGER PRIMARY KEY, signature TEXT NOT NULL UNIQUE);
CREATE TABLE candidate_documents(set_id INTEGER NOT NULL REFERENCES candidate_sets(id),document_id INTEGER NOT NULL REFERENCES documents(id),evidence TEXT NOT NULL,PRIMARY KEY(set_id,document_id));
CREATE TABLE candidate_declarations(set_id INTEGER NOT NULL REFERENCES candidate_sets(id),declaration_id INTEGER NOT NULL REFERENCES declarations(id),evidence TEXT NOT NULL,PRIMARY KEY(set_id,declaration_id));
CREATE INDEX usages_candidates ON usages(candidate_set_id);
CREATE INDEX candidate_documents_target ON candidate_documents(document_id);
CREATE INDEX candidate_declarations_target ON candidate_declarations(declaration_id);
CREATE VIEW usage_documents AS SELECT u.id AS usage_id,c.document_id,c.evidence FROM usages u JOIN candidate_documents c ON c.set_id=u.candidate_set_id;
CREATE VIEW usage_declarations AS SELECT u.id AS usage_id,c.declaration_id,c.evidence FROM usages u JOIN candidate_declarations c ON c.set_id=u.candidate_set_id;
