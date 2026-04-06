from __future__ import annotations

import argparse
import sys

from dbstarter import workspace


# ── Output helpers ──────────────────────────────────────────────────────────


def print_table(rows: list[dict], columns: list[str] | None = None) -> None:
    if not rows:
        print("(no results)")
        return
    columns = columns or list(rows[0].keys())
    widths = {col: len(col) for col in columns}
    for row in rows:
        for col in columns:
            widths[col] = max(widths[col], len(str(row.get(col, ""))))
    header = "  ".join(col.ljust(widths[col]) for col in columns)
    sep = "  ".join("-" * widths[col] for col in columns)
    print(header)
    print(sep)
    for row in rows:
        print("  ".join(str(row.get(col, "")).ljust(widths[col]) for col in columns))


def parse_dot_name(name: str, expected_parts: int, label: str) -> list[str]:
    parts = name.split(".")
    if len(parts) != expected_parts:
        print(f"Error: expected {label} (dot-separated, {expected_parts} parts), got '{name}'")
        sys.exit(1)
    return parts


# ── Subcommand handlers ────────────────────────────────────────────────────


def cmd_catalogs(args: argparse.Namespace) -> None:
    rows = workspace.list_catalogs(limit=args.limit)
    print_table(rows, ["name", "comment"])


def cmd_schemas(args: argparse.Namespace) -> None:
    rows = workspace.list_schemas(args.catalog, limit=args.limit)
    print_table(rows, ["name", "comment"])


def cmd_tables(args: argparse.Namespace) -> None:
    parts = parse_dot_name(args.catalog_schema, 2, "catalog.schema")
    rows = workspace.list_tables(parts[0], parts[1], limit=args.limit)
    print_table(rows, ["name", "table_type"])


def cmd_describe(args: argparse.Namespace) -> None:
    parse_dot_name(args.full_name, 3, "catalog.schema.table")
    info = workspace.describe_table(args.full_name)
    print(f"Table: {info['name']}")
    if info["comment"]:
        print(f"Comment: {info['comment']}")
    print(f"Type: {info['table_type']}")
    print()
    if info["columns"]:
        print_table(info["columns"], ["name", "type", "comment"])
    else:
        print("(no column info available)")


def cmd_jobs(args: argparse.Namespace) -> None:
    rows = workspace.list_jobs(limit=args.limit)
    print_table(rows, ["job_id", "name"])


def cmd_job_run(args: argparse.Namespace) -> None:
    result = workspace.run_job(int(args.job_id))
    print(f"Run started. run_id: {result['run_id']}")


def cmd_job_status(args: argparse.Namespace) -> None:
    result = workspace.get_run_status(int(args.run_id))
    print(f"run_id:       {result['run_id']}")
    print(f"state:        {result['state']}")
    print(f"result_state: {result['result_state']}")


def cmd_clusters(args: argparse.Namespace) -> None:
    rows = workspace.list_clusters(limit=args.limit)
    print_table(rows, ["cluster_id", "name", "state"])


def cmd_secrets(args: argparse.Namespace) -> None:
    scopes = workspace.list_secrets()
    if not scopes:
        print("(no secret scopes)")
        return
    for scope in scopes:
        print(f"[{scope['scope']}]")
        for key in scope["keys"]:
            print(f"  - {key}")
        print()


def cmd_query(args: argparse.Namespace) -> None:
    rows = workspace.run_query(args.sql)
    print_table(rows)


def cmd_job_create(args: argparse.Namespace) -> None:
    import os

    # Determine compute mode
    if args.cluster_id:
        compute_mode = "existing_cluster"
        cluster_id = args.cluster_id
        if cluster_id == "env":
            cluster_id = os.environ.get("DATABRICKS_CLUSTER_ID", "")
            if not cluster_id:
                print("Error: DATABRICKS_CLUSTER_ID is not set in environment")
                sys.exit(1)
    elif args.new_cluster:
        compute_mode = "new_cluster"
        cluster_id = None
    else:
        compute_mode = "serverless"
        cluster_id = None

    # Validate scripts exist
    for script in args.scripts:
        if not os.path.isfile(script):
            print(f"Error: file not found: {script}")
            sys.exit(1)

    # Upload scripts to DBFS
    print(f"Uploading {len(args.scripts)} script(s) to {args.dbfs_path}...")
    dbfs_paths = []
    for script in args.scripts:
        path = workspace.upload_to_dbfs(script, args.dbfs_path)
        print(f"  {script} -> {path}")
        dbfs_paths.append(path)

    # Generate job name if not provided
    if args.name:
        job_name = args.name
    else:
        basenames = [os.path.splitext(os.path.basename(s))[0] for s in args.scripts]
        job_name = "job-" + "-".join(basenames)

    sequential = not args.parallel

    # Create the job
    print(f"Creating job '{job_name}' ({compute_mode})...")
    result = workspace.create_job(
        name=job_name,
        scripts=dbfs_paths,
        compute_mode=compute_mode,
        cluster_id=cluster_id,
        spark_version=args.spark_version,
        node_type_id=args.node_type,
        num_workers=args.num_workers,
        sequential=sequential,
    )

    print(f"Job created. job_id: {result['job_id']}")
    print("View it in Workflows > Jobs in the Databricks workspace.")


# ── Main ────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="dbstarter",
        description="Databricks workspace CLI — browse catalogs, tables, jobs, clusters and run queries.",
    )
    sub = parser.add_subparsers(dest="command")

    # catalogs
    p = sub.add_parser("catalogs", help="List catalogs")
    p.add_argument("--limit", type=int, default=50)

    # schemas
    p = sub.add_parser("schemas", help="List schemas in a catalog")
    p.add_argument("catalog", help="Catalog name")
    p.add_argument("--limit", type=int, default=50)

    # tables
    p = sub.add_parser("tables", help="List tables in a schema")
    p.add_argument("catalog_schema", help="catalog.schema (dot-separated)")
    p.add_argument("--limit", type=int, default=50)

    # describe
    p = sub.add_parser("describe", help="Describe a table (columns and types)")
    p.add_argument("full_name", help="catalog.schema.table (dot-separated)")

    # jobs
    p = sub.add_parser("jobs", help="List jobs")
    p.add_argument("--limit", type=int, default=50)

    # job-run
    p = sub.add_parser("job-run", help="Trigger a job run")
    p.add_argument("job_id", help="Job ID")

    # job-create
    p = sub.add_parser("job-create", help="Create a job from Python scripts")
    p.add_argument("scripts", nargs="+", help="Python script(s) to run as tasks")
    p.add_argument("--name", default=None, help="Job name (auto-generated if omitted)")
    p.add_argument(
        "--dbfs-path",
        default="dbfs:/apps/databricks-connect-starter",
        help="DBFS directory for uploading scripts",
    )
    p.add_argument(
        "--parallel",
        action="store_true",
        help="Run tasks in parallel (default: sequential)",
    )
    compute_group = p.add_mutually_exclusive_group()
    compute_group.add_argument(
        "--cluster-id",
        metavar="ID",
        help="Use an existing cluster (pass 'env' to read from DATABRICKS_CLUSTER_ID)",
    )
    compute_group.add_argument(
        "--new-cluster",
        action="store_true",
        help="Create an ephemeral job cluster per run",
    )
    p.add_argument(
        "--spark-version",
        default="15.4.x-scala2.12",
        help="Spark version for new cluster (default: 15.4.x-scala2.12)",
    )
    p.add_argument(
        "--node-type",
        default="i3.xlarge",
        help="Node type for new cluster (default: i3.xlarge)",
    )
    p.add_argument(
        "--num-workers",
        type=int,
        default=1,
        help="Number of workers for new cluster (default: 1)",
    )

    # job-status
    p = sub.add_parser("job-status", help="Check run status")
    p.add_argument("run_id", help="Run ID")

    # clusters
    p = sub.add_parser("clusters", help="List clusters")
    p.add_argument("--limit", type=int, default=50)

    # secrets
    sub.add_parser("secrets", help="List secret scopes and keys")

    # query
    p = sub.add_parser("query", help="Run a SQL query via Spark")
    p.add_argument("sql", help="SQL statement")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "catalogs": cmd_catalogs,
        "schemas": cmd_schemas,
        "tables": cmd_tables,
        "describe": cmd_describe,
        "jobs": cmd_jobs,
        "job-create": cmd_job_create,
        "job-run": cmd_job_run,
        "job-status": cmd_job_status,
        "clusters": cmd_clusters,
        "secrets": cmd_secrets,
        "query": cmd_query,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
