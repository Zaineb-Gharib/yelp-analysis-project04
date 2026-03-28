from __future__ import annotations

import csv
import io
import json
import logging
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from hive_copilot.backend.app.core.config import get_settings
from hive_copilot.backend.app.services.hms_service import get_schema_overview


SETTINGS = get_settings()
logger = logging.getLogger(__name__)


def sanitize_sql(sql: str) -> str:
    sql = sql.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    if sql.endswith(";"):
        sql = sql[:-1].strip()
    if ";" in sql:
        raise ValueError("Multiple statements are not allowed")

    sql_upper = sql.upper()
    if not (sql_upper.startswith("SELECT") or sql_upper.startswith("WITH")):
        raise ValueError("Only SELECT/CTE queries are allowed")

    dangerous = [
        " DROP ",
        " DELETE ",
        " INSERT ",
        " UPDATE ",
        " ALTER ",
        " CREATE ",
        " TRUNCATE ",
    ]
    padded = f" {sql_upper} "
    for cmd in dangerous:
        if cmd in padded:
            raise ValueError(f"Dangerous command '{cmd.strip()}' not allowed")

    return sql


def _jdbc_url() -> str:
    params: List[str] = []

    if SETTINGS.hive_auth and SETTINGS.hive_auth != "NONE":
        params.append(f"auth={SETTINGS.hive_auth}")

    if SETTINGS.hive_kerberos_service:
        params.append(f"principal={SETTINGS.hive_kerberos_service}")

    if SETTINGS.hive_use_ssl:
        params.append("ssl=true")

    suffix = ""
    if params:
        suffix = ";" + ";".join(params)

    return (
        f"jdbc:hive2://{SETTINGS.hive_host}:{SETTINGS.hive_port}/{SETTINGS.hive_database}{suffix}"
    )


def _beeline_cmd(sql: str) -> List[str]:
    cmd = [
        "beeline",
        "-u",
        _jdbc_url(),
        "--silent=true",
        "--showHeader=true",
        "--outputformat=csv2",
    ]

    if SETTINGS.hive_username:
        cmd.extend(["-n", SETTINGS.hive_username])
    if SETTINGS.hive_password:
        cmd.extend(["-p", SETTINGS.hive_password])

    cmd.extend(["-e", sql])
    return cmd


def _extract_csv_lines(stdout: str) -> List[str]:
    lines: List[str] = []
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("INFO"):
            continue
        if line.startswith("SLF4J:"):
            continue
        if line.startswith("WARNING:"):
            continue
        if line.startswith("Connecting to:"):
            continue
        lines.append(line)
    return lines


def _parse_beeline_rows(stdout: str) -> List[Dict[str, str]]:
    csv_lines = _extract_csv_lines(stdout)
    if len(csv_lines) < 2:
        return []

    reader = csv.DictReader(io.StringIO("\n".join(csv_lines)))
    if not reader.fieldnames:
        return []

    rows: List[Dict[str, str]] = []
    for row in reader:
        normalized = {str(k): ("" if v is None else str(v)) for k, v in row.items()}
        rows.append(normalized)
    return rows


def _run_beeline(sql: str, timeout_sec: int = 300) -> Tuple[List[Dict[str, str]], str | None]:
    process_env = dict(os.environ)
    # Hive's launcher treats any non-empty DEBUG env var as debug mode and injects JDWP flags.
    process_env.pop("DEBUG", None)
    started = time.perf_counter()
    cmd = _beeline_cmd(sql)
    logger.info("beeline.start timeout_sec=%d sql=%r", timeout_sec, sql)

    try:
        result = subprocess.run(
            cmd,
            shell=False,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            env=process_env,
        )
    except subprocess.TimeoutExpired:
        logger.warning(
            "beeline.timeout duration_sec=%.2f sql=%r",
            time.perf_counter() - started,
            sql,
        )
        return [], "Hive query timed out"
    except FileNotFoundError:
        logger.exception("beeline.missing duration_sec=%.2f", time.perf_counter() - started)
        return [], "beeline command not found on PATH"
    except Exception as exc:
        logger.exception(
            "beeline.exception duration_sec=%.2f error=%s",
            time.perf_counter() - started,
            exc,
        )
        return [], str(exc)

    if result.returncode != 0:
        err = result.stderr.strip().replace("\n", " | ")
        logger.warning(
            "beeline.failed rc=%d duration_sec=%.2f error=%s sql=%r",
            result.returncode,
            time.perf_counter() - started,
            err,
            sql,
        )
        return [], f"beeline failed (rc={result.returncode}): {err}"

    rows = _parse_beeline_rows(result.stdout)
    logger.info(
        "beeline.success duration_sec=%.2f row_count=%d sql=%r",
        time.perf_counter() - started,
        len(rows),
        sql,
    )
    if not rows:
        return [], None
    return rows, None


def _dataset_tables() -> Dict[str, str | None]:
    overview = get_schema_overview()
    tables = {
        str(t.get("name", "")).lower(): str(t.get("name", ""))
        for t in overview
        if t.get("name")
    }
    return {
        "business": tables.get("business"),
        "review": tables.get("review"),
        "users": tables.get("users"),
    }


def _table_columns(overview: Sequence[Dict[str, Any]]) -> Dict[str, set[str]]:
    result: Dict[str, set[str]] = {}
    for table in overview:
        name = str(table.get("name", "")).lower()
        cols: set[str] = set()
        for raw_col in table.get("columns", []):
            first = str(raw_col).split()[0].strip().lower()
            if first:
                cols.add(first)
        if name:
            result[name] = cols
    return result


def _qualify_sql_tables(sql: str) -> str:
    if not SETTINGS.hive_database:
        return sql

    overview = get_schema_overview()
    table_names = [str(table.get("name", "")).strip() for table in overview if table.get("name")]
    qualified_sql = sql
    for table_name in table_names:
        pattern = re.compile(rf"\b(FROM|JOIN)\s+{re.escape(table_name)}\b", flags=re.IGNORECASE)
        qualified_sql = pattern.sub(
            lambda match: f"{match.group(1)} {SETTINGS.hive_database}.{table_name}",
            qualified_sql,
        )
    return qualified_sql


def _detect_viz_config(rows: List[Dict[str, str]]) -> Dict[str, str]:
    if not rows:
        return {"type": "none"}

    keys = list(rows[0].keys())
    if len(keys) < 2:
        return {"type": "none"}

    x_axis = keys[0]
    y_axis = keys[1]

    def is_numeric_column(column_name: str) -> bool:
        for row in rows[:50]:
            value = row.get(column_name, "")
            try:
                float(value)
            except (TypeError, ValueError):
                return False
        return True

    numeric_columns = [key for key in keys if is_numeric_column(key)]
    if not numeric_columns:
        return {"type": "none"}

    aggregate_name_markers = (
        "count",
        "avg",
        "sum",
        "total",
        "rating",
        "stars",
        "score",
        "review_count",
        "business_count",
        "value",
    )
    temporal_markers = ("date", "day", "week", "month", "year", "time")

    selected_y = None
    for key in numeric_columns:
        key_lower = key.lower()
        if any(marker in key_lower for marker in aggregate_name_markers):
            selected_y = key
            break
    if selected_y is None and len(keys) == 2:
        selected_y = y_axis
    if selected_y is None:
        return {"type": "none"}

    selected_x = None
    for key in keys:
        if key == selected_y:
            continue
        if not is_numeric_column(key):
            selected_x = key
            break
    if selected_x is None:
        return {"type": "none"}

    x_values = [str(row.get(selected_x, "")).strip() for row in rows[:50]]
    if not any(x_values):
        return {"type": "none"}

    title = selected_y.replace("_", " ").title()
    x_lower = selected_x.lower()
    y_lower = selected_y.lower()

    if any(marker in x_lower for marker in temporal_markers):
        return {"type": "line", "x_axis": selected_x, "y_axis": selected_y, "title": title}

    if len(rows) <= 6 and (
        "distribution" in y_lower
        or "share" in y_lower
        or "count" in y_lower
        or "total" in y_lower
        or "value" in y_lower
    ):
        return {"type": "pie", "x_axis": selected_x, "y_axis": selected_y, "title": title}

    if len(rows) <= 20 and (
        any(marker in y_lower for marker in aggregate_name_markers)
        or any(marker in x_lower for marker in ("state", "city", "category", "categories", "name"))
    ):
        return {"type": "bar", "x_axis": selected_x, "y_axis": selected_y, "title": title}

    return {"type": "none"}


def execute_query_plan(plan_key: str, sql: str) -> Tuple[List[Dict[str, str]], Dict[str, str]]:
    qualified_sql = _qualify_sql_tables(sql)
    rows, error = _run_beeline(qualified_sql)
    if error:
        raise RuntimeError(error)
    return rows, _detect_viz_config(rows)


def _single_value(rows: List[Dict[str, str]], key: str, default: Any = 0) -> Any:
    if not rows:
        return default
    return rows[0].get(key, default)


def _run_query_allow_empty(sql: str) -> List[Dict[str, str]]:
    rows, error = _run_beeline(sql)
    if error:
        print(error)
        return []
    return rows


def _pick_col(available: Iterable[str], candidates: Sequence[str]) -> str | None:
    available_set = {col.lower() for col in available}
    for candidate in candidates:
        if candidate.lower() in available_set:
            return candidate
    return None


_DASHBOARD_CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}
_ROOT_DIR = Path(__file__).resolve().parents[4]
_SNAPSHOT_DIR = _ROOT_DIR / ".cache"
_SUMMARY_SNAPSHOT_PATH = _SNAPSHOT_DIR / "dashboard_summary_snapshot.json"
_ANALYSIS_SNAPSHOT_PATH = _SNAPSHOT_DIR / "precomputed_analysis_snapshot.json"


def _cache_get(key: str, ttl_sec: int) -> Dict[str, Any] | None:
    cached = _DASHBOARD_CACHE.get(key)
    if not cached:
        return None
    cached_at, payload = cached
    if time.time() - cached_at > ttl_sec:
        _DASHBOARD_CACHE.pop(key, None)
        return None
    return payload


def _cache_set(key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    _DASHBOARD_CACHE[key] = (time.time(), payload)
    return payload


def _run_query_allow_empty_with_timeout(sql: str, timeout_sec: int) -> List[Dict[str, str]]:
    rows, error = _run_beeline(sql, timeout_sec=timeout_sec)
    if error:
        logger.warning("dashboard.query_failed timeout_sec=%d sql=%r error=%s", timeout_sec, sql, error)
        return []
    return rows


def _dashboard_timestamp() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def _csv_safe_text_expr(column_name: str | None, alias: str, replacement: str = " / ") -> str:
    if not column_name:
        return f"'' AS {alias}"
    escaped_replacement = replacement.replace("'", "\\'")
    return (
        "regexp_replace(regexp_replace(cast({column} as string), '\\\\r|\\\\n', ' '), ',', '{replacement}') AS {alias}"
    ).format(
        column=column_name,
        replacement=escaped_replacement,
        alias=alias,
    )


def _dashboard_mock_summary() -> Dict[str, Any]:
    snapshot_time = _dashboard_timestamp()
    return {
        "metrics": [
            {"label": "Business Rows", "value": 150346},
            {"label": "Review Rows", "value": 6990280},
            {"label": "Active Users", "value": 1987897},
            {"label": "Avg Stars", "value": 3.84},
        ],
        "top_categories": [
            {"categories": "restaurants", "count": 41892},
            {"categories": "food", "count": 29551},
            {"categories": "shopping", "count": 16422},
        ],
        "top_rated": [
            {"name": "Taco Town", "stars": 4.8, "review_count": 981, "categories": "Mexican, Fast Food"},
            {"name": "Philly Cheesesteak Co", "stars": 4.7, "review_count": 844, "categories": "Sandwiches, Restaurants"},
            {"name": "Chicago Deep Dish", "stars": 4.6, "review_count": 705, "categories": "Pizza, Restaurants"},
        ],
        "business_locations": [
            {"city": "Philadelphia", "lat": 39.9526, "lon": -75.1652, "count": 124},
            {"city": "Phoenix", "lat": 33.4484, "lon": -112.0740, "count": 98},
            {"city": "Las Vegas", "lat": 36.1699, "lon": -115.1398, "count": 87},
        ],
        "state_business_counts": [
            {"state": "PA", "count": 124},
            {"state": "AZ", "count": 98},
            {"state": "NV", "count": 87},
        ],
        "city_business_counts": [
            {"city": "Philadelphia", "count": 124},
            {"city": "Phoenix", "count": 98},
            {"city": "Las Vegas", "count": 87},
        ],
        "rating_distribution": [
            {"rating": "5", "count": 412},
            {"rating": "4", "count": 983},
            {"rating": "3", "count": 611},
            {"rating": "2", "count": 201},
            {"rating": "1", "count": 73},
        ],
        "review_volume": [],
        "sentiment": [],
        "table_health": [],
        "popular_keywords": [],
        "user_demographics": [],
        "rating_by_category": [],
        "data_freshness": snapshot_time,
        "snapshot_generated_at": snapshot_time,
        "status": {
            "level": "mock",
            "message": "Mock dashboard summary loaded.",
        },
    }


def _dashboard_mock_details() -> Dict[str, Any]:
    return {
        "review_volume": [],
        "sentiment": [],
        "rating_by_category": [],
        "user_demographics": [],
        "data_freshness": _dashboard_timestamp(),
        "status": {
            "level": "mock",
            "message": "Mock dashboard details loaded.",
        },
    }


def _dashboard_context() -> Dict[str, Any]:
    overview = get_schema_overview()
    columns_by_table = _table_columns(overview)
    tables = _dataset_tables()
    business = tables["business"]
    review = tables["review"]
    users = tables["users"]

    business_cols = columns_by_table.get((business or "").lower(), set())
    review_cols = columns_by_table.get((review or "").lower(), set())

    return {
        "overview": overview,
        "business": business,
        "review": review,
        "users": users,
        "business_name_col": _pick_col(business_cols, ["name", "business_name"]),
        "business_stars_col": _pick_col(business_cols, ["stars", "business_stars"]),
        "business_review_count_col": _pick_col(business_cols, ["review_count", "reviews_count"]),
        "business_categories_col": _pick_col(business_cols, ["categories"]),
        "business_city_col": _pick_col(business_cols, ["city"]),
        "business_state_col": _pick_col(business_cols, ["state"]),
        "business_lat_col": _pick_col(business_cols, ["latitude", "lat"]),
        "business_lon_col": _pick_col(business_cols, ["longitude", "lon", "lng"]),
        "review_ts_col": _pick_col(review_cols, ["review_date", "rev_date", "date", "rev_timestamp"]),
        "review_stars_col": _pick_col(review_cols, ["stars", "rev_stars"]),
    }


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value)))
    except (TypeError, ValueError):
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return default


def _summary_cache_key() -> str:
    return f"dashboard_summary:{SETTINGS.hive_database}:{SETTINGS.frontend_mode}"


def _details_cache_key() -> str:
    return f"dashboard_details:{SETTINGS.hive_database}:{SETTINGS.frontend_mode}"


def _snapshot_path() -> Path:
    return _SUMMARY_SNAPSHOT_PATH


def _analysis_snapshot_path() -> Path:
    return _ANALYSIS_SNAPSHOT_PATH


def _invalidate_dashboard_cache() -> None:
    _DASHBOARD_CACHE.pop(_summary_cache_key(), None)
    _DASHBOARD_CACHE.pop(_details_cache_key(), None)
    _DASHBOARD_CACHE.pop("precomputed_analysis", None)


def _read_snapshot_file() -> Dict[str, Any] | None:
    path = _snapshot_path()
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("dashboard.snapshot_read_failed path=%s error=%s", path, exc)
        return None


def _write_snapshot_file(payload: Dict[str, Any]) -> None:
    path = _snapshot_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _read_analysis_snapshot_file() -> Dict[str, Any] | None:
    path = _analysis_snapshot_path()
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("analysis.snapshot_read_failed path=%s error=%s", path, exc)
        return None


def _write_analysis_snapshot_file(payload: Dict[str, Any]) -> None:
    path = _analysis_snapshot_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _metric_card(label: str, value: Any) -> Dict[str, Any]:
    return {"label": label, "value": value}


def _sampled_table(table_name: str, limit_rows: int) -> str:
    return f"""
        (
            SELECT *
            FROM {SETTINGS.hive_database}.{table_name}
            LIMIT {limit_rows}
        ) sampled
    """.strip()


def _overview_stats_map(overview: Sequence[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    mapped: Dict[str, Dict[str, Any]] = {}
    for table in overview:
        name = str(table.get("name", "")).lower()
        stats = table.get("stats")
        if name and isinstance(stats, dict):
            mapped[name] = stats
    return mapped


def _metadata_row_count(overview: Sequence[Dict[str, Any]], table_name: str | None, default: int = 0) -> int:
    if not table_name:
        return default
    stats = _overview_stats_map(overview).get(table_name.lower(), {})
    value = stats.get("num_rows")
    return _safe_int(value, default=default)


def _reuse_or_warn(
    fresh_value: Any,
    previous_value: Any,
    warnings: List[str],
    warning_text: str,
) -> Any:
    if fresh_value:
        return fresh_value
    if previous_value:
        warnings.append(f"{warning_text} (reused previous snapshot)")
        return previous_value
    warnings.append(warning_text)
    return fresh_value


def _top_n_counts(items: Iterable[str], limit: int) -> List[Dict[str, Any]]:
    counts: Dict[str, int] = {}
    for item in items:
        cleaned = item.strip()
        if not cleaned:
            continue
        counts[cleaned] = counts.get(cleaned, 0) + 1
    return [
        {"name": key, "count": value}
        for key, value in sorted(counts.items(), key=lambda entry: (-entry[1], entry[0]))[:limit]
    ]


def _top_n_averages(
    pairs: Iterable[Tuple[str, float]],
    limit: int,
    value_key: str = "avg_stars",
    include_count_key: str = "business_count",
) -> List[Dict[str, Any]]:
    aggregates: Dict[str, Dict[str, float]] = {}
    for label, value in pairs:
        cleaned = str(label).strip()
        if not cleaned:
            continue
        bucket = aggregates.setdefault(cleaned, {"sum": 0.0, "count": 0.0})
        bucket["sum"] += value
        bucket["count"] += 1
    rows = []
    for label, bucket in aggregates.items():
        count = int(bucket["count"])
        avg = round(bucket["sum"] / max(bucket["count"], 1), 2)
        rows.append({"label": label, value_key: avg, include_count_key: count})
    rows.sort(key=lambda row: (-_safe_float(row.get(value_key), 0.0), -_safe_int(row.get(include_count_key), 0), str(row.get("label"))))
    return rows[:limit]


def _table_row_count(table_name: str, timeout_sec: int = 45) -> int:
    rows = _run_query_allow_empty_with_timeout(
        f"SELECT COUNT(*) AS value FROM {SETTINGS.hive_database}.{table_name}",
        timeout_sec=timeout_sec,
    )
    return _safe_int(_single_value(rows, "value", 0))


def _avg_metric(table_name: str, column_name: str, timeout_sec: int = 45) -> float:
    rows = _run_query_allow_empty_with_timeout(
        f"SELECT ROUND(AVG(CAST({column_name} AS DOUBLE)), 2) AS value FROM {SETTINGS.hive_database}.{table_name}",
        timeout_sec=timeout_sec,
    )
    return round(_safe_float(_single_value(rows, "value", 0.0)), 2)


def _build_summary_snapshot(previous_snapshot: Dict[str, Any] | None = None) -> Dict[str, Any]:
    context = _dashboard_context()
    overview = context["overview"]
    business = context["business"]
    review = context["review"]
    users = context["users"]
    business_name_col = context["business_name_col"]
    business_stars_col = context["business_stars_col"]
    business_review_count_col = context["business_review_count_col"]
    business_categories_col = context["business_categories_col"]
    business_city_col = context["business_city_col"]
    business_state_col = context["business_state_col"]
    business_lat_col = context["business_lat_col"]
    business_lon_col = context["business_lon_col"]

    snapshot_generated_at = _dashboard_timestamp()
    warnings: List[str] = []
    previous_snapshot = previous_snapshot or {}

    business_rows = _metadata_row_count(overview, business)
    if business and not business_rows:
        warnings.append("business count unavailable")

    review_rows = _metadata_row_count(overview, review)
    if review and not review_rows:
        warnings.append("review count unavailable")

    active_users = _metadata_row_count(overview, users)
    if users and not active_users:
        warnings.append("user count unavailable")

    avg_stars = 0.0
    sampled_business_rows: List[Dict[str, Any]] = []
    if business:
        sample_columns = [
            _csv_safe_text_expr(business_name_col, "name"),
            f"{business_stars_col} AS stars" if business_stars_col else "NULL AS stars",
            f"{business_review_count_col} AS review_count" if business_review_count_col else "0 AS review_count",
            _csv_safe_text_expr(business_categories_col, "categories", " | "),
            _csv_safe_text_expr(business_state_col, "state"),
            _csv_safe_text_expr(business_city_col, "city"),
            f"{business_lat_col} AS latitude" if business_lat_col else "NULL AS latitude",
            f"{business_lon_col} AS longitude" if business_lon_col else "NULL AS longitude",
        ]
        sampled_business_rows = _run_query_allow_empty_with_timeout(
            f"""
            SELECT {", ".join(sample_columns)}
            FROM {SETTINGS.hive_database}.{business}
            LIMIT 1500
            """.strip(),
            timeout_sec=12,
        )

    if sampled_business_rows:
        star_values = [to for to in (_safe_float(row.get("stars"), default=-1.0) for row in sampled_business_rows) if to >= 0]
        if star_values:
            avg_stars = round(sum(star_values) / len(star_values), 2)
    elif business:
        warnings.append("business sample unavailable")

    metrics = [
        _metric_card("Business Rows", business_rows),
        _metric_card("Review Rows", review_rows),
        _metric_card("Active Users", active_users),
        _metric_card("Avg Stars", avg_stars),
    ]

    top_categories: List[Dict[str, Any]] = []
    if sampled_business_rows:
        category_tokens: List[str] = []
        for row in sampled_business_rows:
            raw_categories = str(row.get("categories") or "")
            category_tokens.extend(
                part.strip().lower()
                for part in raw_categories.split("|")
                if part.strip()
            )
        top_categories = [
            {"categories": row["name"], "count": row["count"]}
            for row in _top_n_counts(category_tokens, 8)
        ]
    top_categories = _reuse_or_warn(
        top_categories,
        previous_snapshot.get("top_categories", []),
        warnings,
        "top categories unavailable",
    )

    top_rated: List[Dict[str, Any]] = []
    if sampled_business_rows:
        sorted_rows = sorted(
            sampled_business_rows,
            key=lambda row: (
                -_safe_float(row.get("stars"), 0.0),
                -_safe_int(row.get("review_count"), 0),
                str(row.get("name") or ""),
            ),
        )
        for row in sorted_rows[:5]:
            top_rated.append(
                {
                    "name": row.get("name") or "",
                    "stars": round(_safe_float(row.get("stars"), 0.0), 2),
                    "review_count": _safe_int(row.get("review_count"), 0),
                    "categories": row.get("categories") or "",
                }
            )
    top_rated = _reuse_or_warn(
        top_rated,
        previous_snapshot.get("top_rated", []),
        warnings,
        "top rated businesses unavailable",
    )

    state_business_counts: List[Dict[str, Any]] = []
    if sampled_business_rows:
        state_business_counts = [
            {"state": row["name"], "count": row["count"]}
            for row in _top_n_counts(
                [str(sample.get("state") or "").upper() for sample in sampled_business_rows],
                20,
            )
        ]
    state_business_counts = _reuse_or_warn(
        state_business_counts,
        previous_snapshot.get("state_business_counts", []),
        warnings,
        "state business counts unavailable",
    )

    city_business_counts: List[Dict[str, Any]] = []
    if sampled_business_rows:
        city_business_counts = [
            {"city": row["name"], "count": row["count"]}
            for row in _top_n_counts(
                [str(sample.get("city") or "") for sample in sampled_business_rows],
                8,
            )
        ]
    city_business_counts = _reuse_or_warn(
        city_business_counts,
        previous_snapshot.get("city_business_counts", []),
        warnings,
        "city business counts unavailable",
    )

    business_locations: List[Dict[str, Any]] = []
    if sampled_business_rows:
        city_geo: Dict[str, Dict[str, Any]] = {}
        for row in sampled_business_rows:
            city = str(row.get("city") or "").strip()
            lat = _safe_float(row.get("latitude"), default=0.0)
            lon = _safe_float(row.get("longitude"), default=0.0)
            if not city or not lat or not lon:
                continue
            bucket = city_geo.setdefault(city, {"lat_sum": 0.0, "lon_sum": 0.0, "count": 0})
            bucket["lat_sum"] += lat
            bucket["lon_sum"] += lon
            bucket["count"] += 1
        business_locations = [
            {
                "city": city,
                "lat": round(values["lat_sum"] / values["count"], 4),
                "lon": round(values["lon_sum"] / values["count"], 4),
                "count": values["count"],
            }
            for city, values in sorted(city_geo.items(), key=lambda item: (-item[1]["count"], item[0]))[:8]
        ]
    business_locations = _reuse_or_warn(
        business_locations,
        previous_snapshot.get("business_locations", []),
        warnings,
        "business map points unavailable",
    )

    rating_distribution: List[Dict[str, Any]] = []
    if sampled_business_rows:
        rating_distribution = [
            {"rating": row["name"], "count": row["count"]}
            for row in _top_n_counts(
                [
                    str(int(round(_safe_float(sample.get("stars"), 0.0))))
                    for sample in sampled_business_rows
                    if _safe_float(sample.get("stars"), -1.0) >= 0
                ],
                5,
            )
        ]
        rating_distribution = sorted(
            rating_distribution,
            key=lambda row: -_safe_int(row.get("rating"), 0),
        )
    rating_distribution = _reuse_or_warn(
        rating_distribution,
        previous_snapshot.get("rating_distribution", []),
        warnings,
        "rating distribution unavailable",
    )

    avg_rating_by_state: List[Dict[str, Any]] = []
    if sampled_business_rows:
        averages = _top_n_averages(
            [
                (str(sample.get("state") or "").upper(), _safe_float(sample.get("stars"), -1.0))
                for sample in sampled_business_rows
                if str(sample.get("state") or "").strip() and _safe_float(sample.get("stars"), -1.0) >= 0
            ],
            limit=12,
        )
        avg_rating_by_state = [
            {
                "state": row["label"],
                "avg_stars": row["avg_stars"],
                "business_count": row["business_count"],
            }
            for row in averages
        ]
    avg_rating_by_state = _reuse_or_warn(
        avg_rating_by_state,
        previous_snapshot.get("avg_rating_by_state", []),
        warnings,
        "average rating by state unavailable",
    )

    table_health = [
        {
            "table": table_name,
            "status": "ok",
            "rows": _safe_int(metric_value),
        }
        for table_name, metric_value in [
            (business or "", business_rows),
            (review or "", review_rows),
            (users or "", active_users),
        ]
        if table_name
    ]

    status_level = "summary" if not warnings else "degraded"
    status_message = (
        "Snapshot refreshed from real Hive data."
        if not warnings
        else "Snapshot refreshed with partial data: " + ", ".join(warnings[:3])
    )

    return {
        "metrics": metrics,
        "review_volume": [],
        "top_categories": top_categories,
        "sentiment": [],
        "table_health": table_health,
        "popular_keywords": [],
        "business_locations": business_locations,
        "state_business_counts": state_business_counts,
        "city_business_counts": city_business_counts,
        "rating_distribution": rating_distribution,
        "avg_rating_by_state": avg_rating_by_state,
        "user_demographics": [],
        "rating_by_category": [],
        "top_rated": top_rated,
        "data_freshness": snapshot_generated_at,
        "snapshot_generated_at": snapshot_generated_at,
        "status": {
            "level": status_level,
            "message": status_message,
        },
    }


def _precomputed_analysis_cache_key() -> str:
    return "precomputed_analysis"


def _analysis_item(
    key: str,
    title: str,
    sql: str,
    results: List[Dict[str, Any]],
    viz_config: Dict[str, str],
    summary: str,
) -> Dict[str, Any]:
    return {
        "key": key,
        "title": title,
        "sql": sql,
        "results": results,
        "viz_config": viz_config,
        "summary": summary,
    }


def _build_precomputed_analyses(summary_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    generated_at = summary_snapshot.get("snapshot_generated_at") or _dashboard_timestamp()
    analyses = {
        "top_states_by_business_count": _analysis_item(
            key="top_states_by_business_count",
            title="Top States by Business Count",
            sql=(
                "SELECT state, COUNT(*) AS business_count "
                "FROM business "
                "WHERE state IS NOT NULL AND TRIM(state) != '' "
                "GROUP BY state ORDER BY business_count DESC LIMIT 10"
            ),
            results=summary_snapshot.get("state_business_counts", [])[:10],
            viz_config={
                "type": "bar",
                "x_axis": "state",
                "y_axis": "count",
                "title": "Top States by Business Count",
            },
            summary="Top states by business count ready.",
        ),
        "top_cities_by_business_count": _analysis_item(
            key="top_cities_by_business_count",
            title="Top Cities by Business Count",
            sql=(
                "SELECT city, COUNT(*) AS business_count "
                "FROM business "
                "WHERE city IS NOT NULL AND TRIM(city) != '' "
                "GROUP BY city ORDER BY business_count DESC LIMIT 10"
            ),
            results=summary_snapshot.get("city_business_counts", [])[:10],
            viz_config={
                "type": "bar",
                "x_axis": "city",
                "y_axis": "count",
                "title": "Top Cities by Business Count",
            },
            summary="Top cities by business count ready.",
        ),
        "average_rating_by_state": _analysis_item(
            key="average_rating_by_state",
            title="Average Business Rating by State",
            sql=(
                "SELECT state, ROUND(AVG(stars), 2) AS avg_stars, COUNT(*) AS business_count "
                "FROM business "
                "WHERE state IS NOT NULL AND TRIM(state) != '' "
                "GROUP BY state ORDER BY avg_stars DESC, business_count DESC LIMIT 10"
            ),
            results=summary_snapshot.get("avg_rating_by_state", [])[:10],
            viz_config={
                "type": "bar",
                "x_axis": "state",
                "y_axis": "avg_stars",
                "title": "Average Business Rating by State",
            },
            summary="Average business rating by state ready.",
        ),
        "top_business_categories": _analysis_item(
            key="top_business_categories",
            title="Top Business Categories",
            sql=(
                "SELECT category, COUNT(*) AS business_count "
                "FROM exploded_business_categories "
                "GROUP BY category ORDER BY business_count DESC LIMIT 8"
            ),
            results=summary_snapshot.get("top_categories", [])[:8],
            viz_config={
                "type": "pie",
                "x_axis": "categories",
                "y_axis": "count",
                "title": "Top Business Categories",
            },
            summary="Top business categories ready.",
        ),
        "highest_rated_businesses": _analysis_item(
            key="highest_rated_businesses",
            title="Highest Rated Businesses",
            sql=(
                "SELECT name, stars, review_count "
                "FROM business ORDER BY stars DESC, review_count DESC LIMIT 5"
            ),
            results=summary_snapshot.get("top_rated", [])[:5],
            viz_config={
                "type": "bar",
                "x_axis": "name",
                "y_axis": "stars",
                "title": "Highest Rated Businesses",
            },
            summary="Highest rated businesses ready.",
        ),
        "rating_distribution": _analysis_item(
            key="rating_distribution",
            title="Business Rating Distribution",
            sql=(
                "SELECT CAST(ROUND(stars) AS INT) AS rating, COUNT(*) AS business_count "
                "FROM business GROUP BY CAST(ROUND(stars) AS INT) ORDER BY rating DESC"
            ),
            results=summary_snapshot.get("rating_distribution", [])[:5],
            viz_config={
                "type": "pie",
                "x_axis": "rating",
                "y_axis": "count",
                "title": "Business Rating Distribution",
            },
            summary="Business rating distribution ready.",
        ),
    }
    return {
        "generated_at": generated_at,
        "analyses": analyses,
        "status": {
            "level": summary_snapshot.get("status", {}).get("level", "summary"),
            "message": "Precomputed analyses refreshed from the latest summary snapshot.",
        },
    }


def refresh_precomputed_analyses(summary_snapshot: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = _build_precomputed_analyses(summary_snapshot or get_dashboard_snapshot())
    _write_analysis_snapshot_file(payload)
    _DASHBOARD_CACHE[_precomputed_analysis_cache_key()] = (time.time(), payload)
    return payload


def get_precomputed_analyses() -> Dict[str, Any]:
    cached = _cache_get(_precomputed_analysis_cache_key(), ttl_sec=300)
    if cached is not None:
        return cached

    snapshot = _read_analysis_snapshot_file()
    if snapshot is not None:
        return _cache_set(_precomputed_analysis_cache_key(), snapshot)

    return refresh_precomputed_analyses()


def find_precomputed_analysis(prompt: str) -> Dict[str, Any] | None:
    prompt_lower = " ".join(str(prompt or "").strip().lower().split())
    if not prompt_lower:
        return None

    patterns = [
        ("top_states_by_business_count", ["top 10 states", "states by number of businesses", "states have the most businesses", "most businesses by state"]),
        ("top_cities_by_business_count", ["top 10 cities", "cities by number of businesses", "cities have the most businesses", "most businesses by city", "which cities have the most businesses"]),
        ("average_rating_by_state", ["average business rating by state", "average rating by state", "average stars by state"]),
        ("top_business_categories", ["top business categories", "top categories", "categories by number of businesses", "businesses by category"]),
        ("highest_rated_businesses", ["highest rated businesses", "top rated businesses", "best businesses"]),
        ("rating_distribution", ["rating distribution", "distribution of ratings", "business rating distribution"]),
    ]

    matched_key = None
    for key, variants in patterns:
        if any(variant in prompt_lower for variant in variants):
            matched_key = key
            break
    if not matched_key:
        return None

    payload = get_precomputed_analyses()
    return payload.get("analyses", {}).get(matched_key)


def refresh_dashboard_snapshot() -> Dict[str, Any]:
    cache_key = _summary_cache_key()
    if SETTINGS.frontend_mode == "mock":
        payload = _dashboard_mock_summary()
        _write_snapshot_file(payload)
        _invalidate_dashboard_cache()
        return _cache_set(cache_key, payload)

    previous_snapshot = _read_snapshot_file()
    payload = _build_summary_snapshot(previous_snapshot)
    _write_snapshot_file(payload)
    refresh_precomputed_analyses(payload)
    _invalidate_dashboard_cache()
    return _cache_set(cache_key, payload)


def get_dashboard_snapshot() -> Dict[str, Any]:
    cache_key = _summary_cache_key()
    cached = _cache_get(cache_key, ttl_sec=300)
    if cached is not None:
        return cached

    if SETTINGS.frontend_mode == "mock":
        return _cache_set(cache_key, _dashboard_mock_summary())

    snapshot = _read_snapshot_file()
    if snapshot is not None:
        return _cache_set(cache_key, snapshot)

    return refresh_dashboard_snapshot()


def get_dashboard_details() -> Dict[str, Any]:
    cache_key = _details_cache_key()
    cached = _cache_get(cache_key, ttl_sec=180)
    if cached is not None:
        return cached

    if SETTINGS.frontend_mode == "mock":
        return _cache_set(cache_key, _dashboard_mock_details())

    context = _dashboard_context()
    review = context["review"]
    business = context["business"]
    review_ts_col = context["review_ts_col"]
    review_stars_col = context["review_stars_col"]
    business_categories_col = context["business_categories_col"]
    business_stars_col = context["business_stars_col"]

    review_volume: List[Dict[str, Any]] = []
    if review and review_ts_col:
        review_volume = _run_query_allow_empty_with_timeout(
            f"""
            SELECT substr(cast({review_ts_col} AS string), 1, 7) AS month, COUNT(*) AS count
            FROM {SETTINGS.hive_database}.{review}
            GROUP BY substr(cast({review_ts_col} AS string), 1, 7)
            ORDER BY month ASC
            LIMIT 12
            """.strip(),
            timeout_sec=45,
        )

    sentiment: List[Dict[str, Any]] = []
    if review and review_stars_col:
        sentiment = _run_query_allow_empty_with_timeout(
            f"""
            SELECT sentiment, COUNT(*) AS value
            FROM (
                SELECT CASE
                    WHEN {review_stars_col} >= 4 THEN 'Positive'
                    WHEN {review_stars_col} = 3 THEN 'Neutral'
                    ELSE 'Negative'
                END AS sentiment
                FROM {SETTINGS.hive_database}.{review}
            ) bucketed
            GROUP BY sentiment
            ORDER BY value DESC
            """.strip(),
            timeout_sec=45,
        )
        for row in sentiment:
            lower_name = str(row.get("sentiment", "")).lower()
            if lower_name == "positive":
                row["color"] = "#4ADE80"
            elif lower_name == "neutral":
                row["color"] = "#FBBF24"
            else:
                row["color"] = "#F87171"
            row["name"] = row.pop("sentiment", "")

    rating_by_category: List[Dict[str, Any]] = []
    if business and business_categories_col and business_stars_col:
        rating_by_category = _run_query_allow_empty_with_timeout(
            f"""
            SELECT lower(trim({business_categories_col})) AS categories,
                   ROUND(AVG(CAST({business_stars_col} AS DOUBLE)), 2) AS avg
            FROM {SETTINGS.hive_database}.{business}
            WHERE {business_categories_col} IS NOT NULL AND trim({business_categories_col}) <> ''
            GROUP BY lower(trim({business_categories_col}))
            ORDER BY avg DESC
            LIMIT 6
            """.strip(),
            timeout_sec=45,
        )

    payload = {
        "review_volume": review_volume,
        "sentiment": sentiment,
        "rating_by_category": rating_by_category,
        "user_demographics": [],
        "data_freshness": _dashboard_timestamp(),
        "status": {
            "level": "details",
            "message": "Progressive dashboard details loaded.",
        },
    }
    return _cache_set(cache_key, payload)
def check_hive_connection() -> tuple[bool, str]:
    if SETTINGS.frontend_mode == "mock":
        return True, "mock mode"

    sql = "SELECT 1 AS value"
    rows, error = _run_beeline(sql, timeout_sec=20)
    if error:
        return False, error
    if not rows:
        return False, "no rows returned"
    return True, "ok"
