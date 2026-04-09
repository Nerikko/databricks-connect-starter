---
description: Databricks Connect starter kit — project overview, architecture, CLI, job patterns, and conventions
alwaysApply: true
---

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Databricks Connect starter kit. Two modes of operation:

1. **Interactive (Databricks Connect)** — Run PySpark scripts locally; Spark operations execute remotely on the workspace. No jobs created.
2. **Jobs (`dbstarter job-create`)** — Upload scripts to the Workspace filesystem, create a Databricks Job, run it entirely on Databricks.

Also includes a CLI (`dbstarter`) for workspace exploration (catalogs, tables, jobs, clusters, secrets, SQL).

## Setup & Development

```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e .
```

Credentials go in `.env` (see `.env.example`): `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, and optionally `DATABRICKS_CLUSTER_ID` (empty = serverless).

Verify connection:
```bash
python -c "from dbstarter import get_spark; print(get_spark().sql('SELECT 1').collect())"
```

For dev tools (black, isort): `uv pip install -e ".[dev]"`

For notebooks: `uv pip install -e ".[notebook]"`

Formatting: `black .` and `isort .` (line-length 90, isort black profile -- configured in `pyproject.toml`).

### VS Code

Copy templates to get a working local config:
```bash
cp .vscode/settings_template.json .vscode/settings.json
cp .vscode/launch_template.json .vscode/launch.json
cp .vscode/extensions_template.json .vscode/extensions.json
```
Then fill in your Databricks credentials in `launch.json`. The actual config files are gitignored; only templates are committed.

## Architecture

- **`dbstarter/spark_session.py`** -- `get_spark()` creates a `DatabricksSession` (serverless if no `DATABRICKS_CLUSTER_ID`, otherwise classic cluster). Loads `.env` via `python-dotenv`.
- **`dbstarter/workspace.py`** -- All Databricks SDK interactions: Unity Catalog browsing (`list_catalogs`, `list_schemas`, `list_tables`, `describe_table`), job management (`list_jobs`, `create_job`, `run_job`, `get_run_status`), cluster listing, secret listing, SQL queries, and Workspace filesystem uploads. Each function creates its own `WorkspaceClient`.
- **`dbstarter/__main__.py`** -- CLI entry point via `argparse`. Dispatches subcommands to functions in `workspace.py`. Registered as `dbstarter` console script in `pyproject.toml`.
- **`dbstarter/__init__.py`** -- Re-exports `get_spark` and `get_workspace_client`.
- **`examples/`** -- Demo scripts (`example_query.py`, `example_etl.py`, `test_job.py`) that can run locally via Connect or be deployed as jobs.

## Two ways to run scripts

### 1. Interactive via Databricks Connect (local execution)

The script runs on your machine; Spark operations are sent to Databricks and results stream back. Use `get_spark()` from `dbstarter`:

```python
from dbstarter import get_spark
spark = get_spark()
df = spark.sql("SELECT 1")
df.show()
```

Run with: `python examples/example_query.py` or the VS Code Run/Debug button.

- Requires `DATABRICKS_HOST` + `DATABRICKS_TOKEN` in `.env`
- Serverless by default; set `DATABRICKS_CLUSTER_ID` for a classic cluster
- Cold start can take 30-60s for serverless

### 2. Databricks Job (remote execution)

The script runs entirely on Databricks. Use the CLI to upload, create, and run:

```bash
dbstarter job-create examples/test_job.py --name my-test
dbstarter job-run <job_id>
dbstarter job-status <run_id>
```

**Important:** Job scripts must be **self-contained** -- they cannot `import dbstarter` because that package is not installed on the cluster. Use `SparkSession.builder.getOrCreate()` instead of `get_spark()`:

```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()
```

Scripts are uploaded to the Workspace filesystem at `/Workspace/Users/<your_email>/apps/databricks-connect-starter/` (auto-detected from your token).

### Job compute modes

| Mode | CLI flag | How it works |
|------|----------|-------------|
| **Serverless** | *(default, no flag)* | No cluster config needed. Uses `Environment(client="2")`. |
| **Existing cluster** | `--cluster-id <ID>` | Uses a running cluster. Pass `env` to read from `DATABRICKS_CLUSTER_ID`. |
| **Job cluster** | `--new-cluster` | Ephemeral cluster created per run, terminated after. Customizable with `--spark-version`, `--node-type`, `--num-workers`. |

### Full job-create options

```bash
dbstarter job-create <scripts...> [options]
  --name "my-job"           # custom name (auto-generated if omitted)
  --parallel                # run tasks in parallel (default: sequential)
  --upload-path /Workspace/...  # custom upload dir (default: auto-detect)
  --cluster-id <ID|env>     # existing cluster mode
  --new-cluster             # ephemeral job cluster mode
  --spark-version X         # for --new-cluster (default: 15.4.x-scala2.12)
  --node-type X             # for --new-cluster (default: i3.xlarge)
  --num-workers N           # for --new-cluster (default: 1)
```

## CLI (`dbstarter`)

```bash
# Unity Catalog exploration
dbstarter catalogs                          # list catalogs
dbstarter schemas <catalog>                 # list schemas
dbstarter tables <catalog.schema>           # list tables
dbstarter describe <catalog.schema.table>   # show columns, types, comments

# Jobs
dbstarter jobs                              # list all jobs
dbstarter job-create <scripts...>           # create a job (see above)
dbstarter job-run <job_id>                  # trigger a run
dbstarter job-status <run_id>               # check run state

# Infrastructure
dbstarter clusters                          # list clusters + state
dbstarter secrets                           # list secret scopes and keys

# SQL query (runs via Databricks Connect)
dbstarter query "SELECT * FROM samples.nyctaxi.trips LIMIT 5"
```

All list commands support `--limit N` (default: 50).

## Notebooks

```bash
uv pip install -e ".[notebook]"
python -m ipykernel install --user --name dbstarter
jupyter notebook notebooks/getting_started.ipynb
```

Notebooks run locally but Spark operations execute on Databricks (same as scripts via Connect).

## Key functions reference

| Function | Module | Purpose |
|----------|--------|---------|
| `get_spark()` | `spark_session.py` | Single entry point for `DatabricksSession` (serverless or cluster) |
| `get_workspace_client()` | `workspace.py` | Creates a `WorkspaceClient` from `.env` credentials |
| `upload_to_workspace()` | `workspace.py` | Uploads files to Workspace filesystem (auto-detects user path) |
| `create_job()` | `workspace.py` | Creates a job with tasks; supports serverless/existing/new cluster |
| `run_job()` | `workspace.py` | Triggers a job run, returns `run_id` |
| `get_run_status()` | `workspace.py` | Returns lifecycle state and result state of a run |
| `run_query()` | `workspace.py` | Executes SQL via Spark Connect, returns list of dicts |
| `list_catalogs/schemas/tables()` | `workspace.py` | Unity Catalog browsing |
| `describe_table()` | `workspace.py` | Full table schema (columns, types, comments) |
| `list_clusters()` | `workspace.py` | List clusters with ID, name, and state |
| `list_secrets()` | `workspace.py` | List secret scopes and their keys |

## Known workspace constraints

- **DBFS disabled** -- Many workspaces block public DBFS. Upload uses the Workspace filesystem API (`w.workspace.upload()`) which works everywhere. The old `upload_to_dbfs()` is kept but deprecated.
- **Serverless environment** -- Jobs API requires `spec=compute.Environment(client="2")` in `JobEnvironment`. Using `client="1"` fails on most workspaces.
- **Free Edition** -- Supports serverless compute for jobs but not classic clusters (no Compute tab). Interactive Connect sessions work with serverless.

## Key Conventions

- Python 3.12 only (constrained in `pyproject.toml`).
- Package manager is **uv**, not pip.
- `get_spark()` is the single entry point for obtaining a SparkSession in interactive mode -- always use it rather than constructing sessions directly.
- Job scripts must NOT import `dbstarter` -- use `SparkSession.builder.getOrCreate()` instead.
- Workspace SDK calls go through `dbstarter/workspace.py` functions, not raw SDK usage.
- Example scripts live in `examples/` and import from `dbstarter` for interactive use.

## Testing Strategy

- **Unit tests**: Use a local `SparkSession` (not `DatabricksSession`) for pure transformation logic that doesn't need a live workspace.
- **Integration tests**: Use `get_spark()` (Databricks Connect) to verify end-to-end behavior against a real workspace. These require `.env` credentials and a running cluster or serverless.
- No test framework is configured yet. When adding tests, use `pytest` and place them in a `tests/` directory.

## Troubleshooting / Error Decision Tree

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `AuthorizationError` or `401 Unauthorized` | Invalid or expired `DATABRICKS_TOKEN` | Regenerate token in Databricks: User Settings > Developer > Access Tokens. Update `.env`. |
| `ClusterNotFoundException` or `INVALID_PARAMETER_VALUE` | `DATABRICKS_CLUSTER_ID` points to a non-existent or terminated cluster | Check cluster ID in Databricks UI, or remove it from `.env` to use serverless. |
| `TimeoutError` on first `get_spark()` call | Serverless cold start (30-60s) | Wait and retry. This is normal for the first connection. |
| `PermissionDenied` on `w.workspace.upload()` | Token lacks workspace write permissions | Ensure the token has "Can Manage" or "Can Edit" on the target Workspace path. |
| `DBFS is disabled` or `PERMISSION_DENIED` on DBFS | Workspace has DBFS disabled | Use `upload_to_workspace()` (Workspace filesystem API), never `upload_to_dbfs()`. |
| `ImportError: No module named 'dbstarter'` in a job | Job script imports `dbstarter` which is not on the cluster | Rewrite the script to use `SparkSession.builder.getOrCreate()` instead. |
| `Environment spec client version` error | Serverless jobs created with `client="1"` | Use `compute.Environment(client="2")` — see `create_job()` in `workspace.py`. |
