# Bounded construction and verification

The package resource limits are in [resource-policy.json](../acceptance/resource-policy.json). They are provisional stop thresholds, not measured promises. A limit failure is an incomplete result. Do not weaken tests, omit sources, increase limits or launch replacement full attempts automatically.

## Before execution

Freeze the package input inventory. Create a separate source-only project snapshot with its dependency lock/installed-version record and interface manifest. Hash every delivered source file, not only Git HEAD. Run from the snapshot; development edits belong elsewhere. Preflight and acceptance must use that exact snapshot. Record package digest, project snapshot digest, dependency identities, source identities and command before each attempt. An unchanged code hash alone does not establish unchanged dependencies.

Verify that the actual worker UID can create and retain a probe file in the durable output mount. Verify terminal errors and nonzero exits survive an intentional tiny failing command. Logs must be owned by the supervisor and survive agent termination. Do not silently relocate output into ephemeral container storage.

## Gates

1. Supplied fixture checks, including exact mapped values, external-host resolution and repeated-name storage, pass.
2. Acquire all required public inputs once and record identities. Acquisition may be reused if verified unchanged; it is not repeated automatically after an unrelated parser error.
3. The supplied suite selects, per corpus, the largest file, a deterministic hash-selected file, and one file per selected extension (bounded to eight extensions). The preflight operation processes these real inputs with the frozen extraction/dependency versions. Persist file identities, diagnostics and emitted spans. This is a compatibility sample, not evidence of complete coverage.
4. Any native crash or invalid span blocks the full attempt. Retain the failing file identity and minimal reproducer; a revised snapshot needs a new passing preflight. Native crashes cannot be treated as ordinary unsupported-syntax warnings.
5. Only after the gates, permit one full build. It cannot overlap another full build. The model does not need to poll it repeatedly: deterministic supervision waits for completion, failure or a limit event.

## External enforcement

The supplied acceptance runner uses `bounded.py` for process-group deadlines, stream limits and sampled total-workspace and individual-file limits (including candidates). It kills remaining descendants in the same process group, saves stdout/stderr separately, and writes terminal status including failure. The per-file ceiling is the database_bytes limit and applies to every watched file, including incomplete candidates. Workspace disk limits are sampled and can overshoot; they are not filesystem quotas. Use a quota-limited isolated workspace for strict disk containment. Processes that escape the group or run external containers require container/cgroup supervision; this helper is not an isolation boundary.

The full acceptance entrypoint automatically invokes the outer bounded runner using full_seconds and workspace_bytes. Supply --trial TRIAL_WORKSPACE; it exclusively creates full-attempt there and refuses reuse, even with a different test work directory. Retain that evidence after failure. The internal --supervised-full flag is solely for the spawned child, not a user invocation or an isolation boundary. One authorized trial has one full attempt; a new directory is not authorization to reset the attempt allowance. The skill's launch policy separately controls agent invocations. The acceptance program does not launch a model and cannot measure account credits.

Model construction requires an explicit session budget with a functioning provider/account enforcement mechanism. When that is unavailable, do not launch an autonomous model subprocess; use bounded interactive implementation steps under the user's existing control. A wall-clock deadline cannot guarantee a token budget. Never claim token totals from log bytes. This package amendment authorizes no new trial by itself.

## Evidence and completion

Record all physical table counts and stage-level progress; association views are virtual counts. Preserve interrupted-run evidence and label absent results not_run. Validate the candidate fully before publication, then use focused post-close integrity/identity checks; repeated full content scans are not required by this contract. Independent supplied acceptance still checks source fidelity.

Do not begin independent final verification while the implementation is still changing. A result applies only to the recorded project, dependencies and inputs. An earlier fixture pass cannot certify a later revision. The final report includes every attempt and its reason, peak disk/log usage, exit state and available model usage; unavailable usage is explicitly null.
