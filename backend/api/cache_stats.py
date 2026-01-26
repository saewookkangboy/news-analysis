"""
캐시 통계 API
"""
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException
from backend.middleware.cache_middleware import get_cache_store
from backend.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/cache/stats")
async def get_cache_stats():
    """캐시 통계 조회"""
    try:
        if not settings.CACHE_ENABLED:
            return {
                "enabled": False,
                "message": "캐시가 비활성화되어 있습니다."
            }
        
        cache_store = get_cache_store()
        now = datetime.now()
        
        active_entries = 0
        expired_entries = 0
        
        for key, value in cache_store.items():
            if isinstance(value, dict) and "expires_at" in value:
                if value["expires_at"] > now:
                    active_entries += 1
                else:
                    expired_entries += 1
        
        return {
            "enabled": True,
            "total_entries": len(cache_store),
            "active_entries": active_entries,
            "expired_entries": expired_entries,
            "duration_seconds": settings.CACHE_TTL
        }
        
    except Exception as e:
        logger.error(f"캐시 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cache/clear")
async def clear_cache():
    """캐시 전체 삭제"""
    try:
        if not settings.CACHE_ENABLED:
            raise HTTPException(
                status_code=400,
                detail="캐시가 비활성화되어 있습니다."
            )
        
        cache_store = get_cache_store()
        cache_store.clear()
        
        logger.info("캐시가 모두 삭제되었습니다.")
        
        return {
            "success": True,
            "message": "캐시가 모두 삭제되었습니다."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"캐시 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))
