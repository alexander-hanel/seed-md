# SEED database scope review

Review date: 2026-10-17. Reviewed format: 0.2.0 draft.

Historical review: the current core documents define draft 0.3.0. This dated assessment and its hashes do not cover that revision. See the [0.3.0 review guide](CHANGES.md) for the changes and validation limits.

This review reconciles the documentation with the decision to focus SEED on reusable projects that construct and query regenerable reference databases. It is a design review of the revised text, not an independent validation or a generation trial.

The superseded general-purpose specification, README, template, and original second-pass audit are preserved together in [the 0.1.0 history](history/0.1.0/AUDIT.md). That audit's evidence hashes and relative links refer to the archived documents. Its scope recommendations describe the earlier proposal and are not current format requirements.

## Current assessment

The narrower scope makes the intended handoff concrete: reusable acquisition and build capabilities, a query interface, dependencies, documentation, a generated database, and evidence. A consumer cannot satisfy the package merely by producing one acceptable database while leaving an unusable builder.

The format now distinguishes three activities:

- An agent creates the project from the package.
- The delivered project builds, refreshes, validates, and queries the database.
- An agent or developer revises project code when the implementation or contract needs to change.

A routine refresh does not inherently require new code. Unsupported input changes may still require a project revision; SEED does not guarantee that a builder anticipates every future source format.

The initial scope assumes database contents can be reconstructed from declared sources. This permits full rebuilds as the baseline and avoids a general migration protocol for user-edited records. It does not authorize discarding source inputs, annotations held elsewhere, or changes to project code.

## Changes from the general-purpose draft

| Area | Decision in 0.2.0 |
| --- | --- |
| Deliverable | A reusable reference database project, its required build, and evidence. |
| Package sections | Purpose, Sources, Data contract, Transformations, Queries, Acceptance. |
| Routine operation | Documented acquisition, full build, validation, and read-only query interfaces. |
| Refresh | Build and validate a candidate; retain the previous accepted database on failure. |
| Acceptance | Supplied executable checks of clean operation, data fidelity, queries, refresh, and declared completion scope. |
| Normative content | Bundle requirements and supplied tests; external data cannot silently change the acceptance contract. |
| Comparison | Independent contract satisfaction by default; cross-build equality needs its own declared relation. |
| Revision | Explicitly requested code changes preserve user-owned work; generalized database-state migration is outside scope. |
| Compatibility | Format 0.2 is a scope and structure change, not a compatible reinterpretation of 0.1. |

The engine remains package-defined. The format does not require SQLite, a particular schema, a Windows corpus, a specific implementation language, or exact Git commits.

## Reconciliation of the earlier findings

These are dispositions in the revised documentation, not claims that implementation behavior has been demonstrated.

| Finding | Disposition | Remaining limit |
| --- | --- | --- |
| A01: Tests versus correctness | Completion explicitly excludes known mandatory-requirement violations; test evidence is bounded to checked properties. | Finite fixtures and traceability do not establish exhaustive correctness. |
| A02: Scope and executable coverage | Direct arbitrary artifacts and general applications are outside scope. Required checks now target database construction and query behavior. Process and human-review evidence are distinguished. | Authors still need meaningful requirements, fixtures, and review procedures where used. |
| A03: Effective contract identity | All normative requirements and supplied tests must be bundled. External data has a separate selection policy and resolved identity. | Authors must distinguish source facts from instructions and avoid delegating requirements to mutable remote documents. |
| A04: Acceptance versus pairwise agreement | Independent behavioral acceptance is the default; explicit comparison relations govern any cross-build claims. | Ordering, surrogate identifiers, tolerances, and mutable input differences still need package-specific decisions. |
| A05: Reusable project handoff | Reusable software is mandatory, with supplied clean-operation tests and documented interfaces. | A clean fixture build alone does not demonstrate scale or robustness on every supported source. |
| A06: Complete implementation boundary | Helpers and dependencies have declared roles; a complete implementation cannot be hidden in a test oracle. | This remains a semantic authoring policy, not something syntax validation can establish. |
| A07: Package inventory boundary | Freeze the inventory before generation and exclude outputs, caches, and evidence; record material file metadata. | The format does not yet prescribe canonical inventory serialization across consumers. |
| A08: Update baseline and migration | Project revisions record available baselines and preserve user-owned work. Database contents are rebuilt; general state migration is outside scope. | Preserving customized project code still requires inspection of the actual implementation. |
| A09: Conditional applicability | Author-declared applicability is recorded separately from skipped checks; missing required prerequisites remain blocking. | Profiles must not be chosen after failures to disguise a reduced scope. |

## Design assumptions that still need testing

**Sources do not specify transformations by themselves.** A corpus can support several reasonable databases. Authors must define identity, filtering, joins, conflicting statements, missing values, and query meaning. Narrowing the output type does not remove that work.

**Database integrity is necessary but insufficient.** A database can satisfy its schema while dropping supported inputs or storing incorrect facts. Tests need independent source-to-record expectations and source-coverage evidence. Builder-reported counts alone are not an independent check.

**Refresh safety needs executable evidence.** The specification requires retaining the previous accepted database on failure, but does not select a replacement mechanism or promise continuous availability. A package must declare any stronger concurrency guarantees and test them in its supported environment.

**Fixtures and real-source validation serve different purposes.** Fixed fixtures exercise exact semantics and errors. The declared completion build checks the selected source scope. Neither should be presented as a substitute for the other when both are required.

**Implementation freedom needs a usable test boundary.** Authors must define callable interfaces before generation. A test suite tied to undeclared private modules would defeat that freedom even if the package says languages are unrestricted.

**Scope is narrower, not cost-free.** Source acquisition, changing formats, provenance, large builds, test oracles, and documentation can remain substantial work. The new structure removes unrelated application concerns; it does not make those database concerns trivial.

**A smaller repository does not establish the value of generating a builder.** A conventional builder with a source-acquisition recipe also avoids committing a large database. SEED's additional generation step needs evidence of useful adaptation, portability, or maintenance benefits. Compare total authoring, generation, repair, operation, and revision effort.

## Next validation work

Start with a small package that uses bounded, inspectable source files and independent expected query results. It should include duplicates, missing fields, conflicting records, a permitted source update, and a deliberate failed refresh.

Use that package to test:

1. Fresh generation and clean operation from the delivered project.
2. Detection of deliberately incorrect transformations and omitted source records.
3. Successful refresh and preservation of the last accepted database on failure.
4. Relocation to another supported workspace without author-specific paths or caches.
5. The same supplied suite against another independently generated implementation, using another language if permitted.

Then create a larger example with real acquisition and source-coverage requirements. A reference project may inform package authoring and separate evaluation, while its implementation stays outside fresh-generation inputs.

Record unsuccessful attempts, interventions, elapsed effort, and limitations as well as successful results. Compare with maintaining an ordinary fixed builder. No experiment in this section has been performed as part of the documentation revision.

## Reviewed document identities

These hashes identify the document versions reviewed on 2026-10-17; the historical audit retains its own original identities. Later README guidance about skill invocation and the new SKILL.md are outside this dated review. The original hashes are retained rather than implying those additions were audited here.

| Document | SHA-256 |
| --- | --- |
| `README.md` | `559030b88b9f5ea1bf84831a12cfa873a6c4d7831f45e15c357e4bc590dd73a7` |
| `SPECIFICATION.md` | `90850d8d6d77412fc506ca7f10a20fb82b5e0d57e533b301a323accaff30ca29` |
| `templates/SEED.md` | `3123f4ddfbac80e9e91a4f00ce5de4e409b4fb13844e5b030570ad586e9ed552` |

No runner, validator, conformant example package, database build, or independent agent trial has been implemented by this revision. The authoring template deliberately contains guidance in place of executable tests and must be completed before use.
