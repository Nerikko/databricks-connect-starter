---
description: AI agent workflow rules for Databricks development
alwaysApply: true
---

# Agent Workflow Rules for Databricks Development

## 1. Environment Awareness

**Highest priority rule — check this before every suggestion.**

Code is always written in dev but WILL run in production. The ONLY variable that changes between dev and prod is `CATALOG`. All schemas (raw, processed, marts, etc.) exist under the same catalog.

Always define at the top of every script:

```python
CATALOG = "dev"  # change to "prod" before promoting
```

Rules:

- Never hardcode catalog name anywhere else in the script
- Never hardcode credentials, tokens, or host URLs
- Always use full 3-part names: `f"{CATALOG}.schema.table"`
- Exception: system catalogs like `"samples"` can be hardcoded
- Add this header comment to every script:

```python
# ENV: dev | target: prod
# Inputs:  <catalog.schema.table list>
# Outputs: <catalog.schema.table list>
```

## 2. Environment Config Pattern

**Interactive scripts** — define CATALOG at top as a variable:

```python
CATALOG = "dev"
```

**Job scripts** — read CATALOG from env var with fallback:

```python
import os
CATALOG = os.getenv("CATALOG", "dev")
```

Never use if/else to switch environments inside logic code.

## 3. New Interactive Scripts

- Always use: `from dbstarter import get_spark`
- Never use raw `DatabricksSession` directly

Structure:

```python
# ENV: dev | target: prod
# Inputs:  catalog.schema.source_table
# Outputs: catalog.schema.target_table

from dbstarter import get_spark

CATALOG = "dev"

spark = get_spark()

# ... logic ...
```

## 4. New Job Scripts

- Always self-contained, no `dbstarter` imports
- Always use: `SparkSession.builder.getOrCreate()`
- Always read CATALOG from env var

Structure:

```python
# ENV: dev | target: prod
# Inputs:  catalog.schema.source_table
# Outputs: catalog.schema.target_table

import logging
import os

from pyspark.sql import SparkSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CATALOG = os.getenv("CATALOG", "dev")

spark = SparkSession.builder.getOrCreate()

# ... logic ...
```

## 5. Spark API Choice

- **`spark.sql()`** — for exploration and quick queries
- **DataFrame API** — for reusable ETL logic and production code
- **Never mix** both styles in the same function

## 6. ETL Script Structure

Always in this order:

1. Header comment (ENV, inputs, outputs)
2. CATALOG variable
3. Spark session
4. Read source tables
5. Log row count after read: `logger.info(f"Read {df.count()} rows")`
6. Transform
7. Data quality assertions (see section 7)
8. Write with idempotent pattern (see section 8)
9. Log row count after write

## 7. Data Quality — Required Before Every Write

```python
# Replace 'id', 'name', 'value', 'updated_at' with your actual key columns

# Assert not empty
row_count = df.count()
if row_count == 0:
    raise ValueError("DataFrame is empty — aborting write")

# Assert no nulls on key columns
null_count = df.filter(df["id"].isNull()).count()
if null_count > 0:
    raise ValueError(f"{null_count} null values in key column 'id'")

# Assert schema matches expected
expected_cols = {"id", "name", "value", "updated_at"}
actual_cols = set(df.columns)
if actual_cols != expected_cols:
    raise ValueError(f"Schema mismatch: expected {expected_cols}, got {actual_cols}")

# Warn on significant row count drop (compare vs previous run)
logger.info(f"Row count: {row_count}")
```

Rules:

- Never write bad data silently — always fail loudly
- Log a warning if row count drops more than 20% vs previous run

## 8. Idempotent Writes — Never Use Bare Append

**Full refresh:**

```python
df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(
    f"{CATALOG}.schema.table"
)
```

**Incremental (MERGE with unique key):**

```python
df.createOrReplaceTempView("updates")
spark.sql(f"""
    MERGE INTO {CATALOG}.schema.table AS target
    USING updates AS source
    ON target.id = source.id
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
""")
```

Rules:

- Delta tables: use MERGE or replaceWhere
- Always safe to re-run without duplicating data
- Never use bare `.mode("append")` without deduplication logic

## 9. Error Handling in Jobs

```python
import logging
import traceback

logger = logging.getLogger(__name__)

try:
    # ... main logic ...
    logger.info("Job completed successfully")
except Exception as e:
    logger.error(f"Job failed: {e}")
    logger.error(traceback.format_exc())
    raise  # re-raise so the job shows as FAILED in Databricks
```

Rules:

- Always wrap main logic in try/except
- Use `logging` module, never `print()`
- On failure: log the error with full traceback
- Re-raise the exception so the job shows as failed in Databricks
- Never swallow exceptions silently

## 10. Schema Evolution

- Always use Delta with schema evolution enabled when reading:
  `spark.read.option("mergeSchema", "true")`
- When writing, decide explicitly: evolve schema or reject mismatches
- Document expected schema in the script header comment

## 11. Testing Workflow

Always in this order:

1. **Run locally** via Databricks Connect (`CATALOG = "dev"`)
2. **Verify** in Databricks Query History that it ran on serverless
3. **Deploy** with `dbstarter job-create` only after local run succeeds

Never deploy to job without a successful local test first.

## 12. Production Promotion Checklist

**Surface this checklist before every `job-create` suggestion:**

- [ ] Is `CATALOG` variable set to `"prod"` or reading from env var?
- [ ] Is `CATALOG` env var configured in the job?
- [ ] Are there any hardcoded dev table or catalog names?
- [ ] Are data quality assertions in place?
- [ ] Is the write idempotent (MERGE or overwrite, no bare append)?
- [ ] Is error handling using `logging`, not `print()`?
- [ ] Is the script fully self-contained (no `dbstarter` imports)?
