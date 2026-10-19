# WinAPIDB draft example

The maintained draft package is [seed/SEED.md](seed/SEED.md). It declares SEED format **0.2.0**, package version **0.2.2**, and SQL schema **4**. The core format and skill now target 0.3.0; this package still needs a separate migration review.

| Directory | Purpose |
| --- | --- |
| [seed/](seed/SEED.md) | Portable package inputs: contracts, fixtures, and supplied acceptance checks. |
| `tests/` | Repository authoring checks for this example's schema, source-backed assertions, and bundled helper. |
| `scripts/` | Authoring tools used to prepare reference cases. |

The package was relocated from the temporary workspace without changing its files. Original trial inputs and historical evidence remain separate. Future example edits belong here.

## Run the example checks

From the repository root, with Python 3 and SQLite FTS5 available through the standard-library `sqlite3` module:

```sh
python3 -B -m unittest discover -s examples/winapidb/tests -v
python3 -B examples/winapidb/seed/acceptance/run.py --self-check
```

These checks read the bundled fixtures and use small in-memory databases. They do not acquire sources, launch an agent, or build the full database. The helper-consistency check also reads the repository's generic `scripts/run_bounded.py`. Core tests under `tests/` do not import this example.

The authoring helper `scripts/capture_reference_cases.py` additionally requires PyYAML and explicitly supplied reference-database and notice-tree locations through its arguments. It is not used by either test command.

## Construction inputs and evidence

For an independent reconstruction, the package root is `seed/`. The sibling authoring tools and repository tests are not part of that package. Use a consumer supporting its declared format, or migrate and revalidate it before using the current skill.

A passing authoring check or package self-check does not establish a successful reconstruction. See [the package review](seed/REVIEW.md) and [its historical change notes](seed/CHANGES.md) for the results and limitations attached to this revision.
