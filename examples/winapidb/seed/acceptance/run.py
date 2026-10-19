#!/usr/bin/env python3
"""Supplied black-box acceptance checks. No reference implementation is imported."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import time
import zipfile
from bounded import run as bounded_run
from reference import load_cases, check_relationships, verify_assets, check_database as check_reference_database, check_queries as check_reference_queries
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
HEADER_SUFFIXES = {".h", ".hpp", ".hxx", ".inl"}
GROUPS = [
    "TEST-DELIVERY", "TEST-ACQUIRE", "TEST-CLEAN", "TEST-DATA",
    "TEST-QUERY", "TEST-REFRESH", "TEST-PORTABLE", "TEST-FULL",
]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def json_write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def decode(raw):
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("cp1252", errors="replace")


@contextmanager
def open_db(path):
    connection = sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    try:
        yield connection
    finally:
        connection.close()


def scalar(db, sql, params=()):
    return db.execute(sql, params).fetchone()[0]


def safe_relative(value):
    p = Path(value)
    return bool(value) and not p.is_absolute() and ".." not in p.parts and "\\" not in value


def self_check():
    fixture = read_json(PACKAGE / "acceptance/fixtures.json")
    require(len(fixture["files"]) >= 20, "Missing fixture sources")
    for name, content in fixture["files"].items():
        require(safe_relative(name), "Unsafe fixture path")
        if isinstance(content, dict):
            bytes.fromhex(content["hex"])
        else:
            require(isinstance(content, str), "Invalid fixture text")
    full = read_json(PACKAGE / "sources.full.json")
    require(len(full["acquisition"]) == 6, "Full source scope changed")
    require({x["key"] for x in full["docs"]} == {"sdk", "ddi", "protocols"}, "Unexpected docs scope")
    schema = (PACKAGE / "contracts/schema.sql").read_text(encoding="utf-8")
    with sqlite3.connect(":memory:") as db:
        db.executescript(schema)
        require(scalar(db, "SELECT count(*) FROM sqlite_master WHERE name='source_search'") == 1,
                "Schema does not expose source FTS")
    verify_assets()
    return fixture


class Suite:
    def __init__(self, project, work, profile, timeout):
        self.project = project.resolve()
        self.work = work.resolve()
        self.profile = profile
        self.timeout = timeout
        require(self.project.is_dir(), "Project directory does not exist")
        require(not self.work.exists() or not any(self.work.iterdir()), "Work directory must be empty")
        require(not self.project.is_relative_to(self.work), "Work directory cannot contain the project")
        require(not self.work.is_relative_to(self.project), "Work directory must be separate from project")
        require(not self.work.is_relative_to(PACKAGE), "Work directory must be outside the seed package")
        self.work.mkdir(parents=True, exist_ok=True)
        self.results = []
        self.command_number = 0
        self.build_number = 0
        self.fixture = self_check()
        self.dbpath = self.work / "database.sqlite3"
        self.raw = self.work / "fixture-source"
        self.root = self.work / "acquired"
        self.cfg = self.fixture["config"]
        self.config_path = self.work / "fixture-config.json"

    def portable(self, value):
        if isinstance(value, str):
            for path, label in sorted(
                [(str(self.project), "PROJECT_ROOT"), (str(self.work), "TEST_WORKSPACE"),
                 (str(PACKAGE), "SEED_ROOT")], key=lambda item: -len(item[0])
            ):
                value = value.replace(path, label)
            return value
        if isinstance(value, list):
            return [self.portable(item) for item in value]
        if isinstance(value, dict):
            return {key: self.portable(item) for key, item in value.items()}
        return value

    def invoke(self, operation, arguments, success=True):
        if hasattr(self, "snapshot"):
            require(self.snapshot == {name: digest(self.project / name) for name in self.snapshot}, "Frozen source/dependency files changed")
        argv = self.interface["operations"][operation] + [str(item) for item in arguments]
        self.command_number += 1
        start = time.monotonic()
        policy = read_json(PACKAGE / "resource-policy.json")
        evidence = self.work / "commands" / f"{self.command_number:04}"
        deadline = min(self.timeout, policy["query_seconds"] if operation == "query" else policy["operation_seconds"])
        if operation == "build" and getattr(self, "in_full_build", False):
            deadline = min(self.timeout, policy["full_seconds"])
        execution = bounded_run(argv, self.project, evidence, deadline, policy["workspace_bytes"],
                                policy["command_output_bytes"], self.work, policy["database_bytes"])
        stdout = (evidence / "stdout.log").read_text(errors="replace") if (evidence / "stdout.log").exists() else ""
        stderr = (evidence / "stderr.log").read_text(errors="replace") if (evidence / "stderr.log").exists() else ""
        result = subprocess.CompletedProcess(argv, execution.get("returncode", -1), stdout, stderr)
        json_write(self.work / "commands" / f"{self.command_number:04}.json",
                   self.portable({"argv": argv, **execution, "stdout": stdout, "stderr": stderr}))
        require(execution["status"] != "stopped" and execution.get("returncode") is not None,
                f"{operation}: execution limit or launch failure; see command {self.command_number}")
        if hasattr(self, "snapshot"):
            require(self.snapshot == {name: digest(self.project / name) for name in self.snapshot}, "Operation modified frozen project")
        require((result.returncode == 0) == success,
                f"{operation}: unexpected exit {result.returncode}; see command {self.command_number}")
        try:
            value = json.loads(result.stdout)
        except json.JSONDecodeError as error:
            raise AssertionError(f"{operation}: stdout must be one JSON value") from error
        if not success:
            require(isinstance(value, dict) and "error" in value, "Failure lacks JSON error")
        return value

    def query(self, command, target=None, options=(), success=True, database=None):
        args = [command]
        if target is not None:
            args.append(str(target))
        args += ["--db", database or self.dbpath, *options]
        return self.invoke("query", args, success)

    def build(self, cfg=None, root=None, destination=None, stage="samples", success=True):
        self.build_number += 1
        config_path = self.work / f"build-config-{self.build_number}.json"
        json_write(config_path, cfg if cfg is not None else self.cfg)
        report_path = self.work / f"build-report-{self.build_number}.json"
        value = self.invoke("build", ["--config", config_path, "--root", root or self.root,
                                     "--db", destination or self.dbpath, "--through", stage,
                                     "--report", report_path], success)
        require(report_path.is_file(), "Build attempt did not retain its report")
        return value

    def delivery(self):
        for name in ("README.md", "DEPENDENCIES.md", "interface.json"):
            path = self.project / name
            require(path.is_file() and path.stat().st_size > 0, f"Missing deliverable: {name}")
        self.interface = read_json(self.project / "interface.json")
        for operation in ("acquire", "build", "validate", "query", "preflight"):
            prefix = self.interface["operations"].get(operation)
            require(isinstance(prefix, list) and prefix and all(isinstance(x, str) and x for x in prefix),
                    f"Invalid command prefix: {operation}")
            require(not any(Path(x).is_absolute() for x in prefix), "Published interface has an absolute path")
        source_files = self.interface.get("source_files", [])
        require(source_files, "No implementation source delivered")
        for name in source_files:
            require(safe_relative(name), "Unsafe implementation source path")
            path = (self.project / name).resolve()
            require(path.is_relative_to(self.project) and path.is_file() and path.stat().st_size,
                    f"Missing project source: {name}")

        dependency_files = self.interface.get("dependency_files", [])
        require(dependency_files, "Dependency lock/installed identity files must be inventoried")
        inventory = sorted(set(source_files + dependency_files + ["README.md", "DEPENDENCIES.md", "interface.json"]))
        for name in inventory:
            require(safe_relative(name) and (self.project/name).resolve().is_relative_to(self.project) and (self.project/name).is_file(), "Invalid snapshot file")
        self.snapshot = {name: digest(self.project/name) for name in inventory}
        self.snapshot_sha256 = hashlib.sha256(json.dumps(self.snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
        json_write(self.work / "project-snapshot.json", {"files": self.snapshot, "sha256": self.snapshot_sha256})

    def acquire(self):
        for name, content in self.fixture["files"].items():
            path = self.raw / name
            path.parent.mkdir(parents=True, exist_ok=True)
            raw = bytes.fromhex(content["hex"]) if isinstance(content, dict) else content.encode("utf-8")
            path.write_bytes(raw)
        inventory = [{"path": p.relative_to(self.raw / "headers").as_posix(), "sha256": digest(p)}
                     for p in sorted((self.raw / "headers/include").rglob("*"))
                     if p.is_file() and p.suffix.lower() in HEADER_SUFFIXES]
        json_write(self.raw / "headers/headers-complete.json", inventory)
        self.raw_identity = {p.relative_to(self.raw).as_posix(): digest(p)
                             for p in self.raw.rglob("*") if p.is_file()}
        json_write(self.config_path, self.cfg)
        bindings = self.work / "bindings.json"
        json_write(bindings, {"FIXTURE_SOURCE": str(self.raw)})
        report = self.work / "acquisition.json"
        value = self.invoke("acquire", ["--config", self.config_path, "--root", self.root,
                                        "--bindings", bindings, "--report", report])
        require(value["status"] == "complete" and value.get("sources"), "Acquisition did not complete")
        require(report.is_file(), "Acquisition report missing")
        for name, expected in self.raw_identity.items():
            require(digest(self.root / "inputs" / name) == expected, f"Acquisition changed {name}")
        bad_bindings = self.work / "missing-bindings.json"
        json_write(bad_bindings, {})
        self.invoke("acquire", ["--config", self.config_path, "--root", self.work / "missing-input",
                               "--bindings", bad_bindings, "--report", self.work / "missing-input.json"], False)
        archive = self.work / "fixture.nupkg"
        with zipfile.ZipFile(archive, "w") as zipped:
            zipped.writestr("seed.nuspec", "<package><metadata><id>Seed.Test.Headers</id>"
                            "<version>1.0.0</version></metadata></package>")
            zipped.writestr("include/api.h", "int Acquired(int x);\n")
            zipped.writestr("include/inline.inl", "inline int InlineAcquired() { return 1; }\n")
            zipped.writestr("LICENSE.txt", "Synthetic archive notice.\n")
            zipped.writestr("tools/unwanted.exe", b"not an executable; excluded fixture")
        package_cfg = {"acquisition": [{"id": "ARCHIVE", "kind": "nuget", "package": "Seed.Test.Headers",
                                       "version": "1.0.0", "destination": "package",
                                       "archive_binding": "HEADER_ARCHIVE"}],
                       "docs": [], "headers": [{"key": "archive-headers", "path": "package/extracted/include",
                           "package": "Seed.Test.Headers", "version": "1.0.0", "include_version": "1.0",
                           "manifest": "package/complete-manifest.json", "inventory": "package/headers-complete.json",
                           "inventory_root": "package/extracted"}], "samples": []}
        pcfg = self.work / "package-config.json"
        pbind = self.work / "package-bindings.json"
        json_write(pcfg, package_cfg)
        json_write(pbind, {"HEADER_ARCHIVE": str(archive)})
        package_root = self.work / "package-input"
        self.invoke("acquire", ["--config", pcfg, "--root", package_root, "--bindings", pbind,
                               "--report", self.work / "package-acquisition.json"])
        base = package_root / "package"
        manifest = read_json(base / "complete-manifest.json")
        require(manifest["archive_sha256"] == digest(archive), "Wrong archive hash")
        require(manifest["nuspec_identity_verified"] and manifest["zip_crc_verified"], "Archive not verified")
        require(manifest["package_id"] == "Seed.Test.Headers" and manifest["package_version"] == "1.0.0",
                "Package identity not retained")
        acquired = read_json(base / "headers-complete.json")
        require({r["path"] for r in acquired} == {"include/api.h", "include/inline.inl"}, "Incomplete header inventory")
        require(all(digest(base / "extracted" / r["path"]) == r["sha256"] for r in acquired), "Wrong extracted hash")
        require(not (base / "extracted/tools/unwanted.exe").exists(), "Unrequested binary extracted")
        require((base / "extracted/LICENSE.txt").is_file(), "Notice omitted")
        package_cfg["acquisition"][0]["version"] = "2.0.0"
        json_write(pcfg, package_cfg)
        rejected = self.work / "rejected-package"
        self.invoke("acquire", ["--config", pcfg, "--root", rejected, "--bindings", pbind,
                               "--report", self.work / "rejected-package.json"], False)
        require(not (rejected / "package/extracted/include/api.h").exists(), "Wrong package was published")

    def clean(self):
        require(not self.dbpath.exists(), "Clean build destination was already present")
        value = self.build()
        require(value["stage"] == "samples" and value["limited"] is False, "Wrong build scope")
        require(value["status"] in ("complete", "complete_with_warnings"), "No completed build")
        with open_db(self.dbpath) as db:
            expected = sqlite3.connect(":memory:")
            schema = (PACKAGE / "contracts/schema.sql").read_text(encoding="utf-8")
            expected.executescript(schema)
            for name in re.findall(r"CREATE (?:VIRTUAL )?TABLE (\w+)", schema):
                actual_columns = {tuple(r)[1:4] + (r["pk"],) for r in db.execute(f"PRAGMA table_info({name})")}
                expected_columns = {(r[1], r[2], r[3], r[5]) for r in expected.execute(f"PRAGMA table_info({name})")}
                require(expected_columns <= actual_columns, f"Public schema mismatch: {name}")
                expected_fk = {tuple(r)[2:8] for r in expected.execute(f"PRAGMA foreign_key_list({name})")}
                actual_fk = {tuple(r)[2:8] for r in db.execute(f"PRAGMA foreign_key_list({name})")}
                require(expected_fk <= actual_fk, f"Foreign keys missing: {name}")
                def unique_keys(connection):
                    keys = set()
                    for index in connection.execute(f"PRAGMA index_list({name})"):
                        if index[2]:
                            escaped = index[1].replace("'", "''")
                            keys.add(tuple(row[2] for row in connection.execute(f"PRAGMA index_info('{escaped}')")))
                    return keys
                require(unique_keys(expected) <= unique_keys(db), f"Unique constraints missing: {name}")
            expected.close()
            require(scalar(db, "SELECT value FROM build_info WHERE key='schema_version'") == "4", "Wrong schema version")
            report = json.loads(scalar(db, "SELECT value FROM build_info WHERE key='report'"))
            for key in ("status", "stage", "limited", "schema_version", "project_identity", "sources",
                        "counts", "coverage", "diagnostics", "validation", "started_at", "ended_at", "seconds"):
                require(key in report, f"Embedded report omits {key}")
            require(report["status"] == value["status"], "Embedded and external report disagree")
        require(self.invoke("validate", ["--db", self.dbpath])["status"] == "passed", "Validation failed")
        docs_db = self.work / "docs-only.sqlite3"
        self.build(destination=docs_db, stage="docs")
        with open_db(docs_db) as db:
            require(scalar(db, "SELECT count(*) FROM documents") > 0, "Docs stage empty")
            require(scalar(db, "SELECT count(*) FROM declarations") == 0, "Docs stage imported headers")
        headers_db = self.work / "headers-only.sqlite3"
        self.build(destination=headers_db, stage="headers")
        with open_db(headers_db) as db:
            require(scalar(db, "SELECT count(*) FROM declarations") > 0, "Header stage empty")
            require(scalar(db, "SELECT count(*) FROM usages") == 0, "Header stage imported samples")

    def audit(self, database, root, config):
        with open_db(database) as db:
            require(scalar(db, "PRAGMA integrity_check") == "ok", "SQLite integrity failure")
            require(not db.execute("PRAGMA foreign_key_check").fetchall(), "Foreign key failure")
            require(not scalar(db, "SELECT count(*) FROM source_files WHERE status='pending'"), "Pending files")
            for record in db.execute("SELECT path,raw,sha256 FROM source_files"):
                require(hashlib.sha256(record["raw"]).hexdigest() == record["sha256"], "Stored blob hash mismatch")
            require(scalar(db, "SELECT count(*) FROM section_search") ==
                    scalar(db, "SELECT count(*) FROM sections WHERE plain_text != ''"), "Section search count")
            require(not scalar(db, """SELECT count(*) FROM section_search f LEFT JOIN sections s ON s.id=f.section_id
                    WHERE s.id IS NULL OR f.document_id!=s.document_id OR f.body!=s.plain_text OR f.heading!=s.heading"""),
                    "Section search content mismatch")
            for kind in ("docs", "headers", "samples"):
                for cfg in config.get(kind, []):
                    base = (root / cfg["path"]).resolve()
                    require(base.is_dir(), f"Missing {cfg['key']}")
                    corpus = db.execute("SELECT * FROM corpora WHERE key=?", (cfg["key"],)).fetchone()
                    require(corpus is not None, f"Missing corpus {cfg['key']}")
                    require(not Path(corpus["source_root"]).is_absolute(), "Host path persisted in corpus")
                    if kind == "headers":
                        eligible = [p for p in base.rglob("*") if p.is_file() and p.suffix.lower() in HEADER_SUFFIXES]
                    elif kind == "samples" or cfg.get("include_assets"):
                        eligible = [p for p in base.rglob("*") if p.is_file() and ".git" not in p.relative_to(base).parts]
                    else:
                        candidates = base.glob(cfg["document_glob"]) if cfg.get("document_glob") else base.rglob("*.md")
                        eligible = [p for p in candidates if p.is_file() and
                                    not set(p.relative_to(base).parts) & {".git", "obj", "includes"}]
                    require(eligible, f"Empty selected corpus {cfg['key']}")
                    for path in eligible:
                        relative = path.relative_to(base).as_posix()
                        stored = db.execute("SELECT * FROM source_files WHERE corpus_id=? AND path=?",
                                            (corpus["id"], relative)).fetchone()
                        require(stored is not None, f"Missing source {cfg['key']}/{relative}")
                        require(stored["sha256"] == digest(path) and stored["raw"] == path.read_bytes(),
                                f"Source fidelity failure {cfg['key']}/{relative}")
                        if kind == "headers" or (kind == "samples" and stored["encoding"] != "binary"):
                            text = decode(stored["raw"])
                            search_kind = "header" if kind == "headers" else "sample_file"
                            search = db.execute("SELECT body FROM source_search WHERE file_id=? AND kind=?",
                                                (stored["id"], search_kind)).fetchall()
                            require(len(search) == 1 and search[0]["body"] == text, "Full source search mismatch")
                            encoded = text.encode("utf-8")
                            if kind == "headers":
                                for decl in db.execute("SELECT * FROM declarations WHERE file_id=?", (stored["id"],)):
                                    start, end = decl["byte_start"], decl["byte_end"]
                                    require(0 <= start < end <= len(encoded), "Invalid declaration byte span")
                                    require(encoded[start:end].decode("utf-8") == decl["signature"], "Invented signature")
                            else:
                                for region in db.execute("SELECT * FROM sample_regions WHERE file_id=?", (stored["id"],)):
                                    start, end = region["byte_start"], region["byte_end"]
                                    require(0 <= start <= end <= len(encoded), "Invalid sample byte span")
                        if kind == "docs" and path.suffix.lower() == ".md" and "includes" not in path.parts:
                            document = db.execute("SELECT * FROM documents WHERE file_id=?", (stored["id"],)).fetchone()
                            require(document is not None or
                                    (stored["status"] == "failed" and scalar(db,
                                     "SELECT count(*) FROM extraction_diagnostics WHERE file_id=?", (stored["id"],))),
                                    "Selected documentation silently omitted")
                            if document:
                                require(document["raw_markdown"] == decode(stored["raw"]), "Original Markdown altered")
                    if kind == "headers" and cfg.get("inventory"):
                        selected = {p.resolve() for p in eligible}
                        inventory = read_json(root / cfg["inventory"])
                        inventory_root = root / cfg["inventory_root"]
                        all_selected = {p.resolve() for header in config["headers"]
                                        if header.get("inventory") == cfg["inventory"]
                                        for p in (root / header["path"]).rglob("*")
                                        if p.is_file() and p.suffix.lower() in HEADER_SUFFIXES}
                        require(all((inventory_root / item["path"]).resolve() in all_selected for item in inventory),
                                "Header inventory has unconfigured files")
                        for item in inventory:
                            local = (inventory_root / item["path"]).resolve()
                            if local in selected:
                                require(digest(local) == item["sha256"], "Acquired header changed before full audit")
                    if kind == "docs":
                        require(scalar(db, "SELECT count(*) FROM documents WHERE corpus_id=?", (corpus["id"],)) > 0,
                                "Documentation corpus was not parsed")
                    if kind == "headers":
                        require(scalar(db, """SELECT count(*) FROM declarations d JOIN source_files f ON f.id=d.file_id
                                WHERE f.corpus_id=?""", (corpus["id"],)) > 0, "Header corpus has no declarations")
            for cfg in config.get("docs", []) + config.get("samples", []):
                if not cfg.get("repository"):
                    continue
                for notice in (root / cfg["repository"]).iterdir():
                    if notice.is_file() and notice.name.upper().startswith(("LICENSE", "NOTICE", "COPYING", "THIRDPARTY", "LEGAL")):
                        require(scalar(db, "SELECT count(*) FROM source_files WHERE sha256=?", (digest(notice),)) > 0,
                                f"Source notice omitted: {notice.name}")
            counts = json.loads(scalar(db, "SELECT value FROM build_info WHERE key='report'"))["counts"]
            public_tables = re.findall(r"CREATE (?:VIRTUAL )?TABLE\s+(\w+)", (PACKAGE / "contracts/schema.sql").read_text(), re.I)
            for table in public_tables:
                require(counts.get(table) == scalar(db, f"SELECT count(*) FROM {table}"), f"Wrong count for {table}")

    def data(self):
        self.audit(self.dbpath, self.root, self.cfg)
        with open_db(self.dbpath) as db:
            require(scalar(db, "SELECT count(*) FROM documents WHERE uid='NF:seed.Duplicate'") == 2, "Duplicate UID lost")
            bad = db.execute("""SELECT f.id,f.status FROM source_files f JOIN corpora c ON c.id=f.corpus_id
                              WHERE c.key='sdk' AND f.path='bad.md'""").fetchone()
            require(bad and bad["status"] == "failed", "Duplicate YAML keys not rejected")
            require(scalar(db, "SELECT count(*) FROM extraction_diagnostics WHERE file_id=?", (bad["id"],)) > 0,
                    "Malformed source lacks diagnostic")
            require(scalar(db, "SELECT count(*) FROM source_includes WHERE status='resolved'") > 0, "Includes not recorded")
            require(scalar(db, "SELECT count(*) FROM document_redirects") == 1, "Redirect metadata lost")
            require(scalar(db, "SELECT count(*) FROM links WHERE resolution_status='local'") >= 3, "Local links unresolved")
            require(scalar(db, "SELECT count(*) FROM links WHERE resolution_status='missing'") > 0, "Missing link invented")
            require(scalar(db, "SELECT count(*) FROM document_declarations") > 0, "No doc/declaration evidence")
            require(scalar(db, "SELECT count(*) FROM sample_project_files") >= 2, "Project/file associations missing")
            require(scalar(db, "SELECT count(*) FROM declarations WHERE name='SeedGlobal'") > 0, "Global declaration missing")
            require(scalar(db, "SELECT count(*) FROM declarations WHERE name='SeedForward'") > 0, "Forward type missing")
            require(scalar(db, "SELECT count(*) FROM source_files f JOIN corpora c ON c.id=f.corpus_id WHERE c.key='protocols'") == 2,
                    "Protocol source coverage wrong")

            relationship_failures = check_relationships(db)
            json_write(self.work / "relationship-cases.json", relationship_failures)
            require(not relationship_failures, "Candidate eligibility cases failed")
            reference_failures = check_reference_database(db)
            json_write(self.work / "reference-database.json", reference_failures)
            require(not reference_failures, "Source-backed compatibility cases failed; see reference-database.json")
            expected = read_json(PACKAGE / "expected-fields.json")
            for item in expected["documents"]:
                row = db.execute("SELECT * FROM documents WHERE source_path=?", (item["source_path"],)).fetchone()
                require(row is not None, "Expected document absent")
                for field, value in item["fields"].items():
                    require(row[field] == value, f"Field mapping: {item['source_path']}.{field}")
            for item in expected["members"]:
                row = db.execute("SELECT m.* FROM members m JOIN documents d ON d.id=m.document_id WHERE d.source_path=? AND m.name=?",
                                 (item["source_path"], item["name"])).fetchone()
                require(row is not None, "Expected member absent")
                for field, value in item["fields"].items():
                    require(row[field] == value, f"Member mapping: {item['name']}.{field}")
            external = db.execute("SELECT resolution_status,target_document_id FROM links WHERE raw_target LIKE 'https://unrelated.example/%'").fetchall()
            require(external and all(r[0] == "external" and r[1] is None for r in external), "External host falsely resolved locally")
            for view in ("usage_documents", "usage_declarations"):
                require(scalar(db, "SELECT type FROM sqlite_master WHERE name=?", (view,)) == "view", "Repeated memberships must be shared")
            repeated = db.execute("SELECT id,candidate_set_id FROM usages WHERE name='SeedRepeated'").fetchall()
            require(len(repeated) == 128, "Repeated occurrences lost")
            require(len({r[1] for r in repeated}) == 1, "Identical occurrences failed to share candidate set")
            set_id = repeated[0][1]
            require(scalar(db, "SELECT count(*) FROM declarations WHERE name='SeedRepeated'") == 128, "Repeated declaration alternatives lost")
            require(scalar(db, "SELECT count(*) FROM candidate_declarations WHERE set_id=?", (set_id,)) == 128, "Candidate set incomplete or duplicated")
            require(scalar(db, "SELECT count(*) FROM usage_declarations WHERE usage_id=?", (repeated[0][0],)) == 128, "Candidate view lost alternatives")
            require(self.dbpath.stat().st_size <= read_json(PACKAGE / "resource-policy.json")["fixture_database_bytes"], "Fixture storage budget exceeded")

    def queries(self):
        reference_failures = check_reference_queries(self.query)
        json_write(self.work / "reference-queries.json", reference_failures)
        require(not reference_failures, "Source-backed query cases failed; see reference-queries.json")
        before = digest(self.dbpath)
        lookup = self.query("lookup", "SeedCopy")
        require(lookup["documents"] and lookup["declarations"], "Lookup omitted document or declaration")
        require(len(self.query("lookup", "SeedDuplicate")["documents"]) == 2, "Ambiguity hidden")
        self.query("get", "SeedDuplicate", success=False)
        self.query("get", "SeedText", success=False)
        self.query("get", "MISSING_SEED_DOCUMENT", success=False)
        require(self.query("lookup", "MISSING_SEED_DOCUMENT") == {"documents": [], "declarations": []}, "Missing lookup")
        bundle = self.query("get", "sdk/group/nf-seed-seedcopy.md")
        require(bundle["source_map"] and bundle["sections"] and bundle["declarations"], "Incomplete document bundle")
        require(bundle["published_url"].endswith("/group/nf-seed-seedcopy"), "Publication route wrong")
        args = self.query("arguments", "ISeedDevice::Read")
        require([a["name"] for a in args] == ["value"], "Wrong COM parameters")
        require(args[0]["optional"] == 1 and args[0]["direction"] == "out" and args[0]["declared_type"] == "int*",
                "Parameter provenance wrong")
        require(any(s["heading"] == "STATUS_SEED_READY" for s in args[0]["descendants"]), "Nested status lost")
        require(self.query("members", "SeedCopy")[0]["name"] == "value", "Members missing")
        requirements = self.query("requirements", "IOCTL_SEED_QUERY")
        require(requirements["kmdf-ver"] == "1.0" and requirements["irql"] == "PASSIVE_LEVEL", "DDI requirements wrong")
        require(self.query("arguments", "IOCTL_SEED_QUERY") == [], "IOCTL arguments invented")
        require(self.query("sections", "IOCTL_SEED_QUERY", ["--kind", "input-buffer"]), "IOCTL input section missing")
        scalar_requirements = self.query("requirements", "SeedCopy")
        require(json.loads(scalar_requirements["dll"]) == ["seed-a.dll", "seed-b.dll"], "List requirement lost")
        require(scalar_requirements["target-min-winverclnt"] is None, "Unspecified requirement became false")
        require(any(x["resolution_status"] == "local" for x in self.query("related", "SeedCopy")), "Related links missing")
        require(self.query("declarations", "SeedCopy", ["--version", "1.0.0"]), "Versioned declaration missing")
        require(self.query("declarations", "SeedCopy", ["--version", "999"]) == [], "Version filter ignored")
        read_annotation = self.query("declarations", "SeedRead")
        require(len(read_annotation) == 1 and "__out_data_source(FILE)" in read_annotation[0]["signature"],
                "Data-source annotation suppressed a valid declaration")
        require(self.query("get", "SeedTextW")["primary_name"] == "SeedTextW", "A/W primary name collapsed to generic alias")
        conditional = self.query("declarations", "SeedConditional")
        require(conditional and "SEED_FEATURE" in json.dumps(conditional[0]["conditions"]), "Conditional evidence lost")
        com = self.query("declarations", "ISeedDevice::Read")
        require(com and "_Out_opt_" in com[0]["signature"], "SAL source spelling lost")
        examples = self.query("examples", "SeedCopy", ["--language", "c"])
        require(examples and "SeedCopy(1)" in examples[0]["source"]["text"], "C sample missing")
        require(examples[0]["targets"]["documents"] and examples[0]["targets"]["declarations"], "Usage targets missing")
        require(self.query("sample", examples[0]["region_id"])["items"], "Sample detail missing")
        repeated = self.query("examples", "SeedRepeated", ["--limit", "2"])
        require(len(repeated) == 2, "Top-level example limit")
        for item in repeated:
            targets = item["targets"]
            require(len(targets["declarations"]) == 2 and targets["declarations_total"] == 128 and targets["truncated"] is True,
                    "Nested candidate limit/count incorrect")
            require(len(item["source"]["text"]) <= 4096, "Unbounded source snippet")
        managed = self.query("examples", "SeedCopy", ["--language", "csharp"])
        require(managed and managed[0]["kind"] == "text_reference", "Managed text mislabeled as parsed C call")
        require(self.query("search", "violet orchard")["documents"], "Documentation search failed")
        require(self.query("search", "SeedOnly")["sources"], "Full source search failed")
        require(self.query("search", "NO_SEED_MATCH_92843") == {"documents": [], "sources": []}, "Unrelated search match")
        references = self.query("references", "SeedCopy")
        require(references and any("text" in r["evidence"].lower() for r in references), "Text reference evidence missing")
        self.query("files", "", ["--limit", "0"], success=False)
        files = self.query("files", "ICON.BIN", ["--corpus", "classic"])
        require(len(files) == 1 and files[0]["encoding"] == "binary", "Binary file discovery failed")
        self.binary_id = files[0]["file_id"]
        require(self.query("source", self.binary_id)["text"] is None, "Binary decoded as text")
        self.query("source", 99999999, success=False)
        source = self.query("source", bundle["file_id"])
        require("violet orchard" in source["text"], "Stored source text missing")
        limited = self.query("source", bundle["file_id"], ["--line-start", "1", "--line-end", "2"])
        require(limited["line_start"] == 1 and limited["line_end"] == 2, "Source line range ignored")
        protocol = self.query("get", "protocols/[MS-SEED].md")
        require(protocol["kind"] == "specification" and protocol["published_url"] is None,
                "Protocol identity or unverified URL handling wrong")
        require(self.query("diagnostics"), "Diagnostics missing")
        require(self.query("report")["limited"] is False, "Report scope wrong")
        exported = self.work / "export.bin"
        self.query("export", self.binary_id, ["--output", exported])
        require(exported.read_bytes() == bytes.fromhex(self.fixture["files"]["samples/icon.bin"]["hex"]), "Export changed bytes")
        self.query("export", self.binary_id, ["--output", exported], success=False)
        self.query("export", self.binary_id, ["--output", self.dbpath], success=False)
        require(digest(self.dbpath) == before, "Queries modified the database")

    def refresh(self):
        newdoc = self.root / "inputs/sdk/content/new.md"
        newdoc.write_text("---\nUID: NF:seed.SeedNew\ntitle: SeedNew function\napi_name: [SeedNew]\n---\n"
                          "## -description\nNewly added source evidence.\n", encoding="utf-8")
        self.build()
        require(self.query("lookup", "SeedNew")["documents"], "Successful refresh did not include new input")
        before = digest(self.dbpath)
        missing = json.loads(json.dumps(self.cfg))
        missing["docs"][0]["path"] = "missing-required-source"
        self.build(cfg=missing, success=False)
        require(digest(self.dbpath) == before, "Failed refresh replaced the accepted database")
        initial = self.work / "must-not-publish.sqlite3"
        self.build(cfg=missing, destination=initial, success=False)
        require(not initial.exists(), "Initial failed build published a database")
        empty = self.root / "empty-docs"
        empty.mkdir()
        invalid = json.loads(json.dumps(self.cfg))
        invalid["docs"].append({"key": "empty", "path": "empty-docs"})
        self.build(cfg=invalid, success=False)
        require(digest(self.dbpath) == before, "Invalid candidate replaced the accepted database")
        corrupt = self.work / "corrupt.sqlite3"
        shutil.copy2(self.dbpath, corrupt)
        with sqlite3.connect(corrupt) as db:
            db.execute("DELETE FROM source_search WHERE kind='header'")
        self.invoke("validate", ["--db", corrupt], False)
        header = self.root / "inputs/headers/include/api.h"
        header.write_text(header.read_text(encoding="utf-8") + "\nint SeedUnverified(void);\n", encoding="utf-8")
        self.build()
        require(self.query("declarations", "SeedUnverified") == [], "Quarantined header produced declarations")
        require(self.query("search", "SeedUnverified")["sources"], "Quarantined header became unsearchable")
        with open_db(self.dbpath) as db:
            row = db.execute("""SELECT f.id,f.status FROM source_files f JOIN corpora c ON c.id=f.corpus_id
                                WHERE c.key='fixture-headers' AND f.path='api.h'""").fetchone()
            require(row["status"] == "failed", "Inventory mismatch not quarantined")
            require(scalar(db, "SELECT count(*) FROM declarations WHERE file_id=?", (row["id"],)) == 0,
                    "Quarantined file retained declarations")
            require(scalar(db, "SELECT count(*) FROM extraction_diagnostics WHERE file_id=?", (row["id"],)) > 0,
                    "Quarantine has no diagnostic")
        require({p.relative_to(self.raw).as_posix(): digest(p) for p in self.raw.rglob("*") if p.is_file()}
                == self.raw_identity, "Acquisition or build modified original fixture inputs")

    def portable_query(self):
        self.root.rename(self.work / "retired-inputs")
        self.raw.rename(self.work / "retired-originals")
        relocated = self.work / "relocated"
        relocated.mkdir()
        moved = relocated / "reference.sqlite3"
        shutil.move(str(self.dbpath), moved)
        self.dbpath = moved
        require(self.query("get", "SeedCopy")["sections"], "Relocated document lookup failed")
        require(self.query("search", "violet orchard")["documents"], "Relocated search failed")
        require(self.query("references", "SeedOnly"), "Relocated raw references failed")
        binary = self.query("files", "icon.bin", ["--corpus", "classic"])[0]["file_id"]
        exported = relocated / "recovered.bin"
        self.query("export", binary, ["--output", exported])
        require(exported.read_bytes() == bytes.fromhex(self.fixture["files"]["samples/icon.bin"]["hex"]),
                "Source-free binary export failed")

    def full(self):
        cfg = read_json(PACKAGE / "sources.full.json")
        full_root = self.work / "full-inputs"
        acquisition_report = self.work / "full-acquisition.json"
        result = self.invoke("acquire", ["--config", PACKAGE / "sources.full.json", "--root", full_root,
                                         "--report", acquisition_report])
        require(result["status"] == "complete", "Full acquisition incomplete")
        identities = {item["id"]: item for item in result["sources"]}
        require(set(identities) == {item["id"] for item in cfg["acquisition"]}, "Full acquisition source omitted")
        selection = []
        for kind in ("docs", "headers", "samples"):
            for entry in cfg.get(kind, []):
                base = full_root / entry["path"]
                files = [f for f in base.rglob("*") if f.is_file() and not f.is_symlink() and ".git" not in f.parts]
                if kind == "headers": files = [f for f in files if f.suffix.lower() in HEADER_SUFFIXES]
                if kind == "docs": files = [f for f in files if f.suffix.lower() == ".md" and "includes" not in f.relative_to(base).parts]
                require(files, "No preflight input for " + entry["key"])
                ordered = sorted(files, key=lambda f: f.relative_to(base).as_posix())
                chosen = {max(ordered, key=lambda f: f.stat().st_size),
                          min(ordered, key=lambda f: hashlib.sha256(f.relative_to(base).as_posix().encode()).digest())}
                for extension in sorted({f.suffix.lower() for f in ordered})[:8]:
                    chosen.add(next(f for f in ordered if f.suffix.lower() == extension))
                selection.extend({"corpus": entry["key"], "path": f.relative_to(base).as_posix(), "sha256": digest(f)}
                                 for f in sorted(chosen))
        # Source-backed anchors supplement sampling; one easy span cannot hide a
        # missing required declaration elsewhere in a partially parsed header.
        selected_by_path = {(item["corpus"], item["path"]): item for item in selection}
        header_configs = {entry["key"]: entry for entry in cfg["headers"]}
        for case in load_cases():
            declaration = case["declaration"]
            key = (declaration["full_corpus"], declaration["source_path"])
            source = full_root / header_configs[key[0]]["path"] / key[1]
            require(source.is_file(), "Required compatibility header missing: " + key[1])
            item = selected_by_path.setdefault(key, {"corpus": key[0], "path": key[1], "sha256": digest(source)})
            item.setdefault("required_signatures", []).append(declaration["signature"])
        selection = [selected_by_path[key] for key in sorted(selected_by_path)]
        selection_path = self.work / "preflight-selection.json"
        json_write(selection_path, selection)
        preflight = self.invoke("preflight", ["--config", PACKAGE / "sources.full.json", "--root", full_root,
                                             "--selection", selection_path, "--report", self.work / "preflight.json"])
        require(preflight.get("status") == "passed" and preflight.get("project_identity") and preflight.get("dependency_identity"), "Preflight incomplete")
        require(preflight["project_identity"].get("snapshot_sha256") == self.snapshot_sha256, "Preflight producer digest mismatch")
        observed = {(r["corpus"], r["path"]): r for r in preflight["files"]}
        require(len(preflight["files"]) == len(selection) and set(observed) == {(r["corpus"],r["path"]) for r in selection}, "Preflight coverage mismatch")
        configs = {entry["key"]: (kind, entry) for kind in ("docs", "headers", "samples") for entry in cfg[kind]}
        for selected in selection:
            row = observed[selected["corpus"], selected["path"]]
            require(row["sha256"] == selected["sha256"] and row["status"] in ("complete", "partial"), "Preflight identity/status mismatch")
            kind, entry = configs[selected["corpus"]]
            source = full_root / entry["path"] / selected["path"]
            require(digest(source) == selected["sha256"], "Preflight modified source")
            if kind == "headers": require(row["spans"] or row["diagnostics"], "Empty header preflight claim")
            returned_signatures = {span["text"] for span in row["spans"]}
            require(all(signature in returned_signatures for signature in selected.get("required_signatures", [])),
                    "Preflight omitted a mandatory source-backed declaration")
            if row["spans"]:
                encoded = decode(source.read_bytes()).encode("utf-8")
                for span in row["spans"]:
                    a,b = span["byte_start"],span["byte_end"]
                    require(0 <= a < b <= len(encoded) and encoded[a:b].decode("utf-8") == span["text"], "Preflight fabricated span")
        self.in_full_build = True
        full_db = self.work / "full.sqlite3"
        result = self.build(cfg=cfg, root=full_root, destination=full_db)
        require(result["limited"] is False and result["stage"] == "samples", "Full build scope reduced")
        require(full_db.stat().st_size <= read_json(PACKAGE / "resource-policy.json")["database_bytes"], "Full database size budget exceeded")
        require(result.get("project_identity") == preflight["project_identity"] and result.get("dependency_identity") == preflight["dependency_identity"], "Producer changed after preflight")
        self.audit(full_db, full_root, cfg)
        require(self.invoke("validate", ["--db", full_db])["status"] == "passed", "Full validation failed")
        with open_db(full_db) as db:
            reference_failures = check_reference_database(db, profile="full")
            json_write(self.work / "full-reference-database.json", reference_failures)
            require(not reference_failures, "Full source-backed cases failed")
            require(scalar(db, "SELECT count(*) FROM usages") > 0, "Full samples produced no usage evidence")
            selector = scalar(db, "SELECT source_path FROM documents ORDER BY source_path LIMIT 1")
        require(self.query("get", selector, database=full_db)["source_path"] == selector, "Full query failed")
        reference_failures = check_reference_queries(lambda *args: self.query(*args, database=full_db), profile="full")
        json_write(self.work / "full-reference-queries.json", reference_failures)
        require(not reference_failures, "Full source-backed query cases failed")
        json_write(self.work / "full-artifact.json",
                   {"database": "full.sqlite3", "sha256": digest(full_db), "profile": "full"})

    def run(self):
        actions = [self.delivery, self.acquire, self.clean, self.data, self.queries,
                   self.refresh, self.portable_query, self.full]
        blocked = False
        for name, action in zip(GROUPS, actions):
            if name == "TEST-FULL" and self.profile != "full":
                self.results.append({"test": name, "result": "not_applicable",
                                     "reason": "Fixture checkpoint; full completion is not claimed."})
                continue
            if blocked:
                self.results.append({"test": name, "result": "not_run", "reason": "Earlier prerequisite failed."})
                continue
            started = time.monotonic()
            json_write(self.work / "acceptance-progress.json", {"running": name, "completed": self.results})
            try:
                action()
                outcome = {"test": name, "result": "pass"}
            except Exception as error:
                outcome = {"test": name, "result": "fail", "reason": f"{type(error).__name__}: {error}"}
                blocked = True
            outcome["seconds"] = round(time.monotonic() - started, 3)
            self.results.append(self.portable(outcome))
            json_write(self.work / "acceptance-progress.json", {"running": None, "completed": self.results})
            print(f"{name}: {outcome['result']}", flush=True)
        report = {"profile": self.profile,
                  "status": "failed" if blocked else "full_automated_checks_passed" if self.profile == "full"
                  else "fixture_checkpoint_passed",
                  "review": "not_performed_by_this_script", "generation_completion_claimed": False,
                  "results": self.results}
        json_write(self.work / "acceptance-report.json", report)
        return 1 if blocked else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-check", action="store_true", help="Check package assets without running a project")
    parser.add_argument("--project", type=Path)
    parser.add_argument("--work", type=Path)
    parser.add_argument("--trial", type=Path, help="Durable authorized-trial directory; required for full profile")
    parser.add_argument("--profile", choices=("fixtures", "full"), default="fixtures")
    parser.add_argument("--timeout", type=int, default=7200, help="Per-operation timeout in seconds")
    parser.add_argument("--supervised-full", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.self_check:
        self_check()
        print("Package assets are internally readable; no project was generated or executed.")
        return 0
    if args.project is None or args.work is None:
        parser.error("--project and --work are required unless --self-check is used")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if args.profile == "full" and args.trial is None:
        parser.error("--trial is required for full profile; reuse the authorized trial identity")
    if args.profile == "full" and not args.supervised_full:
        policy = read_json(PACKAGE / "resource-policy.json")
        evidence = args.trial.resolve() / "full-attempt"
        command = [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:], "--supervised-full"]
        result = bounded_run(command, Path.cwd(), evidence, policy["full_seconds"], policy["workspace_bytes"],
                             policy["command_output_bytes"], args.work.resolve(), policy["database_bytes"])
        print(json.dumps(result))
        return 0 if result["status"] == "passed" else 1
    try:
        return Suite(args.project, args.work, args.profile, args.timeout).run()
    except Exception as error:
        print(f"Acceptance setup failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
