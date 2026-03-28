from __future__ import annotations

from pathlib import Path
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))


import requests
import streamlit as st

from hive_copilot.backend.app.services.hive_execution_service import (
    get_dashboard_snapshot,
    refresh_dashboard_snapshot,
)
from hive_copilot.backend.app.services.hms_service import (
    QUICK_QUERIES,
    SCHEMA_TABLES,
)
from hive_copilot.streamlit_components.yelp_tsx_component.yelp_tsx_component import (
    yelp_tsx_component,
)


st.set_page_config(
    page_title="Hive Copilot",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

Payload = Dict[str, Any]

VIEW_CHAT = "chat"
VIEW_EXPLORER = "explorer"
VIEW_DASHBOARD = "dashboard"
VALID_VIEWS = {VIEW_CHAT, VIEW_EXPLORER, VIEW_DASHBOARD}

_FALLBACK_TOP_RATED = [
    {"name": "Taco Town", "stars": 4.8, "categories": "Mexican, Fast Food"},
    {"name": "Philly Cheesesteak Co", "stars": 4.7, "categories": "Sandwiches, Restaurants"},
    {"name": "Chicago Deep Dish", "stars": 4.6, "categories": "Pizza, Restaurants"},
    {"name": "Vibrant Mexican Grill", "stars": 4.5, "categories": "Mexican, Restaurants"},
]

_FALLBACK_RATING_BY_CATEGORY = [
    {"categories": "Mexican", "avg": 4.8},
    {"categories": "Sandwiches", "avg": 4.7},
    {"categories": "Pizza", "avg": 4.6},
    {"categories": "Japanese", "avg": 4.2},
    {"categories": "Nightlife", "avg": 3.5},
]

_FALLBACK_DEMOGRAPHICS = [
    {"age": "18-24", "count": 40},
    {"age": "25-34", "count": 60},
    {"age": "35-44", "count": 35},
    {"age": "45-54", "count": 25},
    {"age": "55+", "count": 15},
]

_SENTIMENT_COLORS = {
    "positive": "#4ADE80",
    "neutral": "#FBBF24",
    "negative": "#F87171",
}

_HOST_STYLES = """
<style>
  html,
  body,
  [data-testid="stAppViewContainer"],
  [data-testid="stAppViewContainer"] > .main,
  .stApp {
    background: #f9f8f6;
    height: 100vh;
    overflow: hidden;
  }

  [data-testid="stAppViewContainer"] {
    background: #f9f8f6;
  }

  [data-testid="stAppViewContainer"] > .main {
    background: #f9f8f6;
  }

  [data-testid="stHeader"],
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  #MainMenu,
  footer {
    display: none;
  }

  [data-testid="stSidebar"] {
    display: none;
  }

  [data-testid="stMainBlockContainer"],
  [data-testid="stAppViewContainer"] .block-container {
    max-width: none;
    padding: 0 !important;
    margin: 0 !important;
  }

  [data-testid="stVerticalBlock"],
  [data-testid="stVerticalBlockBorderWrapper"],
  [data-testid="element-container"],
  [data-testid="stMarkdownContainer"],
  [data-testid="stCustomComponentV1"] {
    margin: 0 !important;
    padding: 0 !important;
    gap: 0 !important;
  }

  [data-testid="stCustomComponentV1"] {
    line-height: 0;
    height: 100vh !important;
  }

  [data-testid="stCustomComponentV1"] iframe,
  iframe {
    border: 0;
    display: block;
    width: 100% !important;
    height: 100vh !important;
  }
</style>
"""


def _inject_host_styles() -> None:
    st.markdown(_HOST_STYLES, unsafe_allow_html=True)


def _get_backend_url() -> str:
    return os.getenv("STREAMLIT_BACKEND_URL", "").rstrip("/")


def _fetch_from_backend(
    path: str,
    method: str = "GET",
    payload: Optional[Payload] = None,
    timeout: int = 8,
) -> Optional[Payload]:
    backend_url = _get_backend_url()
    print(f"DEBUG: backend_url = {backend_url}")
    if not backend_url:
        print("DEBUG: No backend URL, using mock")
        return None

    try:
        if method == "POST":
            response = requests.post(
                f"{backend_url}{path}",
                json=payload,
                timeout=timeout,
            )
        else:
            response = requests.get(
                f"{backend_url}{path}",
                timeout=timeout,
            )
        print(f"DEBUG: Response status = {response.status_code}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"DEBUG: Request failed: {e}")
        return None

def _load_schema_payload() -> Tuple[Payload, str]:
    api_payload = _fetch_from_backend("/api/schema")
    if api_payload is not None:
        return api_payload, "api"

    return {
        "tables": SCHEMA_TABLES,
        "quick_queries": QUICK_QUERIES,
    }, "mock"


def _load_dashboard_payload(force_refresh: bool = False) -> Tuple[Payload, str]:
    path = "/api/dashboard/refresh" if force_refresh else "/api/dashboard"
    method = "POST" if force_refresh else "GET"
    api_payload = _fetch_from_backend(path, method=method, timeout=45 if force_refresh else 12)
    if api_payload is not None:
        return api_payload, "api"

    if force_refresh:
        return refresh_dashboard_snapshot(), "mock"
    return get_dashboard_snapshot(), "mock"


def _load_dashboard_details_payload() -> Tuple[Payload, str]:
    api_payload = _fetch_from_backend("/api/dashboard/details", timeout=10)
    if api_payload is not None:
        return api_payload, "api"

    return {
        "review_volume": [],
        "sentiment": [],
        "rating_by_category": [],
        "user_demographics": [],
        "status": {
            "level": "degraded",
            "message": "Detailed dashboard cards timed out and were skipped.",
        },
    }, "mock"


def _submit_query(prompt: str) -> Tuple[Payload, str]:
    backend_url = _get_backend_url()
    if backend_url:
        try:
            response = requests.post(
                f"{backend_url}/api/query",
                json={"prompt": prompt},
                timeout=None,
            )
            response.raise_for_status()
            return response.json(), "api"
        except (requests.ConnectionError, requests.Timeout) as exc:
            return {
                "message": "The backend did not respond.",
                "sql": "",
                "results": [],
                "viz_config": {"type": "none"},
                "error": str(exc),
            }, "api"
        except requests.HTTPError as exc:
            error_message = str(exc)
            try:
                error_payload = exc.response.json()
                error_message = error_payload.get("detail", error_message)
            except ValueError:
                pass
            return {
                "message": "The backend rejected the request.",
                "sql": "",
                "results": [],
                "viz_config": {"type": "none"},
                "error": error_message,
            }, "api"

    return {
        "message": "No backend URL is configured.",
        "sql": "",
        "results": [],
        "viz_config": {"type": "none"},
        "error": "Set STREAMLIT_BACKEND_URL to enable live API queries.",
    }, "api"


def _initialize_session_state() -> None:
    defaults = {
        "active_view": VIEW_CHAT,
        "messages": [],
        "last_response": None,
        "dashboard_data": None,
        "dashboard_details": None,
        "schema_payload": None,
        "schema_source": "mock",
        "dashboard_source": "mock",
        "dashboard_details_source": "mock",
        "query_source": "mock",
        "last_component_event_id": None,
        "dashboard_details_requested": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _normalize_view(value: str) -> str:
    if value in VALID_VIEWS:
        return value
    return VIEW_CHAT


def _sync_view_query_param() -> None:
    requested_view = st.query_params.get("view", st.session_state.active_view)
    if isinstance(requested_view, list):
        requested_view = requested_view[0] if requested_view else VIEW_CHAT

    normalized_view = _normalize_view(str(requested_view))
    if st.session_state.active_view != normalized_view:
        st.session_state.active_view = normalized_view

    if st.query_params.get("view") != normalized_view:
        st.query_params["view"] = normalized_view


def _set_active_view(view: str) -> None:
    normalized_view = _normalize_view(view)
    st.session_state.active_view = normalized_view
    st.query_params["view"] = normalized_view


def _reset_session() -> None:
    st.session_state.messages = []
    st.session_state.last_response = None
    st.session_state.query_source = "mock"
    st.session_state.dashboard_data = None
    st.session_state.dashboard_details = None
    st.session_state.dashboard_details_requested = False
    _set_active_view(VIEW_CHAT)


def _ensure_schema_loaded() -> None:
    if st.session_state.schema_payload is None:
        schema_payload, schema_source = _load_schema_payload()
        st.session_state.schema_payload = schema_payload
        st.session_state.schema_source = schema_source


def _refresh_dashboard(force_refresh: bool = False) -> None:
    dashboard_payload, source = _load_dashboard_payload(force_refresh=force_refresh)
    st.session_state.dashboard_data = dashboard_payload
    st.session_state.dashboard_source = source
    st.session_state.dashboard_details = None
    st.session_state.dashboard_details_source = "mock"
    st.session_state.dashboard_details_requested = False


def _refresh_dashboard_details() -> None:
    dashboard_payload, source = _load_dashboard_details_payload()
    st.session_state.dashboard_details = dashboard_payload
    st.session_state.dashboard_details_source = source
    st.session_state.dashboard_details_requested = True


def _ensure_dashboard_loaded() -> None:
    if st.session_state.dashboard_data is None:
        _refresh_dashboard()


def _handle_prompt(prompt: str) -> None:
    clean_prompt = prompt.strip()
    if not clean_prompt:
        return

    st.session_state.messages.append(
        {
            "role": "user",
            "content": clean_prompt,
        }
    )

    response, source = _submit_query(clean_prompt)

    assistant_message = {
        "role": "assistant",
        "content": response.get("message", "No response received."),
        "sql": response.get("sql"),
        "results": response.get("results", []),
        "viz_config": response.get("viz_config", {}),
        "error": response.get("error"),
    }

    st.session_state.messages.append(assistant_message)
    st.session_state.last_response = assistant_message
    st.session_state.query_source = source
    _set_active_view(VIEW_CHAT)


def _normalize_messages(messages: List[Payload]) -> List[Payload]:
    normalized: List[Payload] = []
    for index, message in enumerate(messages):
        viz_config = message.get("viz_config") or {}
        normalized.append(
            {
                "id": str(message.get("id") or f"message-{index}"),
                "role": str(message.get("role", "assistant")),
                "content": str(message.get("content", "")),
                "sql": str(message.get("sql", "")) if message.get("sql") else "",
                "results": message.get("results", []),
                "vizConfig": {
                    "type": str(viz_config.get("type", "none")),
                    "xAxis": str(viz_config.get("x_axis") or viz_config.get("xAxis") or ""),
                    "yAxis": str(viz_config.get("y_axis") or viz_config.get("yAxis") or ""),
                    "title": str(viz_config.get("title", "")),
                },
                "error": message.get("error"),
            }
        )
    return normalized


def _normalize_schema_tables(schema_payload: Payload) -> List[Payload]:
    return [
        {
            "name": str(table.get("name", "")),
            "columns": [str(column) for column in table.get("columns", [])],
        }
        for table in schema_payload.get("tables", [])
    ]


def _normalize_quick_queries(schema_payload: Payload) -> List[Payload]:
    return [
        {
            "label": str(query.get("label", "")),
            "prompt": str(query.get("prompt", "")),
        }
        for query in schema_payload.get("quick_queries", [])
    ]


def _metric_lookup(dashboard_data: Payload) -> Dict[str, Any]:
    metrics = dashboard_data.get("metrics", [])
    return {
        str(metric.get("label", "")): metric.get("value")
        for metric in metrics
        if metric.get("label")
    }


def _normalize_sentiment(rows: List[Payload]) -> List[Payload]:
    normalized: List[Payload] = []
    for row in rows:
        name = str(row.get("name", ""))
        normalized.append(
            {
                "name": name,
                "value": row.get("value", 0),
                "color": str(row.get("color") or _SENTIMENT_COLORS.get(name.lower(), "#d97706")),
            }
        )
    return normalized


def _build_dashboard_stats(dashboard_data: Payload) -> Payload:
    dashboard_summary = dashboard_data or {}
    dashboard_details = st.session_state.dashboard_details or {}

    metrics = _metric_lookup(dashboard_summary)
    top_categories = [
        {
            "categories": row.get("categories") or row.get("category") or "",
            "count": row.get("count", 0),
        }
        for row in dashboard_summary.get("top_categories", [])
    ]
    review_trends = [
        {
            "month": row.get("month") or row.get("review_month") or "",
            "count": row.get("count") or row.get("review_count") or 0,
        }
        for row in dashboard_details.get("review_volume", [])
    ]

    return {
        "totalBusinesses": metrics.get("Business Rows", "192K"),
        "totalReviews": metrics.get("Review Rows", "6.9M"),
        "activeUsers": metrics.get("Active Users", "38K"),
        "avgRating": metrics.get("Avg Stars", "3.8"),
        "topCategories": top_categories,
        "topRated": dashboard_summary.get("top_rated", _FALLBACK_TOP_RATED),
        "ratingByCategory": dashboard_details.get(
            "rating_by_category",
            _FALLBACK_RATING_BY_CATEGORY,
        ),
        "reviewTrends": review_trends,
        "sentiment": _normalize_sentiment(dashboard_details.get("sentiment", [])),
        "demographics": dashboard_details.get("user_demographics", _FALLBACK_DEMOGRAPHICS),
        "popularKeywords": dashboard_summary.get("popular_keywords", []),
        "businessLocations": dashboard_summary.get("business_locations", []),
        "stateBusinessCounts": dashboard_summary.get("state_business_counts", []),
        "topStates": dashboard_summary.get("state_business_counts", []),
        "topCities": dashboard_summary.get("city_business_counts", []),
        "ratingDistribution": dashboard_summary.get("rating_distribution", []),
        "tableHealth": dashboard_summary.get("table_health", []),
        "dataFreshness": dashboard_details.get("data_freshness")
        or dashboard_summary.get("data_freshness")
        or "",
        "snapshotGeneratedAt": dashboard_summary.get("snapshot_generated_at") or "",
        "status": dashboard_details.get("status") or dashboard_summary.get("status") or {},
        "detailsLoaded": bool(st.session_state.dashboard_details),
        "detailsRequested": bool(st.session_state.dashboard_details_requested),
    }


def _build_component_props() -> Payload:
    active_view = str(st.session_state.active_view)
    return {
        "theme": "light",
        "activeView": active_view,
        "messages": _normalize_messages(st.session_state.messages),
        "schemaTables": _normalize_schema_tables(st.session_state.schema_payload or {}),
        "quickQueries": _normalize_quick_queries(st.session_state.schema_payload or {}),
        "dashboardStats": _build_dashboard_stats(st.session_state.dashboard_data or {}),
        "isLoading": False,
        "dashboardDetailsLoading": bool(
            st.session_state.active_view == VIEW_DASHBOARD
            and st.session_state.dashboard_data is not None
            and not st.session_state.dashboard_details
        ),
        "frameHeight": 0,
    }


def _dispatch_component_event(event: Any) -> bool:
    if not isinstance(event, dict):
        return False

    event_id = str(event.get("eventId") or "")
    if not event_id or st.session_state.last_component_event_id == event_id:
        return False

    st.session_state.last_component_event_id = event_id
    event_type = str(event.get("type") or "noop")

    if event_type == "noop":
        return False
    if event_type == "set_view":
        _set_active_view(str(event.get("view") or VIEW_CHAT))
        return True
    if event_type == "submit_prompt":
        prompt = str(event.get("prompt") or "").strip()
        if not prompt:
            return False
        _handle_prompt(prompt)
        return True
    if event_type == "refresh_dashboard":
        _refresh_dashboard(force_refresh=True)
        return True
    if event_type == "load_dashboard_details":
        if not st.session_state.dashboard_details_requested:
            _refresh_dashboard_details()
        return True
    if event_type == "reset_session":
        _reset_session()
        return True

    return False


def main() -> None:
    _initialize_session_state()
    _sync_view_query_param()
    _inject_host_styles()

    _ensure_schema_loaded()
    if st.session_state.active_view == VIEW_DASHBOARD:
        _ensure_dashboard_loaded()

    event = yelp_tsx_component(
        key="hive_copilot_component",
        default={"type": "noop", "eventId": "initial"},
        **_build_component_props(),
    )

    if _dispatch_component_event(event):
        st.rerun()


main()
