# SEED format specification

Version: 0.1.0  
Status: Draft

## 1. Purpose and scope

A SEED is a portable package of instructions, specifications, declared inputs, and acceptance criteria that an AI agent uses to create a project.

The package defines what constitutes a satisfactory result while leaving implementation choices open unless explicitly constrained. It MUST supply acceptance tests derived from its specifications, required functions and actions, and declared data. It may also contain supporting code, schemas, fixtures, or templates, and MUST describe enough of the intended behavior to evaluate the result independently of the generated implementation.

A package MUST NOT contain a complete reference implementation of the project it instructs the consumer to create, or direct the consumer to retrieve one as input for fresh generation. An existing implementation MAY be used separately for evaluation. Its source MUST NOT be required to understand the specification or supplied as a substitute for that specification. Ordinary dependencies, tools, and source-code datasets are permitted; this restriction concerns a ready-made implementation of the target project.

For an explicitly requested update, the consumer MAY read and adapt the existing generated project selected by the user, as described in section 7. That project remains outside the SEED package and is identified as the update target. This does not permit bundling a complete reference implementation or making fresh generation depend on an earlier implementation.

Supporting code MAY include templates, examples, acquisition helpers, or verification helpers. The package MUST identify each supporting resource's role and whether it may be reused in the generated project. Supporting resources MUST NOT collectively supply the complete target implementation. The generated project is accepted against the declared requirements; its source layout and repository history need not match any prior project.

This specification defines package structure, instruction semantics, execution responsibilities, and completion evidence. It does not define a runner, agent API, dependency manager, registry, archive extension, or deployment protocol.

The terms MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY express requirements, recommendations, and options within this specification. These requirements apply to participants claiming SEED conformance; they do not grant an agent authority beyond its host environment or the user's authorization.

## 2. Terms

- **Package:** The SEED entry point and all bundled supporting files.
- **Author:** The person or system defining a package.
- **Consumer:** The agent or orchestration system interpreting the package.
- **Input:** Material or a prerequisite needed to create or verify the project.
- **Data source:** A declared origin of information, assets, or source material used to create, verify, or operate the project.
- **Function:** A capability the generated project must provide, independent of how it is divided into code routines.
- **Action:** An operation performed during construction or by the generated project, with defined inputs, a trigger or invocation, and an observable result.
- **Generated project:** The implementation and associated project files created by the consumer.
- **Deliverable:** A required output, including a generated project, artifact, or running capability.
- **Acceptance criterion:** An observable condition used to decide whether a deliverable satisfies a requirement.
- **Supplied acceptance test:** An executable check provided as normative package content, with defined inputs and expected results or assertions derived from the specification. It establishes acceptance independently of tests created during generation.
- **Fresh generation:** Creating a project from the package without relying on a previous implementation of the target project.
- **Update:** Adapting an existing generated project selected by the user to satisfy the current package.
- **Run:** One attempt to generate or update a project from a package in a target workspace.
- **Run report:** A record of the inputs, actions, results, and acceptance evidence for that attempt.

## 3. Package layout and discovery

A package MUST have a UTF-8 Markdown file named `SEED.md` at its root. This is the sole required package filename. Acceptance test content is required; it MAY be embedded in the entry point or placed in explicitly referenced bundled files. Supporting files MAY use any layout.

A consumer MUST begin with this entry point and follow its explicit references. It MUST NOT assume that an arbitrary file in the package is an instruction source. The entry point MUST identify which supporting files are normative specifications and which are examples, fixtures, reference material, or implementation guidance.

Paths identifying package resources resolve from the package root, regardless of the consumer's working directory. Markdown links between bundled documents resolve relative to the document containing the link, so ordinary repository rendering works. Both forms MUST remain within the package root after resolution. External inputs are declared separately through named runtime bindings or portable acquisition locations.

Remote specification references MUST be declared as inputs. An exact reproduction claim requires immutable content identities for those references as well as for other inputs.

Symlinks MUST NOT be used to bypass package boundaries. A consumer MUST reject unsafe archive paths and MUST resolve package paths before using them.

A package MAY be distributed as a directory, repository subtree, or archive. Distribution form does not change these semantics.

### Portability

Published packages and their instructions MUST be independent of the author's filesystem layout and previous execution environment. They MUST NOT contain author-machine absolute paths, home-directory references, local file URIs, editor-specific links, or assumptions about neighboring checkouts, caches, temporary directories, or previous sessions.

Bundled resource paths MUST use relative paths with forward slashes. Deliverable and evidence paths MUST be relative to the consumer's target workspace unless they refer to a declared external binding. Repository documentation MUST use portable relative links for bundled documents when links are included. Consumers map these references to their own filesystem conventions.

An input supplied from the consumer's environment MUST have a named binding, such as `INPUT_DATA`, with its purpose, expected form, and verification requirements declared in the package. The consumer supplies the actual location when running the package. A binding name is not an assumed environment variable or an implicit string-substitution syntax; any command-specific mapping MUST be declared. A binding MAY resolve outside the package or workspace without making that host-specific location part of the published package.

Tool requirements MUST identify capabilities, names, or versions rather than executables in the author's installation. An operating system, architecture, or platform MAY be a declared project requirement; the format itself imposes none. Commands MUST declare their execution environment and portable working-directory base.

Relocating a package or target workspace MUST NOT require editing the package's normative instructions. Runtime binding values may change with the consumer's environment. Consumers MUST NOT write resolved host paths back into published specifications or templates.

## 4. Entry-point metadata

`SEED.md` MUST begin with the following metadata block, using the shown delimiters and TOML syntax:

```text
+++
seed_format = "0.1.0"
name = "example-project"
version = "0.1.0"
+++
```

`seed_format` identifies this format's version. `name` identifies the package and MUST match `[a-z0-9]+(?:[._-][a-z0-9]+)*`. `version` identifies the author's package revision. Both version fields MUST use three nonnegative decimal components separated by dots, without leading zeros except the value zero itself.

Metadata MAY include `description`, a string. Additional metadata keys MUST start with `x_`; consumers MAY ignore them. Authors MUST NOT make acceptance depend on an extension unless its semantics are documented as a required prerequisite.

Consumers MUST reject malformed metadata or missing required fields. A consumer MUST declare which format versions it supports and MUST NOT silently interpret an unsupported version. In the draft 0.x series, support for one minor version does not imply support for another. A patch revision is intended to clarify compatible semantics.

Package version and format version are independent. Authors MUST change the package version when normative package content changes, including requirements, source-selection rules, bundled normative inputs, or supplied acceptance tests. Changes to external data within an unchanged permitted source-selection policy do not by themselves require a new package version; the run records the data actually used.

Each revised package MUST remain sufficient for fresh generation of a project satisfying its current specification. Earlier package versions or generated implementations MUST NOT be required to explain the current requirements. Compatibility and migration promises MUST be stated explicitly; a version number alone does not establish them.

A content digest identifies the actual package used; the version string alone is not proof of identity.

The metadata is deliberately small. Version 0.1 does not prescribe a separate machine-readable manifest or lockfile schema.

## 5. Required content

The body MUST contain the following level-two headings, once each. Their contents MAY reference bundled normative files. Additional sections MAY be added. Empty required sections are invalid; an inapplicable section MUST explicitly say so.

### `## Objective`

State the intended project, its users or consumers, the problem it solves, and the scope. State material exclusions where they prevent ambiguity. The objective MUST be understandable without access to an existing implementation.

### `## Deliverables`

List each required output with a stable identifier, its form, its destination relative to the target workspace or a declared external binding, and its observable interface or contract. Distinguish the generated project from artifacts it produces. Declare whether build instructions, operation instructions, or source files are required.

Destinations requiring external publication MUST be identified explicitly. Declaring a destination does not authorize publication.

### `## Inputs`

Every package MUST explicitly define its data sources in this section or in a normative supporting document referenced from this section. A consumer MUST NOT have to infer where the project's data comes from. If there are no data sources, state `Data sources: None` and explain how the project operates without them. Declare other inputs or prerequisites here as needed.

For each data source, declare:

- A stable identifier and the information or material it supplies.
- Its origin and acquisition method, with a package-relative resource path, a downloadable location, or a defined acquisition procedure.
- Its expected format, relevant scope or subset, and identity or selection rule.
- Whether it is needed during construction, verification, operation, or more than one of these stages.
- Whether it is required or optional, and the effect of its absence.
- How to verify that the acquired material is suitable for its intended use.
- The functions, actions, or requirements that use it, including relevant filtering or transformations.

Data sources support the following acquisition methods, which MAY be combined:

- **Bundled:** Material distributed inside the package and addressed relative to its root.
- **Downloadable:** Material acquired from a declared repository, archive, package service, or other remote source. Git repositories are one supported source type; exact commits are not required by the format.
- **Scripted:** Material acquired, extracted, or produced by executing scripts or code. Declare where the helper code comes from or the procedure the consumer must implement, its tools and parameters, its upstream inputs, its expected outputs, and how to verify those outputs. Acquisition helpers do not replace the declaration of the underlying data source.

For example, a downloadable package may be processed by an extraction script to provide header files. Each step and the material consumed by the generated project must be identifiable. Source code used as data is permitted under the reference-implementation boundary in section 1.

Runtime bindings provide consumer-specific locations or access for declared resources; they do not replace data-source declarations. If data is supplied during operation, define its expected form and how it enters the project. An external location alone MUST NOT be represented as an immutable identity.

Exact source commit matches are not a format requirement. An author MAY select inputs by a release, version range, branch, or documented freshness and compatibility policy. Commit pins and checksums MAY be required by an individual package when justified by its contract.

For mutable inputs, declare the selection policy and require the run to record the resolved identity or snapshot when possible. Recording the commit actually used does not require future runs to select that same commit. For optional inputs, define the effect of absence. For required unavailable inputs, the consumer MUST report the blocked requirement instead of silently substituting content.

Declare relevant transformations, filtering, provenance requirements, attribution, and applicable handling restrictions. Credentials MUST be supplied through environment bindings or equivalent secret handling; they MUST NOT be embedded in the package or run report.

### `## Requirements`

Assign stable identifiers to mandatory behaviors and quality requirements, such as `REQ-001`. Define observable behavior, supported cases, failure behavior, and interpretation rules precisely enough to evaluate the outputs. Identify normative contracts and fixtures here or through explicit references.

Define the project's required functions and actions, identifying the data sources they use where applicable. Specify their inputs, outputs, and observable behavior; actions MUST also identify their trigger or invocation and any required state changes or side effects. These descriptions concern project behavior and do not require a particular arrangement of code routines. A source-to-use relationship MAY be stated once and referenced from the corresponding requirements.

Implementation freedom is the default. Within the declared requirements, constraints, and authorized environment, the consumer MAY choose the language, libraries, architecture, algorithms, build tools, and internal project structure. A package is not required to prescribe a language or toolchain. The consumer MUST preserve the specified behavior, interfaces, data handling, and acceptance conditions.

Clearly label recommendations and examples. Suggested architecture or tools MUST NOT implicitly become mandatory requirements. An illustrative implementation, helper, or test written in a particular language does not by itself require the generated project to use that language. Unspecified implementation details remain the consumer's choice.

### `## Constraints`

State required environmental capabilities, tool or runtime restrictions, resource limits where relevant, permitted acquisition or network behavior, and any operations requiring an external binding or approval. State `None` if there are no package-specific constraints.

Any mandatory choice of implementation language, library, architecture, toolchain, or internal structure MUST be stated explicitly here or in an identified normative contract referenced here. Such restrictions MUST be distinguishable from optional guidance and covered by acceptance criteria. Requirements for running acquisition helpers or acceptance tests MUST be identified separately from requirements for the generated project.

State how existing target-workspace content must be handled, including user changes and persisted data when updating a project. If unspecified, consumers MUST preserve unrelated content and user changes and MUST report conflicts that cannot be resolved without destructive changes.

### `## Construction`

Describe the intended creation workflow, dependencies between stages, and any required intermediate results. The workflow MAY be high-level and MAY allow the consumer to select tools or architecture. It MUST distinguish normative steps from advisory approaches. For acquisition and preparation actions, reference the declared data sources and identify the expected material passed to subsequent stages.

Fresh generation is the default. A package MAY additionally define compatibility guarantees, supported prior versions, and migration steps for explicitly requested updates. Declare any required data migration or preservation behavior and provide supplied tests for those requirements. An update request does not imply a compatibility guarantee that the package has not declared.

Commands MAY be supplied, but MUST declare their working directory, relevant environment assumptions, and expected result. Commands are not required for construction stages that use other interfaces. Advisory commands or example workflows MUST NOT silently restrict the consumer's implementation choices; required construction steps MUST be explicitly identified.

### `## Acceptance`

The package MUST supply executable acceptance tests that establish whether the generated project succeeds. These tests MUST be derived from the specifications, required functions and actions, and declared data. Instructions telling the generating consumer to invent its own acceptance suite do not satisfy this requirement.

Give each acceptance criterion a stable identifier and identify the supplied tests that evaluate it. Every mandatory requirement, function, action, and deliverable MUST be covered by at least one supplied test. A test MAY cover several requirements. Tests MUST identify the relevant data sources or fixtures; checks that do not use data MUST state that explicitly. Tests MUST exercise the declared behavior and outputs rather than rely on implementation assertions of success.

For each supplied test or test group, define:

- A stable identifier and its normative test content, either embedded verbatim or in bundled files.
- The acceptance criteria, requirements, functions, actions, and deliverables it covers, with relevant data-source references.
- The setup, execution environment, dependencies, invocation, and interface to the actual generated deliverables.
- The input data or fixtures and the expected results, assertions, or comparison procedure derived from the specification.
- The pass conditions, any tolerances, and the evidence to retain, including failures and checks that did not run.

When source data may change, the supplied tests MUST specify how expectations remain valid under the source selection policy. They MAY use fixed fixtures, properties that must hold for every accepted input, or a supplied independent procedure to derive expected results from the acquired data. A change in source commit is not itself a failure unless the package requires a particular commit. Expected results MUST NOT simply be copied from the generated implementation's output.

Supplied tests MUST evaluate the specified behavior, outputs, and declared interfaces. They MUST NOT impose an unstated implementation language, private module layout, algorithm, or dependency. Checks of implementation details are permitted only when those details are explicit requirements. Test-runner dependencies do not by themselves constrain the implementation language of the generated project. A public interface that requires a particular runtime or language binding MUST be declared as part of the contract.

The consumer MAY add implementation and diagnostic tests, but they MUST NOT replace or weaken the supplied acceptance tests. Inline supplied tests MAY be materialized into files without changing their meaning. Any required integration adapter MUST preserve the test assertions and invoke the actual deliverables through the declared interface.

Inspection, demonstrations, or human review MAY supplement the supplied tests. Human review MUST define a rubric and identify the reviewer role. Required review remains pending until performed; review cannot turn a failed required test into a pass.

The package MUST distinguish required tests and reviews from advisory evaluation. It MUST define any allowed warnings or tolerances. Every required supplied test MUST run and pass before completion can be claimed. A failed, skipped, unavailable, or waived required test prevents completion under the unchanged package. Partial success MAY be reported as progress but does not satisfy full acceptance.

### `## Completion`

Define when the consumer may claim completion, identify the required run-report destination, and state what must be handed back to the user. Any external acceptance or publication step MUST be identified.

Completion MUST require all mandatory deliverables and acceptance criteria to be satisfied, with every required supplied test executed and passed against the delivered result. A prototype, limited-data build, successful compilation, or passing agent-created tests alone MUST NOT be called complete unless the supplied acceptance suite and declared objective are also satisfied.

## 6. Input identity and reproduction

Behavioral reproduction is the default. Independently generated projects MUST satisfy the same specifications and supplied acceptance tests for inputs permitted by the package. Implementations, internal organization, source commits, and artifact bytes may differ unless explicitly constrained.

A package MAY declare stronger reproduction targets in the Inputs section, identifying the deliverables and properties to which they apply:

- **Behavioral:** Required behavior and results satisfy the specified conditions and tolerances. This target applies when no stronger target is declared.
- **Structural:** Behavioral acceptance plus specified public interfaces, file formats, schemas, or other output structures must match. Unspecified internal organization remains free.
- **Exact:** Behavioral acceptance plus named artifacts must match specified bytes or digests under declared conditions.

Explicit interface and output-format requirements always apply, including under the behavioral default. The target label MUST NOT be used to disregard a declared contract. Different targets MAY apply to different deliverables, but a consumer MUST NOT imply structural or exact reproduction beyond the scope explicitly required and verified.

For the same inputs, the required results MUST agree within the specification's declared conditions and tolerances. The supplied tests MUST define the comparisons or accepted variation for nondeterministic behavior where relevant. This does not require equality of unspecified implementation details or artifact bytes.

When a permitted data source changes, results MAY change accordingly. The run MUST record the resolved data identities and verify the project against the applicable expectations in the supplied tests. Differences caused by permitted input changes do not by themselves invalidate behavioral reproduction.

A prior implementation or a matching repository history is not required to establish behavioral reproduction. The specification, data declarations, and supplied tests define the acceptance contract. No target guarantees correctness beyond that contract.

An exact target MUST declare immutable identities for all inputs affecting the named artifacts, required environment controls, and expected artifact digests or an independently specified comparison procedure. If those conditions cannot be met, exact reproduction MUST remain unverified.

Source lockfiles, content inventories, checksums, toolchain locks, and environment images MAY be used. Their format is package-defined in version 0.1. Checksums establish content identity, not publisher authenticity. Exact reproduction is an optional package requirement. Behavioral and structural targets do not require identical source commits across runs unless the package explicitly imposes that constraint.

A run MUST record actual input identities, including relevant local modifications. A repository commit alone is insufficient when modified or untracked files affect the result. For services or inputs that cannot be snapshotted, record the limitation and evaluate only the declared achievable reproduction target.

## 7. Consumer lifecycle

Fresh generation is the default run mode. An existing project in the target workspace, a newer SEED version, or the availability of previous outputs does not by itself authorize an update. A consumer MAY update an existing generated project when the user explicitly requests it and identifies the target. Format support for updates does not require every package to guarantee migration from every earlier version.

A conforming consumer MUST:

1. Read the entry point, validate metadata, resolve normative references and supplied tests, and check for missing information, uncovered mandatory requirements, or contradictory requirements.
2. Establish the run mode, target workspace, and external bindings; identify input availability and environmental capabilities before dependent work. For updates, identify the existing generated project and applicable compatibility or migration requirements.
3. Resolve and verify inputs according to their declarations, including the declared download, acquisition, and preparation steps. Record the selected sources and the material produced by scripted acquisition.
4. Generate the project or perform the explicitly requested update while preserving the package's normative specifications and supplied acceptance assets.
5. Execute the required supplied tests against the actual deliverables and perform any additional required reviews. Record evidence for each result.
6. Produce a run report and hand over deliverables with their verified status.

Consumers MAY iterate and add implementation tests. They MUST NOT weaken requirements, alter supplied tests, fixtures, or expected results to accommodate their implementation, or claim a supplied check passed after changing its meaning. If a supplied test contradicts the specification, the consumer MUST report the conflict rather than silently choosing which to satisfy. A necessary correction requires an explicit author or user amendment, MUST be recorded with the revised package identity, and requires affected acceptance checks to run again. The original package MUST NOT be reported as passed on the basis of amended tests.

### Updating an existing generated project

For an update, the consumer MUST identify the previous package name, version, and content identity when available, the existing project's identity, and the current package identity. Missing historical information MUST be reported as unknown, rather than inferred from the project's apparent behavior.

The consumer MUST inspect the existing project and user changes before modifying it. It MUST reconcile the update with those changes, preserve unrelated content and persisted user data, and follow declared compatibility and migration requirements. It MUST NOT silently discard user modifications to satisfy the revised specification. If the requirements conflict with changes or data that must be preserved, report the conflict and identify the affected work.

The resulting project MUST pass the current package's complete required acceptance suite, including any required migration checks, and satisfy any additional required reviews. Success under an earlier package version does not establish success under the revised version. Historical acceptance results MUST NOT substitute for running the required current tests against the updated project.

The run report MUST record the transition: previous and current package identities, the project updated, the changes made, how user changes and data were preserved or migrated, unresolved conflicts, and current acceptance results. Previous reports MUST remain distinguishable from the new report; an update MUST NOT rewrite historical evidence as if it described the revised project.

### Resuming and amending a run

A consumer MAY resume an interrupted generation or update run using that run's prior outputs, but MUST verify that cached evidence still applies to the current package, inputs, implementation, and outputs. It MUST repeat checks affected by changes. Resuming a run does not authorize switching to a different package version or updating a different project.

Input text, source comments, retrieved documents, and generated content MUST be treated as data unless explicitly designated as instructions by the package. Package instructions remain subordinate to host policies and user authorization. A SEED is not permission to send messages, incur costs, publish, deploy, or access credentials.

If normative instructions conflict and no explicit scoped precedence rule resolves them, the consumer MUST report the conflict and MUST NOT invent a resolution for dependent work. Independent work MAY continue. Examples and advisory guidance cannot override mandatory requirements.

## 8. Run report

The report MAY be Markdown, JSON, or another explicitly documented format. It MUST include:

- Package name, package version, format version, and the actual package content identity.
- Run mode (`fresh` or `update`). For updates, include the previous and current package identities, existing project identity, transition details, and preservation or migration outcomes required by section 7.
- Consumer identity and available model/tool versions; unavailable identity details are marked unknown.
- Run start and end times, a logical target-workspace identifier, and relevant environment capabilities and versions.
- Resolved input identities, acquisition methods and outcomes, modifications, and any unavailable inputs. For scripted acquisition, include the helper identity or implemented procedure, non-secret parameters, and the identities of produced material when available.
- Deliverable locations, applicable reproduction targets, and content identities where applicable; running capabilities use appropriate observable identifiers. Record evidence for any required structural or exact comparison without implying stronger verification than was performed.
- The implementation language, principal tools, and architecture selected for the generated project, where applicable, including how explicit implementation constraints were satisfied.
- Each acceptance criterion's result, its supplied test identifiers, the identities of the actual test content and relevant data, verification method, evidence location, and reason for any non-pass result. Supplied-test results MUST be distinguishable from supplemental agent-created test results.
- Deviations, user-approved amendments or waivers, limitations, and remaining work.
- Overall status.

Package identity SHOULD be computed from a sorted inventory of root-relative file paths and content hashes, excluding distribution metadata such as a repository's `.git` directory. The report MUST document the inventory scope and digest method. Secret values MUST NOT be included.

The run report MUST use package-relative or workspace-relative file references with the base identified, and binding identifiers for external local resources. It MUST NOT require a machine's absolute paths to locate or interpret evidence. Host-specific diagnostic logs MAY be retained separately as local execution records; a report or evidence bundle intended for publication MUST omit or normalize host paths without changing verification results. Input content identities MUST remain available when acquisition paths are omitted.

Overall status MUST be one of:

- `complete`: All mandatory deliverables and criteria are satisfied, every required supplied test has run and passed, and all additional required reviews are complete.
- `incomplete`: Work or required verification remains, including pending human review.
- `blocked`: A missing prerequisite, unresolved conflict, or authorization prevents required progress.
- `failed`: The attempt ended unsuccessfully because construction or required acceptance failed.

Individual acceptance results MUST be `pass`, `fail`, `not_run`, or `waived`. A waiver MUST be explicitly authorized and recorded; it is not a passing test. A waived required criterion prevents completion under the unchanged package. An amendment removing or changing a requirement changes the acceptance contract and MUST be identified as such. Consumers MUST NOT silently omit criteria or convert unavailable verification to a pass.

Completion of generation does not imply that deployment or external publication occurred.

## 9. Conformance and minimality

An authoring-conformant package satisfies the metadata, layout, required-content, identity, and acceptance requirements of this specification, including supplied executable tests with coverage of all mandatory requirements and deliverables. Valid syntax alone does not establish that a specification is complete or feasible.

A consumer-conformant run follows the lifecycle and reporting requirements. A conformant run may end blocked or failed; conformance is distinct from success.

The minimum package is one `SEED.md` containing the required specifications and supplied executable acceptance tests. Larger suites MAY be bundled in separate files with no prescribed filenames. Manifests, schemas, additional data, and acquisition scripts are optional. A package does not need external data, a database, a compiler, a network connection, or a particular test framework.

## 10. Deferred work

Future revisions may standardize machine-readable manifests, lockfiles, report schemas, dependency composition, registries, signing, or runner interoperability. They are outside version 0.1. Implementations MUST NOT assume undocumented semantics for them.

Example-specific requirements do not become format requirements automatically.
