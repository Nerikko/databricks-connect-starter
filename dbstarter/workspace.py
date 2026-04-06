from __future__ import annotations

from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv


def get_workspace_client() -> WorkspaceClient:
    load_dotenv()
    return WorkspaceClient()


# ── Unity Catalog ───────────────────────────────────────────────────────────


def list_catalogs(limit: int = 50) -> list[dict]:
    w = get_workspace_client()
    results = []
    for cat in w.catalogs.list():
        results.append({"name": cat.name, "comment": cat.comment or ""})
        if len(results) >= limit:
            break
    return results


def list_schemas(catalog: str, limit: int = 50) -> list[dict]:
    w = get_workspace_client()
    results = []
    for schema in w.schemas.list(catalog_name=catalog):
        results.append({"name": schema.name, "comment": schema.comment or ""})
        if len(results) >= limit:
            break
    return results


def list_tables(catalog: str, schema: str, limit: int = 50) -> list[dict]:
    w = get_workspace_client()
    results = []
    for table in w.tables.list(catalog_name=catalog, schema_name=schema):
        results.append({
            "name": table.name,
            "table_type": str(table.table_type.value) if table.table_type else "",
        })
        if len(results) >= limit:
            break
    return results


def describe_table(full_name: str) -> dict:
    w = get_workspace_client()
    table = w.tables.get(full_name)
    columns = []
    for col in table.columns or []:
        columns.append({
            "name": col.name,
            "type": col.type_text or "",
            "comment": col.comment or "",
        })
    return {
        "name": table.full_name,
        "table_type": str(table.table_type.value) if table.table_type else "",
        "comment": table.comment or "",
        "columns": columns,
    }


# ── Jobs ────────────────────────────────────────────────────────────────────


def list_jobs(limit: int = 50) -> list[dict]:
    w = get_workspace_client()
    results = []
    for job in w.jobs.list():
        results.append({
            "job_id": job.job_id,
            "name": job.settings.name if job.settings else "",
        })
        if len(results) >= limit:
            break
    return results


def run_job(job_id: int) -> dict:
    w = get_workspace_client()
    wait = w.jobs.run_now(job_id)
    return {"run_id": wait.run_id}


def get_run_status(run_id: int) -> dict:
    w = get_workspace_client()
    run = w.jobs.get_run(run_id)
    state = run.state
    return {
        "run_id": run.run_id,
        "state": str(state.life_cycle_state.value) if state and state.life_cycle_state else "",
        "result_state": str(state.result_state.value) if state and state.result_state else "",
    }


# ── Clusters ────────────────────────────────────────────────────────────────


def list_clusters(limit: int = 50) -> list[dict]:
    w = get_workspace_client()
    results = []
    for cluster in w.clusters.list():
        results.append({
            "cluster_id": cluster.cluster_id,
            "name": cluster.cluster_name or "",
            "state": str(cluster.state.value) if cluster.state else "",
        })
        if len(results) >= limit:
            break
    return results


# ── Secrets ─────────────────────────────────────────────────────────────────


def list_secrets() -> list[dict]:
    w = get_workspace_client()
    results = []
    for scope in w.secrets.list_scopes():
        keys = [s.key for s in w.secrets.list_secrets(scope.name)]
        results.append({"scope": scope.name, "keys": keys})
    return results


# ── Query ───────────────────────────────────────────────────────────────────


def run_query(sql: str) -> list[dict]:
    from dbstarter.spark_session import get_spark

    spark = get_spark()
    rows = spark.sql(sql).collect()
    return [row.asDict() for row in rows]
