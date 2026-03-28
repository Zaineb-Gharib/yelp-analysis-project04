from __future__ import annotations

import socket
from typing import Dict, List

from hive_copilot.backend.app.core.config import get_settings


SETTINGS = get_settings()


SCHEMA_TABLES: List[Dict[str, object]] = [
    {
        "name": "business",
        "description": "Core business attributes loaded from the Yelp Hive warehouse.",
        "columns": [
            "business_id STRING",
            "name STRING",
            "city STRING",
            "state STRING",
            "stars DOUBLE",
            "review_count INT",
            "categories STRING",
        ],
    },
    {
        "name": "users",
        "description": "Yelp user profiles and engagement fields exposed in Hive.",
        "columns": [
            "user_id STRING",
            "name STRING",
            "review_count INT",
            "yelping_since STRING",
            "fans INT",
            "average_stars DOUBLE",
            "elite STRING",
        ],
    },
    {
        "name": "review",
        "description": "Review facts partitioned by review date in the analytical layer.",
        "columns": [
            "review_id STRING",
            "user_id STRING",
            "business_id STRING",
            "stars INT",
            "review_date STRING",
            "text STRING",
            "useful INT",
            "funny INT",
            "cool INT",
        ],
    },
]

QUICK_QUERIES: List[Dict[str, str]] = [
    {
        "label": "Sample Businesses",
        "prompt": "Show 5 businesses with name, city, state, stars, and review count.",
    },
    {
        "label": "Top Mexican in Philly",
        "prompt": "Show me the top 5 highest-rated Mexican restaurants in Philadelphia with more than 500 reviews.",
    },
    {
        "label": "Average Stars by State",
        "prompt": "What is the average business rating by state?",
    },
    {
        "label": "Top Cities by Businesses",
        "prompt": "Which cities have the most businesses?",
    },
    {
        "label": "Elite Users by City",
        "prompt": "Which cities have the most elite Yelp users?",
    },
    {
        "label": "Top Business Categories",
        "prompt": "What are the top business categories?",
    },
    {
        "label": "Highest Rated Businesses",
        "prompt": "Show the top 5 highest rated businesses with city and state.",
    },
]


def _table_description(name: str) -> str:
    return f"Hive table '{name}' discovered from metastore database '{SETTINGS.hive_database}'."


def _extract_columns(table_obj: object) -> List[str]:
    cols: List[str] = []

    sd = getattr(table_obj, "sd", None)
    if sd is not None and getattr(sd, "cols", None):
        for col in sd.cols:
            col_name = str(getattr(col, "name", "")).strip()
            col_type = str(getattr(col, "type", "")).strip()
            if col_name:
                cols.append(f"{col_name} {col_type or 'STRING'}")

    if cols:
        return cols

    if isinstance(table_obj, dict):
        columns = table_obj.get("columns") or table_obj.get("cols") or []
        for col in columns:
            if isinstance(col, dict):
                col_name = str(col.get("name", "")).strip()
                col_type = str(col.get("type", "")).strip()
                if col_name:
                    cols.append(f"{col_name} {col_type or 'STRING'}")
            elif isinstance(col, str) and col.strip():
                cols.append(col.strip())

    return cols


def _extract_stats(table_obj: object) -> Dict[str, object]:
    parameters = getattr(table_obj, "parameters", None)
    if isinstance(parameters, dict):
        return {
            "num_rows": parameters.get("numRows") or parameters.get("numrows"),
            "total_size": parameters.get("totalSize") or parameters.get("totalsize"),
        }

    if isinstance(table_obj, dict):
        table_parameters = table_obj.get("parameters")
        if isinstance(table_parameters, dict):
            return {
                "num_rows": table_parameters.get("numRows") or table_parameters.get("numrows"),
                "total_size": table_parameters.get("totalSize") or table_parameters.get("totalsize"),
            }

    return {}


def _load_schema_overview_from_hms() -> List[Dict[str, object]]:
    try:
        from hmsclient import hmsclient as thrift_hmsclient
    except Exception as exc:
        raise RuntimeError(f"Failed to import hmsclient: {exc}") from exc

    tables: List[Dict[str, object]] = []

    # hmsclient currently supports host/port and optional auth mechanism depending on deployment.
    with thrift_hmsclient.HMSClient(host=SETTINGS.hms_host, port=SETTINGS.hms_port) as client:
        table_names = client.get_all_tables(SETTINGS.hive_database)

        for table_name in sorted(table_names):
            table_obj = client.get_table(SETTINGS.hive_database, table_name)
            columns = _extract_columns(table_obj)
            stats = _extract_stats(table_obj)
            tables.append(
                {
                    "name": table_name,
                    "description": _table_description(table_name),
                    "columns": columns,
                    "stats": stats,
                }
            )

    return tables


def get_schema_overview() -> List[Dict[str, object]]:
    if SETTINGS.frontend_mode == "mock":
        return SCHEMA_TABLES
    return _load_schema_overview_from_hms()


def get_quick_queries() -> List[Dict[str, str]]:
    return QUICK_QUERIES


def build_schema_context() -> str:
    blocks: List[str] = []
    for table in get_schema_overview():
        columns = ", ".join([str(column) for column in table.get("columns", [])])
        blocks.append(
            "Table: {name}\nDescription: {description}\nColumns: {columns}".format(
                name=table.get("name", ""),
                description=table.get("description", ""),
                columns=columns,
            )
        )
    return "\n\n".join(blocks)


def check_hms_connection() -> tuple[bool, str]:
    if SETTINGS.frontend_mode == "mock":
        return True, "mock mode"
    try:
        with socket.create_connection((SETTINGS.hms_host, SETTINGS.hms_port), timeout=5):
            pass
    except Exception as exc:
        return False, f"socket check failed: {exc}"

    try:
        tables = _load_schema_overview_from_hms()
        return True, f"ok ({len(tables)} tables in {SETTINGS.hive_database})"
    except Exception as exc:
        return False, str(exc)
