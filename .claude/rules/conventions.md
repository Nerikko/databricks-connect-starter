---
description: Code patterns, naming conventions, and logging guidance
globs: ["**/*.py"]
alwaysApply: false
---

# Code Conventions

## Import Order

Standard library → third-party → local (isort enforces). `from __future__ import annotations` is used in `workspace.py` and `__main__.py`.

## Function Patterns

- **Workspace functions** return `list[dict]` or `dict` — SDK objects never leak out.
- **Each workspace function** creates its own client via `get_workspace_client()`.
- **Limit pattern**: `limit: int = 50` with early `break` in iteration loop.
- **CLI handlers**: named `cmd_<subcommand>(args)`, take `argparse.Namespace`.
- **No try/except** around SDK calls — let errors propagate. Validate inputs in CLI handlers only.

## Naming

- **Functions**: `snake_case` — `get_spark`, `list_catalogs`, `upload_to_workspace`
- **CLI subcommands**: kebab-case — `job-create`, `job-run`, `job-status`
- **CLI handler functions**: `cmd_` prefix — `cmd_catalogs`, `cmd_job_create`
- **Job task keys**: underscore-separated, derived from filename — `test_job`, `example_etl`

## Logging in Job Scripts

Job script output from `print()` is **not reliably visible** via the Databricks Jobs API or `dbstarter job-status`. For job scripts that need observable output, use the `logging` module:

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Processing started")
```

The CLI (`__main__.py`) uses `print()` for user-facing output — that is fine since it runs locally.

## CLI Output

- Tabular output uses `print_table(rows, columns)` in `__main__.py`.
- Rows are `list[dict]`, columns are `list[str]` of keys.
- Validation errors: print message + `sys.exit(1)`.
