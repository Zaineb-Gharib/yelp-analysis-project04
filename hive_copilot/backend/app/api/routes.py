import logging
import time

from fastapi import APIRouter, HTTPException

from hive_copilot.backend.app.schemas.query import (
    DashboardDetailsResponse,
    DashboardResponse,
    QueryRequest,
    QueryResponse,
    SchemaResponse,
    SchemaTable,
    QuickQuery,
    VizConfig,
)
from hive_copilot.backend.app.services.hive_execution_service import (
    execute_query_plan,
    find_precomputed_analysis,
    get_dashboard_details,
    get_dashboard_snapshot,
    refresh_dashboard_snapshot,
    sanitize_sql,
)
from hive_copilot.backend.app.services.hms_service import (
    build_schema_context,
    get_quick_queries,
    get_schema_overview,
)
from hive_copilot.backend.app.services.llm_service import (
    detect_fast_path_query,
    generate_corrected_query_plan,
    generate_query_plan,
)


router = APIRouter(tags=["hive-copilot"])
logger = logging.getLogger(__name__)


def _user_facing_message(summary: str, row_count: int) -> str:
    clean_summary = (summary or "").strip()
    lowered = clean_summary.lower()
    if "precomputed" in lowered or "snapshot" in lowered:
        clean_summary = ""
    if clean_summary:
        return f"{clean_summary} Found {row_count} rows."
    return f"Found {row_count} rows."


@router.get("/schema", response_model=SchemaResponse)
def read_schema() -> SchemaResponse:
    try:
        tables = [SchemaTable(**table) for table in get_schema_overview()]
        quick_queries = [QuickQuery(**query) for query in get_quick_queries()]
        return SchemaResponse(tables=tables, quick_queries=quick_queries)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Failed to load schema from HMS: {exc}")


@router.post("/query", response_model=QueryResponse)
def run_query(payload: QueryRequest) -> QueryResponse:
    request_started = time.perf_counter()
    try:
        logger.info("query.start prompt=%r", payload.prompt)
        precomputed = find_precomputed_analysis(payload.prompt)
        if precomputed:
            total_duration = time.perf_counter() - request_started
            logger.info(
                "query.precomputed_hit total_sec=%.2f key=%s",
                total_duration,
                precomputed.get("key"),
            )
            return QueryResponse(
                message=_user_facing_message(
                    str(precomputed.get("summary", "")),
                    len(precomputed.get("results", [])),
                ),
                sql=str(precomputed.get("sql", "")),
                results=precomputed.get("results", []),
                viz_config=VizConfig(**(precomputed.get("viz_config", {"type": "none"}))),
            )

        schema_context = build_schema_context()

        llm_started = time.perf_counter()
        plan = detect_fast_path_query(payload.prompt) or generate_query_plan(payload.prompt, schema_context)
        llm_duration = time.perf_counter() - llm_started
        logger.info(
            "query.plan_ready duration_sec=%.2f summary=%r sql=%r",
            llm_duration,
            plan.summary,
            plan.sql,
        )

        sql = sanitize_sql(plan.sql)
        final_sql = sql

        hive_started = time.perf_counter()
        try:
            results, viz_config = execute_query_plan(plan.key, sql)
        except Exception as first_exec_error:
            logger.warning(
                "query.execution_failed sql=%r error=%s",
                sql,
                first_exec_error,
            )
            repair_started = time.perf_counter()
            repaired_plan = generate_corrected_query_plan(
                payload.prompt,
                schema_context,
                sql,
                str(first_exec_error),
            )
            repaired_sql = sanitize_sql(repaired_plan.sql)
            logger.info(
                "query.repair_ready duration_sec=%.2f repaired_sql=%r",
                time.perf_counter() - repair_started,
                repaired_sql,
            )
            results, viz_config = execute_query_plan(repaired_plan.key, repaired_sql)
            plan = repaired_plan
            final_sql = repaired_sql

        hive_duration = time.perf_counter() - hive_started
        total_duration = time.perf_counter() - request_started
        logger.info(
            "query.complete hive_sec=%.2f total_sec=%.2f row_count=%d viz=%r",
            hive_duration,
            total_duration,
            len(results),
            viz_config,
        )
        return QueryResponse(
            message=_user_facing_message(plan.summary, len(results)),
            sql=final_sql,
            results=results,
            viz_config=VizConfig(**viz_config),
        )
    except ValueError as exc:
        logger.warning("query.validation_error error=%s", exc)
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("query.failed error=%s", exc)
        raise HTTPException(status_code=503, detail=f"Failed to execute Hive query: {exc}")


@router.get("/dashboard", response_model=DashboardResponse)
def read_dashboard() -> DashboardResponse:
    try:
        return DashboardResponse(**get_dashboard_snapshot())
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Failed to load dashboard from Hive: {exc}")


@router.post("/dashboard/refresh", response_model=DashboardResponse)
def refresh_dashboard() -> DashboardResponse:
    try:
        return DashboardResponse(**refresh_dashboard_snapshot())
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Failed to refresh dashboard from Hive: {exc}")


@router.get("/dashboard/details", response_model=DashboardDetailsResponse)
def read_dashboard_details() -> DashboardDetailsResponse:
    try:
        return DashboardDetailsResponse(**get_dashboard_details())
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Failed to load dashboard details from Hive: {exc}")
