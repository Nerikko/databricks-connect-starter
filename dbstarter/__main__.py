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
        "job-run": cmd_job_run,
        "job-status": cmd_job_status,
        "clusters": cmd_clusters,
        "secrets": cmd_secrets,
        "query": cmd_query,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
