# Changes following the interrupted reconstruction

The draft package is now **0.2.2**, using **schema 4**. The generic SEED format remains 0.2.0. No reconstruction, acquisition, generated-project execution or model subprocess was started. The interrupted worker and its historical inputs were not modified.

## Implemented changes

- [Field rules](contracts/population.md) define metadata precedence, section boundaries, ordering, status/language vocabularies, minimum JSON shapes, and candidate eligibility. The [dictionary](contracts/data-dictionary.md) maps all 171 public columns across 28 tables/views to their sources or generating operations.
- [Schema](contracts/schema.sql) stores shared candidate sets. Occurrence relationships are views; identical occurrences no longer require duplicate physical membership rows. The supplied repeated-name case requires 128 alternatives across 128 occurrences while storing one membership set.
- [Supplied acceptance](acceptance/run.py) checks exact expected field values, external-origin link behavior, candidate sharing and nested query truncation. Real-source preflight is required before full construction, and producer/dependency identities must match.
- Source/dependency file inventories are hashed and checked before/after operations. Full acceptance requires a durable trial directory; its full-attempt evidence directory cannot be reused. Test progress and command starts/results are persisted.
- [Execution policy](contracts/execution.md) sets one full attempt, 60 minutes overall, 20 GiB per-file/candidate limit, 48 GiB acceptance workspace limit, bounded output and query deadlines. These are provisional stop thresholds, not measured estimates. Limits do not authorize another trial.
- The reusable skill now requires externally enforceable model spending limits before autonomous agent launches. Ordinary build/test processes use the bounded helper. Logs remain in files; model supervision reads short state changes or selected failures.

## Validation performed

Nine small offline tests passed: completion/failure evidence, timeout, output and disk limits, candidate-size limit, nested descendant termination, refusal to reuse evidence, shared-candidate schema/dictionary behavior, and bundled-helper consistency (some tests cover more than one property). Package self-check and skill validation passed. Python syntax, documentation links, and original trial input hashes were checked.

Detailed validation logs are retained separately in the repository's validation workspace; no full logs were streamed into model context. No generated implementation has been tested against the new package. A static contract check is not a successful reconstruction.

## Remaining limitations

Disk limits are sampled and may overshoot. The Linux supervisor is not a sandbox; strict quotas and escaped/remote processes need environment-level containment. It cannot enforce provider tokens, so the skill prohibits autonomous generation without a functioning external budget mechanism. Fixture cases establish selected behaviors, not all C/C++ semantics or full-corpus scalability. The original candidate's table-by-table size breakdown remains unknown.

Direct row comparisons additionally informed the A/W name precedence and data-source annotation fixtures. See REVIEW.md amendment 0.2.1.

## Source-backed behavior added in 0.2.2

[Compatibility requirements](contracts/compatibility.md) now specify seven actual API/DDI examples and forty parameter expectations. [reference-cases.json](acceptance/reference-cases.json) records exact source provenance and expected values, while [relationship-cases.json](acceptance/relationship-cases.json) checks qualification, receiver types, shadowing and ambiguity. Supplied row/query checks and required real-header preflight signatures make these behaviors mandatory. A source-verified comparison accepted the original database and identified six semantic defects in the candidate's readable document/header data. Its interrupted relationship tables were excluded from that diagnostic comparison, not from acceptance.

The 0.2.2 amendment passed sixteen small offline tests and package self-check. Source-verified row checks accepted the original baseline and identified two wrong primary names and four missing declarations in the candidate. Public query acceptance against a new 0.2.2 implementation remains unrun.
