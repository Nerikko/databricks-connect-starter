---
description: Development commands for setup, running scripts, formatting, and CLI usage
alwaysApply: true
---

# Development Commands

## Setup

```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e .              # core dependencies
uv pip install -e ".[dev]"       # + black, isort
uv pip install -e ".[notebook]"  # + jupyter, ipykernel
```

Always use `uv`, never `pip` directly.

## Verify Connection

```bash
python -c "from dbstarter import get_spark; print(get_spark().sql('SELECT 1').collect())"
# Expected: [Row(1=1)]
```

## Run Scripts

```bash
python examples/example_query.py    # NYC taxi query demo
python examples/example_etl.py      # ETL pipeline demo
dbstarter <subcommand>              # CLI (installed as console script)
python -m dbstarter <subcommand>    # alternative CLI invocation
```

## Formatting

```bash
black . && isort .
```

## CLI Quick Reference

```bash
# Unity Catalog exploration
dbstarter catalogs                          # list catalogs
dbstarter schemas <catalog>                 # list schemas
dbstarter tables <catalog.schema>           # list tables
dbstarter describe <catalog.schema.table>   # show columns and types

# Jobs
dbstarter job-create <scripts...>           # create a job from scripts
dbstarter job-run <job_id>                  # trigger a run
dbstarter job-status <run_id>              # check run state
dbstarter jobs                              # list all jobs

# Infrastructure
dbstarter clusters                          # list clusters + state
dbstarter secrets                           # list secret scopes and keys

# SQL query (via Databricks Connect)
dbstarter query "SELECT * FROM samples.nyctaxi.trips LIMIT 5"
```

All list commands support `--limit N` (default: 50).

## VS Code / Cursor Setup

```bash
cp .vscode/settings_template.json .vscode/settings.json
cp .vscode/launch_template.json .vscode/launch.json
cp .vscode/extensions_template.json .vscode/extensions.json
```

Then fill in your Databricks credentials in `launch.json`.

## Notebooks

```bash
uv pip install -e ".[notebook]"
python -m ipykernel install --user --name dbstarter
jupyter notebook notebooks/getting_started.ipynb
```
