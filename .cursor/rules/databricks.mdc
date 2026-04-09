---
description: Databricks Connect, SDK, and workspace patterns for this project
globs: ["dbstarter/**/*.py", "examples/**/*.py", "notebooks/**/*.ipynb"]
alwaysApply: false
---

# Databricks Patterns

## Two Execution Modes

| Mode | Where script runs | SparkSession source | Can import `dbstarter`? |
|------|-------------------|---------------------|------------------------|
| **Interactive (Connect)** | Locally | `from dbstarter import get_spark` | Yes |
| **Jobs** | On Databricks | `SparkSession.builder.getOrCreate()` | No |

**Interactive**: Script runs on your machine. Spark operations are sent to Databricks and results stream back. Always use `get_spark()` which handles dotenv loading, serverless/cluster detection, and session construction.

**Jobs**: Script runs entirely on a Databricks cluster. The `dbstarter` package is NOT installed there. Scripts must be self-contained — use only PySpark and standard library imports.

## SparkSession Patterns

Interactive scripts:
```python
from dbstarter import get_spark
spark = get_spark()  # Handles everything: dotenv, serverless/cluster, session builder
```

Job scripts (self-contained):
```python
from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()
```

Never construct `DatabricksSession` directly outside `spark_session.py`.

## Workspace SDK Patterns

- All SDK calls go through functions in `dbstarter/workspace.py`
- `get_workspace_client()` creates `WorkspaceClient` from `.env` credentials
- Each function creates its own client — no client passing between functions
- Functions return `list[dict]` or `dict` — SDK objects never leak out

### File Upload

Use `upload_to_workspace()` — DBFS is disabled on most workspaces.

- Uses `w.workspace.upload()` (Workspace filesystem API)
- Default target: `/Workspace/Users/<email>/apps/databricks-connect-starter/`
- Auto-detects user email from token

### Job Creation

Three compute modes for `create_job()`:

| Mode | CLI flag | Config |
|------|----------|--------|
| **Serverless** | *(default)* | `Environment(client="2")` in `JobEnvironment` |
| **Existing cluster** | `--cluster-id <ID>` | `existing_cluster_id` on each task |
| **Job cluster** | `--new-cluster` | Ephemeral `ClusterSpec`, `job_cluster_key="shared_job_cluster"` |

- Task keys are derived from script filenames (sanitized, de-duplicated with counter)
- Sequential by default (dependency chain). `--parallel` removes dependencies.
- All tasks share the same compute.

## Known Workspace Constraints

- **DBFS disabled** — Many workspaces block public DBFS. Always use Workspace filesystem API.
- **Serverless `client="2"`** — Jobs API requires `spec=compute.Environment(client="2")`. Using `"1"` fails.
- **Free Edition** — Supports serverless for jobs but not classic clusters. Interactive Connect works with serverless.
- **Cold start** — Serverless sessions take 30-60 seconds on first connection.
- **Test dataset** — `samples.nyctaxi.trips` is available on all workspaces for testing.
