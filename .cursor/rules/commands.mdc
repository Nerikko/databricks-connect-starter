---
description: Quick command reference for setup, running, and formatting
alwaysApply: true
---

# Commands Cheatsheet

```bash
# Setup
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -e .              # core
uv pip install -e ".[dev]"       # + black, isort
uv pip install -e ".[notebook]"  # + jupyter

# Verify connection
python -c "from dbstarter import get_spark; print(get_spark().sql('SELECT 1').collect())"

# Format
black . && isort .

# Run examples
python examples/example_query.py
python examples/example_etl.py

# CLI (full reference in CLAUDE.md)
dbstarter catalogs | schemas | tables | describe | jobs | job-create | job-run | job-status | clusters | secrets | query
```
