# Field-level source mappings

This document is normative for package version 0.2.2. It describes **every public database column**, including generated and derived values. Read it with [schema.sql](schema.sql), [interfaces.md](interfaces.md), and [SEED.md](../SEED.md). The exact enums, JSON shapes, precedence and candidate eligibility are specified in [population.md](population.md) and refine these mappings. SQLite structure and constraints remain in the schema; field meanings and population rules are here. No table contents from the original database are construction inputs.

## Reading the mappings

[Compatibility cases](compatibility.md) provide source-verified real examples and executable row/query assertions in addition to the illustrative mappings here.

Every row names the originating input or operation, how to populate the field, and an example. There are four kinds of origin: acquired source content; manifest/acquisition metadata; a derivation from other records; and an actual build/extraction event. Generated IDs and timestamps have no upstream document field: their generating operation is their source. Do not invent source values to fill missing fields.

`F_*`, `D_*`, `C_*`, `S_*`, `R_*`, `P_*`, `U_*` and `DECL_*` are symbolic example row IDs, not literal values or stable IDs. Resolve foreign keys through their stated source identity, never by assuming an insertion order. Digests shown as SHA256(...) mean compute the digest from the stated bytes. Ellipses denote abbreviated illustrations, not valid stored JSON. JSON examples with implementation-defined shapes illustrate contents; implementations must document their chosen keys and preserve the required evidence.

Examples use [fixtures.json](../acceptance/fixtures.json) unless explicitly described as an additional illustrative case. Synthetic `sdk`, `headers`, and `samples` entries exercise the same mapping rules as the full sources. Empty and absent metadata are NULL where specified; an unavailable non-null source value blocks that row or produces a documented extraction diagnostic, not a fabricated placeholder. Unknown structured content must retain raw bytes and required search coverage.

For schema 4, usage_documents and usage_declarations are views: their legacy type/FK annotations below describe logical output values, not enforced view constraints. Type notation for physical tables below reports declared SQL type, NOT NULL, primary-key position, and foreign key target. SQLite INTEGER PRIMARY KEY is a generated non-null row identity. Composite keys and UNIQUE/CHECK constraints additionally apply as written in schema.sql. FTS columns lack declared SQL types and enforced foreign keys; use logical integer IDs and text values as described. SQL-nullable foreign keys that these mappings require must still be populated.

## Source groups and field origins

| Input | Fields originate from |
| --- | --- |
| SDK/DDI Git documentation | YAML metadata, Markdown headings/body/links, local include fragments, repository notices and redirection JSON |
| SDK/WDK NuGet headers | Acquired header bytes, declaration spans, lexical scope and preprocessor conditions; package identity/digests from acquisition records |
| Git sample collection | Source tokens/routines, full text, project XML and distributed binary assets |
| Public protocol Git subtree | Markdown sections, explicit metadata and distributed assets; no inferred original PDFs or publication dates |
| Manifest and acquisition results | Corpus keys, logical roots, selected package versions and actual Git/archive identities |
| Build/extraction execution | Row IDs, extraction diagnostics/statuses, durations, stage, coverage and validation outcomes |

The full URLs, selected paths, and packages are defined in [sources.full.json](../sources.full.json). They are acquisition origins, not values to substitute for absent content fields.

## `build_info`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `key` | TEXT; PK 1 | Build operation contract | Generated metadata key; required keys schema_version, through, limited_build, report; configuration may also be retained. | schema_version |
| `value` | TEXT; NOT NULL | Schema constant, invocation, or completed build report selected by key | Text encoding: schema_version is 4; through is invocation stage; limited_build is JSON boolean; report is serialized authoritative report. No missing required values. | 4; samples; false; report JSON |

## `documents`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `id` | INTEGER; PK 1 | Builder row allocation | Generated document ID. | D_COPY |
| `source_path` | TEXT; NOT NULL | Owning corpora.key + source_files.path | Join with /; unique corpus-qualified document identity, independent of UID. | sdk/group/nf-seed-seedcopy.md |
| `source_sha256` | TEXT; NOT NULL | source_files.sha256 for this document | Copy exact stored-byte digest. | same digest as F_DOC |
| `uid` | TEXT | YAML front matter UID | Copy scalar; NULL if absent; duplicate UIDs remain separate documents. | NF:seed.SeedCopy |
| `title` | TEXT | YAML front matter title; first Markdown title for specification documents without YAML title | Preserve source text; NULL if neither exists; do not synthesize a title from an inferred API. | SeedCopy function |
| `kind` | TEXT | Config format, documented UID prefix and explicit document/title markers | specification for format specification; infer function/interface/struct/enum/IOCTL only from explicit markers; NULL for unknown/conflicting classification and diagnose conflict. | function; specification |
| `primary_name` | TEXT | YAML api_name, then UID symbol component, then title or filename stem | Choose explicit API name matching UID, then specific title, before first-entry fallback, as defined in population.md; remove recognized descriptive title suffixes only. Retain spelling; ambiguous metadata stays in metadata_json. | SeedCopy |
| `header` | TEXT | YAML req.header | Scalar as text; list as JSON text; NULL when absent/empty. Never infer from matching header declarations. | api.h |
| `include_header` | TEXT | YAML req.include-header | Same scalar/list/NULL conversion as header; do not substitute req.header. | NULL |
| `technology` | TEXT | YAML tech.root | Scalar as text; list as JSON text; NULL when absent/empty. | NULL in SeedCopy fixture |
| `library` | TEXT | YAML req.lib | Scalar as text; list as JSON text; NULL when absent/empty. | NULL in SeedCopy fixture |
| `dll` | TEXT | YAML req.dll | Scalar as text; list as JSON text; NULL when absent/empty. | ["seed-a.dll","seed-b.dll"] |
| `description` | TEXT | Description section of expanded document | Nonempty YAML description first, otherwise plain text of description section own body; NULL if neither exists. | Copies a seed value. violet orchard evidence. plus description links/include text |
| `source_date` | TEXT | YAML ms.date or explicit documentary date metadata | Preserve documentary value as text; NULL if absent; never use import time or infer a publication date. | NULL in SeedCopy fixture |
| `published_url` | TEXT | Explicit source publication URL, otherwise config published_url_base + corpus-relative document route | Construct offline; remove Markdown extension and apply route rules in SEED; NULL without URL metadata/base; not a verified-live URL. | https://learn.microsoft.com/windows/win32/api/group/nf-seed-seedcopy |
| `metadata_json` | TEXT; NOT NULL | Entire parsed YAML front matter | JSON object retaining unknown keys, arrays and scalar types; {} without front matter. Duplicate keys cause diagnostic, not last-value selection. | {"UID":"NF:seed.SeedCopy","api_name":["SeedCopy"],...} |
| `raw_markdown` | TEXT; NOT NULL | Decoded source_files.raw for this file | Entire original decoded text including YAML, before include expansion. | entire SeedCopy fixture document |
| `corpus_id` | INTEGER; FK corpora.id | source_files.corpus_id for this document | Copy owning corpus reference; required for imported documents despite nullable SQL column. | C_SDK |
| `file_id` | INTEGER; FK source_files.id | source_files row for exact document path and corpus | Resolve by corpus and relative path; required for imported documents. | F_DOC |
| `source_map_json` | TEXT | Include expansion operation and original line locations | JSON mapping every expanded line to retained source file and original one-based line; identity mapping when no expansion. Each entry is {file_id,path,line} as defined in population.md; never point only to unavailable files. | expanded included heading → F_INCLUDE, line 1 |
| `expanded_markdown` | TEXT | raw_markdown plus safely resolved local include contents | Preserve unresolved directives and diagnose cycles/missing targets; store expansion separately from original. | SeedCopy document with part.md inserted |

## `requirements`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `document_id` | INTEGER; NOT NULL; PK 1; FK documents.id | Document whose YAML contains requirement | Resolve documents.id by corpus-qualified source path. | D_COPY |
| `name` | TEXT; NOT NULL; PK 2 | YAML key starting req. | Remove req. prefix; preserve remaining key spelling; unique per document. | dll |
| `value` | TEXT | Value of corresponding req.* YAML key | List → JSON text; scalar → text; absent/empty → NULL if represented, otherwise absent row. Never convert missing to false. Query missing as unspecified. | ["seed-a.dll","seed-b.dll"]; NULL for target-min-winverclnt |

## `aliases`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `document_id` | INTEGER; NOT NULL; PK 1; FK documents.id | Document from which name is extracted | Resolve owning documents row; duplicate names may map to multiple documents. | D_COPY |
| `name` | TEXT; NOT NULL; PK 2 | documents.primary_name, YAML api_name/f1_keywords, or specified derived A/W/COM variant | Retain spelling; derivation must be traceable to original name; no invented synonyms. | SeedCopy |
| `normalized_name` | TEXT; NOT NULL | This row's name | Trim, case-fold, convert interface dots to ::; do not destroy underscores. | seedcopy; iseeddevice::read |
| `origin` | TEXT; NOT NULL; PK 3 | Which source field or derivation produced name | primary, api_name, f1_keywords, or derived with documented derivation. Distinct provenance may yield separate alias rows. | api_name |

## `sections`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `id` | INTEGER; PK 1 | Builder row allocation | Generated section ID. | S_VALUE |
| `document_id` | INTEGER; NOT NULL; FK documents.id | Document being parsed | Resolve documents.id. | D_COPY |
| `ordinal` | INTEGER; NOT NULL | Heading traversal order in expanded_markdown | Zero-based document-local heading order; unique per document. | second parameter section follows first |
| `parent_id` | INTEGER; FK sections.id | Nearest preceding heading at enclosing level | Reference section in same document; NULL for top-level heading. | S_PARAMETERS |
| `kind` | TEXT; NOT NULL | Explicit heading marker or specification heading | Map -description to description, -param to parameter, -field to field, enum member to enum_constant; other headings retain documented classification without invented semantics. | parameter |
| `heading` | TEXT; NOT NULL | Markdown heading text | Remove Markdown delimiter and one leading DocFX hyphen; preserve remaining wording. | param value [in] |
| `line_start` | INTEGER; NOT NULL | Heading location in expanded_markdown | One-based expanded-document line; translate to original via source_map_json. | line containing ### -param value [in] |
| `line_end` | INTEGER; NOT NULL | Section's final included line in expanded_markdown | Inclusive end; stop before the next heading of any level; children have separate rows. | line before ## -returns |
| `markdown` | TEXT; NOT NULL | Expanded document slice for this heading's section | Preserve own-body text, excluding heading and child sections; use parent_id for hierarchy. | Type: <b>int</b> followed by Input value. |
| `plain_text` | TEXT; NOT NULL | This section's markdown | Remove presentation markup without deleting meaningful punctuation, pointer stars or underscores; preserve text ordering. | Type: int followed by Input value. |

## `members`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `id` | INTEGER; PK 1 | Builder row allocation | Generated documented-member ID. | M_VALUE |
| `document_id` | INTEGER; NOT NULL; FK documents.id | Owning sections.document_id | Copy; must match referenced section. | D_COPY |
| `section_id` | INTEGER; NOT NULL; FK sections.id | Section containing explicit member heading | Reference exactly one section; unique; never associate unrelated same-name sections. | S_VALUE |
| `kind` | TEXT; NOT NULL | Section marker | parameter, field, enum_constant only; IOCTL buffer headings are sections, not invented parameters. | parameter |
| `name` | TEXT; NOT NULL | Explicit member heading token | Extract member name without direction/type markers; retain spelling. | value |
| `normalized_name` | TEXT; NOT NULL | Member name | Same trim/case-fold/interface-dot normalization as aliases. | value |
| `position` | INTEGER; NOT NULL | Member order in document | One-based across all members in document order, not inferred ABI position. | first documented parameter |
| `direction` | TEXT | Explicit member heading/description direction marker | in, out, or documented combination; NULL without explicit evidence. | in |
| `optional` | INTEGER | Explicit optional/required annotation | 1 for explicitly optional, 0 for explicitly required, NULL for unspecified; do not infer required from missing optional marker. | NULL for SeedCopy.value; 1 for ISeedDevice.Read.value |
| `declared_type` | TEXT | Explicit Type: line in this member's documentation | Remove presentation markup only; preserve pointer stars and source spelling; NULL absent; never substitute header type. | int; int* |
| `value_text` | TEXT | Explicit enumerator value in heading or member text | Preserve expression text without evaluation; NULL absent; never infer numeric succession. | NULL for parameter; 0x10 when explicitly documented |

## `links`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `id` | INTEGER; PK 1 | Builder row allocation | Generated link ID. | L_TARGET |
| `source_document_id` | INTEGER; NOT NULL; FK documents.id | Document containing expanded link | Reference owning document, including links expanded from fragments. | D_COPY |
| `source_section_id` | INTEGER; FK sections.id | Section enclosing link occurrence | Reference section in owning document; NULL when no section contains it. | S_DESCRIPTION |
| `source_line` | INTEGER | Link location in expanded_markdown | One-based expanded line; source_map_json identifies original fragment location. | line containing `[Target](nf-seed-seedtarget.md)` |
| `label` | TEXT | Original Markdown link label | Preserve label text; NULL when unavailable. | Target |
| `raw_target` | TEXT; NOT NULL | Original Markdown destination | Copy including fragment/path spelling; do not replace with resolved path. | nf-seed-seedtarget.md |
| `normalized_target` | TEXT | raw_target resolved using original fragment location and route rules | Store canonical lookup path/route separately; NULL when normalization cannot be established. | sdk/group/nf-seed-seedtarget.md |
| `fragment` | TEXT | Fragment component of raw_target | Separate from path; NULL when absent; retain original fragment spelling. | NULL; description for #description |
| `target_document_id` | INTEGER; FK documents.id | Unique resolved local document | Resolve by corpus/path/redirect evidence; NULL for missing, external or ambiguous targets. | D_TARGET |
| `relation` | TEXT; NOT NULL | Link syntax/context | reference by default; other documented relations only with source evidence, such as an image. | reference |
| `resolution_status` | TEXT; NOT NULL | Local resolution outcome | local with target; external, missing, ambiguous otherwise; distinguish unresolved cases without inventing a target. | local |

## `diagnostics`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `id` | INTEGER; PK 1 | Builder row allocation | Generated document-diagnostic ID. | DIAG_DOC |
| `document_id` | INTEGER; FK documents.id | Document extraction context | Affected documents.id; NULL only when diagnostic cannot be assigned to a parsed document. | D_COPY |
| `source_line` | INTEGER | Offending location in expanded document | One-based line translated by source map; NULL when no line can be established. | line of unresolved include |
| `code` | TEXT; NOT NULL | Detected document parsing/resolution condition | Stable implementation-documented category; not source prose. | include_cycle |
| `detail` | TEXT; NOT NULL | Observed condition and relevant source evidence | Explain limitation without claiming successful extraction or including machine-specific paths. | Local include refers back to cycle.md |

## `section_search`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `document_id` | FTS value | sections.document_id | Copy owning document ID; required even though FTS does not enforce FK. | D_COPY |
| `section_id` | FTS value | sections.id | Exactly one row per nonempty sections.plain_text; omit empty sections. | S_VALUE |
| `symbol` | FTS value | Owning documents.primary_name and permitted searchable name expansion | Index original symbol; CamelCase spaced form may supplement it, never replace exact aliases. | SeedCopy Seed Copy |
| `title` | FTS value | Owning documents.title | Copy title; empty search text if NULL. | SeedCopy function |
| `heading` | FTS value | sections.heading | Copy exactly. | param value [in] |
| `body` | FTS value | sections.plain_text | Copy exactly; no independently regenerated summary. | Type: int followed by Input value. |

## `corpora`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `id` | INTEGER; PK 1 | Builder row allocation | Generated build-local ID; never taken from upstream. | C_SDK |
| `key` | TEXT; NOT NULL | Selected config entry: docs/headers/samples[].key | Copy exactly; unique across this build; missing or duplicate key is an error. | sdk |
| `kind` | TEXT; NOT NULL | Config array containing the entry | docs, headers, or samples; protocol format remains a docs corpus. | docs |
| `source_root` | TEXT; NOT NULL | Config entry.path | Copy logical SOURCE_ROOT-relative path; never resolve to an author-machine absolute path. | inputs/sdk/content |
| `revision` | TEXT | Acquisition result for entry.repository | Resolved Git commit; NULL for non-Git material. Never inherit the generated project's commit. | resolved Git SHA; NULL for NuGet |
| `metadata_json` | TEXT; NOT NULL | Selected config entry plus its acquisition evidence | JSON object with config and identity objects as defined in population.md, retaining package/version, actual repository identity, archive digest and inventory references where applicable; missing required identity fails acquisition. | {"key":"sdk","path":"inputs/sdk/content"} plus acquired identity |

## `source_files`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `id` | INTEGER; PK 1 | Builder row allocation | Generated build-local file ID. | F_DOC |
| `corpus_id` | INTEGER; NOT NULL; FK corpora.id | Config entry selecting this file → corpora.key | Look up the owning corpus; never infer from a filename alone. | C_SDK |
| `path` | TEXT; NOT NULL | Selected source file location relative to its corpus root | POSIX relative path, unique within corpus. Outside-root notices require a documented logical namespace, not absolute paths. | group/nf-seed-seedcopy.md |
| `sha256` | TEXT; NOT NULL | Exact source file bytes | Lowercase SHA-256 hex of raw; never hash decoded/reformatted text. | SHA256(bytes of fixture document) |
| `encoding` | TEXT; NOT NULL | Source bytes, BOM and documented decoder decision | Record actual decoder; binary for nontext; fallback/replacement decoding requires diagnostic. | utf-8; utf-16; binary |
| `raw` | BLOB; NOT NULL | Exact acquired file bytes | Copy all bytes without decoding or rewriting, including malformed and unsupported material. | UTF-8 bytes of SeedCopy fixture |
| `status` | TEXT; NOT NULL | Extraction outcome for this file | pending only during construction; final parsed/supported state or partial/failed with diagnostics. Document the success label; no accepted pending rows. | failed for quarantined header |

## `extraction_diagnostics`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `id` | INTEGER; PK 1 | Builder row allocation | Generated source-diagnostic ID. | DIAG_FILE |
| `file_id` | INTEGER; FK source_files.id | Affected source_files row | Resolve exact retained source file; NULL only for a corpus/build-level condition with no file. | F_HEADER |
| `line` | INTEGER | Offending original decoded source location | One-based original file line; NULL if unavailable. | 1 for malformed wrapper |
| `code` | TEXT; NOT NULL | Detected acquisition/extraction condition | Stable documented category; retain raw/search data despite unsupported extraction. | inventory_quarantine |
| `detail` | TEXT; NOT NULL | Observed failure or unsupported construct | Evidence-based explanation; no fabricated parser success. | File digest differs from configured archive inventory |

## `source_includes`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `file_id` | INTEGER; FK source_files.id | Source file containing include directive | Resolve original file, including when directive occurs inside another fragment. | F_DOC |
| `target_file_id` | INTEGER; FK source_files.id | Resolved retained include file | Reference exact source_files row; NULL for missing/unsafe target. | F_INCLUDE |
| `line` | INTEGER | Directive location in original including file | One-based original line, not expanded document line. | line containing [!INCLUDE ...] |
| `raw_target` | TEXT | Include directive's target text | Copy before normalization. | ../includes/part.md |
| `status` | TEXT; NOT NULL | Safe local include resolution | Document resolved/missing/cycle/unsafe/unsupported outcomes; never escape corpus root. | resolved |

## `link_candidates`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `link_id` | INTEGER; PK 1; FK links.id | Ambiguous links row | Reference the unresolved ambiguous occurrence. | L_AMBIGUOUS |
| `document_id` | INTEGER; PK 2; FK documents.id | Each eligible document found by route/redirect resolution | One distinct row per candidate; preserve ambiguity rather than selecting arbitrarily. | D_TARGET_A and D_TARGET_B in separate rows |

## `declarations`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `id` | INTEGER; PK 1 | Builder row allocation | Generated declaration ID; separate source spans/versions remain separate records. | DECL_COPY |
| `file_id` | INTEGER; NOT NULL; FK source_files.id | Header containing declaration | Resolve source_files by owning header corpus and relative path. | F_HEADER |
| `name` | TEXT; NOT NULL | Identifier token in source declaration | Retain unqualified spelling; do not fabricate names from parse-error nodes. | SeedCopy |
| `qualified_name` | TEXT; NOT NULL | Identifier and explicit enclosing source scopes | Join known namespaces/types with ::; free function uses name; no compiler resolution assumed. | SeedCopy; ISeedDevice::Read |
| `normalized_name` | TEXT; NOT NULL | qualified_name | Trim/case-fold/interface-dot normalization; retain original fields separately. | seedcopy |
| `kind` | TEXT; NOT NULL | Supported source syntax or recognized declaration macro | Document kind vocabulary, including function, method, callback, type, field, enumerator, variable, forward declaration, GUID/property key; unsupported syntax produces diagnostic. | function |
| `language` | TEXT; NOT NULL | Selected file syntax and parser mode | c or cpp for supported declarations; record actual interpretation, not compiler validation. | c |
| `line_start` | INTEGER; NOT NULL | Declaration start in decoded source | One-based original file line derived from byte_start. | 2 for SeedCopy in api.h |
| `line_end` | INTEGER; NOT NULL | Last source line touched by declaration span | Inclusive, derived from byte_end; must refer to same file. | 2 |
| `byte_start` | INTEGER; NOT NULL | Declaration start in UTF-8 encoding of decoded source | Zero-based byte offset; not offset in original UTF-16/BOM bytes. | 13 for SeedCopy after #pragma once newline |
| `byte_end` | INTEGER; NOT NULL | Declaration end in same UTF-8 encoding | Exclusive end; exact selected source span; document treatment of terminal delimiter. | 37 for span including semicolon |
| `signature` | TEXT; NOT NULL | UTF-8 decoded source slice [byte_start, byte_end) | Exact source spelling including SAL and punctuation; no pretty-printing or inferred ABI. | int SeedCopy(int value); |
| `details_json` | TEXT; NOT NULL | Source syntax within declaration and explicit annotations | JSON object of observed attributes, fields/parameters/macros as supported; {} when none; document keys; never invent evaluated constants/layout. | {"parameters":[{"name":"value","type":"int"}]} as illustrative representation |
| `conditions_json` | TEXT; NOT NULL | Lexically enclosing preprocessor directives | JSON array retaining conditional expressions/branches, unevaluated; [] if none. | []; condition SEED_FEATURE for SeedConditional |
| `method` | TEXT; NOT NULL | Extraction mechanism actually used | Document parser/macro rule identifier; do not claim compiler verification. | documented C syntax parser identifier |
| `status` | TEXT; NOT NULL | Extraction confidence/outcome for this declaration | Document supported/partial vocabulary; no fabricated declarations for malformed spans or quarantined headers. | supported |

## `document_declarations`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `document_id` | INTEGER; PK 1; FK documents.id | Document alias matching a source-backed declaration | Reference eligible document; same symbol can have multiple documents. | D_COPY |
| `declaration_id` | INTEGER; PK 2; FK declarations.id | Declaration matched using normalized names and available scope evidence | Reference exact version/file/span; candidate association only, not ABI equivalence. | DECL_COPY |
| `status` | TEXT; NOT NULL | Relationship's evidential strength | candidate unless stronger explicit evidence is defined; never label name-only matching as verified ABI. | candidate |
| `evidence_json` | TEXT; NOT NULL | Actual alias/declaration match evidence | JSON identifying matching name and basis, plus qualification evidence if used; preserve ambiguity. | {"basis":"normalized name","name":"seedcopy","abi_verified":false} |

## `sample_regions`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `id` | INTEGER; PK 1 | Builder row allocation | Generated region ID. | R_EXAMPLE |
| `file_id` | INTEGER; NOT NULL; FK source_files.id | Selected sample source file | Resolve source_files for this exact sample. | F_SAMPLE |
| `name` | TEXT; NOT NULL | Routine identifier or whole-file fallback | Routine name when parsed; file name for whole-file region; no invented routine for unsupported text. | example; other.cs |
| `line_start` | INTEGER; NOT NULL | Region start in original decoded sample | One-based line derived from region span. | 1 |
| `line_end` | INTEGER; NOT NULL | Last line touched by region span | Inclusive original line; empty whole-file region uses documented empty-file convention. | 1 |
| `byte_start` | INTEGER; NOT NULL | Region start in UTF-8 encoding of decoded sample | Zero-based offset; 0 for whole-file region. | 0 |
| `byte_end` | INTEGER; NOT NULL | Region end in same encoding | Exclusive; whole-file uses full encoded text length; preserve exact source retrieval. | 48 for example function including closing brace |
| `language` | TEXT; NOT NULL | File extension/content and documented syntax classification | Record actual language or text/unknown fallback; binaries have no textual region. | c; csharp |
| `kind` | TEXT; NOT NULL | How region was selected | routine for parsed routine; whole_file for fallback; source-backed categories only. | routine |

## `sample_projects`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `id` | INTEGER; PK 1 | Builder row allocation | Generated project metadata ID. | P_EXAMPLE |
| `file_id` | INTEGER; NOT NULL; FK source_files.id | Selected project XML file | Resolve source_files for project, not a routine source file. | F_PROJECT |
| `details_json` | TEXT; NOT NULL | Project XML elements, attributes and literal item entries | JSON object retaining observed metadata, imports and conditions without executing them; document shape; diagnose malformed XML. | ClCompile Include=example.c from example.vcxproj |

## `usages`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `id` | INTEGER; PK 1 | Builder row allocation | Generated observation ID; identify occurrence, not merely symbol. | U_COPY |
| `file_id` | INTEGER; NOT NULL; FK source_files.id | Sample file containing observation | Resolve exact source_files row. | F_SAMPLE |
| `region_id` | INTEGER; FK sample_regions.id | Containing sample_regions span | Reference region in same file; NULL if no region available; do not attach unrelated routine. | R_EXAMPLE |
| `name` | TEXT; NOT NULL | Observed callee identifier or textual identifier token | Retain token spelling; comments/strings are not parsed calls. | SeedCopy |
| `qualified_name` | TEXT | Explicit source qualification or explicit receiver type | Store only supported qualification; NULL when unknown; preserve ambiguity rather than guessing receiver. | NULL for unqualified SeedCopy |
| `kind` | TEXT; NOT NULL | Observation extraction mode | call for supported parsed calls; text_reference for non-C/C++ textual identifier observations. | call; text_reference for other.cs |
| `line` | INTEGER; NOT NULL | Observation token in original decoded source | One-based source line; do not use header declaration location. | 1 |
| `column_number` | INTEGER; NOT NULL | Observation token on original source line | One-based Unicode character position, not UTF-8 byte position. | 22 for SeedCopy in example.c |
| `conditions_json` | TEXT; NOT NULL | Enclosing source preprocessor conditions | Unevaluated JSON array; [] if none or non-preprocessed text. | [] |
| `status` | TEXT; NOT NULL | Observed resolution uncertainty/extraction mode | Document textual/ambiguous/candidate classification; do not equate a parsed call with verified binding. | textual for other.cs |
| `evidence_json` | TEXT; NOT NULL | Syntax/text observation and receiver/shadowing information | JSON object describing source-backed basis; text observations explicitly indicate not a parsed call. | {"textual":true,"parsed_call":false} |
| `candidate_set_id` | INTEGER; NOT NULL; FK candidate_sets.id | Candidate eligibility result for this occurrence | Canonicalize membership per population.md and resolve/reuse its set; empty targets use the shared empty set. | SET_COPY |


## `usage_documents`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `usage_id` | INTEGER; PK 1; FK usages.id | Observed usages row | Reference occurrence being associated; no rows for invented observations. | U_COPY |
| `document_id` | INTEGER; PK 2; FK documents.id | Eligible documents rows matched to observation name/scope | Reference each distinct candidate; preserve unknown receiver/alias ambiguity; no proof of binding from a matching name. | D_COPY |
| `evidence` | TEXT; NOT NULL | Actual matching rule and source evidence | View exposes shared candidate member evidence: normalized_name or qualified_name; never assert execution or ABI agreement. | normalized_name |

## `usage_declarations`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `usage_id` | INTEGER; PK 1; FK usages.id | Observed usages row | Reference occurrence being associated; no rows for invented observations. | U_COPY |
| `declaration_id` | INTEGER; PK 2; FK declarations.id | Eligible declarations rows matched to observation name/scope | Reference each distinct candidate; preserve unknown receiver/alias ambiguity; no proof of binding from a matching name. | DECL_COPY |
| `evidence` | TEXT; NOT NULL | Actual matching rule and source evidence | View exposes shared candidate member evidence: normalized_name or qualified_name; never assert execution or ABI agreement. | normalized_name |

## `source_search`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `file_id` | FTS value | Source file supplying indexed text | Reference source_files; required even though FTS has no enforced FK. | F_HEADER |
| `region_id` | FTS value | Declaration or sample region supplying a span | declaration → declarations.id; sample → sample_regions.id; NULL for whole-file rows. Interpret by kind, not ID value alone. | NULL for whole header; R_EXAMPLE for sample |
| `kind` | FTS value | Indexed source selection | header, declaration, sample_file, sample, reference_asset; exactly one header row per selected header and one sample_file row per nonbinary sample. | header |
| `name` | FTS value | Source filename or extracted declaration/region name | Use corresponding source-backed label; no invented symbols. | api.h; SeedCopy |
| `body` | FTS value | Decoded whole-file bytes or exact source span selected by kind | Whole-file body equals decoded source; declaration body equals signature; sample body equals region slice. Binary has no fabricated text. | complete api.h decoded text |

## `sample_project_files`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `project_id` | INTEGER; PK 1; FK sample_projects.id | sample_projects row for project XML | Reference owning project metadata record. | P_EXAMPLE |
| `file_id` | INTEGER; PK 2; FK source_files.id | Literal project file item resolved relative to project file | Associate retained source file only when safe resolution succeeds; preserve unresolved/conditional items in project metadata; never evaluate builds. | F_SAMPLE |
| `evidence` | TEXT; NOT NULL | Original XML item and path resolution | Retain item type, Include text, and relevant condition; association is textual, not proof file is compiled. | ClCompile Include="example.c" |

## `document_assets`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `document_id` | INTEGER; NOT NULL; PK 1; FK documents.id | Document linking a distributed asset | Resolve document containing asset reference. | D_PROTOCOL |
| `file_id` | INTEGER; NOT NULL; PK 2; FK source_files.id | Safely resolved asset present in selected corpus | Reference retained file; no row for absent or excluded original PDF/image. | F_IMAGE |
| `role` | TEXT; NOT NULL | Source link syntax/context | image for explicit Markdown image; attachment or other documented source-supported role otherwise. | image |

## `document_redirects`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `corpus_id` | INTEGER; NOT NULL; PK 1; FK corpora.id | Documentation config whose repository provides redirect metadata | Resolve corpora by owning configuration, not target URL host alone. | C_SDK |
| `source_path` | TEXT; NOT NULL; PK 2 | Redirect metadata redirections[].source_path | Normalize relative to owning documentation corpus root, removing repository content prefix where applicable. | group/old.md |
| `target` | TEXT; NOT NULL | Same entry's redirect_URL | Preserve provided route/URL; resolve offline under link rules; no scraping. | /windows/win32/api/group/nf-seed-seedtarget |
| `file_id` | INTEGER; NOT NULL; FK source_files.id | Retained redirect metadata file | Resolve source_files row containing the actual redirection entry. | F_REDIRECT |

## Worked mapping: SeedCopy

The following chain uses the actual bundled fixture contents. Symbolic IDs express joins, not prescribed numeric values.

1. `sdk/content/group/nf-seed-seedcopy.md` contains `UID: NF:seed.SeedCopy`, `api_name: [SeedCopy]`, `req.header: api.h`, and a `-param value [in]` section with `Type: <b>int</b>`.
2. Store its original bytes as `source_files(F_DOC)` under `corpora(C_SDK)`, with path `group/nf-seed-seedcopy.md` and computed SHA-256. Populate `documents(D_COPY)` with `file_id=F_DOC`, `corpus_id=C_SDK`, `primary_name=SeedCopy`, `header=api.h`, and source path `sdk/group/nf-seed-seedcopy.md`.
3. Create `aliases(D_COPY, SeedCopy, seedcopy, api_name)` and the primary alias provenance. Store the parameter section as `S_VALUE`; `members(M_VALUE)` references `D_COPY` and `S_VALUE`, with `name=value`, `kind=parameter`, `direction=in`, `optional=NULL`, `declared_type=int`, and `value_text=NULL`. Missing optionality is not false.
4. `headers/include/api.h` contains `int SeedCopy(int value);` on line 2 after `#pragma once\n`. Retain the file as `F_HEADER`; a declaration span including its semicolon is bytes `[13,37)` in UTF-8 decoded source. Store `DECL_COPY` with that exact signature, `file_id=F_HEADER`, and line coordinates 2–2.
5. `document_declarations(D_COPY, DECL_COPY)` records normalized-name candidate evidence. The matching `req.header` is additional available evidence, not permission to claim compiled ABI equivalence.
6. `samples/example.c` contains `void example(void) { SeedCopy(1); SeedOnly(2); }`. Retain `F_SAMPLE`, parse region `R_EXAMPLE`, and create occurrence `U_COPY` for `SeedCopy` at line 1, column 22. Associate `U_COPY` to `D_COPY` and `DECL_COPY` with candidate evidence. Its trailing comment mentions SeedCopy but must not become a parsed call.
7. `samples/other.cs` contains `SeedCopy(3)`. Its occurrence is a `text_reference`, not a parsed C/C++ call. The observation's provenance remains that C# file even if candidate targets are the same.

`lookup SeedCopy` returns document and declaration candidates separately. `get` uses the document relationships for parameters and declarations. `examples SeedCopy` follows usage associations back to the sample region. `source F_HEADER` retrieves the retained source; `export F_HEADER` returns its exact original bytes. These are relational mappings, not independent copies of invented query data.

## Ambiguous and missing values

The fixture's SDK and DDI `group/dup.md` files share a UID. They must produce separate document/source identities. An ambiguous name lookup must not pick one arbitrarily. Likewise, multiple source versions of a declaration remain distinct candidates; no row ID is a cross-build identity.

The fixture's list-valued `req.dll` populates both the document summary and requirement value as JSON text. Its empty `req.target-min-winverclnt` remains unspecified. The fixture's `ISeedDevice.Read` parameter preserves `int*`, including the pointer star. Missing include targets and invalid YAML retain raw evidence and diagnostics; they do not justify invented extracted fields.

Candidate views expand shared target sets. The normative population rules define eligibility, canonical set identity and reuse; execution policy and supplied tests impose storage/resource checks.

## Verification coverage

The supplied suite already checks selected source bytes/digests, relationships, spans, query behavior and fixture-derived values. It does not yet assert every mapping in this dictionary. Column coverage was checked against the bundled SQL, including ALTER-added fields and public FTS columns; this is documentation coverage, not a successful generated-project test. Additional synthetic cases above (such as an explicit enum value or a distributed image) are illustrations, not claims of existing executable fixture coverage.

## `candidate_sets`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `id` | INTEGER; PK | Builder allocation | Generated build-local identity; usages reference this row. | SET_COPY |
| `signature` | TEXT; NOT NULL; UNIQUE | Sorted eligible document/declaration target IDs and evidence | SHA-256 of canonical JSON defined in population.md; verify membership equality on reuse. | SHA256(canonical target arrays for SeedCopy) |

## `candidate_documents`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `set_id` | INTEGER; NOT NULL; composite PK; FK candidate_sets.id | Canonical matching target set | Resolve set identity; never missing. | SET_COPY |
| `document_id` | INTEGER; NOT NULL; composite PK; FK documents.id | Eligible document alias/qualification match | One membership per distinct target in set. | D_COPY |
| `evidence` | TEXT; NOT NULL | Match rule actually used | normalized_name or qualified_name; occurrence-specific facts remain in usages. | normalized_name |

## `candidate_declarations`

| Field | Type / constraints | Source | Population and missing-value rule | Example |
| --- | --- | --- | --- | --- |
| `set_id` | INTEGER; NOT NULL; composite PK; FK candidate_sets.id | Canonical matching target set | Resolve set identity; never missing. | SET_COPY |
| `declaration_id` | INTEGER; NOT NULL; composite PK; FK declarations.id | Eligible source-backed declaration | Keep distinct source versions, one membership per target. | DECL_COPY |
| `evidence` | TEXT; NOT NULL | Match rule actually used | normalized_name or qualified_name; not compiler binding. | normalized_name |
