"""
API 라우트
"""
import asyncio
import logging
import json
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Body, Query
from fastapi.responses import StreamingResponse

from backend.services.target_analyzer import analyze_target, analyze_target_stream
from backend.services.sentiment_analyzer import analyze_sentiment, analyze_context, analyze_tone
from backend.services.keyword_recommender import recommend_keywords
from backend.services.progress_tracker import create_progress_tracker, get_progress_tracker, remove_progress_tracker
from backend.utils.error_handler import (
    handle_api_error,
    validate_target_type,
    validate_date_format,
    ServiceUnavailableError
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/target/analyze/stream",
    summary="타겟 분석 수행 (스트리밍)",
    description="""
    AI를 사용하여 타겟 분석을 스트리밍 방식으로 수행합니다 (문장 단위 실시간 출력).
    
    **스트리밍 형식:**
    - NDJSON (Newline Delimited JSON)
    - 각 줄은 JSON 객체
    - 타입: `sentence`, `progress`, `complete`, `error`
    
    **응답 예시:**
    ```
    {"type": "sentence", "content": "전기차 시장은...", "section": "executive_summary"}
    {"type": "progress", "progress": 50, "message": "분석 진행 중..."}
    {"type": "complete", "data": {...}}
    ```
    
    **사용 사례:**
    - 실시간 분석 결과 표시
    - 긴 분석 결과의 점진적 로딩
    - 진행 상황 표시
    """,
    response_description="스트리밍 응답 (NDJSON 형식)",
    tags=["analysis", "streaming"]
)
async def analyze_target_stream_endpoint(
    target_keyword: str = Body(..., description="분석할 타겟 키워드 또는 주제", example="전기차"),
    target_type: str = Body("keyword", description="분석 유형: keyword, audience, comprehensive", example="keyword"),
    additional_context: Optional[str] = Body(None, description="추가 컨텍스트 정보", example="2025년 한국 시장"),
    use_gemini: bool = Body(True, description="Gemini API 사용 여부", example=True),
    start_date: Optional[str] = Body(None, description="분석 시작일 (YYYY-MM-DD 형식)", example="2025-01-01"),
    end_date: Optional[str] = Body(None, description="분석 종료일 (YYYY-MM-DD 형식)", example="2025-01-31")
):
    """AI를 사용하여 타겟 분석을 스트리밍 방식으로 수행합니다 (문장 단위 실시간 출력)."""
    try:
        logger.info(f"타겟 분석 스트리밍 요청: {target_keyword} ({target_type})")
        
        # 타겟 타입 검증
        validate_target_type(target_type)
        
        # 날짜 형식 검증
        validate_date_format(start_date, "start_date")
        validate_date_format(end_date, "end_date")
        
        # Progress tracker 생성
        try:
            progress_tracker = create_progress_tracker()
        except Exception as e:
            logger.warning(f"Progress tracker 생성 실패 (계속 진행): {e}")
            progress_tracker = None
        
        async def generate():
            chunk_count = 0
            try:
                # 초기 진행률 전송
                yield json.dumps({
                    "type": "progress",
                    "progress": 5,
                    "message": "분석 준비 중..."
                }, ensure_ascii=False) + "\n"
                
                async for chunk in analyze_target_stream(
                    target_keyword=target_keyword,
                    target_type=target_type,
                    additional_context=additional_context,
                    use_gemini=use_gemini,
                    start_date=start_date,
                    end_date=end_date,
                    progress_tracker=progress_tracker
                ):
                    chunk_count += 1
                    # JSON 형식으로 스트리밍
                    yield json.dumps(chunk, ensure_ascii=False) + "\n"
                    
                    # 완료 또는 오류 시 종료
                    if chunk.get("type") in ["complete", "error"]:
                        logger.info(f"스트리밍 완료: {chunk_count}개 청크 전송")
                        break
                
                # 청크를 하나도 받지 못한 경우 (에러 처리)
                if chunk_count == 0:
                    logger.error("스트리밍: 청크를 받지 못함")
                    yield json.dumps({
                        "type": "error",
                        "message": "분석이 시작되지 않았습니다. API 키 설정 및 서버 로그를 확인해주세요."
                    }, ensure_ascii=False) + "\n"
                    
            except Exception as e:
                logger.error(f"스트리밍 생성 중 오류: {e}", exc_info=True)
                yield json.dumps({
                    "type": "error",
                    "message": f"분석 중 오류가 발생했습니다: {str(e)}"
                }, ensure_ascii=False) + "\n"
            finally:
                # Progress tracker 정리
                if progress_tracker:
                    try:
                        remove_progress_tracker(progress_tracker.task_id)
                    except Exception as e:
                        logger.warning(f"Progress tracker 정리 실패: {e}")
        
        return StreamingResponse(
            generate(),
            media_type="application/x-ndjson",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_api_error(e, "타겟 분석 스트리밍")


@router.post(
    "/target/analyze",
    summary="타겟 분석 수행",
    description="""
    AI를 사용하여 타겟 키워드, 오디언스, 또는 종합 분석을 수행합니다.
    
    **분석 유형:**
    - `keyword`: 키워드 분석 (검색 트렌드, 연관 키워드, 경쟁 분석)
    - `audience`: 오디언스 분석 (페르소나, 고객 여정, 채널 전략)
    - `comprehensive`: 종합 분석 (키워드 + 오디언스 통합)
    
    **응답 형식:**
    - MECE 구조의 상세 분석 결과
    - Executive Summary, Key Findings, Detailed Analysis, Strategic Recommendations 포함
    
    **예시 요청:**
    ```json
    {
        "target_keyword": "전기차",
        "target_type": "keyword",
        "additional_context": "2025년 한국 시장",
        "use_gemini": false,
        "start_date": "2025-01-01",
        "end_date": "2025-01-31"
    }
    ```
    """,
    response_description="분석 결과 객체 (MECE 구조)",
    tags=["analysis"]
)
async def analyze_target_endpoint(
    target_keyword: str = Body(..., description="분석할 타겟 키워드 또는 주제", example="전기차"),
    target_type: str = Body("keyword", description="분석 유형: keyword, audience, comprehensive", example="keyword"),
    additional_context: Optional[str] = Body(None, description="추가 컨텍스트 정보", example="2025년 한국 시장"),
    use_gemini: bool = Body(True, description="Gemini API 사용 여부 (OpenAI 결과 보완)", example=True),
    start_date: Optional[str] = Body(None, description="분석 시작일 (YYYY-MM-DD 형식)", example="2025-01-01"),
    end_date: Optional[str] = Body(None, description="분석 종료일 (YYYY-MM-DD 형식)", example="2025-01-31"),
    include_sentiment: bool = Body(True, description="정성적 분석 포함 여부", example=True),
    include_recommendations: bool = Body(True, description="키워드 추천 포함 여부", example=True)
):
    """AI를 사용하여 타겟 분석을 수행합니다. 정성적 분석 및 키워드 추천 옵션 포함."""
    progress_tracker = None
    try:
        logger.info(f"타겟 분석 요청: {target_keyword} ({target_type})")
        logger.info(f"요청 파라미터 - use_gemini: {use_gemini}, start_date: {start_date}, end_date: {end_date}")
        
        # 타겟 타입 검증
        validate_target_type(target_type)
        
        # 날짜 형식 검증
        validate_date_format(start_date, "start_date")
        validate_date_format(end_date, "end_date")
        
        # Progress tracker 생성
        try:
            progress_tracker = create_progress_tracker()
        except Exception as e:
            logger.warning(f"Progress tracker 생성 실패 (계속 진행): {e}")
            progress_tracker = None
        
        # 타겟 분석 수행
        result = await analyze_target(
            target_keyword=target_keyword,
            target_type=target_type,
            additional_context=additional_context,
            use_gemini=use_gemini,
            start_date=start_date,
            end_date=end_date,
            progress_tracker=progress_tracker
        )
        
        # 정성적 분석 포함 (감정/맥락/톤 분석 병렬 실행)
        if include_sentiment:
            try:
                if progress_tracker:
                    await progress_tracker.update(50, "정성적 분석 수행 중...")
                sentiment_result, context_result, tone_result = await asyncio.gather(
                    analyze_sentiment(
                        target_keyword=target_keyword,
                        additional_context=additional_context,
                        use_gemini=use_gemini
                    ),
                    analyze_context(
                        target_keyword=target_keyword,
                        additional_context=additional_context,
                        use_gemini=use_gemini
                    ),
                    analyze_tone(
                        target_keyword=target_keyword,
                        additional_context=additional_context,
                        use_gemini=use_gemini
                    ),
                )
                result["sentiment"] = sentiment_result.get("sentiment", {})
                result["context"] = context_result.get("context", {})
                result["tone"] = tone_result.get("tone", {})
                if progress_tracker:
                    await progress_tracker.update(70, "정성적 분석 완료")
            except Exception as e:
                logger.warning(f"정성적 분석 중 오류 (무시됨): {e}")
        
        # 키워드 추천 포함
        if include_recommendations:
            try:
                if progress_tracker:
                    await progress_tracker.update(75, "키워드 추천 생성 중...")
                recommendations = await recommend_keywords(
                    target_keyword=target_keyword,
                    recommendation_type="all",
                    max_results=10,
                    additional_context=additional_context,
                    use_gemini=use_gemini
                )
                result["recommendations"] = recommendations
                if progress_tracker:
                    await progress_tracker.update(95, "키워드 추천 완료")
            except Exception as e:
                logger.warning(f"키워드 추천 중 오류 (무시됨): {e}")
        
        logger.info(f"타겟 분석 완료: {target_keyword} ({target_type})")
        
        # 결과에 API 키 상태 정보 추가 (디버깅용)
        if isinstance(result, dict):
            # 기본 분석 모드인지 확인
            if result.get("api_key_status"):
                logger.warning(f"⚠️ 기본 분석 모드로 실행됨: {result.get('api_key_status', {}).get('message', '')}")
        
        # Progress tracker 정리
        if 'progress_tracker' in locals() and progress_tracker:
            try:
                remove_progress_tracker(progress_tracker.task_id)
            except Exception as e:
                logger.warning(f"Progress tracker 정리 실패: {e}")
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        # HTTPException 발생 시에도 progress tracker 정리
        if 'progress_tracker' in locals() and progress_tracker:
            remove_progress_tracker(progress_tracker.task_id)
        raise
    except Exception as e:
        # 오류 발생 시에도 progress tracker 정리
        if 'progress_tracker' in locals() and progress_tracker:
            remove_progress_tracker(progress_tracker.task_id)
        raise handle_api_error(e, "타겟 분석")


@router.get("/target/analyze")
async def analyze_target_get(
    target_keyword: str = Query(..., description="분석할 타겟 키워드 또는 주제"),
    target_type: str = Query("keyword", description="분석 유형: keyword, audience, comprehensive"),
    additional_context: Optional[str] = Query(None, description="추가 컨텍스트 정보"),
    use_gemini: bool = Query(True, description="Gemini API 사용 여부"),
    start_date: Optional[str] = Query(None, description="분석 시작일 (YYYY-MM-DD 형식)"),
    end_date: Optional[str] = Query(None, description="분석 종료일 (YYYY-MM-DD 형식)")
):
    """AI를 사용하여 타겟 분석을 수행합니다. (GET 방식)"""
    try:
        logger.info(f"타겟 분석 요청 (GET): {target_keyword} ({target_type})")
        
        # 타겟 타입 검증
        validate_target_type(target_type)
        
        # 날짜 형식 검증
        validate_date_format(start_date, "start_date")
        validate_date_format(end_date, "end_date")
        
        # 타겟 분석 수행
        result = await analyze_target(
            target_keyword=target_keyword,
            target_type=target_type,
            additional_context=additional_context,
            use_gemini=use_gemini,
            start_date=start_date,
            end_date=end_date
        )
        
        logger.info(f"타겟 분석 완료: {target_keyword} ({target_type})")
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_api_error(e, "타겟 분석")


@router.post("/analysis/sentiment")
async def analyze_sentiment_endpoint(
    target_keyword: str = Body(..., description="분석할 키워드"),
    additional_context: Optional[str] = Body(None, description="추가 컨텍스트 정보"),
    use_gemini: bool = Body(True, description="Gemini API 사용 여부")
):
    """감정 분석을 수행합니다."""
    try:
        logger.info(f"감정 분석 요청: {target_keyword}")
        
        result = await analyze_sentiment(
            target_keyword=target_keyword,
            additional_context=additional_context,
            use_gemini=use_gemini
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_api_error(e, "감정 분석")


@router.post("/analysis/context")
async def analyze_context_endpoint(
    target_keyword: str = Body(..., description="분석할 키워드"),
    additional_context: Optional[str] = Body(None, description="추가 컨텍스트 정보"),
    use_gemini: bool = Body(True, description="Gemini API 사용 여부")
):
    """맥락 분석을 수행합니다."""
    try:
        logger.info(f"맥락 분석 요청: {target_keyword}")
        
        result = await analyze_context(
            target_keyword=target_keyword,
            additional_context=additional_context,
            use_gemini=use_gemini
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_api_error(e, "맥락 분석")


@router.post("/analysis/tone")
async def analyze_tone_endpoint(
    target_keyword: str = Body(..., description="분석할 키워드"),
    additional_context: Optional[str] = Body(None, description="추가 컨텍스트 정보"),
    use_gemini: bool = Body(True, description="Gemini API 사용 여부")
):
    """톤 분석을 수행합니다."""
    try:
        logger.info(f"톤 분석 요청: {target_keyword}")
        
        result = await analyze_tone(
            target_keyword=target_keyword,
            additional_context=additional_context,
            use_gemini=use_gemini
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_api_error(e, "톤 분석")


@router.post("/recommend/keywords")
async def recommend_keywords_endpoint(
    target_keyword: str = Body(..., description="기준 키워드"),
    recommendation_type: str = Body("all", description="추천 유형: all, semantic, co_occurring, hierarchical, trending, alternative"),
    max_results: int = Body(10, description="최대 결과 수"),
    additional_context: Optional[str] = Body(None, description="추가 컨텍스트 정보"),
    use_gemini: bool = Body(True, description="Gemini API 사용 여부")
):
    """관련 키워드를 추천합니다."""
    try:
        logger.info(f"키워드 추천 요청: {target_keyword} (유형: {recommendation_type})")
        
        if recommendation_type not in ["all", "semantic", "co_occurring", "hierarchical", "trending", "alternative"]:
            raise HTTPException(
                status_code=400,
                detail="recommendation_type은 'all', 'semantic', 'co_occurring', 'hierarchical', 'trending', 'alternative' 중 하나여야 합니다."
            )
        
        result = await recommend_keywords(
            target_keyword=target_keyword,
            recommendation_type=recommendation_type,
            max_results=max_results,
            additional_context=additional_context,
            use_gemini=use_gemini
        )
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_api_error(e, "키워드 추천")


@router.post("/analysis/comprehensive")
async def comprehensive_analysis_endpoint(
    target_keyword: str = Body(..., description="분석할 키워드"),
    target_type: str = Body("keyword", description="분석 유형: keyword, audience, comprehensive"),
    additional_context: Optional[str] = Body(None, description="추가 컨텍스트 정보"),
    use_gemini: bool = Body(True, description="Gemini API 사용 여부"),
    analysis_depth: str = Body("standard", description="분석 깊이: basic, standard, deep")
):
    """종합 분석을 수행합니다 (기본 분석 + 정성적 분석 + 키워드 추천)."""
    try:
        logger.info(f"종합 분석 요청: {target_keyword} ({target_type}, 깊이: {analysis_depth})")
        
        # 기본 분석
        result = await analyze_target(
            target_keyword=target_keyword,
            target_type=target_type,
            additional_context=additional_context,
            use_gemini=use_gemini
        )
        
        # 정성적 분석 (감정/맥락/톤 병렬 실행)
        try:
            sentiment_result, context_result, tone_result = await asyncio.gather(
                analyze_sentiment(
                    target_keyword=target_keyword,
                    additional_context=additional_context,
                    use_gemini=use_gemini
                ),
                analyze_context(
                    target_keyword=target_keyword,
                    additional_context=additional_context,
                    use_gemini=use_gemini
                ),
                analyze_tone(
                    target_keyword=target_keyword,
                    additional_context=additional_context,
                    use_gemini=use_gemini
                ),
            )
            result["sentiment"] = sentiment_result.get("sentiment", {})
            result["context"] = context_result.get("context", {})
            result["tone"] = tone_result.get("tone", {})
        except Exception as e:
            logger.warning(f"정성적 분석 중 오류 (무시됨): {e}")
        
        # 키워드 추천
        try:
            recommendations = await recommend_keywords(
                target_keyword=target_keyword,
                recommendation_type="all",
                max_results=15 if analysis_depth == "deep" else 10,
                additional_context=additional_context,
                use_gemini=use_gemini
            )
            result["recommendations"] = recommendations
        except Exception as e:
            logger.warning(f"키워드 추천 중 오류 (무시됨): {e}")
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"종합 분석 중 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"종합 분석 실패: {str(e)}"
        )


@router.post("/analysis/compare")
async def compare_keywords_endpoint(
    keywords: List[str] = Body(..., description="비교할 키워드 목록"),
    comparison_aspects: Optional[List[str]] = Body(None, description="비교 관점: sentiment, context, trend, market"),
    use_gemini: bool = Body(True, description="Gemini API 사용 여부")
):
    """여러 키워드를 비교 분석합니다."""
    try:
        logger.info(f"키워드 비교 분석 요청: {keywords}")
        
        if len(keywords) < 2:
            raise HTTPException(
                status_code=400,
                detail="비교하려면 최소 2개 이상의 키워드가 필요합니다."
            )
        
        if len(keywords) > 5:
            raise HTTPException(
                status_code=400,
                detail="한 번에 비교할 수 있는 키워드는 최대 5개입니다."
            )
        
        # 각 키워드에 대한 분석 병렬 수행
        async def analyze_one_keyword(keyword: str):
            result = await analyze_target(
                target_keyword=keyword,
                target_type="keyword",
                use_gemini=use_gemini
            )
            if not comparison_aspects or "sentiment" in comparison_aspects:
                try:
                    sentiment_result = await analyze_sentiment(
                        target_keyword=keyword,
                        use_gemini=use_gemini
                    )
                    result["sentiment"] = sentiment_result.get("sentiment", {})
                except Exception as e:
                    logger.warning(f"감정 분석 중 오류 (무시됨): {e}")
            return keyword, result

        results_list = await asyncio.gather(
            *[analyze_one_keyword(kw) for kw in keywords],
            return_exceptions=False
        )
        comparison_results = {kw: res for kw, res in results_list}
        
        # 비교 요약 생성
        comparison_summary = {
            "keywords": keywords,
            "comparison_results": comparison_results,
            "summary": f"{len(keywords)}개 키워드 비교 분석 완료"
        }
        
        return {
            "success": True,
            "data": comparison_summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"비교 분석 중 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"비교 분석 실패: {str(e)}"
        )
