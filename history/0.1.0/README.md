# SEED

SEED is a package format for instructing an AI agent to create a project from declared inputs, specifications, and acceptance criteria.

A SEED describes the intended result and supplies acceptance tests derived from its specifications, functions, actions, and data. The agent creates the implementation and must pass those tests to establish success. Additional tests created by the agent may assist development but do not replace the supplied tests. Projects may produce applications, libraries, services, datasets, documents, assets, or combinations of these.

Every package explicitly defines its data sources and how they support the project's functions and actions. Sources may be bundled, downloaded from locations such as Git repositories, or acquired and prepared by scripts or code. Scripted acquisition describes both the upstream source and the expected material. A project without data sources declares that explicitly.

The format is independent of any model, agent product, programming language, build system, hosting provider, or author's machine. A package can be distributed through a repository or archive and used in a workspace chosen by its consumer.

The agent chooses its language, libraries, tools, architecture, and internal structure unless the package explicitly constrains them. Supplied tests verify the declared behavior and interfaces. The language used to write a test or acquisition helper does not by itself dictate the generated project's language.

Reproduction is behavioral by default: independently generated projects satisfy the same specifications and supplied tests. Required interfaces and output formats remain consistent where specified. Exact source code, commits, or artifact bytes need not match unless explicitly required. Results may change when permitted source data changes; each run records which data it used.

Each package has a Markdown entry point named `SEED.md`. It defines the objective, deliverables, inputs, requirements, constraints, construction workflow, acceptance criteria, and completion conditions. Acceptance tests are required and may be embedded in the entry point or bundled in separate files. Supporting specifications, fixtures, and other resources are included as needed. Supporting code may assist construction and verification, but complete reference implementations remain outside the package and fresh-generation inputs.

Published packages use portable references for bundled resources and named bindings for resources supplied at runtime. They do not depend on the author's filesystem layout, installed tools, or previous sessions. Required capabilities and tools are declared explicitly. Inputs may follow declared versions, branches, or selection policies; exact source commit matches are optional. Runs record the input versions actually used when available.

Fresh generation is the default. When explicitly requested, an agent may update an existing generated project, preserve user changes and data, and follow declared compatibility or migration requirements. The updated project must pass the current package's supplied tests. Its report records the previous and current package versions, the changes made, and the acceptance results.

Changes to the specification, source-selection rules, or supplied tests require a new package version. External data changing within an already permitted selection policy does not itself require a new version.

This repository contains the format specification and an authoring template. The current specification is **0.1.0, draft**. No runner or validator is implemented yet.
