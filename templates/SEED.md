+++
seed_format = "0.3.0"
name = "replace-with-package-name"
version = "0.1.0"
description = "Replace with the purpose of this reference database project."
+++

# Reference database project title

This is an authoring template, not a runnable or conformant example package. Replace the guidance and placeholders with complete contracts and supplied executable tests.

Use package-relative paths for bundled resources, workspace-relative paths for outputs, and named bindings for external inputs. Bundle normative requirements and tests. Identify supporting resources by role and reuse permission; keep complete reference implementations outside fresh-generation inputs.

## Purpose

Describe the subject, users, questions the database must answer, and exclusions. Its contents must be regenerable from declared sources.

### Deliverables and scope

- OUT-001: Reusable project source, dependency information, and operating documentation at a declared destination.
- OUT-002: Generated database at a declared destination.
- OUT-003: Build records and generation report at declared evidence destinations.
- Completion scope: Name the sources, subsets, and supported profiles that must be built and checked. State explicitly if the entire scope is a bounded fixture demonstration.

### Operating interfaces

Define exact invocations or requests, configuration, results, errors, execution environment, and working-directory base. Operations may share an interface.

- REQ-ACQUIRE: Obtain and verify the sources in Sources.
- REQ-BUILD: Perform a full build and refresh through Transformations.
- REQ-VALIDATE: Check the invariants in Data contract and report failures.
- REQ-QUERY: Expose the operations in Queries.

Declare project dependencies and platform capabilities. Separately identify test-runner and helper dependencies. The agent chooses implementation details unless constrained here. Declare any operational model or service dependency.

### Workloads and limits

For fixture checks, source checkpoints, scale checks, acquisition, full builds, and queries, define the applicable dataset scope, invocation, environment assumptions, time/disk/output limits, metrics, and failure behavior. Explain any inapplicable workload.

The consumer must record a finite run plan with total duration, command deadlines, full-attempt and concurrency allowances, working-data and database byte limits, log limits, and evidence destinations. Package defaults may be supplied here; no format-wide numeric defaults exist. Autonomous model work also requires an externally enforced model spending or usage cap.

Identify required enforcement capabilities, such as a strict filesystem quota when sampled limits would be insufficient. A smaller available allowance may prevent completion; it does not reduce required scope. Define any permitted retry policy within the run allowance.

## Sources

Declare every source, including fixtures and scripted inputs. At least one source is required.

### SRC-001: Source name

- Material and purpose: Define the supplied information.
- Acquisition: Bundled path, downloadable location, scripted procedure, or a combination.
- Selection: Define the permitted release, range, branch, snapshot, or other policy. Exact historical commits are optional.
- Format and scope: Define the selected subset and materially different extraction paths.
- Availability: Required or optional; identify profiles and the effect of absence.
- Verification: Define suitability and content-identity checks.
- Use: Reference the transformations, fields, and queries consuming this material.
- Provenance: Define identities, source locators, attribution, and handling restrictions.
- Reference links: Distinguish citation and record-link URLs from acquisition locations.

For scripts, declare the upstream inputs, helper or procedure to implement, tools, parameters, expected output, and checks. Record what was actually selected and used. For unsnapshotable sources, define consistency handling and limitations. Runtime bindings supply locations or access; they do not replace source declarations.

### Representative cases

Supply bounded inputs and independent expectations for clean builds, changed-source refreshes, and failed refreshes. For external sources, include source-backed cases covering each materially different required extraction path. Bundle permitted excerpts or define acquisition with content checks.

For each case identify the source and exact locator, applicable input identity, expected fields, eligible and excluded relationships, public query requests/results, and test IDs. Explain the selection criteria and known coverage gaps. If reproducing an existing project, verify expectations against source evidence.

Keep fixed expectations tied to their declared inputs. Specify compatibility checks for the current selected snapshot; an allowed branch update does not silently change a fixed case's expected meaning.

## Data contract

### Public schema and field dictionary

- REQ-DATA-001: Specify the database engine and features, or allowed alternatives with test interfaces.
- REQ-DATA-002: Define public schema, types, keys, nullability, constraints, and schema identity.
- REQ-DATA-003: Define provenance, source locators, and any retained source content.
- REQ-DATA-004: Define integrity and source-coverage invariants, including allowed partial results.

Cover every public database and query-result field, including nested structures. Query fields may reference database-field definitions. Shared definitions must list the fields they cover.

| Field | Meaning and type | Source or generating rule | Population rules | Expected example and check |
| --- | --- | --- | --- | --- |
| Replace with public field name | Include units, enum, or structured shape where relevant | Exact source ID/element; derivation with inputs; relationship lookup; or generated value | Null/empty/default behavior, normalization, precedence, and ordering | Source/fixture locator, expected value or constraint, and supplied test ID |

Provide worked rows showing how the fields are populated together. Cover supported missing-value and conflict cases. Generated IDs and timestamps need generating rules and appropriate assertions; exact values need not be identical across builds unless required.

Identify public identifiers, required stability across rebuilds, and how consumers distinguish database revisions. Declare which generated artifacts may be replaced; source inputs and user-owned files remain separate.

### Relationships and scale

For every public relationship define eligible endpoints, matching keys and scope, direction, cardinality, duplicates, unresolved cases, and ambiguity. Include query-only relationships. Distinguish an inferred candidate from a confirmed relationship.

Where associations can multiply, supply a bounded repeated-key/multiple-target workload with eligible and excluded targets, expected logical results, and measurable storage or work limits. Record dataset size, environment assumptions, metric, and threshold. If this risk does not apply, explain why.

Implementation choices such as shared sets, indexes, and materialized joins remain free unless explicitly constrained. Limits must preserve required results.

## Transformations

- REQ-TRANSFORM-001: For each source, specify extraction, normalization, filtering, identity, joins, deduplication, and conflict rules.
- REQ-TRANSFORM-002: Specify missing, malformed, unsupported, contradictory, and uncertain input handling. Distinguish inferred values from extracted facts and explain coverage accounting.
- REQ-REFRESH-001: Support a full rebuild through the documented interface. Validate a candidate before making it current; preserve the previous accepted database when a refresh fails.

Declare stage inputs, outputs, diagnostics, failure conditions, and allowed warnings. If partial extraction is supported, define allowable omissions and mandatory supported cases. A partial-file status cannot waive those cases.

Define checkpoint selection and checks for bounded inputs from the selected sources. These checks must exercise required extraction paths and mandatory cases before construction beyond fixture scope. Ordinary build/query interfaces may implement the checkpoint.

Record implementation, schema/configuration, resolved and installed dependencies, toolchain, and relevant source identities for verification. Affected checkpoints must pass again after changes. Retain an extraction failure's input identity and obtain a passing small regression before another authorized full attempt.

A routine source refresh uses the delivered builder without regenerating project code. Add concurrency guarantees only where required.

## Queries

### QUERY-001: Operation name

- Requirement: Identify a stable requirement such as REQ-QUERY-001.
- Invocation: Specify the public CLI, SQL, library, or API interface.
- Inputs: Define parameters, filters, types, and valid limits.
- Results: Define fields through the dictionary, result meaning, ordering, and identifier semantics.
- Bounds: Cover top-level and nested collections and text. Define truncation, pagination, streaming, or rejection, and the meaning/availability of totals.
- Errors: Define missing results, ambiguous matches, invalid input, and database compatibility behavior.
- Examples: Supply requests and independent expected results tied to source/fixture records, with applicable error cases.
- Dependencies: Identify runtime components or retained assets.
- Deadline: Define a workload limit for the run plan; distinguish it from any mandatory performance threshold.

Queries are read-only over the database and declared runtime dependencies. They must not rely on undeclared checkouts, caches, or the original agent session.

## Acceptance

Supply executable tests inline or as explicitly referenced bundled files. A checklist or an instruction for the agent to write tests is insufficient. Map each mandatory behavior, field, relationship, query, and deliverable to supplied checks. Expected results come from the contract or an independent author-supplied oracle.

### Required coverage

| Area | Author must supply |
| --- | --- |
| Clean operation | Set up the delivered project with declared dependencies, prepare inputs, build in a new location, validate, and query. |
| Data fidelity | Expected records and field population, relationship eligibility, provenance, coverage, and relevant negative cases. |
| Query behavior | Assertions through the actual public interface, including bounds, errors, ordering, and ambiguity. |
| Refresh | Successful source change and failed refresh preserving the previous accepted database. |
| Completion scope | Checks against the actual selected sources and database required by Purpose. |

Include source-backed cases and applicable scale workloads in those checks. Supply bounded demonstrations that representative incorrect outputs are rejected: for example a missing required record, incorrect field, or ineligible relationship. These may use small altered artifacts; a second implementation is unnecessary.

### TEST-001: Supplied test or group

- Content: Embed executable code or reference a bundled test file.
- Coverage: Identify requirements, fields, relationships, queries, and deliverables.
- Inputs: Identify fixture/source IDs and independent expected values or assertions.
- Execution: Define setup, dependencies, invocation, working-directory base, workload limits, and the interface to actual deliverables.
- Checkpoint: State whether it runs before a full build, against the completed build, or both.
- Applicability: Always, or a declared condition based on supported scope. Decide before observing results.
- Evidence: Define results, logs, input/project/dependency identities, and observed process outcomes.
- Changing sources: Explain how assertions apply under the source-selection policy.

The consumer must verify writable evidence destinations and enforced limits before launch. Preserve durable start records, bounded diagnostics, terminal or unknown/interrupted state, and cumulative attempts. Do not infer success from file growth or reuse a successful check from a changed implementation.

Tests must not impose hidden implementation languages or private layouts. Missing prerequisites for applicable required checks block acceptance. A fresh generation still requires fixture refresh tests.

### Comparison and completion

Independent behavioral acceptance is the default; declared schemas and interfaces always apply. If comparisons across builds are required, define input conditions, ordering, identifier mapping, ignored fields, and tolerances. Identical database bytes are not assumed.

All applicable required supplied tests must run and pass. Known mandatory violations prevent completion even when tests pass. Additional tests cannot replace the supplied suite. Define any required human review and its rubric.

Preserve each build record and the generation report required by the specification, including scope, identities, run allowance and enforcement, resource use or unavailable values, applicability, test evidence, failures, limitations, and deliverable locations. Use relative references and binding names.

Fresh generation is the default. For a requested project revision, identify the existing target and recoverable baseline, preserve user changes and sources, and run the current applicable suite. Review or editing alone does not start a reconstruction.
