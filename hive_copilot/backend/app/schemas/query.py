from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class VizConfig(BaseModel):
    type: Literal["bar", "line", "pie", "none"] = "none"
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    title: Optional[str] = None


class QueryRequest(BaseModel):
    prompt: str = Field(..., min_length=3, max_length=500)


class QueryResponse(BaseModel):
    message: str
    sql: str
    results: List[Dict[str, Any]]
    viz_config: VizConfig = Field(default_factory=VizConfig)
    error: Optional[str] = None


class SchemaTable(BaseModel):
    name: str
    description: str
    columns: List[str]


class QuickQuery(BaseModel):
    label: str
    prompt: str


class SchemaResponse(BaseModel):
    tables: List[SchemaTable]
    quick_queries: List[QuickQuery]


class MetricCard(BaseModel):
    label: str
    value: Any
    delta: Optional[str] = None


class DashboardStatus(BaseModel):
    level: Literal["summary", "details", "degraded", "mock"] = "summary"
    message: str


class DashboardResponse(BaseModel):
    metrics: List[MetricCard]
    review_volume: List[Dict[str, Any]]
    top_categories: List[Dict[str, Any]]
    sentiment: List[Dict[str, Any]]
    table_health: List[Dict[str, Any]]
    top_rated: List[Dict[str, Any]] = []
    popular_keywords: List[Dict] = []
    business_locations: List[Dict] = []
    state_business_counts: List[Dict[str, Any]] = []
    city_business_counts: List[Dict[str, Any]] = []
    rating_distribution: List[Dict[str, Any]] = []
    user_demographics: List[Dict] = []
    rating_by_category: List[Dict[str, Any]] = []
    data_freshness: Optional[str] = None
    snapshot_generated_at: Optional[str] = None
    status: Optional[DashboardStatus] = None


class DashboardDetailsResponse(BaseModel):
    review_volume: List[Dict[str, Any]]
    sentiment: List[Dict[str, Any]]
    rating_by_category: List[Dict[str, Any]] = []
    user_demographics: List[Dict] = []
    data_freshness: Optional[str] = None
    status: Optional[DashboardStatus] = None
