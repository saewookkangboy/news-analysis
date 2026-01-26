"""
API 라우트
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Body, Query

from backend.services.target_analyzer import analyze_target

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/target/analyze")
async def analyze_target_endpoint(
    target_keyword: str = Body(..., description="분석할 타겟 키워드 또는 주제"),
    target_type: str = Body("keyword", description="분석 유형: keyword, audience, competitor"),
    additional_context: Optional[str] = Body(None, description="추가 컨텍스트 정보"),
    use_gemini: bool = Body(False, description="Gemini API 사용 여부")
):
    """AI를 사용하여 타겟 분석을 수행합니다."""
    try:
        logger.info(f"타겟 분석 요청: {target_keyword} ({target_type})")
        
        # 타겟 타입 검증
        if target_type not in ["keyword", "audience", "competitor"]:
            raise HTTPException(
                status_code=400,
                detail="target_type은 'keyword', 'audience', 'competitor' 중 하나여야 합니다."
            )
        
        # 타겟 분석 수행
        result = await analyze_target(
            target_keyword=target_keyword,
            target_type=target_type,
            additional_context=additional_context,
            use_gemini=use_gemini
        )
        
        logger.info(f"타겟 분석 완료: {target_keyword} ({target_type})")
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"타겟 분석 중 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"타겟 분석 실패: {str(e)}"
        )


@router.get("/target/analyze")
async def analyze_target_get(
    target_keyword: str = Query(..., description="분석할 타겟 키워드 또는 주제"),
    target_type: str = Query("keyword", description="분석 유형: keyword, audience, competitor"),
    additional_context: Optional[str] = Query(None, description="추가 컨텍스트 정보"),
    use_gemini: bool = Query(False, description="Gemini API 사용 여부")
):
    """AI를 사용하여 타겟 분석을 수행합니다. (GET 방식)"""
    try:
        logger.info(f"타겟 분석 요청 (GET): {target_keyword} ({target_type})")
        
        # 타겟 타입 검증
        if target_type not in ["keyword", "audience", "competitor"]:
            raise HTTPException(
                status_code=400,
                detail="target_type은 'keyword', 'audience', 'competitor' 중 하나여야 합니다."
            )
        
        # 타겟 분석 수행
        result = await analyze_target(
            target_keyword=target_keyword,
            target_type=target_type,
            additional_context=additional_context,
            use_gemini=use_gemini
        )
        
        logger.info(f"타겟 분석 완료: {target_keyword} ({target_type})")
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"타겟 분석 중 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"타겟 분석 실패: {str(e)}"
        )
