---
description: Databricks-specific patterns beyond what CLAUDE.md covers — Delta Lake, secrets, SDK internals
globs: ["dbstarter/**/*.py", "examples/**/*.py", "notebooks/**/*.ipynb"]
alwaysApply: false
---

# Databricks Patterns

## Quick Mode Reference

| Mode | SparkSession | Can import `dbstarter`? |
|------|-------------|------------------------|
| **Interactive** | `get_spark()` | Yes |
| **Job** | `SparkSession.builder.getOrCreate()` | No — self-contained only |

## Deprecated: upload_to_dbfs()

`upload_to_dbfs()` in `workspace.py` is deprecated. DBFS is disabled on most workspaces. Always use `upload_to_workspace()` which uses the Workspace filesystem API (`w.workspace.upload()`).

## Secrets in Job Scripts

Job scripts cannot read `.env`. To access secrets on the cluster, use the Databricks Secrets API via `dbutils`:

```python
# Inside a job script (not interactive — dbutils is only available on clusters)
token = dbutils.secrets.get(scope="my-scope", key="my-key")
```

For interactive scripts, continue using `.env` + `python-dotenv`.

## Delta Lake Conventions

When writing to Delta tables in this project:

- **MERGE** for upserts — prefer `MERGE INTO ... USING ... WHEN MATCHED THEN UPDATE WHEN NOT MATCHED THEN INSERT` over delete+insert.
- **OPTIMIZE** after large writes to compact small files: `spark.sql("OPTIMIZE catalog.schema.table")`.
- **ZORDER** on high-cardinality filter columns: `spark.sql("OPTIMIZE catalog.schema.table ZORDER BY (col)")`.
- **Partitioning** — only partition by low-cardinality columns (date, region). Over-partitioning creates small file problems.
- **Schema evolution** — use `option("mergeSchema", "true")` on `.write` when adding new columns.

## SDK Internals (for workspace.py contributors)

- Each workspace function calls `get_workspace_client()` internally — no client passing.
- Functions return `list[dict]` or `dict` — SDK objects must not leak to callers.
- Limit pattern: `limit: int = 50` with early `break` in iteration.
- Upload target auto-detected: `/Workspace/Users/<email>/apps/databricks-connect-starter/`.
- Serverless jobs: `spec=compute.Environment(client="2")` — `"1"` fails silently.
- Task keys derived from filenames, de-duplicated with `_2`, `_3` suffix.
