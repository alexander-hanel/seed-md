# Status 
Don't use. This is a concept I'm playing around with. 

# SEED

SEED is a package format for instructing an AI agent to create a reusable project that builds and queries a regenerable reference database.

The package supplies data sources, field mappings, transformation rules, query behavior, and executable acceptance tests. The agent creates the implementation. The delivered project can acquire its inputs, build and validate a database, and answer queries through documented interfaces without returning to the original agent session.

The database is generated output, so a large database need not be distributed with its seed. The deliverable includes reusable project source, dependencies, operating instructions, the required database build, and evidence of what passed. Any model or service needed during normal operation must be a declared, testable dependency.

## Review this baseline

The current format is **0.3.0, draft**. Start with the [review guide and changes](CHANGES.md), then read the [specification](SPECIFICATION.md) for the requirements.

| Document | Role |
| --- | --- |
| [SPECIFICATION.md](SPECIFICATION.md) | Authoritative requirements for packages, consumers, and execution evidence. |
| [templates/SEED.md](templates/SEED.md) | Authoring guidance for the six required package sections; complete it with actual contracts and tests. |
| [SKILL.md](SKILL.md) | Reusable instructions for an agent following a package. |
| [CHANGES.md](CHANGES.md) | Changes from 0.2.0, review points, and migration limits. |
| [AUDIT.md](AUDIT.md) | Dated review of the earlier 0.2.0 design; it does not validate this baseline. |

## What a seed defines

Every package starts with `SEED.md`, containing six sections:

| Section | Defines |
| --- | --- |
| Purpose | Users, supported questions, deliverables, operating interfaces, build scope, and workload limits. |
| Sources | Acquisition, selection, source identities, and representative input cases. |
| Data contract | Public fields and their population rules, schema, relationship eligibility, and scale requirements. |
| Transformations | Extraction, normalization, conflicts, omissions, mandatory supported cases, and refresh behavior. |
| Queries | Requests and expected results, ordering, ambiguity, errors, and output bounds. |
| Acceptance | Supplied executable tests, checkpoints before full construction, and retained evidence. |

Every public database and query field must explain where its value comes from. A schema alone cannot tell an agent which source element to use or how to resolve conflicting values. Generated values such as identifiers have generating rules; they do not need a fictional upstream field.

For example, an illustrative input record `{"code":"A7","name":" North ","region":"NW"}` might produce:

| Public field | Population rule | Expected value |
| --- | --- | --- |
| `stations.code` | Copy the input's `code`. | `"A7"` |
| `stations.name` | Trim surrounding whitespace from `name`. | `"North"` |
| `stations.region_id` | Resolve `region` against the unique `regions.code`; reject a missing match. | The ID of the region whose code is `"NW"`. |

A complete package also declares the source locator, types, missing-value behavior, fixtures, and executable assertions. Relationship rules must say which targets are eligible, what multiple matches mean, and how duplicates are handled. Query examples continue that same trace from source to stored fields to observable results.

Sources may be bundled, downloaded from Git or other locations, or acquired and prepared by scripts. Exact historical commits are optional: packages may permit releases, branches, or other selection policies while builds record the inputs actually used. Citation URLs have a different role from acquisition locations.

The agent chooses its implementation language, libraries, algorithms, and internal layout unless the package explicitly constrains them. A test runner's language does not determine the project's language. Complete reference implementations stay outside fresh-generation inputs; permitted helpers have declared roles and reuse permissions.

## Using the SEED skill

`SKILL.md` explains how an agent should follow a seed. Each project's `SEED.md` contains that project's requirements.

Make `SKILL.md`, `SPECIFICATION.md`, and `scripts/run_bounded.py` available together, preserving the scripts directory, in a skill folder named `seed`. Register it through the agent's supported skill mechanism. The current skill supports format `0.3.0`; older packages need migration or a consumer explicitly supporting their declared format.

With an agent that supports named skill invocation, a user can say:

```text
Use $seed to build the package in packages/example/.
```

Otherwise explicitly instruct the agent to read the skill and the selected package. A fresh or delegated agent must receive those files and instructions; they are not assumed to be inherited. For an independent reconstruction, use an isolated workspace containing the permitted inputs and record its actual isolation.

## Construction and acceptance

Before a full build, check the recorded project and dependency snapshot against small fixtures, representative selected-source cases, and applicable relationship-scale workloads. Mandatory cases remain required even if their containing file is partially extracted. These checkpoints expose specific defects early; they do not replace acceptance of the required full scope.

Supplied tests exercise a clean build, field and relationship fidelity, public query behavior, and successful and failed refreshes. Authors also supply checks showing that representative incorrect outputs are rejected. Passing tests supplies evidence for the checked cases; known violations still prevent completion.

The consumer records finite execution allowances for duration, attempts, concurrency, disk, and logs. Autonomous model workers additionally need an externally enforced spending or usage cap. The execution environment enforces those limits and preserves failure evidence. A time limit is not a token limit. The included command supervisor is a Linux helper, not a model-budget service or an isolation boundary.

Acceptance is behavioral by default. Declared schemas and query interfaces apply, but permitted source revisions, implementation code, and database bytes need not match across runs. Packages define any stronger comparison.

## Operation and revision

Refreshing data means running the delivered project against newly selected sources. It validates a replacement before making it current and preserves the last accepted database if the refresh fails. Revising project code supports a changed contract or input format; routine refreshes must not depend on interactive agent repair.

This format covers reference databases whose contents can be regenerated. User annotations belong in separately declared sources or external storage if they must survive rebuilding. General transactional applications and migration of user-edited database state are outside this draft's scope.

Published packages use portable references and named runtime bindings. They contain no assumptions about the author's filesystem, neighboring checkouts, caches, or previous sessions.

## Repository checks

Run the core suite from the repository root on Linux with Python 3:

```sh
python3 -B -m unittest discover -s tests -v
```

These offline tests exercise the generic process supervisor using only the Python standard library. They create their own small temporary inputs and do not depend on example packages, acquired data, or the repository's ignored `tmp/` directory.

Example-specific authoring checks live beside their examples. The [WinAPIDB draft](examples/winapidb/README.md) has a separate suite:

```sh
python3 -B -m unittest discover -s examples/winapidb/tests -v
```

These commands run local checks; they do not reconstruct a project or download a corpus.

## Validation status

This baseline incorporates lessons from an unsuccessful reconstruction and subsequent targeted comparisons. It has not been demonstrated by a successful full reconstruction under format 0.3.0. Documentation and skill checks do not establish that an agent will successfully build a project.

The [WinAPIDB draft package](examples/winapidb/seed/SEED.md) remains on format 0.2.0 pending a separate migration review. Its previous evidence is not a 0.3.0 acceptance result. The superseded general-purpose draft remains under [history/0.1.0/](history/0.1.0/README.md).
