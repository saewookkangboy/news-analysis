"""
캐싱 미들웨어
API 응답을 캐싱하여 성능을 향상시킵니다.
"""
import hashlib
import json
import logging
from typing import Callable
from datetime import datetime, timedelta
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class CacheMiddleware(BaseHTTPMiddleware):
    """캐싱 미들웨어 클래스"""
    
    def __init__(
        self,
        app,
        duration: int = 3600,
        max_entries: int = 500,
        cleanup_interval: int = 100,
    ):
        """
        Args:
            app: FastAPI 애플리케이션
            duration: 캐시 유지 시간 (초)
            max_entries: 최대 캐시 엔트리 수
            cleanup_interval: N개 요청마다 만료 캐시 정리
        """
        super().__init__(app)
        self.cache: dict = {}
        self.duration = duration
        self.max_entries = max_entries
        self.cleanup_interval = max(1, cleanup_interval)
        self._request_count = 0
        self._cache_hits = 0
        self._cache_misses = 0

        # 캐시 메트릭 전역 저장 (모니터링 API 용)
        set_cache_metrics(
            {
                "requests": 0,
                "hits": 0,
                "misses": 0,
                "hit_rate": 0.0,
            }
        )
        # 전역 저장소에 참조 저장 (함수는 파일 하단에 정의됨)
        set_cache_store(self.cache)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """요청 처리 및 캐싱"""
        
        # API GET 요청만 캐싱
        if request.method != "GET" or not request.url.path.startswith("/api"):
            return await call_next(request)

        # 스트리밍/실시간 경로 제외
        if request.url.path.startswith("/api/target/analyze/stream"):
            return await call_next(request)

        # 클라이언트 캐시 무효화 요청 지원
        cache_control = request.headers.get("cache-control", "")
        if "no-store" in cache_control or "no-cache" in cache_control:
            return await call_next(request)

        self._request_count += 1
        
        # 캐시 키 생성
        cache_key = self._generate_cache_key(request)
        
        # 캐시 확인
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            
            # 캐시 만료 확인
            if datetime.now() < cached_data["expires_at"]:
                logger.debug(f"캐시 히트: {cache_key}")
                self._cache_hits += 1
                self._sync_metrics()
                return JSONResponse(
                    content=cached_data["data"],
                    headers={"X-Cache": "HIT", "X-Cache-TTL": str(self.duration)}
                )
            else:
                # 만료된 캐시 제거
                del self.cache[cache_key]
                logger.debug(f"캐시 만료: {cache_key}")

        self._cache_misses += 1
        self._sync_metrics()
        
        # 원본 요청 처리
        response = await call_next(request)
        
        # 성공 응답만 캐싱
        if response.status_code == 200:
            try:
                # 응답 본문 읽기
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk
                
                # JSON 파싱
                try:
                    data = json.loads(response_body.decode())
                except json.JSONDecodeError:
                    # JSON이 아니면 캐싱하지 않음
                    return Response(
                        content=response_body,
                        status_code=response.status_code,
                        headers=dict(response.headers)
                    )
                
                # 주기적 만료 캐시 정리
                if self._request_count % self.cleanup_interval == 0:
                    self._cleanup_expired_entries()

                # 엔트리 수 상한 관리 (오래된 항목 제거)
                if len(self.cache) >= self.max_entries:
                    self._evict_oldest_entry()

                # 캐시 저장
                self.cache[cache_key] = {
                    "data": data,
                    "expires_at": datetime.now() + timedelta(seconds=self.duration),
                    "created_at": datetime.now()
                }
                
                logger.debug(f"캐시 저장: {cache_key}")
                
                # 응답 재생성
                return JSONResponse(
                    content=data,
                    headers={**dict(response.headers), "X-Cache": "MISS"}
                )
                
            except Exception as e:
                logger.error(f"캐싱 중 오류: {e}")
                return response
        
        return response
    
    def _generate_cache_key(self, request: Request) -> str:
        """캐시 키 생성"""
        # URL과 쿼리 파라미터를 기반으로 키 생성
        url = str(request.url)
        key_string = f"{request.method}:{url}"
        
        # 해시 생성
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def clear_cache(self):
        """캐시 전체 삭제"""
        self.cache.clear()
        logger.info("캐시가 모두 삭제되었습니다.")
    
    def get_cache_stats(self) -> dict:
        """캐시 통계 반환"""
        now = datetime.now()
        active_cache = {
            k: v for k, v in self.cache.items()
            if v["expires_at"] > now
        }
        
        return {
            "total_entries": len(self.cache),
            "active_entries": len(active_cache),
            "expired_entries": len(self.cache) - len(active_cache),
            "duration_seconds": self.duration,
            "max_entries": self.max_entries,
            "requests": self._request_count,
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "hit_rate": round((self._cache_hits / self._request_count) * 100, 2) if self._request_count else 0.0,
        }

    def _cleanup_expired_entries(self):
        """만료된 캐시 엔트리 정리"""
        now = datetime.now()
        expired_keys = [
            key for key, value in self.cache.items()
            if isinstance(value, dict) and value.get("expires_at") and value["expires_at"] <= now
        ]
        for key in expired_keys:
            self.cache.pop(key, None)

    def _evict_oldest_entry(self):
        """가장 오래된 캐시 엔트리 제거"""
        if not self.cache:
            return

        oldest_key = min(
            self.cache,
            key=lambda key: self.cache[key].get("created_at", datetime.min),
        )
        self.cache.pop(oldest_key, None)

    def _sync_metrics(self):
        """전역 메트릭 동기화"""
        set_cache_metrics(
            {
                "requests": self._request_count,
                "hits": self._cache_hits,
                "misses": self._cache_misses,
                "hit_rate": round((self._cache_hits / self._request_count) * 100, 2) if self._request_count else 0.0,
            }
        )


# 전역 캐시 저장소 (통계용)
_cache_store: dict = {}
_cache_metrics: dict = {}


def get_cache_store() -> dict:
    """캐시 저장소 반환"""
    return _cache_store


def set_cache_store(store: dict):
    """캐시 저장소 설정"""
    global _cache_store
    _cache_store = store


def get_cache_metrics() -> dict:
    """캐시 메트릭 반환"""
    return _cache_metrics


def set_cache_metrics(metrics: dict):
    """캐시 메트릭 설정"""
    global _cache_metrics
    _cache_metrics = metrics
