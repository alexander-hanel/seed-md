# Deterministic population rules

Normative for package 0.2.2 and schema 4. These rules refine the [field dictionary](data-dictionary.md). Where an older dictionary illustration leaves a choice, the rules here fix it. SQL defines storage constraints; implementations may add private attributes without changing these meanings.

## Names, sections and metadata

- `documents.primary_name`: select the api_name entry matching the UID symbol after removing its kind/module prefix; if none, select the entry matching the title's specific symbol (remove recognized descriptive suffix only); otherwise the first nonempty api_name. Without api_name, use UID symbol then title/stem fallback. Match with the declared normalization but preserve original spelling. For UID NF:seed.SeedTextW and api_name [SeedText, SeedTextA, SeedTextW], the primary name is SeedTextW. Keep all other names as aliases; an unqualified alias is not a reason to merge A/W documents.

- `documents.title`: nonempty YAML `title`, otherwise first level-one Markdown heading for a specification document, otherwise NULL. `primary_name` still has the separate UID/title/stem fallback described in SEED.
- `documents.description`: nonempty YAML `description`, otherwise plain text of the description section's own body, otherwise NULL. Preserve both original sources; do not concatenate summaries silently.
- `documents.kind`: `specification` for configured protocol material; recognized DocFX UID prefixes NF/NS/NE/NC/NI map to function/structure/enumeration/callback/ioctl; otherwise NULL. Conflicting explicit metadata requires a diagnostic, not a fabricated resolution.
- Section headings remove the Markdown delimiter and one leading DocFX hyphen. `-param value [in]` becomes `param value [in]`. `ordinal` starts at 0. A section's body starts after its heading and stops before the next heading of any level. Children are represented through parent_id, not duplicated inside every ancestor. line_start is the heading line and line_end is the final own-body line (or heading line for an empty body). A synthetic pre-heading description uses its first body line and an empty heading.
- `members.position` starts at 1 across all members in document order. `direction` is NULL, `in`, `out`, or `in,out`; optional is NULL/0/1 only on explicit evidence. Type text comes solely from an explicit Type line. No inference from matching headers. Source aliases preserve underscores and pointer stars where relevant.
- `links.normalized_target` is a corpus-qualified path when a local path can be established. External absolute targets remain their absolute URL. The fragment is stored separately. Absolute HTTP(S) URLs must match both the configured publication origin (scheme, hostname, effective port) and route, or an explicit source canonical URL, before local resolution. Scheme-relative URLs also require origin checking. Same-path links on unrelated hosts remain external.
- `source_files.status`: complete, partial, failed; pending is transient only. `source_includes.status`: resolved, missing, cycle, unsafe, unsupported. `links.resolution_status`: local, external, missing, ambiguous, asset, malformed. `declarations.status`: supported or partial. `usages.status`: candidate, ambiguous, unresolved or textual. Diagnostics have a stable nonempty code and human-readable detail; their vocabulary may extend as new unsupported syntax is encountered.
- Language tags: c, cpp, csharp, javascript, powershell, xml, text, binary. An unsupported text language uses text and retains its actual extension in provenance. No textual region for binary files.

## Structured fields

These are minimum JSON shapes; extra keys are permitted. Missing lists are empty lists, not NULL. Unknown source metadata retains its parsed source types rather than being replaced by this schema.

| Column | Shape and required meaning |
| --- | --- |
| documents.metadata_json | Object preserving all parsed YAML keys; {} without YAML. |
| documents.source_map_json | Array in expanded-line order of `{file_id: integer, path: string, line: integer}`; one entry per expanded line; paths corpus-relative and lines one-based in original retained files. |
| corpora.metadata_json | Object containing `config` (selected entry) and `identity` (actual acquisition record). Package/version filters read `config.package` and `config.version`. |
| declarations.details_json | Object with `parameters: [{name: string or null, type: string or null}]`, `annotations: [string]`; empty lists if none. Preserve source spelling, no inferred layout. |
| declarations.conditions_json / usages.conditions_json | Array of `{directive: string, expression: string}` for enclosing lexical conditional branches, outermost first; expressions unevaluated. |
| document_declarations.evidence_json | Object `{basis: "normalized_name", name: string, qualified: boolean, abi_verified: false}`. |
| usages.evidence_json | Object `{parsed_call: boolean, textual: boolean, receiver: string or null, receiver_type: string or null, shadowed: boolean}`; source-backed observations only. |
| sample_projects.details_json | Object `{items: [{kind: string, include: string, condition: string or null}], imports: [string], evaluated: false}`; preserve literal XML, never evaluate projects. |
| build_info.report | Object with fields in interfaces.md; project identity includes complete delivered-source snapshot SHA-256; dependency identity includes installed versions. |

`declarations.method` names the actual parser or recognized macro rule; the dependency report resolves its tool/version. It is deliberately not a fixed tool choice. Generated IDs, timestamps, digests and tool names need not be identical across implementations. Their origin and relationships must be correct.

## Candidate eligibility and shared storage

A candidate is a possible target, not a claim of executed binding or ABI agreement.

1. Qualified observations match normalized qualified names only. An explicitly typed receiver supplies qualification. Do not discard that qualification to obtain more matches.
2. Unqualified parsed calls may match callable declarations (functions, methods, callbacks, or recognized callable macros) and corresponding document aliases. Local shadowing suppresses external target associations unless explicit qualification disambiguates them. Unknown receivers retain ambiguous status.
3. Unqualified textual observations can match exact normalized document aliases and declaration terminal names of any supported kind, but remain textual. A/W derived aliases remain candidate evidence, not exact-name proof. Repeated header versions remain distinct targets.
4. Deduplicate target IDs within a set. Keep occurrence-specific receiver/shadowing/conditions in usages; they affect eligibility, but are not duplicated as relation text. Target association `evidence` is `normalized_name` or `qualified_name`, according to the actual match rule.
5. Canonicalize the sorted arrays of `[target_id,evidence]` for documents and declarations as JSON `[document_array,declaration_array]`, with no insignificant spaces and UTF-8 encoding. `candidate_sets.signature` is its lowercase SHA-256. Reuse the set if its membership and evidence are identical; verify equality before reuse rather than assuming a hash collision impossible. An empty set is valid and shared.
6. Each usage points to exactly one candidate set. Store member rows once in candidate_documents/candidate_declarations. `usage_documents` and `usage_declarations` are read-only views expanding these sets for compatibility. Do not also materialize a private occurrence-by-target copy. Counts and storage checks distinguish physical member rows from expanded view rows.
7. Every nonbinary non-C/C++ text identifier observation selected by this contract is retained as text_reference, even with an empty target set; comments and strings in C/C++ remain accessible through references, not fabricated calls. Query output bounds must expose truncation and exact totals.

The supplied repeated-name fixture has 128 declarations in distinct namespaces and 128 identical textual occurrences. All 128 declaration candidates must remain available, but their membership must be stored once and shared across occurrences. This is a physical-storage assertion, not a permission to lose alternatives.
