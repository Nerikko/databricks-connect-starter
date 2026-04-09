---
description: Code style, formatting, import patterns, and naming conventions
globs: ["**/*.py"]
alwaysApply: false
---

# Code Conventions

## Formatting

- **black**: line-length 90 (configured in `pyproject.toml`)
- **isort**: black profile, line-length 90 (configured in `pyproject.toml`)
- Run before committing: `black . && isort .`

## Python Version

Python 3.12 only (`>=3.12,<3.13`). Use 3.12 features freely.

## Import Patterns

Standard library → third-party → local (isort enforces this).

Databricks imports used in this project:
```python
from databricks.connect import DatabricksSession       # spark_session.py only
from databricks.sdk import WorkspaceClient              # workspace.py only
from databricks.sdk.service import compute, jobs        # workspace.py for types
from databricks.sdk.service.workspace import ImportFormat  # workspace.py for upload
```

PySpark imports:
```python
from pyspark.sql import SparkSession                    # job scripts only
from pyspark.sql import functions as F                  # data transformations
```

Local imports:
```python
from dbstarter import get_spark                         # interactive scripts
from dbstarter import get_spark, get_workspace_client   # when both needed
from dbstarter.spark_session import get_spark           # internal (workspace.py)
from dbstarter.workspace import list_catalogs, ...      # internal (__main__.py)
```

## Function Patterns

- **Workspace functions** return `list[dict]` or `dict` — plain data, no SDK objects leak out
- **Each workspace function** calls `get_workspace_client()` internally — no client passing
- **Limit pattern**: `limit: int = 50` parameter with early `break` in iteration loop
- **CLI handlers**: named `cmd_<subcommand>(args)`, take `argparse.Namespace`
- **Minimal error handling**: no try/except around SDK calls — let errors propagate. Validate inputs in CLI handlers only.

## Naming

- **Functions**: `snake_case` — `get_spark`, `list_catalogs`, `upload_to_workspace`
- **CLI subcommands**: kebab-case — `job-create`, `job-run`, `job-status`
- **Task keys** (in jobs): underscore-separated, derived from filename — `test_job`, `example_etl`
- **CLI handler functions**: `cmd_` prefix — `cmd_catalogs`, `cmd_job_create`

## CLI Output

- Tabular output uses `print_table(rows, columns)` helper in `__main__.py`
- Rows are `list[dict]`, columns are `list[str]` of keys to display
- Dynamic column widths based on content
- Validation errors: print message and `sys.exit(1)`
