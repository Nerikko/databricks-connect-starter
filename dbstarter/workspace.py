from __future__ import annotations

import os

from databricks.sdk import WorkspaceClient
from databricks.sdk.service import compute, jobs
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


# ── DBFS upload ────────────────────────────────────────────────────────────


def upload_to_dbfs(
    local_path: str,
    dbfs_dir: str = "dbfs:/apps/databricks-connect-starter",
) -> str:
    w = get_workspace_client()
    filename = os.path.basename(local_path)
    dbfs_path = f"{dbfs_dir}/{filename}"
    api_path = dbfs_path.removeprefix("dbfs:")

    dir_api_path = dbfs_dir.removeprefix("dbfs:")
    w.dbfs.mkdirs(dir_api_path)

    with open(local_path, "rb") as f:
        w.dbfs.upload(api_path, f, overwrite=True)

    return dbfs_path


# ── Job creation ───────────────────────────────────────────────────────────


def create_job(
    name: str,
    scripts: list[str],
    compute_mode: str = "serverless",
    cluster_id: str | None = None,
    spark_version: str = "15.4.x-scala2.12",
    node_type_id: str = "i3.xlarge",
    num_workers: int = 1,
    sequential: bool = True,
) -> dict:
    w = get_workspace_client()

    # Build task list
    task_list: list[jobs.Task] = []
    seen_keys: dict[str, int] = {}
    prev_key: str | None = None

    for script_path in scripts:
        base = script_path.rsplit("/", 1)[-1].removesuffix(".py")
        task_key = base.replace(" ", "_").replace("-", "_")

        # Ensure unique task keys
        if task_key in seen_keys:
            seen_keys[task_key] += 1
            task_key = f"{task_key}_{seen_keys[task_key]}"
        else:
            seen_keys[task_key] = 1

        task = jobs.Task(
            task_key=task_key,
            spark_python_task=jobs.SparkPythonTask(python_file=script_path),
        )

        if compute_mode == "existing_cluster":
            task.existing_cluster_id = cluster_id
        elif compute_mode == "new_cluster":
            task.job_cluster_key = "shared_job_cluster"
        elif compute_mode == "serverless":
            task.environment_key = "Default"

        if sequential and prev_key:
            task.depends_on = [jobs.TaskDependency(task_key=prev_key)]

        task_list.append(task)
        prev_key = task_key

    # Build job-level config
    create_kwargs: dict = {"name": name, "tasks": task_list}

    if compute_mode == "new_cluster":
        create_kwargs["job_clusters"] = [
            jobs.JobCluster(
                job_cluster_key="shared_job_cluster",
                new_cluster=compute.ClusterSpec(
                    spark_version=spark_version,
                    node_type_id=node_type_id,
                    num_workers=num_workers,
                ),
            )
        ]
    elif compute_mode == "serverless":
        create_kwargs["environments"] = [
            jobs.JobEnvironment(environment_key="Default"),
        ]

    result = w.jobs.create(**create_kwargs)
    return {"job_id": result.job_id}
