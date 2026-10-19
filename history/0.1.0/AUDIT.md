# SEED conceptual and specification audit

Audit date: 2026-10-17. Reviewed format: 0.1.0 draft. Review pass: 2. Status: findings and proposed revisions, not an amendment to the format.

**Assessment**

SEED is a coherent proposal for distributing a project-construction contract: intended behavior, source material, constraints, and acceptance evidence travel together, while an agent chooses an implementation. Its usefulness does not require byte-identical regeneration or a prescribed programming language. The six agreed decisions can coexist.

The draft is suitable for experiments. It is not yet a validated general-purpose standard. Its main weaknesses concern the meaning of acceptance, the scope of test coverage, the identity of the effective specification, and the distinction between independently acceptable implementations and matching results. These can be corrected without abandoning the central concept.

After a second pass, the audit identifies eight medium-priority clarifications or design boundaries and one low-priority wording issue. No fundamental contradiction among the six agreed decisions was established. These priorities describe impact on interpretation and use, not software vulnerability severity. Findings identify ambiguity, scope decisions, or untested assumptions rather than demonstrated failures of a SEED consumer.

The first pass overstated three findings. A01 is downgraded because the draft already prohibits completion when mandatory requirements are unmet. A02 is narrowed because required human review is already allowed, although executable coverage for every requirement remains ambiguous. A03 is narrowed because resolved input identities are already recorded; the unresolved question is how external normative material contributes to the effective contract's identity. A09 adds a concrete ambiguity around test applicability. These corrections supersede the first-pass severity assessments.

The specification, README, and template were left unchanged during this audit. Proposed changes that affect scope or acceptance policy are identified as decisions to make rather than silently applied.

**Scope and evidence**

The review examined all three documents, traced the six design decisions through them, worked through counterexamples, and compared the concept with primary material on synthesis, testing, reproducible builds, and specification-driven development. Two small logical counterexamples and an illustrative mode-dependent acceptance calculation were executed in memory. The second pass also challenged each finding against existing safeguards and confirmed that the reviewed document hashes were unchanged. No SEED package was generated, no existing project was rebuilt, and no agent trial was conducted. Applicability judgments below are reasoned predictions, not measured success rates. This is not an exhaustive novelty or prior-art search.

Locations refer to the following exact document contents; later edits can move the line numbers.

| Document | SHA-256 |
| --- | --- |
| `README.md` | `b6208b65afb13cd7cd97c3403b10e3c7a5855f14bb8d0f9cd2069762e367b355` |
| `SPECIFICATION.md` | `bb1681bc8e80e3e23e9c8e29aa0c3abd8585f5b9b0f34220f3aac64822902f2a` |
| `templates/SEED.md` | `881365c8acd27cb950af04fad71c16d48647875b12c4a3f13563ad5df5ae2883` |

**The reasoning model**

Let `S` denote the effective specification, `D` the resolved data, `E` the declared environment, `T` the supplied acceptance suite, and `P` a generated project. A SEED asks a consumer to find a `P` satisfying `S` under the relevant assumptions about `D` and `E`.

The suite supplies an operational acceptance predicate, `T(P, D, E)`. A passing result is evidence about the cases and properties actually checked. It is not automatically a proof of every statement in `S`. For a finite domain with exhaustive checking, or a sound proof procedure under stated assumptions, stronger evidence may be possible. The format must identify the evidence actually obtained.

A specification generally permits a set of implementations. This freedom is desirable: choosing one member of that set is the agent's job. The author must determine which variations matter to users. Source data constrains possible outputs but does not by itself determine the desired transformations, functions, or actions; the draft correctly requires those to be specified separately.

There are also two distinct operations: generating the project, and executing the generated project to produce its runtime behavior or artifacts. Their inputs, costs, environments, and reproducibility claims can differ.

**A01 — Low: acceptance wording should preserve the distinction between evidence and correctness**

Evidence: [specification](SPECIFICATION.md), section 5, Acceptance and Completion (lines 164–190); [README](README.md), line 5.

The phrase that tests establish whether the project succeeds benefits from a bounded meaning. The specification already requires all mandatory requirements to be satisfied. Therefore a consumer aware of an unmet requirement cannot legitimately report completion merely because tests pass. My first pass overstated the missing safeguard: the conjunction is already present.

The remaining concern is explanatory precision. The documents could explicitly distinguish passing the supplied suite from establishing every required property and explain how to report a known violation missed by the suite. They do not need a new correctness gate to make such a violation disqualifying.

Counterexample, executed during this audit: a suite tests sorting only on `[1, 2]` and `[2, 1]`. Both `sorted(values)` and `sorted(set(values))` pass. On `[2, 1, 2]`, their outputs are `[1, 2, 2]` and `[1, 2]`. Mapping a test to the sorting requirement did not test preservation of duplicates.

The invalid inference would be: a correct implementation passes sound tests; this implementation passes; therefore it is correct. That is affirming the consequent. Declaring an operational acceptance rule is not itself a fallacy; claiming more than that rule establishes is the problem. The general limitation of ordinary test sampling is longstanding, as discussed in [Dijkstra's reliability lecture](https://www.cs.utexas.edu/~EWD/transcriptions/EWD03xx/EWD303.html).

Recommendation: retain supplied tests as mandatory acceptance gates and explicitly explain the existing rule that a known mandatory-requirement violation prevents completion. Record the uncovered violation and propose a versioned regression test; do not authorize the generating agent to weaken the suite. Separate requirement-to-test traceability from claims of exhaustive coverage. This is a clarification of the agreed policy, not evidence that the draft asserts a proof it does not have.

**A02 — Medium: the meaning of executable coverage and the intended project scope need clarification**

Evidence: [README](README.md), line 5; [specification](SPECIFICATION.md), lines 166, 182, and 281.

The README includes documents and creative assets alongside software. The specification requires an executable test for every mandatory requirement, function, action, and deliverable. It also already permits required human review; supplemental does not mean optional when a package makes that review mandatory. This is workable for many objective software contracts. The ambiguous part is whether executable coverage must directly establish a requirement or may verify that another declared evidence procedure was completed.

This is a scope tension rather than a proof that such projects are impossible. An executable test can check document structure or record that a reviewer approved it. But a script reading an approval flag does not itself judge the underlying quality. Likewise, final-output tests do not necessarily establish that required construction procedures were followed; process requirements may need separate execution evidence.

This does not force a choice between abandoning supplied tests and excluding all subjective criteria. A supplied automated suite and a required author-defined review procedure can jointly establish acceptance. The report should identify which evidence supports which claim, without describing a script that reads an approval as the evaluator of the underlying quality.

The original concept concerns creating software projects. A sensible initial scope is general-purpose software and its declared outputs, including software that produces documents or assets. Direct creation of an arbitrary creative artifact is a broader scope choice. The draft should say which meaning is intended rather than expand the domain merely because an agent can perform those tasks.

Decision needed: clarify what counts as test coverage and whether direct non-software creation belongs in the initial scope. Preserve the required executable suite and any required review. If executable evidence cannot establish a claim, identify the other author-supplied evidence procedure or keep that claim outside the initial supported scope. An executable wrapper must not conceal who or what actually judged the requirement.

**A03 — Medium: mutable normative references need an explicit effective-contract identity**

Evidence: [specification](SPECIFICATION.md), section 3 (line 48), section 4 (lines 84–88), Inputs (lines 130–132), and section 8 (lines 253–264).

Remote specifications are permitted as inputs. Immutable identities are explicitly required for exact reproduction, while ordinary inputs may follow changing selection policies. A package can therefore refer to the current remote API specification and acquire different normative requirements on two runs despite unchanged bundled bytes and package version.

The draft already asks runs to record resolved inputs. A careful consumer can therefore retain the relevant evidence today; this is not an absence-of-provenance defect. A dynamic selector can also legitimately be part of the author's contract. The ambiguity is whether two uses of the same package version are being compared by the authored selection rule or by the normative requirements actually resolved. A bundled package digest alone does not settle that question.

Counterexample: the same remote document changes an output field from optional to required. Two runs have the same SEED package identity but different required interfaces. That is a different issue from a dataset acquiring more rows under an unchanged transformation rule.

Recommendation: distinguish normative dependencies from data dependencies. Record or snapshot the resolved normative material and identify the effective contract used for acceptance separately from the bundled package identity. Report changes in the effective contract. Authored edits to normative requirements still require package revisions; changes allowed by an explicit dynamic rule must remain identifiable. This does not require pinning every data source to an exact commit.

**A04 — Medium: satisfying one contract is not necessarily pairwise output agreement**

Evidence: [specification](SPECIFICATION.md), section 6 (lines 194–208); [template](templates/SEED.md), line 24.

The behavioral default is sound, but the rule that required results must agree within specified tolerances leaves the comparison relation ambiguous. Independently satisfying the specification and matching another accepted implementation are different conditions.

Counterexample, executed during this audit: an approximation to zero with maximum absolute error 1 accepts both -0.75 and 0.75. Their difference is 1.5. Both meet the reference-relative tolerance, but they fail a pairwise comparison using that same tolerance. Similarly, two different valid routes can both satisfy a routing contract.

Recommendation: make independent satisfaction of the contract the default. Where cross-run equality matters, explicitly declare the comparison relation, canonicalization, reference result, distribution, or pairwise tolerance. Data selection, interface compatibility, and artifact byte identity are separate dimensions. Structural requirements already apply under the behavioral default, so the structural label should describe which comparisons are promised rather than imply an automatic hierarchy of guarantees.

The [Reproducible Builds definition](https://reproducible-builds.org/docs/definition/) uses artifact byte identity with fixed source and build conditions. SEED's broader behavioral usage is legitimate if clearly qualified; a single accepted generation should not be presented as evidence of repeatable generation across agents.

**A05 — Medium: generation and later use of the generated project need separate contracts**

Evidence: [specification](SPECIFICATION.md), Deliverables (line 102), source stages (line 115), Construction (lines 156–160), and Completion (line 190).

The draft distinguishes projects from artifacts and allows stage declarations. That is a useful foundation. It still leaves the relationship between initial generation and subsequent use largely to inference.

Counterexample: an agent produces a valid dataset and a source directory. Supplied tests inspect the dataset, but nobody checks whether the source can rebuild it without an undeclared cache or an interactive repair step. The artifact can pass while the promised reusable software project fails its purpose. Conversely, a package intentionally requesting only a one-time artifact should not inherit unnecessary build-system obligations.

Recommendation: each deliverable should state whether it is a one-time artifact, reusable project, running capability, or a combination. When reusable software is promised, specify its ordinary build or execution entry point, dependencies, and acceptance method using a fresh applicable environment. Record the generation environment separately from the project's build and runtime environments. Continued agent participation may be explicitly required by a project, but it must not be an accidental dependency.

The principle is durable handoff, not a demand that every project produce deterministic bytes or support every operating system.

**A06 — Medium: the reference-implementation boundary is an authoring policy with edge cases**

Evidence: [specification](SPECIFICATION.md), section 1 (lines 12–16) and Acceptance (lines 174–180).

Excluding a complete reference implementation is a valid agreed boundary for studying generation from a specification. The difficult phrase is that supporting resources must not collectively supply the complete target implementation.

Counterexamples: a permitted dependency already performs most of a small project's target function; an executable test oracle for a tiny mathematical library is itself an implementation of that library; or a supposedly generic acquisition helper performs the central transformation that the agent was supposed to implement.

Recommendation: keep the exclusion, and require authors to identify the behavior the consumer is expected to implement, what dependencies may supply, and the reuse role of helpers and oracles. Decide explicitly how a complete oracle for a small target is handled. Static expected cases or checks of general properties may avoid including such an oracle. Do not substitute a percentage-of-generated-code threshold: it measures text volume rather than responsibility.

Conformance here requires semantic review. A syntax checker cannot reliably determine whether a collection of helpers constitutes the project. Excluding a reference from the workspace also does not prove that a model has never encountered similar code; no such model-independence claim should be inferred.

**A07 — Medium: package identity lacks a stable boundary when outputs share its directory**

Evidence: [specification](SPECIFICATION.md), Package definition (line 24), section 3 (lines 42–46), and section 8 (line 264); [template](templates/SEED.md), line 81.

The recommended identity method hashes a sorted inventory of package files. The format does not require the package directory and target workspace to be separate or specify when package membership is frozen. If a consumer generates files or writes the report below the package root, a later inventory can include those outputs.

Consequences include different package digests for the same supplied instructions, accumulated outputs entering later runs, and a report whose own inclusion changes the digest it is reporting. This is a boundary ambiguity, not a cryptographic-hash weakness.

Recommendation: define an immutable input inventory at run start, or require output placement outside that inventory. Explicitly exclude generated projects, caches, and run evidence from package membership. State whether identity records executable modes and symlink targets where they affect acquisition or testing. A package may choose its digest serialization initially, provided the method and scope are recorded; a canonical interoperable digest can be standardized later.

**A08 — Medium: update support needs a baseline and implementation-aware migration conditions**

Evidence: [specification](SPECIFICATION.md), section 4 (line 86), Constraints (line 152), and section 7 (lines 233–243).

The update rules correctly require an explicit request, preservation of user changes, and the current suite. They cannot by themselves determine which edits are user changes or how to migrate every valid implementation of an earlier package.

Counterexample: two implementations of version 1 pass the same public tests but use different internal storage layouts. A version 2 migration written for one layout is not necessarily valid for the other. A package version identifies a contract, not one concrete generated architecture. Passing the new suite against a fresh empty store also does not demonstrate preservation of old user data.

Recommendation: identify a recoverable baseline or record that it is unavailable; a hash alone identifies bytes but does not recover them. Define migration preconditions in terms of observable data formats or capabilities as well as prior package versions. Test migration against representative prior state. When preservation cannot be established, report that limitation and resolve the conflict instead of claiming it was verified. Keep update support general without promising a universal merge algorithm.

**A09 — Medium: mode-dependent test applicability is not represented explicitly**

Evidence: [specification](SPECIFICATION.md), source optionality (lines 116 and 132), update requirements (line 158), required tests (lines 184 and 237), and result states (line 275); [template](templates/SEED.md), line 75.

The format supports fresh generation and updates, optional inputs, and package-specific compatibility conditions. It requires every required test to run and pass, but does not explicitly define when a test applies to a particular run. Its result vocabulary distinguishes pass, fail, not_run, and waived, but not a declared check outside the selected run's scope.

Example: a package includes a normal behavior check and a check that an explicitly requested update preserved the user's existing records. In a fresh run there are no such records or transition to inspect. Marking the transition check not_run appears to block completion; marking it pass hides that no actual transition was checked. In an update run, leaving the same check unperformed must prevent completion. A supplied migration test using bundled historical fixtures is a different test and may legitimately apply to both modes.

The illustrative calculation performed in this audit gave the same raw statuses to both modes: behavior passed, existing-state preservation did not run. An unscoped all-tests rule rejected both. An author-declared applicability rule accepted the fresh run and rejected the update. This demonstrates the distinction, not an execution of a SEED consumer.

An author can currently encode conditions inside test code or prose, so the format is not unusable. The missing rule is how those conditions affect the meaning of the report and completion claim.

Recommendation: let the author declare applicability by run mode, supported profile, or explicit precondition. Require all applicable required tests to pass, record the applicability decision and untested scopes, and distinguish not-applicable checks from skipped or failed required checks. The consumer must not choose applicability after seeing a failure. A missing prerequisite for a required applicable test remains blocking; it cannot be relabeled out of scope. This preserves the decision that supplied tests establish acceptance.

**What is already reasoned well**

| Decision | Why it is useful | Limit to retain |
| --- | --- | --- |
| Explicit source declarations | They make acquisition and provenance reviewable. | A location or digest does not guarantee continued availability. |
| Supplied acceptance tests | They prevent the generator from unilaterally defining success. | Supplied does not mean complete or error-free. |
| Implementation freedom | It allows adaptation to supported environments and different engineering choices. | Public interfaces and genuine constraints still bind the implementation. |
| Tests cannot introduce hidden restrictions | It protects the promised freedom. | Demonstrate the boundary with at least two implementations. |
| Behavioral acceptance | It matches the intended flexibility. | It does not imply identical code, identical data snapshots, or pairwise equality. |
| Host-independent instructions | They remove accidental dependence on the author's machine. | They do not imply universal execution on unsupported platforms. |
| Explicit update mode | It distinguishes regeneration from modifying user-owned work. | Migration evidence is specific to the actual existing project. |
| Conformance separate from completion | A consumer can follow the format and honestly report failure. | A valid package need not be feasible for every model or resource budget. |

The functions/actions distinction is usable but overlapping: a capability can be exposed through an operation. Shared requirement identifiers are sufficient; authors need not duplicate the same behavior under separate taxonomies. Bundled, downloadable, and scripted acquisition are also overlapping mechanisms. The specification already permits combinations, so this is not a contradiction.

**Applicability assessment**

These are hypotheses to test, not claims of demonstrated support.

| Project class | Expected fit | Evidence needed |
| --- | --- | --- |
| Batch data transformation, indexing, conversion | Strong initial candidate | Input coverage, data fidelity, negative cases, scale checks, and reusable execution where promised |
| Library or command-line utility | Strong when interfaces are explicit | Boundary cases, independent expected values, and a test interface compatible with permitted implementations |
| Service or interactive application | Conditional | Stateful scenarios, lifecycle, concurrency, external-service assumptions, and operation evidence |
| Native library or device-facing software | Conditional | Explicit ABI/platform/tool requirements and access to representative verification environments |
| Stochastic or model-based outputs | Conditional | Declared statistical acceptance procedures, sample sizes, and treatment of nondeterminism |
| Documents, visual assets, or subjective design | Scope decision required | Meaningful author-supplied review procedures; executable structural checks alone are insufficient |
| Long-lived customized projects | Conditional update fit | Baseline identity, customization handling, and tests of migration using existing state |

No row requires the format to become specialized for a database or a particular operating system. Some packages will need substantial platform-specific constraints while remaining portable as packages.

**Novelty and the value hypothesis**

Creating implementations from specifications has established antecedents. Solar-Lezama's [synthesis material](https://people.csail.mit.edu/asolar/SynthesisCourse/Lecture17.htm) describes specification-driven program search and generate/check refinement. [GitHub Spec Kit](https://github.com/github/spec-kit) provides structured agent workflows from specification through implementation and verification. These references establish relevant precedents; they do not establish that SEED's exact packaging choices already exist or exhaust the field.

My assessment is that SEED's potential contribution is a portable, reviewable distribution unit for generation: data acquisition rules, required behavior, supplied acceptance, and outcome evidence are packaged together while implementation remains replaceable. Its merit should be measured on that boundary, without asserting that generation from specifications is itself new.

A large generated artifact motivates distributing a recipe instead of the artifact. It does not by itself establish that regenerating the implementation is better than distributing an existing builder and its acquisition instructions. That is a non sequitur if presented as sufficient justification for SEED's additional generation step.

The useful experimental question is whether maintaining specifications and acceptance suites produces worthwhile adaptability, portability, or maintenance benefits relative to maintaining one implementation. Measure authoring effort, input acquisition, generation and repair costs, acceptance quality, repeated-use costs, and maintenance over a revision. No claim of lower total cost follows merely from a smaller repository.

SEED shifts some engineering work into requirements, examples, test oracles, and contracts. It does not remove that work. A compact package still depends on knowledge supplied by the consumer and its tools. The current consumer-conformance rule correctly allows an honest unsuccessful run rather than guaranteeing that every agent can solve every package.

**Reasoning hazards to name precisely**

- Affirming the consequent: treating passing a necessarily incomplete suite as proof of full correctness.
- Equivocation: using reproduction to mean contract satisfaction in one place and output identity in another.
- Proxy substitution: satisfying the visible metric while missing the intended behavior. This need not be deliberate cheating. [DeepMind's specification-gaming examples](https://deepmind.google/blog/specification-gaming-the-flip-side-of-ai-ingenuity/) illustrate this broader mismatch; they are not evidence that a SEED consumer has done it.
- Circular validation: deriving expected results from the implementation being checked. The draft already prohibits this; preserve that rule.
- Unsupported generalization: treating one successful package or one agent run as evidence of general applicability.
- Category confusion: treating portable package references as proof that every execution environment is compatible.

These are reasoning hazards to avoid, not six demonstrated fallacies in the documents. In particular, the draft already forbids circular expected results and already makes requirement satisfaction necessary for completion. Excluding reference implementations, requiring supplied tests, and granting implementation freedom are design choices, not fallacies.

**Revisions recommended before a generation trial**

1. Define author-declared test applicability and reporting, especially for fresh runs versus updates. Applicable required tests remain mandatory.
2. Define behavioral acceptance through the specified predicates; require an explicit relation for any cross-run comparison.
3. Clarify the intended initial project scope and what executable coverage establishes. Preserve required supplied tests and required review; label their distinct evidence roles.
4. Clarify the effective contract identity and the boundary between package inputs and generated outputs.
5. Specify the handoff for reusable software and the evidence needed for conditional updates; clarify helper and oracle roles.
6. Make the existing completion rule explicit in explanatory prose: required checks pass, required reviews are complete, and known mandatory-requirement violations prevent completion. Do not claim exhaustive correctness from traceability.

These revisions should clarify the six decisions, not add a registry, mandatory runner, agent-specific integration, or database-specific schema. The audit does not recommend expanding the format simply to encode every possible engineering concern.

**Constraints on the proposed remedies**

The second pass rejects several unnecessary expansions. A required machine-readable manifest, registry, universal runner, or universal migration mechanism is not needed to resolve these findings. Source data need not be frozen to an exact commit. Human review is already supported and should not be described as absent. The format already requires interfaces for testing the actual deliverables; the next step there is to test that requirement with different implementations, not invent it again.

Conformance and successful generation must remain separate. A blocked or failed run can be honest and conformant. Likewise, an author can provide a valid but demanding contract that a particular agent cannot implement within its resources. No new unconditional generation guarantee should be added while clarifying acceptance.

**Experiments that would test the concept**

Use the planned data-oriented example, plus a small computation or transformation project with no external corpus and one stateful application. A small diverse set is more informative about format generality than a single large example. No experiment described here has yet been performed.

| Experiment | What it tests | Useful observation |
| --- | --- | --- |
| Two independent implementations, using different languages where allowed | Whether the contract and suite permit the promised freedom | Both can run the same supplied checks without changing their meaning |
| Repeated generation with a declared attempt budget | Practical generation reliability | Record every attempt, elapsed effort, interventions, and failure causes; avoid reporting only the successful run |
| Deliberately incorrect candidates | Whether supplied tests discriminate useful failures | Reject dropped records, invented data, ignored inputs, and other specification-relevant defects |
| New valid input cases beyond authored examples | Whether finite examples encourage overfitting | Evaluate generalization separately; do not silently change the package's acceptance contract |
| A permitted source update | Whether data variability is handled | Distinguish expected output changes from behavior regressions and contract changes |
| A relocated supported environment | Whether host independence holds | Acquire declared inputs and validate without author-specific paths or caches |
| Update a customized generated project with existing state | Whether update semantics are practical | Preserve relevant changes and data and pass the current required suite |
| Compare with a fixed builder and data-acquisition recipe | Whether generation adds value | Compare total effort, adaptation ability, maintenance, and acceptance quality |

For software deliverables, include an independent ordinary build or execution from the delivered project where reusable software is promised. For tests of SEED generation, keep the old reference implementation outside the generating agent's accessible inputs. If the evaluator uses it for comparison, record that separately. Do not assume this establishes anything about the model's training history.

The first successful trial would show feasibility for that package, agent, input selection, and environment. Repeated trials, deliberate failure cases, and contrasting project types are needed before making stronger claims about reliability or generality.
