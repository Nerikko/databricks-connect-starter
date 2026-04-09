---
description: How credentials are loaded and which files contain secrets
globs: [".env*", "dbstarter/spark_session.py", "dbstarter/workspace.py"]
alwaysApply: false
---

# Credential Loading Mechanics

Both `get_spark()` and `get_workspace_client()` call `load_dotenv()` at the top. After that:

- `DatabricksSession.builder` auto-discovers `DATABRICKS_HOST` + `DATABRICKS_TOKEN` from env.
- `WorkspaceClient()` does the same auto-discovery.
- `DATABRICKS_CLUSTER_ID` is read via `os.environ.get()` — empty/missing means serverless.

## Secret Files — Never Commit

| File | Gitignored | Contains |
|------|-----------|----------|
| `.env` | Yes | `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `DATABRICKS_CLUSTER_ID` |
| `.vscode/launch.json` | Yes | Same credentials for debug sessions |

Committed safe files: `.env.example` (placeholders), `.vscode/launch_template.json` (placeholders).

## PYARROW_IGNORE_TIMEZONE

Set to `"1"` in VS Code launch config to suppress PyArrow timezone warnings. Can also be added to `.env` if running outside an IDE.
