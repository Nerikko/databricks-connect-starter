# Databricks Connect Starter

Run PySpark scripts on your local machine while all Spark operations execute on Databricks. Errors, logs, and output appear in your local terminal — no jobs are created on Databricks; it's a live interactive session.

## Prerequisites

- Python 3.12
- [UV](https://github.com/astral-sh/uv) (package manager)
- A Databricks workspace with either serverless compute or a classic cluster

## Setup

### 1. Clone and install

```bash
cd databricks-connect-starter

uv venv --python 3.12
source .venv/bin/activate
uv pip install -e .
uv pip install -e ".[dev]"   # black, isort
```

### 2. Configure credentials

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:

```
DATABRICKS_HOST=https://dbc-xxxxx.cloud.databricks.com
DATABRICKS_TOKEN=dapi...
DATABRICKS_CLUSTER_ID=       # leave empty for serverless (recommended)
```

**Where to find these values:**
- **DATABRICKS_HOST** — your workspace URL (just the host, no query params like `?o=...`)
- **DATABRICKS_TOKEN** — generate a Personal Access Token in Databricks: User Settings > Developer > Access Tokens
- **DATABRICKS_CLUSTER_ID** — only needed if you want to use a classic cluster instead of serverless. Find it in Compute > your cluster > Advanced Options > Tags

### 3. Verify the connection

```bash
python -c "from dbstarter import get_spark; print(get_spark().sql('SELECT 1').collect())"
```

Expected output:

```
[Row(1=1)]
```

### 4. Generate your agent context file

Before writing any code, have a conversation with your code agent (Claude Code, Cursor, Copilot, etc.) to generate a context file (`CLAUDE.md`, `.cursorrules`, or equivalent) for this project. This file gives the agent full context about your specific Databricks workspace so it can help you effectively.

**Tell your agent something like:**

> Explore my Databricks workspace and create a CLAUDE.md file with context about my environment — catalogs, key tables, schemas, existing jobs, clusters, and any conventions I use.

The agent can use the built-in CLI to discover your workspace:

```bash
dbstarter catalogs                          # list all catalogs
dbstarter schemas my_catalog                # list schemas in a catalog
dbstarter tables my_catalog.my_schema       # list tables
dbstarter describe my_catalog.my_schema.my_table  # show columns and types
dbstarter jobs                              # list existing jobs
dbstarter clusters                          # list clusters and their state
```

The agent will ask you follow-up questions (which tables are important? what's your typical workflow?) and produce a context file that makes every future session more productive.

## Usage

### Quick start

```bash
python examples/example_query.py    # reads NYC taxi data, runs SQL, prints results
python examples/example_etl.py      # runs a simple ETL pipeline with aggregations
```

### CLI Reference

The `dbstarter` CLI lets you interact with your Databricks workspace directly from the terminal:

```bash
# Unity Catalog
dbstarter catalogs                          # list catalogs
dbstarter schemas <catalog>                 # list schemas in a catalog
dbstarter tables <catalog.schema>           # list tables in a schema
dbstarter describe <catalog.schema.table>   # show table columns and types

# Jobs
dbstarter jobs                              # list all jobs
dbstarter job-create script1.py script2.py  # create a job (serverless by default)
dbstarter job-run <job_id>                  # trigger a job, prints run_id
dbstarter job-status <run_id>               # check run status

# Infrastructure
dbstarter clusters                          # list clusters and state
dbstarter secrets                           # list secret scopes and keys

# Query
dbstarter query "SELECT * FROM samples.nyctaxi.trips LIMIT 5"
```

All list commands support `--limit N` (default: 50).

### VS Code

The project includes VS Code template configs in `.vscode/`. To set up your local environment:

```bash
cp .vscode/settings_template.json .vscode/settings.json
cp .vscode/launch_template.json .vscode/launch.json
cp .vscode/extensions_template.json .vscode/extensions.json
```

Then edit `.vscode/launch.json` and fill in your Databricks credentials (`DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `DATABRICKS_CLUSTER_ID`).

What each file gives you:
- **settings.json** — Python interpreter pointing to `.venv`, black formatter (line-length 90), isort with black profile, format-on-save enabled
- **launch.json** — "Debugger: current file" config with Databricks env vars and `justMyCode: false` so you can step into library code (F5)
- **extensions.json** — recommended extensions (Python, Debugpy, Jupyter)

The actual config files are gitignored — only the `*_template.json` files are committed. You can customize your local copies without affecting the repo.

### Notebooks

Install the optional notebook dependencies:

```bash
uv pip install -e ".[notebook]"
python -m ipykernel install --user --name dbstarter
```

Then open the sample notebook:

```bash
jupyter notebook notebooks/getting_started.ipynb
```

Your notebooks run locally but all Spark operations execute on Databricks — same as the scripts.

### Creating a Databricks Job

Use `dbstarter job-create` to turn your scripts into a Databricks Job. Choose the compute mode that fits your use case:

**Serverless (default)** — no cluster setup, simplest option:

```bash
dbstarter job-create example_query.py example_etl.py
```

**Existing cluster** — use a cluster that's already running:

```bash
dbstarter job-create --cluster-id 1234-567890-abcd123 example_query.py example_etl.py
```

**Job cluster** — creates an ephemeral cluster per run (cheaper for scheduled jobs):

```bash
dbstarter job-create --new-cluster example_query.py example_etl.py
```

You can customize the job cluster with `--spark-version`, `--node-type`, and `--num-workers`:

```bash
dbstarter job-create --new-cluster --spark-version 15.4.x-scala2.12 --node-type i3.xlarge --num-workers 4 example_etl.py
```

Other options:
- `--name "my-job"` — custom job name (auto-generated from script names if omitted)
- `--parallel` — run tasks in parallel instead of sequential
- `--dbfs-path dbfs:/my/path` — custom DBFS upload directory

Scripts are uploaded to DBFS and tasks are created in the order you list them (sequential by default).

### In your own scripts

```python
from dbstarter import get_spark

spark = get_spark()
df = spark.read.table("my_catalog.my_schema.my_table")
df.show()
```

Or use the workspace utilities programmatically:

```python
from dbstarter.workspace import list_catalogs, describe_table

for cat in list_catalogs():
    print(cat["name"])

info = describe_table("my_catalog.my_schema.my_table")
for col in info["columns"]:
    print(f"{col['name']:30s} {col['type']}")
```

## How it works

1. You run `python your_script.py` in your terminal
2. `databricks-connect` creates a SparkSession connected to your Databricks workspace
3. All Spark operations (reads, SQL, transforms) are sent to Databricks and executed there
4. Results stream back to your local terminal
5. All errors and stack traces appear locally — easy to debug

## File structure

```
dbstarter/                # Python package
  __init__.py             # Re-exports get_spark, get_workspace_client
  spark_session.py        # Core: creates remote SparkSession
  workspace.py            # Workspace utilities (catalogs, tables, jobs, clusters)
  __main__.py             # CLI entry point (dbstarter command)
examples/
  example_query.py        # Demo: read tables, SQL, see output
  example_etl.py          # Demo: a more realistic ETL script
notebooks/
  getting_started.ipynb   # Sample Jupyter notebook
.vscode/
  settings_template.json  # VS Code settings (black, isort, interpreter)
  launch_template.json    # Debug config with Databricks env vars
  extensions_template.json # Recommended extensions
.env.example              # Template for credentials
```

## Troubleshooting

**"pyspark and databricks-connect cannot be installed at the same time"**

```bash
uv pip uninstall pyspark pyspark-connect pyspark-client
uv pip install --upgrade --reinstall "databricks-connect>=16.1.0"
```

**Connection errors / DNS errors**

- Verify `DATABRICKS_HOST` matches your browser workspace URL exactly
- Make sure the token hasn't expired
- Run `databricks auth env` to check credentials are visible

**"Table not found" or permission errors**

- Check you have access to the catalog/schema in Databricks
- The example scripts use `samples.nyctaxi.trips` — this is a built-in sample dataset available in most workspaces

## Compute Modes

### Interactive sessions (Databricks Connect)

- **Serverless (default):** Leave `DATABRICKS_CLUSTER_ID` empty. Compute spins up automatically.
- **Classic cluster:** Set `DATABRICKS_CLUSTER_ID` in `.env`. The cluster must be running and its DBR version must match your `databricks-connect` package version.

### Jobs (`dbstarter job-create`)

| Mode | Flag | Best for |
|------|------|----------|
| **Serverless** | *(default, no flag)* | Simplest — no cluster config needed |
| **Existing cluster** | `--cluster-id ID` | Dev/testing with a running cluster |
| **Job cluster** | `--new-cluster` | Scheduled/production — ephemeral cluster is created per run and terminates after, which is cheaper |
