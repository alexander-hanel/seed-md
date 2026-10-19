# Operating and configuration contract

This document is normative. Commands below specify argument vectors, not shell scripts. Every operation is run with the generated project root as its working directory. Arguments supplied by the caller may be absolute runtime paths; published examples and saved provenance use relative paths or named bindings.

## Project handoff

The project root contains `README.md`, `DEPENDENCIES.md`, and `interface.json`. The README explains setup, acquisition, staged/full builds, validation, queries, refresh, and known limitations. DEPENDENCIES lists runtime/build tools and supported versions, including how to install them.

`interface.json` has this structure; command prefixes and source filenames are chosen by the implementation:

```json
{
  "operations": {
    "acquire": ["./reference-tool", "acquire"],
    "build": ["./reference-tool", "build"],
    "validate": ["./reference-tool", "validate"],
    "query": ["./reference-tool", "query"],
    "preflight": ["./reference-tool", "preflight"]
  },
  "source_files": ["src/main.example"],
  "dependency_files": ["dependencies.lock", "installed-dependencies.json"]
}
```

`dependency_files` inventories portable dependency locks and actual installed-version records; both are mandatory and must be complete. `source_files` lists all delivered implementation source using project-relative paths; it is not a replacement for source files. Command prefixes are nonempty arrays of strings without shell substitution. Executables may be tools on PATH or project-relative executables. All five operations must work after documented setup. The supplied test runner appends the arguments below without changing assertions.

Successful operations return exit code 0 and one JSON value on stdout. Progress goes to stderr. Failures return nonzero and JSON containing `error`; error wording is not fixed. Query failures must not create or modify the database.

## Source configuration

Configuration is UTF-8 JSON. It contains `acquisition`, `docs`, `headers`, and `samples` arrays. Paths resolve from the caller's `--root`, independent of the config file's location. Keys identify corpora uniquely. Unknown fields may be retained but cannot override these rules.

Acquisition entries use:

| Kind | Fields |
| --- | --- |
| `git` | `id`, `url`, `ref` equal to `default` or an explicit ref, `destination` |
| `nuget` | `id`, `package`, `version`, `destination`; optional `archive_binding` for a caller-supplied archive |
| `directory` | `id`, `binding`, `destination`; copy an explicitly supplied source tree without modifying it |

The `directory` and local archive forms support fixture verification and reuse of independently acquired input data. The full manifest uses public Git/NuGet acquisition only.

A binding file is a JSON object mapping binding names to runtime locations. Relative binding values resolve from that file's directory. Binding values must not be written into published package content. Copy/import records use the binding name and relative paths.

Git acquisition records the actual repository URL/ref/commit and relevant local modifications. A destination already containing the selected verified input may be reused without refetching for a resumed run. A refresh must explicitly resolve its selected new input state and record it; it must not silently modify a source during a build.

NuGet acquisition:
- Download `https://api.nuget.org/v3-flatcontainer/{lowercase-package}/{version}/{lowercase-package}.{version}.nupkg`, or use `archive_binding`.
- Check ZIP CRCs and the nuspec package ID/version before publishing extracted content.
- Reject path traversal, absolute archive members, and symlink escapes.
- Extract header/inline extensions and license/notice files below `destination/extracted`.
- Write `headers-complete.json` as a sorted array of `{"path": "relative/member.h", "sha256": "..."}` calculated from the archive.
- Write `complete-manifest.json` with `package_id`, `package_version`, `archive_sha256`, `header_count`, `zip_crc_verified`, and `nuspec_identity_verified`.
- Preserve differing existing extracted files and fail instead of silently overwriting local modifications.
- Package acquisition checks bytes and package metadata; it does not establish a vendor signature or compiler correctness.

Each docs entry has `key`, `path`, and optional `repository`, `published_url_base`, `document_glob`, `format`, and `include_assets`. Default document selection is recursive `*.md`, excluding path components `.git`, `obj`, and `includes` as standalone documents. Referenced includes are still captured. `document_glob` overrides the pattern. `format: "specification"` requests specification documents; `include_assets: true` retains all files under that selected source root except Git internals. Root notices and redirect metadata under `repository` are retained separately.

`docs.path` identifies the input files already downloaded from GitHub. `docs.published_url_base` is optional citation metadata: use it offline to construct the `published_url` returned in query results and to recognize publication routes in stored links. It is not an acquisition endpoint. Do not fetch, scrape, or check the availability of pages at this base while acquiring, building, validating, or querying the corpus. Network acquisition is defined only by the `acquisition` entries. A constructed link is not a claim that the page was verified online. When no publication base or explicit publication metadata is supplied, leave `published_url` NULL.

Each headers entry has `key`, `path`, `package`, `version`, and `include_version`; `manifest`, `inventory`, and `inventory_root` declare acquisition evidence. Selected extensions are `.h`, `.hpp`, `.hxx`, and `.inl`, case-insensitively, recursively. Inventory paths resolve from `inventory_root`. An inventory's absence when configured is a missing prerequisite; an individual entry mismatch causes quarantine as specified in the seed.

Each samples entry has `key`, `path`, and optionally `repository`. Select all regular files except Git internals. Do not follow a symlink outside its declared source root. Binary assets are retained and exportable.

## Operations

### Acquisition

Append:

```text
--config CONFIG --root SOURCE_ROOT --report ACQUISITION_REPORT [--bindings BINDINGS]
```

Process declared acquisitions and verify configured source roots and header inventory coverage. Return a JSON object with `status: "complete"` and a `sources` array on success. Each source record includes its `id`, acquisition kind, logical destination, actual identity, and verification outcomes. Preserve the report at the requested location. Failure returns a nonzero result and records the failed prerequisite.

### Build

Append:

```text
--config CONFIG --root SOURCE_ROOT --db DATABASE --through docs|headers|samples --report BUILD_REPORT [--limit N]
```

Default stage is docs when omitted; the suite supplies it explicitly. `N` must be positive. All entries relevant to selected stages are required. At least one docs corpus is required. Every docs corpus must produce a document; full header/sample stages require structured results where supported source material is present.

Build from existing inputs only. Return/embed a report with:

- `status`: `complete` or `complete_with_warnings`;
- `stage`, boolean `limited`, `schema_version`, `project_identity`, and `sources` identities;
- `counts`, `coverage`, `diagnostics`, `validation`, `started_at`, `ended_at`, and `seconds`.

Schema version is also stored as text `4` in `build_info`. Store the report JSON under key `report`. Store `through` and a boolean JSON representation under `limited_build`. Reports may add fields; elapsed times and numeric IDs need not match across runs.

External evidence may record the final database digest after close. A failed attempt writes a failure report with stage/reason and the identity of any retained accepted database.

### Validation

Append `--db DATABASE`. Verify the database contract, stored-byte hashes, spans, search coverage/content, and embedded report structure. Return `{"status": "passed"}` with optional details, or a nonzero JSON error. Validation must not damage the supplied database. The supplied suite independently compares selected source files with stored bytes.

### Query

Append `COMMAND [TARGET] --db DATABASE [OPTIONS]`.

Read-only access is mandatory. Stable result ordering is defined below; relevance scores and tied relevance order are not fixed. Defaults: `--limit 20`; allowed range 1..1000. Commands returning one selected document use a corpus-qualified path, numeric ID, or unambiguous alias. An ambiguous/missing document is an error; a search/lookup with no match returns empty collections.

| Command | Options and required result |
| --- | --- |
| `lookup NAME` | `--corpus`, `--version`, `--language`, `--limit`; object with `documents` and `declarations` arrays. Documents contain `id, source_path, primary_name, kind, header, description, published_url, corpus, rank`. Order by match rank then source path. |
| `get SELECTOR` | `--corpus`; object with `id, source_path, primary_name, kind, header, published_url, file_id, metadata, source_map, sha256, status, sections, members, requirements, declarations, diagnostics, assets`. |
| `arguments SELECTOR` | `--corpus`; parameter objects in documentation order, with member fields, section text, source lines, and `descendants` array. |
| `members SELECTOR` | `--corpus`; all documented parameter/field/enum member kinds in their documented order. |
| `sections SELECTOR` | `--corpus`, `--kind`; section rows ordered by ordinal; a kind filter includes descendants. |
| `requirements SELECTOR` | `--corpus`; object from requirement name to value/NULL. Remove the `req.` metadata prefix in requirement names. |
| `related SELECTOR` | `--corpus`; outgoing link rows, including `raw_target, resolution_status, target_document_id, target_path`; order by link ID. |
| `declarations NAME` | `--corpus`, `--version`, `--language`, `--limit`; declarations with `file_id, name, qualified_name, kind, language, signature, byte_start, byte_end, line_start, line_end, conditions, details, path, corpus, package`. Order by corpus, path, line. |
| `examples NAME` | `--language`, `--limit`; usage objects with `file_id, region_id, kind, path, corpus, language, routine, source, targets, projects`. Targets contain `documents` and `declarations` arrays. Order by path and source line. |
| `sample REGION_ID` | Usages in source order with target arrays. Unknown region is an error. |
| `search TEXT` | `--corpus`, `--limit`; object with `documents` and `sources` arrays, each independently bounded. Treat input as literal word tokens ANDed together, not arbitrary FTS syntax. Include source kind/file ID and snippets. |
| `references NAME` | `--corpus`, `--limit`; exact identifier occurrences in full header/sample text, including comments/strings. Results contain `file_id, corpus, path, occurrences, total_occurrences, evidence`. Each occurrence contains one-based `line` and `text`; evidence explicitly says textual, not a parsed call. Order by corpus/path. |
| `source FILE_ID` | `--line-start`, `--line-end`; `file_id, corpus, path, sha256, encoding, status, text`, plus bounded line coordinates for text. Binary returns `text: null` and byte count. Invalid IDs/ranges fail. |
| `files TEXT` | `--corpus`, `--limit`; case-insensitive path-substring results with `file_id, corpus, path, sha256, encoding, status, bytes`, ordered by corpus/path. Empty text selects any file. |
| `export FILE_ID` | Required `--output DESTINATION`; exclusive creation of exact raw bytes. Return `file_id, sha256, bytes`. Refuse an existing destination or the database. |
| `diagnostics [FILE_ID]` | `--limit`; extraction diagnostics with `file_id, code, detail`, ordered by ID. Document diagnostics also appear in `get`. |
| `report` | Embedded build report. |

JSON columns such as `metadata_json`, `details_json`, `conditions_json`, and `source_map_json` are decoded into their suffix-free keys in query output. SQL retains the original JSON-text columns.

FTS `source_search.kind` distinguishes `header`, `declaration`, `sample_file`, `sample`, and `reference_asset`. For a declaration row, `region_id` refers to a declaration; for a sample row, it refers to a sample region. Whole-file rows have a NULL region. Exact source text remains retrievable regardless of structured extraction success.

Decode UTF-8/BOM and UTF-16/BOM strictly where possible; retain original bytes on errors and label any replacement decoding with a diagnostic. CP1252 fallback is allowed when recorded. Binary files have `encoding: "binary"`. Query text is decoded source evidence, not regenerated source code.

## Representative-source preflight (schema 4 package)

Append `--config CONFIG --root SOURCE_ROOT --selection SELECTION --report REPORT`. SELECTION is an array of `{corpus, path, sha256}` entries selected by the supplied suite, optionally including `required_signatures` (an array of exact declaration strings). Each required signature must appear as a verified emitted span; a diagnostic does not waive it. Offline, use the same extraction code and dependency versions as build. Process every selected file, retain source bytes/hashes, and check any emitted spans against exact decoded source. Unsupported syntax must have diagnostics; a native crash, timeout, or invalid emitted span is a failure. Return `{status: "passed", files: [...]}` only if all selected inputs were processed without those failures. Each file entry includes corpus/path/sha256, `status` (complete or partial), `diagnostics` array, and `spans` array of `{byte_start, byte_end, text}` for emitted declarations/regions. Each selected header must emit at least one span or a nonempty diagnostic; an empty claim of success is invalid. Report project and dependency identities. Preflight does not publish an accepted database.

Build reports include counts for every physical public table, including candidate sets and their members. Expanded view cardinalities are optional and must be labeled as virtual. Emit progress as JSON lines on stderr at stage transitions and at least every 30 seconds while processing files: stage, processed_files, selected_files, candidate_bytes, elapsed_seconds. Counts must represent completed work, not estimated success. Do not repeatedly embed entire source files or reports in progress.

For queries, `--limit` bounds top-level records and each nested target array separately. `targets` additionally contains `documents_total`, `declarations_total`, and `truncated` (true if either array is shortened). Never imply a truncated list is complete. `get` declaration results follow the same bound with `declarations_total` and `declarations_truncated`. `sample` also uses the top-level limit and returns `{items, total, truncated}`. Sample source snippets contain at most 4096 characters and include `truncated`; full text remains available through `source`. Reference occurrences per file are limited to the requested limit, with exact `total_occurrences` and `truncated`. Read-only queries have a 30-second deadline; bounded stdout is enforced by the supplied runner. Limits constrain work/output; indexing choices remain implementation decisions.

The supplied suite hashes every inventoried source/dependency file plus README.md, DEPENDENCIES.md and interface.json. Sort the relative-path keys, serialize the path-to-SHA-256 object with compact JSON separators (comma and colon), Unicode preserved (ensure_ascii=false), and hash its UTF-8 bytes. `project_identity.snapshot_sha256` must equal that value. The source inventory includes all executable source, schemas and required runtime configuration; it cannot omit an imported module. The suite checks these files before and after operations. Installed dependency identity must come from the actual environment and remain equal across preflight/build. The launcher must freeze or isolate that environment; file hashing alone cannot prevent external tool replacement.
