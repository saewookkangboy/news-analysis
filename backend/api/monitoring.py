"""
모니터링 및 헬스 체크 API
"""
import logging
import time
import os
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter
from backend.config import settings
from backend.utils.security import check_api_keys_status

logger = logging.getLogger(__name__)

router = APIRouter()

# 시작 시간 기록
START_TIME = time.time()

# psutil 임포트 (선택적)
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil이 설치되지 않아 시스템 메트릭 수집이 제한됩니다.")


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    헬스 체크 엔드포인트
    서비스 상태, API 키 상태, 시스템 리소스 정보를 반환
    """
    try:
        # API 키 상태 확인
        api_key_status = check_api_keys_status()
        
        # 시스템 리소스 정보 (가능한 경우)
        system_info = {
            "uptime_seconds": int(time.time() - START_TIME)
        }
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process(os.getpid())
                system_info.update({
                    "cpu_percent": process.cpu_percent(interval=0.1),
                    "memory_mb": round(process.memory_info().rss / 1024 / 1024, 2),
                })
            except Exception as e:
                logger.warning(f"시스템 정보 수집 실패: {e}")
                system_info["error"] = "시스템 정보를 수집할 수 없습니다"
        
        # 서비스 상태
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "environment": "production" if os.environ.get("VERCEL") == "1" else "development",
            "api_keys": {
                "openai_configured": api_key_status["openai_configured"],
                "gemini_configured": api_key_status["gemini_configured"]
            },
            "system": system_info,
            "cache": {
                "enabled": settings.CACHE_ENABLED,
                "ttl_seconds": settings.CACHE_TTL
            }
        }
        
        # API 키가 하나도 없으면 경고 상태
        if not api_key_status["openai_configured"] and not api_key_status["gemini_configured"]:
            health_status["status"] = "degraded"
            health_status["warning"] = "API 키가 설정되지 않았습니다. 기본 분석 모드만 사용 가능합니다."
        
        return health_status
        
    except Exception as e:
        logger.error(f"헬스 체크 실패: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    성능 메트릭 수집
    """
    try:
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": int(time.time() - START_TIME),
        }
        
        # 시스템 메트릭 (가능한 경우)
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process(os.getpid())
                metrics["system"] = {
                    "cpu_percent": process.cpu_percent(interval=0.1),
                    "memory_mb": round(process.memory_info().rss / 1024 / 1024, 2),
                    "memory_percent": round(process.memory_percent(), 2),
                    "num_threads": process.num_threads()
                }
            except Exception as e:
                logger.warning(f"시스템 메트릭 수집 실패: {e}")
                metrics["system"] = {"error": "메트릭을 수집할 수 없습니다"}
        else:
            metrics["system"] = {"note": "psutil이 설치되지 않아 기본 메트릭만 제공됩니다"}
        
        # 캐시 메트릭
        try:
            from backend.middleware.cache_middleware import get_cache_store
            cache_store = get_cache_store()
            metrics["cache"] = {
                "total_entries": len(cache_store),
                "enabled": settings.CACHE_ENABLED,
                "ttl_seconds": settings.CACHE_TTL
            }
        except Exception as e:
            logger.warning(f"캐시 메트릭 수집 실패: {e}")
            metrics["cache"] = {"error": "캐시 메트릭을 수집할 수 없습니다"}
        
        return metrics
        
    except Exception as e:
        logger.error(f"메트릭 수집 실패: {e}", exc_info=True)
        raise
