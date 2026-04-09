---
description: Module boundaries and where to place new code
globs: ["**/*.py"]
alwaysApply: false
---

# Module Boundaries

These boundaries are strict — violating them breaks the architecture.

- **`__init__.py`** — Public API surface only. Re-exports only. No logic.
- **`spark_session.py`** — Owns `DatabricksSession`. No SDK client code here.
- **`workspace.py`** — Owns all `WorkspaceClient` interactions. New API features go here.
- **`__main__.py`** — Owns CLI. Each subcommand is a `cmd_*` handler that dispatches to `workspace.py`.

## Where to Put New Code

| What you're adding | Where it goes |
|---|---|
| New Databricks API call | `workspace.py` — new function returning `dict` or `list[dict]` |
| New CLI subcommand | `__main__.py` — `cmd_*` handler + parser + dispatch dict entry |
| New interactive example | `examples/` — `from dbstarter import get_spark` |
| New job-compatible script | `examples/` — `SparkSession.builder.getOrCreate()`, no dbstarter imports |
| New shared utility | New module in `dbstarter/`, re-export from `__init__.py` if public |
