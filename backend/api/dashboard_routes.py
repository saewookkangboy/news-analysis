"""
Dashboard API 라우트 (스텁)
대시보드 UI 연동을 위한 목 데이터 API. 추후 실제 이벤트/분석 연동 시 교체.
"""
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query

logger = logging.getLogger(__name__)

router = APIRouter()


def _mock_overview(category: str) -> Dict[str, Any]:
    base = {
        "total_events": 12450,
        "total_users": 8920,
        "conversion_rate": 4.2,
        "total_sessions": 15600,
        "total_conversions": 655,
        "average_conversion_rate": 4.2,
    }
    if category == "ecommerce":
        base["total_revenue"] = 42_500_000
        base["average_order_value"] = 64_885
    elif category == "lead_generation":
        base["total_leads"] = 1203
        base["lead_conversion_rate"] = 7.1
    elif category == "general_website":
        base["total_page_views"] = 48_200
        base["unique_visitors"] = 12_100
    return base


def _mock_funnels(_category: str) -> List[Dict[str, Any]]:
    return [
        {"step": "방문", "count": 10000, "percentage": 100},
        {"step": "상품조회", "count": 6200, "percentage": 62},
        {"step": "장바구니", "count": 2100, "percentage": 21},
        {"step": "결제", "count": 650, "percentage": 6.5},
    ]


def _mock_kpi_trends(_category: str) -> List[Dict[str, Any]]:
    return [
        {"date": "2025-01-22", "value": 3.8, "metric": "conversion_rate"},
        {"date": "2025-01-23", "value": 4.0, "metric": "conversion_rate"},
        {"date": "2025-01-24", "value": 4.2, "metric": "conversion_rate"},
        {"date": "2025-01-25", "value": 4.1, "metric": "conversion_rate"},
        {"date": "2025-01-26", "value": 4.3, "metric": "conversion_rate"},
        {"date": "2025-01-27", "value": 4.2, "metric": "conversion_rate"},
    ]


def _mock_recent_events(_category: str) -> List[Dict[str, Any]]:
    return [
        {"id": "evt-1", "timestamp": "2025-01-27T14:32:00Z", "event_type": "page_view", "user_id": "u-101"},
        {"id": "evt-2", "timestamp": "2025-01-27T14:28:00Z", "event_type": "conversion", "user_id": "u-102"},
        {"id": "evt-3", "timestamp": "2025-01-27T14:15:00Z", "event_type": "add_to_cart", "user_id": "u-103"},
        {"id": "evt-4", "timestamp": "2025-01-27T14:10:00Z", "event_type": "page_view", "user_id": "u-104"},
        {"id": "evt-5", "timestamp": "2025-01-27T14:05:00Z", "event_type": "signup", "user_id": "u-105"},
    ]


def _mock_scenario_performance(_category: str) -> List[Dict[str, Any]]:
    return [
        {"scenario_id": "s1", "name": "랜딩 A", "conversion_rate": 5.2, "total_events": 3200},
        {"scenario_id": "s2", "name": "랜딩 B", "conversion_rate": 3.8, "total_events": 4100},
        {"scenario_id": "s3", "name": "랜딩 C", "conversion_rate": 4.5, "total_events": 2800},
    ]


def _mock_category_metrics(category: str) -> Dict[str, Any]:
    if category == "ecommerce":
        return {
            "ecommerce": {"revenue": 42_500_000, "orders": 655, "average_order_value": 64_885},
        }
    if category == "lead_generation":
        return {"lead_generation": {"leads": 1203, "conversion_rate": 7.1}}
    if category == "general_website":
        return {"general_website": {"page_views": 48_200, "unique_visitors": 12_100}}
    return {
        "ecommerce": {"revenue": 42_500_000, "orders": 655, "average_order_value": 64_885},
        "lead_generation": {"leads": 1203, "conversion_rate": 7.1},
        "general_website": {"page_views": 48_200, "unique_visitors": 12_100},
    }


@router.get(
    "/overview",
    summary="대시보드 개요 조회",
    description="""
    대시보드 개요 메트릭을 조회합니다.
    
    **카테고리:**
    - `all`: 전체
    - `ecommerce`: 전자상거래
    - `lead_generation`: 잠재고객 확보
    - `general_website`: 일반 웹사이트
    
    **응답 예시:**
    ```json
    {
        "success": true,
        "data": {
            "total_events": 12450,
            "total_users": 8920,
            "conversion_rate": 4.2,
            "total_sessions": 15600,
            "total_conversions": 655,
            "average_conversion_rate": 4.2
        }
    }
    ```
    """,
    tags=["dashboard"]
)
async def get_overview(category: str = Query("all", description="카테고리", example="all")):
    """대시보드 개요 (스텁)"""
    valid = ("all", "ecommerce", "lead_generation", "general_website")
    c = category if category in valid else "all"
    return {"success": True, "data": _mock_overview(c)}


@router.get("/funnels")
async def get_funnels(
    scenario_id: Optional[str] = Query(None),
    category: str = Query("all", description="카테고리"),
):
    """퍼널 데이터 (스텁)"""
    valid = ("all", "ecommerce", "lead_generation", "general_website")
    c = category if category in valid else "all"
    return {"success": True, "data": _mock_funnels(c)}


@router.get("/kpi-trends")
async def get_kpi_trends(
    metric: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    category: str = Query("all", description="카테고리"),
):
    """KPI 트렌드 (스텁)"""
    valid = ("all", "ecommerce", "lead_generation", "general_website")
    c = category if category in valid else "all"
    return {"success": True, "data": _mock_kpi_trends(c)}


@router.get("/recent-events")
async def get_recent_events(
    limit: Optional[int] = Query(None),
    category: str = Query("all", description="카테고리"),
):
    """최근 이벤트 (스텁)"""
    valid = ("all", "ecommerce", "lead_generation", "general_website")
    c = category if category in valid else "all"
    data = _mock_recent_events(c)
    if limit is not None and limit > 0:
        data = data[:limit]
    return {"success": True, "data": data}


@router.get("/scenario-performance")
async def get_scenario_performance(category: str = Query("all", description="카테고리")):
    """시나리오 성능 (스텁)"""
    valid = ("all", "ecommerce", "lead_generation", "general_website")
    c = category if category in valid else "all"
    return {"success": True, "data": _mock_scenario_performance(c)}


@router.get("/category-metrics")
async def get_category_metrics(category: str = Query("all", description="카테고리")):
    """카테고리별 메트릭 (스텁)"""
    valid = ("all", "ecommerce", "lead_generation", "general_website")
    c = category if category in valid else "all"
    return {"success": True, "data": _mock_category_metrics(c)}
