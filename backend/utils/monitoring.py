"""
성능 모니터링 유틸리티
API 응답 시간, 에러율, 사용량 추적
"""
import time
import logging
from typing import Optional, Dict, Any
from functools import wraps
from contextlib import contextmanager
from datetime import datetime

logger = logging.getLogger(__name__)

# 간단한 메모리 기반 메트릭 저장소 (프로덕션에서는 Redis 등 사용 권장)
_metrics_store: Dict[str, Any] = {
    "api_calls": [],
    "errors": [],
    "response_times": [],
}


def track_api_call(endpoint: str, method: str = "GET", status_code: int = 200, response_time: float = 0.0):
    """
    API 호출 추적
    
    Args:
        endpoint: API 엔드포인트
        method: HTTP 메서드
        status_code: 응답 상태 코드
        response_time: 응답 시간 (초)
    """
    try:
        _metrics_store["api_calls"].append({
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        })
        
        # 최근 1000개만 유지
        if len(_metrics_store["api_calls"]) > 1000:
            _metrics_store["api_calls"] = _metrics_store["api_calls"][-1000:]
        
        _metrics_store["response_times"].append(response_time)
        if len(_metrics_store["response_times"]) > 1000:
            _metrics_store["response_times"] = _metrics_store["response_times"][-1000:]
        
        # 에러 추적
        if status_code >= 400:
            _metrics_store["errors"].append({
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "timestamp": datetime.now().isoformat()
            })
            if len(_metrics_store["errors"]) > 500:
                _metrics_store["errors"] = _metrics_store["errors"][-500:]
                
    except Exception as e:
        logger.warning(f"메트릭 추적 중 오류: {e}")


def get_metrics_summary() -> Dict[str, Any]:
    """
    메트릭 요약 정보 반환
    
    Returns:
        메트릭 요약 딕셔너리
    """
    try:
        api_calls = _metrics_store.get("api_calls", [])
        errors = _metrics_store.get("errors", [])
        response_times = _metrics_store.get("response_times", [])
        
        if not response_times:
            return {
                "total_calls": 0,
                "total_errors": 0,
                "error_rate": 0.0,
                "avg_response_time": 0.0,
                "min_response_time": 0.0,
                "max_response_time": 0.0,
            }
        
        total_calls = len(api_calls)
        total_errors = len(errors)
        error_rate = (total_errors / total_calls * 100) if total_calls > 0 else 0.0
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        
        return {
            "total_calls": total_calls,
            "total_errors": total_errors,
            "error_rate": round(error_rate, 2),
            "avg_response_time": round(avg_response_time, 3),
            "min_response_time": round(min_response_time, 3),
            "max_response_time": round(max_response_time, 3),
            "recent_errors": errors[-10:] if errors else [],
        }
    except Exception as e:
        logger.error(f"메트릭 요약 생성 중 오류: {e}")
        return {}


def reset_metrics():
    """메트릭 저장소 초기화"""
    global _metrics_store
    _metrics_store = {
        "api_calls": [],
        "errors": [],
        "response_times": [],
    }


@contextmanager
def measure_time(operation_name: str):
    """
    작업 시간 측정 컨텍스트 매니저
    
    Usage:
        with measure_time("api_call"):
            # 작업 수행
            pass
    """
    start_time = time.time()
    try:
        yield
    finally:
        elapsed_time = time.time() - start_time
        logger.debug(f"{operation_name} 소요 시간: {elapsed_time:.3f}초")


def monitor_api_performance(func):
    """
    API 성능 모니터링 데코레이터
    
    Usage:
        @monitor_api_performance
        async def my_api_endpoint():
            pass
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        status_code = 200
        
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            status_code = 500
            raise
        finally:
            response_time = time.time() - start_time
            endpoint = getattr(func, "__name__", "unknown")
            track_api_call(endpoint, "POST", status_code, response_time)
    
    return wrapper
