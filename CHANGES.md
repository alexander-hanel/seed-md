# SEED 0.3.0 review baseline

Date: 2026-10-18. Status: draft for review.

This revision brings requirements learned from package development and an unsuccessful reconstruction into the core format. The six package sections and the reusable database-project scope remain. Stronger conformance requirements justify a new draft minor version.

The [specification](SPECIFICATION.md) is authoritative. The [README](README.md) explains the format, the [template](templates/SEED.md) guides authors, and the [skill](SKILL.md) guides consumers.

## Changes and review points

| Area | Requirement in 0.3.0 | What to review |
| --- | --- | --- |
| [Fields](SPECIFICATION.md#field-mappings) | Every public database and query field maps to source elements, derivations, relationship lookups, or generating rules, with semantics, examples, and supplied assertions. | Can an implementer populate each field without guessing? Can repeated definitions be referenced without leaving gaps? |
| [Relationships](SPECIFICATION.md#relationships-and-scale) | Eligibility, scope, cardinality, ambiguity, and duplicates are explicit. Multiplying associations require bounded scale workloads and measurable limits. | Are valid and invalid targets distinguishable? Do limits preserve required results while leaving implementation choices open? |
| [Partial results](SPECIFICATION.md#transformations) | Allowed omissions and mandatory supported cases are declared. Partial status cannot excuse a missing mandatory case. | Is partial support useful and measurable without becoming an escape from correctness? |
| [Source-backed cases](SPECIFICATION.md#source-backed-cases) | Representative external-source cases have locators, identities, expected fields, relationships, and public query results. Authors demonstrate rejection of representative incorrect outputs. | Are expectations independently justified and usable when selected sources change? |
| [Queries](SPECIFICATION.md#queries) | Examples trace to source records. Bounds cover nested collections and text, with explicit truncation, streaming, pagination, or rejection behavior. | Can a caller distinguish an empty result, an ambiguous result, and an incomplete result? |
| [Checkpoints](SPECIFICATION.md#41-checkpoints-before-full-construction) | Small checks precede full construction and apply to the recorded implementation, dependencies, and selected source scope. Relevant changes invalidate affected evidence. | Can defects be found cheaply without treating a small pass as proof of full completion? |
| [Execution](SPECIFICATION.md#42-execution-limits-and-failure-evidence) | A finite authorized run plan is externally enforced. Failed attempts and cumulative limits persist; autonomous model work requires an enforceable usage/spending cap. | Are author, consumer, and environment responsibilities clear? Are stopping limits distinguished from performance promises? |
| [Evidence](SPECIFICATION.md#6-evidence-and-completion) | Start/failure records, process outcomes, checkpoints, snapshots, and usage limitations accompany acceptance. Unknown values stay unknown. | Would an interrupted run still leave enough evidence to inspect what happened? |

## Scope choices

The format requires observable behavior and evidence. It does not select a database engine, association-table design, parser, implementation language, universal budget, or database-size ratio. Packages may impose justified domain-specific constraints.

Source versions may vary under the declared selection policy. Fixed expected examples apply to identified inputs; compatibility checks cover the current selected sources. Exact historical commits for all sources remain optional.

A fixture-only package may use the same bounded workload for its checkpoints and completion. A package with no relationship-multiplication risk records why the scale check does not apply. Generated IDs and timestamps use generating rules and assertions rather than artificial source mappings.

The command supervisor remains an optional Linux implementation aid. It does not supply provider quotas, strict filesystem isolation, or a general SEED runtime.

## Migration

An existing package must be checked against the strengthened requirements before changing its `seed_format` to `0.3.0`. Supply missing mappings, cases, workload limits, and evidence procedures; revise its package version and inventory identity; then rerun affected checks. Merely changing the metadata does not establish conformance.

The current skill supports 0.3.0. The [WinAPIDB draft example](examples/winapidb/README.md) remains on format 0.2.0 and package version 0.2.2 pending a separate migration review. Its schema, fixtures, and numerical limits are example contracts. Its previous reports and the interrupted trial keep their original identities and claims.

## Evidence and open validation

This is a documentation baseline, not a successful reconstruction result. Earlier targeted comparisons and small regression tests informed the changes; they do not validate the whole 0.3.0 format. The dated [AUDIT.md](AUDIT.md) concerns the earlier design.

Review the requirements first. Subsequent behavioral validation should establish that authors can supply these contracts for another database domain, that an independently generated project passes them within an authorized allowance, and that the resulting reusable project remains practical to operate and refresh. A documentation edit or review does not authorize that trial.
