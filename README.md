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
python -c "from spark_session import get_spark; print(get_spark().sql('SELECT 1').collect())"
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
python example_query.py    # reads NYC taxi data, runs SQL, prints results
python example_etl.py      # runs a simple ETL pipeline with aggregations
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
dbstarter job-run <job_id>                  # trigger a job, prints run_id
dbstarter job-status <run_id>               # check run status

# Infrastructure
dbstarter clusters                          # list clusters and state
dbstarter secrets                           # list secret scopes and keys

# Query
dbstarter query "SELECT * FROM samples.nyctaxi.trips LIMIT 5"
```

All list commands support `--limit N` (default: 50).

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

### Criar um Job no Databricks via CLI

Se você quiser transformar esses dois scripts em um **Job** no Databricks (com duas tasks em sequência), use o script `create_job.sh`, que chama a **Databricks CLI**:

1. Autentique a CLI:

```bash
databricks auth login
```

2. Descubra o **Cluster ID** (em Compute > seu cluster).

3. Na raiz do projeto, rode:

```bash
chmod +x create_job.sh
./create_job.sh <SEU_CLUSTER_ID>
```

Isso vai:

- Copiar `example_query.py` e `example_etl.py` para `dbfs:/apps/databricks-connect-starter/`
- Criar um Job chamado `databricks-connect-starter-job` com:
  - Task `example_query` executando `example_query.py`
  - Task `example_etl` executando `example_etl.py` depois da primeira

### In your own scripts

```python
from spark_session import get_spark

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
spark_session.py          # Backward-compat shim (re-exports from package)
example_query.py          # Demo: read tables, SQL, see output
example_etl.py            # Demo: a more realistic ETL script
create_job.sh             # Creates a Databricks Job via CLI
notebooks/
  getting_started.ipynb   # Sample Jupyter notebook
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

## Serverless vs Classic Cluster

- **Serverless (default):** No cluster setup needed. Leave `DATABRICKS_CLUSTER_ID` empty. Compute spins up automatically.
- **Classic cluster:** Set `DATABRICKS_CLUSTER_ID` in `.env`. The cluster must be running and its DBR version must match your `databricks-connect` package version.
