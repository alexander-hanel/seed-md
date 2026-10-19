+++
seed_format = "0.1.0"
name = "replace-with-package-name"
version = "0.1.0"
description = "Replace with a short description."
+++

# Project title

This is an authoring template. Replace all placeholders before distribution. Use package-relative paths for bundled resources, workspace-relative paths for outputs, and named runtime bindings for external local resources. Do not include paths from the author's machine.

## Objective

Describe the project, intended users, purpose, and scope without relying on an existing implementation. Keep any complete reference implementation outside the package and fresh-generation inputs. An explicitly requested update may use the existing generated project selected by the user. Label supporting resources by role and state whether they may be reused.

## Deliverables

- OUT-001: Describe the required output, destination, form, and public contract.

## Inputs

Reproduction target: Behavioral (default).

Independently generated projects must satisfy the specifications and supplied tests. Declare any stronger structural or exact target here, with the affected deliverables, properties, and comparison method. Explicit interface and output-format requirements apply under every target. Define tolerances or accepted variation where relevant. Permitted changes in source data may change results; record the data actually used.

Define every data source here or reference a normative supporting document. If none exist, state `Data sources: None` and explain why. Remove the following entry if it does not apply.

### SRC-001: Source name

- Material and purpose: Describe the information or assets supplied.
- Acquisition: Bundled, downloadable, scripted, or a combination. Identify a package-relative resource, portable remote location, or acquisition procedure.
- Selection: Specify a release, version range, branch, or other documented policy. Exact source commit matches are optional.
- Format and scope: Describe the expected format and relevant subset.
- Stage: Construction, verification, operation, or a combination.
- Availability: Required or optional; describe the effect of absence.
- Verification: Describe how to establish that the material is suitable.
- Use: Identify the functions, actions, or requirements consuming the material and any transformations.

For scripted acquisition, describe the helper code or procedure to implement, tools, parameters, upstream inputs, expected outputs, and verification. Declare other inputs or prerequisites as needed. Runtime bindings supply actual host locations when the package is used; they do not replace source definitions. Record resolved identities when available.

## Requirements

- REQ-001: Define a required function or action for OUT-001. Identify the data sources it uses, where applicable, its inputs, outputs, and failure behavior. For an action, state its trigger or invocation and expected state changes or side effects. Reference SRC-001 if that source applies.

## Constraints

Implementation freedom is the default: the agent chooses its language, libraries, tools, architecture, algorithms, and internal structure unless explicitly constrained here or in a referenced normative contract.

Declare required environment capabilities, tools, resource limits, and workspace constraints, or state None. Identify tools by name and version rather than by paths to the author's installations. Separate requirements for test runners and acquisition helpers from restrictions on the generated project. Label optional implementation guidance explicitly.

## Construction

Describe required creation stages. Label optional guidance explicitly. Reference data-source declarations for acquisition and preparation actions, including the expected material passed to later stages.

Run mode: Fresh generation by default. Update an existing generated project only when explicitly requested and the target is identified.

Describe any compatibility guarantees, supported prior versions, migration steps, and preservation requirements for updates, or explicitly state that no migration guarantees are provided. Preserve user changes and data; report conflicts that prevent satisfying the revised requirements. The current package must also stand alone for fresh generation.

## Acceptance

Supply executable tests derived from the specifications, required functions and actions, and declared data. Embed the actual test content or reference bundled test files; instructions for the generating consumer to write tests are insufficient. Cover every mandatory requirement and deliverable. Test declared interfaces and outputs. Do not require a particular implementation language or private structure unless it is an explicit package requirement.

- ACC-001: Covers OUT-001 and REQ-001, evaluated by TEST-001.

### TEST-001: Supplied acceptance test

- Content: Provide the actual executable test inline or identify a bundled test file.
- Coverage: Identify ACC-001, REQ-001, OUT-001, and the functions or actions exercised.
- Data: Identify SRC-001 or the relevant fixtures, or state that this test uses no data.
- Execution: Define setup, dependencies, invocation, working-directory base, and interface to the generated deliverable.
- Expectations: Define expected results or assertions derived from the specification, including failure cases and any tolerances.
- Changing sources: Explain how expectations remain valid for the declared source selection policy, if applicable.
- Evidence: Define the test results and supporting evidence to retain.

Every required supplied test must run and pass. Agent-created tests may supplement this suite but cannot replace it. If additional human review is required, define its rubric and reviewer role. For updates, run the current package's complete required suite, including tests for any declared compatibility or migration requirements. Success under an earlier package version is insufficient.

## Completion

Claim completion only after all required outputs and acceptance criteria are satisfied, every required supplied test has run and passed against the delivered result, and any additional required reviews are complete. Failed, skipped, unavailable, or waived required tests prevent completion.

Write the run report to `seed-run-report.md` in the target workspace with the fields required by the SEED specification, including the run mode and implementation choices made. If a previous report occupies that destination, preserve it under a distinct workspace-relative name before publishing the new report. Use relative evidence paths and binding identifiers.

For updates, record the previous and current package identities, the existing project identity, changes made, preservation or migration outcomes, and current acceptance results. Report unavailable historical information as unknown. Hand back the deliverables, their locations, and the acceptance status.
