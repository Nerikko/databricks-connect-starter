# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Databricks Connect starter kit — run PySpark scripts locally while all Spark operations execute remotely on a Databricks workspace. No jobs are created; it's a live interactive session. Also includes a CLI (`dbstarter`) for workspace exploration and job management.

## Setup & Development

```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e .
```

Credentials go in `.env` (see `.env.example`): `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, and optionally `DATABRICKS_CLUSTER_ID` (empty = serverless).

Verify connection:
```bash
python -c "from spark_session import get_spark; print(get_spark().sql('SELECT 1').collect())"
```

For notebooks: `uv pip install -e ".[notebook]"`

No test suite or linter is configured.

## Architecture

- **`dbstarter/spark_session.py`** — `get_spark()` creates a `DatabricksSession` (serverless if no `DATABRICKS_CLUSTER_ID`, otherwise classic cluster). Loads `.env` via `python-dotenv`.
- **`dbstarter/workspace.py`** — All Databricks SDK interactions: Unity Catalog browsing (`list_catalogs`, `list_schemas`, `list_tables`, `describe_table`), job management (`list_jobs`, `create_job`, `run_job`, `get_run_status`), cluster listing, secret listing, SQL queries, and DBFS uploads. Each function creates its own `WorkspaceClient`.
- **`dbstarter/__main__.py`** — CLI entry point via `argparse`. Dispatches subcommands to functions in `workspace.py`. Registered as `dbstarter` console script in `pyproject.toml`.
- **`dbstarter/__init__.py`** — Re-exports `get_spark` and `get_workspace_client`.
- **`spark_session.py` (root)** — Backward-compat shim that re-exports `get_spark` from the package. Example scripts import from here.

## CLI (`dbstarter`)

```bash
dbstarter catalogs | schemas <catalog> | tables <cat.schema> | describe <cat.schema.table>
dbstarter jobs | job-create <scripts...> | job-run <job_id> | job-status <run_id>
dbstarter clusters | secrets | query "<SQL>"
```

`job-create` supports three compute modes: serverless (default), `--cluster-id`, or `--new-cluster` (ephemeral). Scripts are uploaded to DBFS before job creation.

## Key Conventions

- Python 3.12 only (constrained in `pyproject.toml`).
- Package manager is **uv**, not pip.
- `get_spark()` is the single entry point for obtaining a SparkSession — always use it rather than constructing sessions directly.
- Workspace SDK calls go through `dbstarter/workspace.py` functions, not raw SDK usage.
- Example scripts (`example_query.py`, `example_etl.py`) import from the root `spark_session.py` shim.
