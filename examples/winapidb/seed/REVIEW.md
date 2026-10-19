# WinAPIDB seed review notes

Status: amended review draft, package 0.2.2. The earlier 0.1.1 reconstruction trial was interrupted without full acceptance. This amendment has not been used in a new construction trial.

Start with [SEED.md](SEED.md). The supporting interface contract fixes callable behavior, the SQL file fixes the public data model, [the data dictionary](contracts/data-dictionary.md) maps every column to its source and population rules, and the supplied executable tests contain independent synthetic expectations.

This package was authored by reviewing the existing WinAPIDB documentation, source configuration, schema, public queries, validation, acquisition script, and regression scenarios. The database schema is adapted from implementation assets. The real compatibility fixtures contain retained upstream source data and source-verified expected values, not reference implementation code. Importers, parsers, query code, the existing database, and implementation-coupled unit tests are not bundled.

## Scope decisions reflected here

- The local Windows file-format collection and its PDF/OCR assets are excluded at the user's request.
- The publicly downloadable protocol Markdown from awakecoding/openspecs remains included.
- Full completion includes SDK/DDI documentation, SDK/WDK headers, samples, and protocol Markdown. Fixture success is a development checkpoint.
- The existing public SQL schema is retained to make results inspectable and comparable; source layout and language are free.
- Source acquisition is a generated project capability. Four Git sources and two NuGet packages provide the full corpus.
- `docs.published_url_base` supplies reference-link metadata only. Documentation is acquired from GitHub; Microsoft Learn pages are not scraped or fetched by the project.
- Default Git branches may advance. The selected NuGet versions provide a concrete baseline; their package versions and include versions are recorded separately.
- Portable configuration and a command-prefix manifest replace the original Python-specific entry points. This is a proposed public interface for the new implementation, not a claim of exact CLI compatibility.

## Points for feedback

1. Does the full source scope include everything wanted after removing file-format documents?
2. Is preserving the public SQL schema desirable, or should only the query behavior be fixed?
3. Are the proposed interfaces and completion checks appropriate for the first reconstruction trial?

These are review prompts, not missing fields in the package. The draft chooses concrete defaults so it can be assessed as a whole.

The synthetic fixture suite covers the principal database behaviors and several failure cases. It does not recreate every historical parser regression. The broader prose requirements still apply; known failures cannot be excused because a fixture did not exercise them. The earlier trial recorded fixture passes, but no full acceptance pass. Those results do not validate this amended package.

A future generation trial should use a fresh agent context and a separate output workspace, exposing only the seed and permitted data. The current authoring conversation has already inspected the reference code and is unsuitable as evidence of an independent reconstruction.

No downloads of the full corpus, source imports, or database rebuilds were performed while creating this draft. Static package checks do not constitute a successful generation trial.

## Amendment 0.1.2

Added field-level source mappings for every public schema column, with source/derived/generated distinctions, foreign-key resolution, missing-value rules, and fixture-based examples. The SQL and existing executable assertions are unchanged. Column coverage is statically checked; the new prose is not fully covered by existing assertions. Historical trial inputs remain unchanged.

## Amendment 0.2.0

Schema 4 shares candidate sets and exposes occurrence associations as views. Added exact population rules, source-derived expected field assertions, repeated-name/foreign-host fixtures, bounded process supervision and a required real-source preflight. Full runs are limited to one attempt, 60 minutes, 20 GiB final database and 48 GiB acceptance workspace; these provisional stops are not performance promises. New query truncation/total semantics are explicit. No generated implementation has been run against this version. The supplied runner does not enforce provider token quotas; autonomous generation requires external usage enforcement. Original trial inputs and recovered source remain unchanged.

## Amendment 0.2.1

Direct database comparisons found a generic-first api_name list collapsing CreateFileW's document name, and a missing ReadFile declaration despite identical header bytes. Added synthetic A/W alias-order and __out_data_source annotation regressions, with explicit primary-name precedence. Physical scanning of the interrupted candidate independently confirmed excessive candidate-association storage. No candidate rebuild or final acceptance was performed.

## Amendment 0.2.2

Added seven real API/DDI source-backed cases with forty parameter expectations, exact original-byte document snapshots, source-slice header excerpts, provenance and notices. Expected metadata was checked against actual YAML keys; names/flags/types against the original Markdown; declaration signatures against source bytes. The supplied oracle checks database rows and public query behavior. Full preflight must emit the required declarations from their complete real headers. Partial extraction cannot waive these cases. Added five scoped/receiver/shadowing relationship cases and negative tests for their acceptance assertions. Original zero-based parameter positions are normalized to the new one-based convention for diagnostic comparison. No reconstruction was launched.
