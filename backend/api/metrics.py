"""
성능 메트릭 API 엔드포인트
"""
import logging
from fastapi import APIRouter
from backend.utils.monitoring import get_metrics_summary, reset_metrics

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/metrics/summary")
async def get_metrics_summary_endpoint():
    """
    성능 메트릭 요약 조회
    
    Returns:
        - total_calls: 총 API 호출 수
        - total_errors: 총 에러 수
        - error_rate: 에러율 (%)
        - avg_response_time: 평균 응답 시간 (초)
        - min_response_time: 최소 응답 시간 (초)
        - max_response_time: 최대 응답 시간 (초)
        - recent_errors: 최근 에러 목록
    """
    try:
        summary = get_metrics_summary()
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        logger.error(f"메트릭 요약 조회 중 오류: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/metrics/reset")
async def reset_metrics_endpoint():
    """
    메트릭 저장소 초기화
    
    주의: 프로덕션 환경에서는 사용하지 않는 것을 권장합니다.
    """
    try:
        reset_metrics()
        return {
            "success": True,
            "message": "메트릭이 초기화되었습니다."
        }
    except Exception as e:
        logger.error(f"메트릭 초기화 중 오류: {e}")
        return {
            "success": False,
            "error": str(e)
        }
