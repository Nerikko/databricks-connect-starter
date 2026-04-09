---
description: Environment variables, credentials setup, and .env configuration
globs: [".env*", "dbstarter/spark_session.py", "dbstarter/workspace.py"]
alwaysApply: false
---

# Environment & Credentials

## Required Environment Variables

Stored in `.env` at project root (gitignored). See `.env.example` for template.

| Variable | Required | Example | Purpose |
|----------|----------|---------|---------|
| `DATABRICKS_HOST` | Yes | `https://dbc-xxxxx.cloud.databricks.com` | Workspace URL (host only, no path/query) |
| `DATABRICKS_TOKEN` | Yes | `dapi...` | Personal Access Token (from Databricks: User Settings > Developer > Access Tokens) |
| `DATABRICKS_CLUSTER_ID` | No | `0123-456789-abcdefgh` | Classic cluster ID. Leave empty for serverless (recommended). |

## How Credentials Are Loaded

Both `get_spark()` and `get_workspace_client()` call `load_dotenv()` which reads `.env`:

- **`get_spark()`** (`spark_session.py`): Reads `DATABRICKS_CLUSTER_ID` via `os.environ.get()`. Empty/missing = serverless mode. The `DatabricksSession.builder` auto-discovers `DATABRICKS_HOST` and `DATABRICKS_TOKEN` from environment.
- **`get_workspace_client()`** (`workspace.py`): Returns `WorkspaceClient()` which auto-discovers `DATABRICKS_HOST` and `DATABRICKS_TOKEN` from environment.

## Credential Files

| File | Committed? | Contains |
|------|-----------|----------|
| `.env` | No (gitignored) | Actual credentials |
| `.env.example` | Yes | Template with placeholder values |
| `.vscode/launch.json` | No (gitignored) | Can also hold credentials for debugging |
| `.vscode/launch_template.json` | Yes | Template with placeholder fields |

Never suggest committing `.env`, `.vscode/launch.json`, or any file containing tokens.

## PYARROW_IGNORE_TIMEZONE

Set to `"1"` in VS Code launch config to suppress PyArrow timezone warnings during interactive sessions. Not required in `.env` but can be added if running outside VS Code/Cursor.

## Compute Selection

**Interactive sessions** (via `get_spark()`):
- `DATABRICKS_CLUSTER_ID` empty → serverless (recommended, no cluster management)
- `DATABRICKS_CLUSTER_ID` set → classic cluster (must be running, DBR version must match databricks-connect)

**Jobs** (via `dbstarter job-create`):
- Default → serverless
- `--cluster-id <ID>` → existing cluster (use `--cluster-id env` to read from `DATABRICKS_CLUSTER_ID`)
- `--new-cluster` → ephemeral job cluster (customizable with `--spark-version`, `--node-type`, `--num-workers`)
