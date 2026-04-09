---
description: Project folder structure, module responsibilities, and where to place new code
globs: ["**/*.py"]
alwaysApply: false
---

# Project Structure

## Directory Layout

```
databricks-connect-starter/
├── dbstarter/                    # Main package
│   ├── __init__.py               # Public API: get_spark, get_workspace_client
│   ├── __main__.py               # CLI entry point (11 subcommands via argparse)
│   ├── spark_session.py          # get_spark() — DatabricksSession factory
│   └── workspace.py              # All Databricks SDK operations
├── examples/                     # Demo scripts
│   ├── example_query.py          # NYC taxi query demo (interactive)
│   ├── example_etl.py            # ETL pipeline demo (interactive)
│   └── test_job.py               # Minimal job-compatible script (no dbstarter imports)
├── notebooks/
│   └── getting_started.ipynb     # Interactive Jupyter walkthrough
├── .vscode/
│   ├── *_template.json           # Committed templates (settings, launch, extensions)
│   └── *.json                    # Actual configs (gitignored, user-specific)
├── pyproject.toml                # Dependencies, scripts, black/isort config
├── .env.example                  # Env var template (committed)
├── .env                          # Actual credentials (gitignored)
├── CLAUDE.md                     # Claude Code context
├── .cursorrules                  # Cursor AI context
└── README.md                     # User documentation
```

## Module Responsibilities

### `dbstarter/__init__.py`
Public API surface only. Re-exports `get_spark` and `get_workspace_client`. Do not add logic here.

### `dbstarter/spark_session.py`
Owns DatabricksSession lifecycle. Single function `get_spark()`. Handles dotenv loading, serverless vs cluster detection. Do not add SDK client code here.

### `dbstarter/workspace.py`
All Databricks SDK interactions. Every workspace function creates its own `WorkspaceClient` via `get_workspace_client()`. Functions return plain dicts, not SDK objects. New workspace features go here.

### `dbstarter/__main__.py`
CLI entry point. Uses argparse with subparsers. Each subcommand has a handler function (`cmd_*`) that dispatches to `workspace.py`. Includes `print_table()` for formatted output.

### `examples/`
Runnable demo scripts. Interactive scripts import from `dbstarter`. Job-compatible scripts (like `test_job.py`) use `SparkSession.builder.getOrCreate()` with no external imports.

### `notebooks/`
Jupyter notebooks for interactive exploration. Same execution model as interactive scripts.

## Where to Put New Code

| What you're adding | Where it goes |
|---|---|
| New Databricks API interaction | `workspace.py` — new function |
| New CLI subcommand | `__main__.py` — add `cmd_*` handler + parser + dispatch entry |
| New interactive example | `examples/` — import `from dbstarter import get_spark` |
| New job-compatible script | `examples/` — use `SparkSession.builder.getOrCreate()`, no dbstarter imports |
| New shared utility | New module in `dbstarter/`, re-export from `__init__.py` if public |

## Entry Points

- **Console script**: `dbstarter` → `dbstarter.__main__:main` (registered in `pyproject.toml`)
- **Package import**: `from dbstarter import get_spark, get_workspace_client`
- **Direct execution**: `python -m dbstarter <subcommand>`
