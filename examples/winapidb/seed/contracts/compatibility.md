# Source-backed compatibility requirements

The package includes selected real source data and independent expected results in [reference-cases.json](../acceptance/reference-cases.json), materialized by [fixtures.json](../acceptance/fixtures.json). These are mandatory acceptance cases, not optional illustrations. They contain no reference implementation. A consumer needs no original database or author-machine checkout.

## What each case proves

| Cases | Source material | Required behavior |
| --- | --- | --- |
| CreateFileA / CreateFileW | SDK Markdown including generic-first api_name arrays; exact fileapi.h declaration excerpts | Distinct specific primary names, all documented aliases preserved, parameters and source signatures retained. |
| ReadFile / ReadFileEx | SDK Markdown and SAL/__out_data_source annotated declarations | Valid declarations remain present despite annotations; missing declarations fail acceptance even if the file has a partial diagnostic. |
| DeviceIoControl | SDK Markdown and ioapiset.h excerpt | Parameter order and input/output/optional evidence; declaration-to-document relationship. |
| IoCreateDevice / IoDeleteDevice | Driver documentation and versioned WDK wdm.h excerpts | Driver API extraction and query behavior, with actual source identity and exact signatures. |

Seven cases contain forty documented parameters. The expected document fields are UID, title, primary name, header, DLL and library. The row checks additionally cover parameter order/direction/optionality/documented type, exact declaration text, selected header identity and document/declaration association. Public queries check lookup, get, declarations and arguments against the same independently supplied expectations. Each case supplies complete expected values for the tested fields; untested fields remain governed by the field dictionary.

## How the expected data was established

Document bytes were exported unchanged from the reference database's retained source material and checked against their stored SHA-256. Each expected scalar appears in that source. Parameter names and flags were checked against the actual Markdown headings. Header signatures were verified against the UTF-8 byte slices of the retained header and its digest. Full source locators, source group IDs, revisions, hashes and original spans are recorded alongside each excerpt. Repository notices and header copyright comments are retained with the bundled material.

Numeric row IDs, import times and filesystem locations from the reference are excluded. The reference's zero-based parameter positions are translated to the explicitly specified one-based positions; source order remains identical. This is a documented schema convention, not an extraction difference. Examples are acceptance data, not a copy of the original software.

The original database is a comparison aid, not an unquestionable oracle. If an expected value disagrees with the supplied source, report a package defect and amend it explicitly rather than matching the error. Additional assets can be authored using the repository helper with explicit database, package and notice-root arguments; this authoring activity is outside fresh generation.

## Full-source and preflight obligations

The fixture profile uses the bundled documents and excerpts under reference-sdk/reference-ddi and reference-sdk-headers/reference-wdk-headers. The full profile checks the corresponding declared public corpora. Exact historical Git commits are not required. Stable identity/parameter expectations still apply; an upstream semantic change must be reported as a changed source contract for review, not silently skipped. The pinned SDK/WDK package excerpts must match the selected header bytes.

Real-source preflight includes the complete fileapi.h, ioapiset.h and WDK wdm.h files containing these examples, in addition to deterministic sampled inputs. Their required signatures are listed in the selection manifest. A partial result or nonempty diagnostics list does not waive a missing required signature. Native crashes block construction. This catches failures hidden by otherwise successful extraction elsewhere in a large header.

## Relationship eligibility and scale

[relationship-cases.json](../acceptance/relationship-cases.json) identifies exact source occurrences and eligible targets:

- Left::Probe must not resolve to Right::Probe.
- A receiver explicitly typed ReceiverA must not resolve to ReceiverB::Read.
- A local function-pointer variable shadows the same-named global function.
- An unknown receiver retains all eligible Read method alternatives and ambiguous status.
- An unqualified parsed Probe call may target callable declarations, but not a same-named field.

Separately, the repeated-name fixture retains 128 occurrences and 128 alternatives while storing candidate membership once. This tests storage sharing without discarding ambiguity. The suite checks both meaningful target eligibility and physical representation; a small database produced by dropping alternatives fails.

## Evidence limits

These cases are a required baseline, not proof of every Windows declaration or future source revision. Report their individual failures and preserve source identities. Passing them does not waive full-source coverage, provenance, integrity, query bounds or resource limits. Static checks of these assets and deliberately corrupted test rows validate the acceptance checks; they are not a successful project reconstruction.
