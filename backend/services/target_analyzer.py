"""
타겟 분석 서비스
AI를 사용하여 키워드, 오디언스, 종합 분석을 수행합니다.
"""
import os
import logging
import re
from typing import Optional, Dict, Any, AsyncGenerator
import json

from backend.config import settings

# Vercel 환경 확인
IS_VERCEL = os.environ.get("VERCEL") == "1"
from backend.services.progress_tracker import ProgressTracker
from backend.utils.token_optimizer import (
    optimize_prompt, estimate_tokens, get_max_tokens_for_model, optimize_additional_context,
    extract_and_fix_json, parse_json_with_fallback
)
from backend.utils.result_normalizer import normalize_analysis_result, ensure_result_structure
from backend.utils.gemini_utils import (
    generate_content_with_fallback,
    generate_content_stream_with_fallback,
    build_model_candidates,
    is_model_not_found_error,
)
from backend.utils.security import (
    get_api_key_safely,
    check_api_keys_status,
    log_api_key_status_safely,
    validate_api_key
)

logger = logging.getLogger(__name__)


async def analyze_target(
    target_keyword: str,
    target_type: str = "keyword",
    additional_context: Optional[str] = None,
    use_gemini: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    progress_tracker: Optional[ProgressTracker] = None
) -> Dict[str, Any]:
    """
    타겟 분석 수행
    
    Args:
        target_keyword: 분석할 타겟 키워드 또는 주제
        target_type: 분석 유형 (keyword, audience, comprehensive)
        additional_context: 추가 컨텍스트 정보
        use_gemini: Gemini API 사용 여부 (True일 경우 OpenAI + Gemini 보완 분석)
        start_date: 분석 시작일 (YYYY-MM-DD 형식)
        end_date: 분석 종료일 (YYYY-MM-DD 형식)
        progress_tracker: 진행 상황 추적 객체
        
    Returns:
        분석 결과 딕셔너리
    """
    try:
        logger.info(f"타겟 분석 시작: {target_keyword} (타입: {target_type}, Gemini 보완: {use_gemini})")
        
        # API 키 상태 확인 (보안 강화: 키 값은 로깅하지 않음)
        openai_key = get_api_key_safely('OPENAI_API_KEY')
        gemini_key = get_api_key_safely('GEMINI_API_KEY')
        
        has_openai_key = bool(openai_key)
        has_gemini_key = bool(gemini_key)
        
        # 안전한 로깅 (키 값은 노출하지 않음)
        logger.info("=" * 60)
        logger.info("API 키 상태 확인")
        log_api_key_status_safely('OPENAI_API_KEY', has_openai_key)
        log_api_key_status_safely('GEMINI_API_KEY', has_gemini_key)
        logger.info("=" * 60)
        
        if not has_openai_key and not has_gemini_key:
            logger.error("⚠️ AI API 키가 설정되지 않았습니다! 기본 분석 모드로 전환됩니다.")
            logger.error("환경 변수 OPENAI_API_KEY 또는 GEMINI_API_KEY를 설정해주세요.")
            if progress_tracker:
                await progress_tracker.update(100, "AI API 키 미설정 - 기본 분석 모드")
            return _analyze_basic(target_keyword, target_type, additional_context, start_date, end_date)
        
        # 기본적으로 OpenAI API 사용
        if has_openai_key:
            if progress_tracker:
                await progress_tracker.update(10, "OpenAI API로 기본 분석 시작...")
            # 디버그 모드에서만 상세 로깅
            if settings.LOG_LEVEL == "DEBUG":
                logger.debug("=" * 60)
                logger.debug("🚀 OpenAI API 호출 시작")
                logger.debug(f"API 키: ✅ 설정됨")
                logger.debug(f"모델: {settings.OPENAI_MODEL}")
                logger.debug("=" * 60)
            else:
                logger.info("OpenAI API 호출 시작")
            try:
                result = await _analyze_with_openai(
                    target_keyword, target_type, additional_context, start_date, end_date, progress_tracker
                )
                if settings.LOG_LEVEL == "DEBUG":
                    logger.debug("=" * 60)
                    logger.debug("✅ OpenAI API 분석 성공 완료")
                    logger.debug(f"결과 키: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
                    logger.debug("=" * 60)
                else:
                    logger.info("OpenAI API 분석 성공 완료")
            except ValueError as ve:
                # API 키 관련 오류는 재시도하지 않음
                logger.error(f"❌ OpenAI API 키 오류: {ve}", exc_info=True)
                raise
            except Exception as e:
                logger.error("=" * 60)
                logger.error(f"❌ OpenAI API 호출 실패: {type(e).__name__}: {e}")
                # 프로덕션에서는 상세 스택 트레이스 제한 (보안)
                if not IS_VERCEL:
                    import traceback
                    logger.error(f"상세 스택 트레이스:\n{traceback.format_exc()}")
                else:
                    logger.error("상세 오류 정보는 서버 로그에서만 확인 가능합니다.")
                logger.error("=" * 60)
                # OpenAI 실패 시 Gemini로 재시도
                if has_gemini_key:
                    logger.info("🔄 Gemini API로 재시도 중...")
                    try:
                        if progress_tracker:
                            await progress_tracker.update(50, "OpenAI 실패, Gemini로 재시도 중...")
                        result = await _analyze_with_gemini(
                            target_keyword, target_type, additional_context, start_date, end_date, progress_tracker
                        )
                        logger.info("✅ Gemini API 분석 성공 (OpenAI 실패 후 재시도)")
                    except Exception as e2:
                        logger.error(f"❌ Gemini API 재시도도 실패: {type(e2).__name__}: {e2}", exc_info=True)
                        logger.error("⚠️ 모든 AI API 호출 실패 - 기본 분석 모드로 전환")
                        if progress_tracker:
                            await progress_tracker.update(100, "모든 AI API 실패 - 기본 분석 모드")
                        return _analyze_basic(target_keyword, target_type, additional_context, start_date, end_date)
                else:
                    logger.error("⚠️ OpenAI 실패 및 Gemini API 키 없음 - 기본 분석 모드로 전환")
                    if progress_tracker:
                        await progress_tracker.update(100, "OpenAI 실패, Gemini 없음 - 기본 분석 모드")
                    return _analyze_basic(target_keyword, target_type, additional_context, start_date, end_date)
            
            # Gemini API가 선택되고 사용 가능한 경우, OpenAI 결과를 보완
            if use_gemini and has_gemini_key:
                try:
                    if progress_tracker:
                        await progress_tracker.update(60, "Gemini API로 결과 보완 중...")
                    if settings.LOG_LEVEL == "DEBUG":
                        logger.debug("=" * 60)
                        logger.debug("🔄 Gemini API로 결과 보완 시작")
                        logger.debug("=" * 60)
                    else:
                        logger.info("Gemini API로 결과 보완 시작")
                    gemini_result = await _analyze_with_gemini(
                        target_keyword, target_type, additional_context, start_date, end_date, progress_tracker
                    )
                    # OpenAI와 Gemini 결과 통합
                    if progress_tracker:
                        await progress_tracker.update(85, "OpenAI + Gemini 결과 통합 중...")
                    result = _merge_analysis_results(result, gemini_result, target_type)
                    if settings.LOG_LEVEL == "DEBUG":
                        logger.debug("=" * 60)
                        logger.debug("✅ OpenAI + Gemini 결과 통합 완료")
                        logger.debug("=" * 60)
                    else:
                        logger.info("OpenAI + Gemini 결과 통합 완료")
                except Exception as e:
                    logger.warning("=" * 60)
                    logger.warning(f"⚠️ Gemini API 보완 중 오류 발생 (OpenAI 결과만 사용): {type(e).__name__}: {e}")
                    # 프로덕션에서는 상세 스택 트레이스 제한 (보안)
                    if not IS_VERCEL:
                        import traceback
                        logger.warning(f"상세 스택 트레이스:\n{traceback.format_exc()}")
                    logger.warning("=" * 60)
                    # Gemini 실패해도 OpenAI 결과는 유지
                    if progress_tracker:
                        await progress_tracker.update(90, "Gemini 보완 실패, OpenAI 결과만 사용")
        elif use_gemini and has_gemini_key:
            # OpenAI가 없고 Gemini만 있는 경우
            if progress_tracker:
                await progress_tracker.update(10, "Gemini API로 분석 시작...")
            if settings.LOG_LEVEL == "DEBUG":
                logger.debug("=" * 60)
                logger.debug("🚀 Gemini API 호출 시작 (OpenAI 없음)")
                logger.debug(f"API 키: ✅ 설정됨")
                logger.debug("=" * 60)
            else:
                logger.info("Gemini API 호출 시작")
            try:
                result = await _analyze_with_gemini(
                    target_keyword, target_type, additional_context, start_date, end_date, progress_tracker
                )
                if settings.LOG_LEVEL == "DEBUG":
                    logger.debug("=" * 60)
                    logger.debug("✅ Gemini API 분석 성공 완료")
                    logger.debug(f"결과 키: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
                    logger.debug("=" * 60)
                else:
                    logger.info("Gemini API 분석 성공 완료")
            except ValueError as ve:
                # API 키 관련 오류는 재시도하지 않음
                logger.error(f"❌ Gemini API 키 오류: {ve}", exc_info=True)
                raise
            except Exception as e:
                logger.error("=" * 60)
                logger.error(f"❌ Gemini API 호출 실패: {type(e).__name__}: {e}")
                import traceback
                logger.error(f"상세 스택 트레이스:\n{traceback.format_exc()}")
                logger.error("=" * 60)
                logger.error("⚠️ Gemini API 실패 - 기본 분석 모드로 전환")
                if progress_tracker:
                    await progress_tracker.update(100, "Gemini 실패 - 기본 분석 모드")
                return _analyze_basic(target_keyword, target_type, additional_context, start_date, end_date)
        else:
            # AI API가 없으면 기본 분석 수행
            logger.warning("⚠️ AI API 키가 설정되지 않아 기본 분석 모드 사용")
            logger.warning("환경 변수 OPENAI_API_KEY 또는 GEMINI_API_KEY를 설정해주세요.")
            if progress_tracker:
                await progress_tracker.update(100, "AI API 키 미설정 - 기본 분석 모드")
            result = _analyze_basic(target_keyword, target_type, additional_context, start_date, end_date)
        
        logger.info(f"✅ 타겟 분석 완료: {target_keyword}")
        
        # 결과 정규화 (분석 유형별 표준화된 구조로 변환)
        try:
            normalized_result = normalize_analysis_result(result, target_type)
            normalized_result = ensure_result_structure(normalized_result, target_type)
            logger.info(f"✅ 결과 정규화 완료: {target_type}")
            return normalized_result
        except Exception as e:
            logger.warning(f"⚠️ 결과 정규화 실패 (원본 결과 반환): {e}")
            # 정규화 실패해도 원본 결과는 반환
            return ensure_result_structure(result, target_type)
        
    except ValueError as ve:
        # API 키 관련 오류는 그대로 전파
        logger.error(f"❌ API 키 오류: {ve}")
        raise
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ 타겟 분석 중 치명적 오류: {type(e).__name__}: {e}")
        # 프로덕션에서는 상세 스택 트레이스 제한 (보안)
        if not IS_VERCEL:
            import traceback
            logger.error(f"상세 스택 트레이스:\n{traceback.format_exc()}")
        else:
            logger.error("상세 오류 정보는 서버 로그에서만 확인 가능합니다.")
        logger.error("=" * 60)
        # 예외 발생 시에도 기본 분석 결과라도 반환
        logger.warning("⚠️ 기본 분석 모드로 fallback 시도")
        try:
            return _analyze_basic(target_keyword, target_type, additional_context, start_date, end_date)
        except Exception as e2:
            logger.error(f"❌ 기본 분석 모드도 실패: {e2}")
            raise


async def _analyze_with_gemini(
    target_keyword: str,
    target_type: str,
    additional_context: Optional[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    progress_tracker: Optional[ProgressTracker] = None
) -> Dict[str, Any]:
    """Gemini API를 사용한 분석"""
    try:
        import asyncio
        
        # API 키 확인 (환경 변수에서 직접 읽기 - Vercel 호환성)
        # 여러 소스에서 API 키 확인 (우선순위: 환경 변수 > Settings)
        api_key = get_api_key_safely('GEMINI_API_KEY')
        
        if not api_key:
            logger.error("GEMINI_API_KEY 미설정")
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
        
        if settings.LOG_LEVEL == "DEBUG":
            logger.debug("=" * 60)
            logger.debug("🚀 Gemini API 호출 시작")
            logger.debug(f"API 키: ✅ 설정됨")
            logger.debug(f"모델: {getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash')}")
            logger.debug("=" * 60)
        else:
            logger.info("Gemini API 호출 시작")
        
        # 프롬프트 생성 및 최적화 (토큰 최적화 강화)
        additional_context_optimized = optimize_additional_context(additional_context, max_length=300)
        prompt = _build_analysis_prompt(target_keyword, target_type, additional_context_optimized, start_date, end_date)
        
        # 토큰 최적화 적용 (설정 파일에서 값 가져오기)
        prompt = optimize_prompt(prompt, max_length=getattr(settings, 'PROMPT_MAX_LENGTH', 4000))
        prompt_tokens = estimate_tokens(prompt)
        
        # 모델 설정 (기본값: gemini-2.5-flash)
        model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash')
        logger.info(f"Gemini API 클라이언트 초기화 중... (모델: {model_name})")
        logger.info(f"토큰 최적화: 프롬프트 {prompt_tokens} 토큰, 길이: {len(prompt)} 문자")
        
        # 새로운 Gemini API 방식 시도 (from google import genai)
        try:
            from google import genai
            
            # API 키 설정 (보안 유틸리티 사용)
            api_key = get_api_key_safely('GEMINI_API_KEY')
            if api_key:
                client = genai.Client(api_key=api_key)
            else:
                # 환경 변수에서 자동으로 가져오기
                client = genai.Client()
            
            # 시스템 메시지와 프롬프트 결합 (이미 간소화됨)
            system_message = _build_system_message(target_type)
            full_prompt = f"{system_message}\n\n{prompt}\n\nJSON only."
            
            # 토큰 수 계산 및 max_tokens 설정 (출력 토큰 제한)
            full_prompt_tokens = estimate_tokens(full_prompt)
            max_output_tokens = min(get_max_tokens_for_model(model_name, full_prompt_tokens), getattr(settings, 'MAX_OUTPUT_TOKENS', 3000))
            
            # API 호출 (비동기 실행을 위해 run_in_executor 사용)
            if settings.LOG_LEVEL == "DEBUG":
                logger.debug("=" * 60)
                logger.debug("📡 Gemini API 요청 전송 중...")
                logger.debug(f"모델: {model_name}")
                logger.debug(f"프롬프트 길이: {len(full_prompt)} 문자")
                logger.debug(f"프롬프트 토큰 추정: {full_prompt_tokens}")
                logger.debug(f"최대 출력 토큰: {max_output_tokens}")
                logger.debug("=" * 60)
            else:
                logger.info(f"Gemini API 요청 전송 중... (모델: {model_name})")
            try:
                response = await generate_content_with_fallback(
                    client=client,
                    model=model_name,
                    contents=full_prompt,
                    config={
                        "response_mime_type": "application/json",
                        "max_output_tokens": max_output_tokens,
                        "temperature": 0.5,
                    },
                    logger=logger,
                )
                if settings.LOG_LEVEL == "DEBUG":
                    logger.debug("=" * 60)
                    logger.debug("✅ Gemini API 응답 수신 완료")
                    logger.debug("=" * 60)
                else:
                    logger.info("Gemini API 응답 수신 완료")
            except Exception as e:
                logger.error("=" * 60)
                logger.error(f"❌ Gemini API 호출 실패: {type(e).__name__}: {e}")
                # 프로덕션에서는 상세 스택 트레이스 제한 (보안)
                if not IS_VERCEL:
                    import traceback
                    logger.error(f"상세 스택 트레이스:\n{traceback.format_exc()}")
                else:
                    logger.error("상세 오류 정보는 서버 로그에서만 확인 가능합니다.")
                logger.error("=" * 60)
                raise ValueError(f"Gemini API 호출 실패: {str(e)}")
            
            # 응답 파싱
            result_text = response.text if hasattr(response, 'text') else str(response)
            logger.info(f"Gemini 응답 길이: {len(result_text)} 문자")
            
        except ImportError:
            # 새로운 방식이 없으면 기존 방식 시도
            import google.generativeai as genai_old
            
            api_key_old = get_api_key_safely('GEMINI_API_KEY')
            if not api_key_old:
                raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
            genai_old.configure(api_key=api_key_old)
            
            # 시스템 메시지와 프롬프트 결합 (최적화)
            system_message = _build_system_message(target_type)
            full_prompt = f"{system_message}\n\n{prompt}\n\nJSON only."
            
            # 토큰 수 계산 및 max_tokens 설정 (출력 토큰 제한)
            full_prompt_tokens = estimate_tokens(full_prompt)
            max_output_tokens = min(get_max_tokens_for_model(model_name, full_prompt_tokens), getattr(settings, 'MAX_OUTPUT_TOKENS', 3000))
            
            # API 호출 (비동기 실행을 위해 run_in_executor 사용)
            loop = asyncio.get_event_loop()
            response = None
            last_error = None
            for candidate in build_model_candidates(model_name):
                try:
                    if candidate != model_name:
                        logger.warning(f"GEMINI_MODEL fallback 사용: {candidate}")
                    model = genai_old.GenerativeModel(candidate)
                    # JSON 응답 강제 시도 (기존 API 방식)
                    # google.generativeai에서는 generation_config 사용
                    try:
                        if hasattr(genai_old, 'types') and hasattr(genai_old.types, 'GenerationConfig'):
                            gen_config = genai_old.types.GenerationConfig(
                                response_mime_type="application/json",
                                max_output_tokens=max_output_tokens,
                                temperature=0.5,
                            )
                        else:
                            gen_config = {
                                "response_mime_type": "application/json",
                                "max_output_tokens": max_output_tokens,
                                "temperature": 0.5,
                            }
                        response = await loop.run_in_executor(
                            None,
                            lambda: model.generate_content(
                                full_prompt,
                                generation_config=gen_config,
                            ),
                        )
                    except (AttributeError, TypeError):
                        response = await loop.run_in_executor(
                            None,
                            lambda: model.generate_content(
                                full_prompt,
                                generation_config={
                                    "response_mime_type": "application/json",
                                    "max_output_tokens": max_output_tokens,
                                    "temperature": 0.5,
                                },
                            ),
                        )
                    logger.info("✅ JSON 모드로 Gemini API 응답 수신 완료")
                    break
                except Exception as e:
                    last_error = e
                    if not is_model_not_found_error(e):
                        raise
                    continue
            if response is None:
                logger.error("=" * 60)
                logger.error(f"❌ Gemini API 호출 실패: {last_error}")
                logger.error("=" * 60)
                raise ValueError(f"Gemini API 호출 실패: {str(last_error)}")
            
            # 응답 파싱
            result_text = response.text if hasattr(response, 'text') else str(response)
            logger.info(f"Gemini 응답 길이: {len(result_text)} 문자 (기존 방식)")
        
        if progress_tracker:
            await progress_tracker.update(80, "AI 응답 수신 완료, 결과 파싱 중...")
        
        # JSON 형식으로 파싱 시도
        if not result_text:
            raise ValueError("Gemini API 응답이 비어있습니다.")
        
        # 강화된 JSON 파싱 사용
        try:
            result = parse_json_with_fallback(result_text)
            logger.info("✅ JSON 파싱 성공 (강화된 파서 사용)")
        except ValueError as e:
            logger.error(f"JSON 파싱 최종 실패: {e}")
            logger.error(f"원본 텍스트 (처음 500자): {result_text[:500] if len(result_text) > 500 else result_text}")
            logger.error(f"원본 텍스트 (마지막 500자): {result_text[-500:] if len(result_text) > 500 else result_text}")
            
            # 최소한의 구조라도 반환
            result = {
                "executive_summary": f"{target_keyword}에 대한 {target_type} 분석을 수행했습니다. (JSON 파싱 실패로 기본 구조만 반환)",
                "key_findings": {
                    "primary_insights": [
                        "AI 응답 파싱에 실패했습니다.",
                        "원본 응답을 확인하세요.",
                        f"오류: {str(e)[:200]}"
                    ],
                    "quantitative_metrics": {}
                },
                "detailed_analysis": {
                    "insights": {
                        "raw_response": result_text[:2000] if len(result_text) > 2000 else result_text
                    }
                },
                "strategic_recommendations": {
                    "immediate_actions": [
                        "서버 로그를 확인하여 AI 응답을 검토하세요.",
                        "프롬프트를 조정하여 JSON 형식 응답을 강제하세요."
                    ]
                },
                "target_keyword": target_keyword,
                "target_type": target_type,
                "error": "JSON 파싱 실패",
                "raw_response_length": len(result_text)
            }
        
        # 결과에 메타데이터 추가 (없는 경우에만)
        if "target_keyword" not in result:
            result["target_keyword"] = target_keyword
        if "target_type" not in result:
            result["target_type"] = target_type
        
        return result
        
    except ImportError as e:
        logger.error("=" * 60)
        logger.error(f"❌ Gemini API 패키지가 설치되지 않았습니다: {e}")
        logger.error("'pip install google-genai' 또는 'pip install google-generativeai'를 실행해주세요.")
        logger.error("=" * 60)
        raise ValueError(f"Gemini API 패키지 미설치: {e}")
    except ValueError as ve:
        # API 키 관련 오류는 그대로 전파
        raise
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ Gemini API 호출 실패: {type(e).__name__}: {e}")
        # 프로덕션에서는 상세 스택 트레이스 제한 (보안)
        if not IS_VERCEL:
            import traceback
            logger.error(f"상세 스택 트레이스:\n{traceback.format_exc()}")
        else:
            logger.error("상세 오류 정보는 서버 로그에서만 확인 가능합니다.")
        logger.error("=" * 60)
        raise ValueError(f"Gemini API 호출 실패: {str(e)}")


async def _analyze_with_openai(
    target_keyword: str,
    target_type: str,
    additional_context: Optional[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    progress_tracker: Optional[ProgressTracker] = None
) -> Dict[str, Any]:
    """OpenAI API를 사용한 분석"""
    try:
        from openai import AsyncOpenAI
        
        # API 키 확인 (환경 변수에서 직접 읽기 - Vercel 호환성)
        # 여러 소스에서 API 키 확인 (우선순위: 환경 변수 > Settings)
        api_key = get_api_key_safely('OPENAI_API_KEY')
        
        if not api_key:
            logger.error("OPENAI_API_KEY 미설정")
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        
        if settings.LOG_LEVEL == "DEBUG":
            logger.debug(f"OpenAI API 클라이언트 초기화 중... (모델: {settings.OPENAI_MODEL})")
            logger.debug(f"API 키: ✅ 설정됨")
        else:
            logger.info(f"OpenAI API 클라이언트 초기화 중... (모델: {settings.OPENAI_MODEL})")
        client = AsyncOpenAI(api_key=api_key)
        
        # 프롬프트 생성 및 최적화 (토큰 최적화 강화)
        if progress_tracker:
            await progress_tracker.update(20, "프롬프트 생성 중...")
        
        # 추가 컨텍스트 최적화 (더 짧게)
        additional_context_optimized = optimize_additional_context(additional_context, max_length=300)
        prompt = _build_analysis_prompt(target_keyword, target_type, additional_context_optimized, start_date, end_date)
        
        # 토큰 최적화 적용 (설정 파일에서 값 가져오기)
        prompt = optimize_prompt(prompt, max_length=getattr(settings, 'PROMPT_MAX_LENGTH', 4000))
        prompt_tokens = estimate_tokens(prompt)
        
        # 시스템 메시지 생성 및 최적화 (이미 간소화됨)
        system_message = _build_system_message(target_type)
        
        # 토큰 수 계산 및 max_tokens 설정
        full_prompt_tokens = estimate_tokens(system_message) + prompt_tokens
        max_output_tokens = get_max_tokens_for_model(settings.OPENAI_MODEL, full_prompt_tokens)
        
        logger.info(f"토큰 최적화: 프롬프트 {prompt_tokens} 토큰, 시스템 {estimate_tokens(system_message)} 토큰, 총 {full_prompt_tokens} 토큰")
        
        if progress_tracker:
            await progress_tracker.update(30, "OpenAI API 요청 전송 중...")
        
        # API 호출
        if settings.LOG_LEVEL == "DEBUG":
            logger.debug("=" * 60)
            logger.debug("📡 OpenAI API 요청 전송 중...")
            logger.debug(f"모델: {settings.OPENAI_MODEL}")
            logger.debug(f"프롬프트 길이: {len(prompt)} 문자")
            logger.debug(f"프롬프트 토큰 추정: {full_prompt_tokens}")
            logger.debug(f"최대 출력 토큰: {max_output_tokens}")
            logger.debug("=" * 60)
        else:
            logger.info(f"OpenAI API 요청 전송 중... (모델: {settings.OPENAI_MODEL})")
        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,  # 0.7에서 0.5로 낮춰서 더 빠르고 일관된 응답
                max_tokens=min(max_output_tokens, 4000),  # 최대 출력 토큰 제한 (4000으로 제한하여 속도 향상)
                response_format={"type": "json_object"}  # JSON 응답 강제
            )
            if settings.LOG_LEVEL == "DEBUG":
                logger.debug("=" * 60)
                logger.debug("✅ OpenAI API 응답 수신 완료")
                logger.debug(f"응답 ID: {response.id if hasattr(response, 'id') else 'N/A'}")
                logger.debug(f"사용된 토큰: {response.usage.total_tokens if hasattr(response, 'usage') else 'N/A'}")
                logger.debug("=" * 60)
            else:
                logger.info("OpenAI API 응답 수신 완료")
        except Exception as api_error:
            logger.error("=" * 60)
            logger.error(f"❌ OpenAI API 호출 중 오류 발생: {type(api_error).__name__}: {api_error}")
            # 프로덕션에서는 상세 스택 트레이스 제한 (보안)
            if not IS_VERCEL:
                import traceback
                logger.error(f"상세 스택 트레이스:\n{traceback.format_exc()}")
            else:
                logger.error("상세 오류 정보는 서버 로그에서만 확인 가능합니다.")
            logger.error("=" * 60)
            raise ValueError(f"OpenAI API 호출 실패: {str(api_error)}")
        
        result_text = response.choices[0].message.content
        
        if not result_text:
            raise ValueError("OpenAI API 응답이 비어있습니다.")
        
        logger.info(f"OpenAI 응답 길이: {len(result_text)} 문자")
        
        if progress_tracker:
            await progress_tracker.update(80, "AI 응답 수신 완료, 결과 파싱 중...")
        
        # 강화된 JSON 파싱 사용
        try:
            if isinstance(result_text, str):
                result = parse_json_with_fallback(result_text)
                if progress_tracker:
                    await progress_tracker.update(90, "JSON 파싱 완료, 결과 정리 중...")
            else:
                # 문자열이 아닌 경우
                result = {
                    "executive_summary": f"{target_keyword}에 대한 {target_type} 분석을 수행했습니다.",
                    "key_findings": {
                        "primary_insights": [
                            "AI 응답이 문자열 형식으로 반환되었습니다.",
                            "JSON 형식으로 변환할 수 없습니다."
                        ],
                        "quantitative_metrics": {}
                    },
                    "detailed_analysis": {
                        "insights": {
                            "raw_response": str(result_text)[:500]
                        }
                    },
                    "strategic_recommendations": {
                        "immediate_actions": [
                            "AI 응답 형식을 확인하세요.",
                            "JSON 형식 응답을 강제하도록 프롬프트를 수정하세요."
                        ]
                    },
                    "target_keyword": target_keyword,
                    "target_type": target_type
                }
        except ValueError as e:
            logger.error(f"JSON 파싱 최종 실패: {e}")
            # 구조화된 오류 응답 반환
            result = {
                "executive_summary": f"{target_keyword}에 대한 {target_type} 분석을 수행했습니다.",
                "key_findings": {
                    "primary_insights": [
                        "AI 응답 파싱에 실패했습니다.",
                        "원본 응답을 확인하세요."
                    ],
                    "quantitative_metrics": {}
                },
                "detailed_analysis": {
                    "insights": {
                        "raw_response": str(result_text)[:2000] if isinstance(result_text, str) else str(result_text)
                    }
                },
                "strategic_recommendations": {
                    "immediate_actions": [
                        "서버 로그를 확인하여 AI 응답을 검토하세요.",
                        "프롬프트를 조정하여 JSON 형식 응답을 강제하세요."
                    ]
                },
                "target_keyword": target_keyword,
                "target_type": target_type,
                "error": "JSON 파싱 실패"
            }
        
        # 결과에 메타데이터 추가 (없는 경우에만)
        if "target_keyword" not in result:
            result["target_keyword"] = target_keyword
        if "target_type" not in result:
            result["target_type"] = target_type
        
        return result
        
    except ImportError as ie:
        logger.error("=" * 60)
        logger.error(f"❌ OpenAI 패키지가 설치되지 않았습니다: {ie}")
        logger.error("'pip install openai'를 실행해주세요.")
        logger.error("=" * 60)
        raise ValueError(f"OpenAI 패키지 미설치: {ie}")
    except ValueError as ve:
        # API 키 관련 오류는 그대로 전파
        raise
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ OpenAI API 호출 실패: {type(e).__name__}: {e}")
        # 프로덕션에서는 상세 스택 트레이스 제한 (보안)
        if not IS_VERCEL:
            import traceback
            logger.error(f"상세 스택 트레이스:\n{traceback.format_exc()}")
        else:
            logger.error("상세 오류 정보는 서버 로그에서만 확인 가능합니다.")
        logger.error("=" * 60)
        raise ValueError(f"OpenAI API 호출 실패: {str(e)}")


def _analyze_basic(
    target_keyword: str,
    target_type: str,
    additional_context: Optional[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """기본 분석 (AI API 없이)"""
    logger.info("기본 분석 모드 사용")
    
    period_note = ""
    if start_date and end_date:
        period_note = f" (분석 기간: {start_date} ~ {end_date})"
    elif start_date:
        period_note = f" (시작일: {start_date})"
    elif end_date:
        period_note = f" (종료일: {end_date})"
    
    # MECE 구조로 기본 분석 결과 반환
    # API 키 상태 확인 (환경 변수에서 직접 확인 - Vercel 호환성)
    openai_key = get_api_key_safely('OPENAI_API_KEY')
    gemini_key = get_api_key_safely('GEMINI_API_KEY')
    
    has_openai = bool(openai_key)
    has_gemini = bool(gemini_key)
    
    api_key_status = {
        "openai_configured": has_openai,
        "gemini_configured": has_gemini,
        "message": "⚠️ AI API 키가 설정되지 않아 기본 분석 모드로 실행되었습니다."
    }
    
    if not api_key_status["openai_configured"] and not api_key_status["gemini_configured"]:
        api_key_status["message"] = "❌ OpenAI API 키와 Gemini API 키가 모두 설정되지 않았습니다. 환경 변수 OPENAI_API_KEY 또는 GEMINI_API_KEY를 설정해주세요."
    elif not api_key_status["openai_configured"]:
        api_key_status["message"] = "⚠️ OpenAI API 키가 설정되지 않았습니다. 환경 변수 OPENAI_API_KEY를 설정하면 더 정확한 분석이 가능합니다."
    elif not api_key_status["gemini_configured"]:
        api_key_status["message"] = "ℹ️ Gemini API 키가 설정되지 않았습니다. 환경 변수 GEMINI_API_KEY를 설정하면 보완 분석이 가능합니다."
    
    result = {
        "target_keyword": target_keyword,
        "target_type": target_type,
        "api_key_status": api_key_status,
        "executive_summary": f"{target_keyword}에 대한 {target_type} 분석 결과입니다.{period_note}\n\n{api_key_status['message']}\n\nAI API를 설정하면 더 상세하고 정확한 분석이 가능합니다.",
        "key_findings": {
            "primary_insights": [
                f"{target_keyword}의 주요 특징",
                f"{target_type} 관점에서의 분석",
                "추가 컨텍스트가 제공된 경우 이를 반영한 분석",
                "⚠️ 이 결과는 기본 분석 모드입니다. AI API 키를 설정하면 훨씬 더 상세한 분석을 받을 수 있습니다."
            ],
            "quantitative_metrics": {
                "estimated_volume": "AI API 필요 - OpenAI 또는 Gemini API 키를 설정해주세요",
                "competition_level": "AI API 필요 - OpenAI 또는 Gemini API 키를 설정해주세요",
                "growth_potential": "AI API 필요 - OpenAI 또는 Gemini API 키를 설정해주세요"
            }
        },
        "detailed_analysis": {
            "insights": {
                "note": api_key_status["message"],
                "setup_instructions": {
                    "openai": "환경 변수에 OPENAI_API_KEY를 설정하세요. 예: export OPENAI_API_KEY='sk-...'",
                    "gemini": "환경 변수에 GEMINI_API_KEY를 설정하세요. 예: export GEMINI_API_KEY='...'",
                    "vercel": "Vercel 배포 시 환경 변수는 Vercel 대시보드의 Settings > Environment Variables에서 설정하세요."
                }
            }
        },
        "strategic_recommendations": {
            "immediate_actions": [
                "OpenAI 또는 Gemini API 키를 환경 변수에 설정해주세요.",
                "API 키 설정 후 서버를 재시작하고 다시 분석을 시도하세요.",
                "Vercel 배포 시: Vercel 대시보드 > Settings > Environment Variables에서 설정",
                "로컬 개발 시: .env 파일에 OPENAI_API_KEY 또는 GEMINI_API_KEY 추가"
            ],
            "short_term_strategies": [
                "AI API를 통한 정량적 데이터 수집",
                "정성적 인사이트 도출",
                "기간별 트렌드 분석"
            ],
            "long_term_strategies": [
                "지속적인 데이터 모니터링",
                "트렌드 분석 및 예측",
                "자동화된 분석 파이프라인 구축"
            ]
        },
        # 하위 호환성을 위한 기존 구조도 포함
        "analysis": {
            "summary": f"{target_keyword}에 대한 {target_type} 분석 결과입니다.{period_note}",
            "key_points": [
                f"{target_keyword}의 주요 특징",
                f"{target_type} 관점에서의 분석",
                "추가 컨텍스트가 제공된 경우 이를 반영한 분석"
            ],
            "recommendations": [
                "AI API를 설정하면 더 상세한 분석이 가능합니다.",
                "OpenAI 또는 Gemini API 키를 설정해주세요."
            ]
        }
    }
    
    if additional_context:
        result["additional_context"] = additional_context
        if isinstance(result["analysis"], dict):
            result["analysis"]["context_applied"] = True
    
    if start_date or end_date:
        result["analysis"]["period"] = {
            "start_date": start_date,
            "end_date": end_date
        }
    
    return result


def _merge_analysis_results(openai_result: Dict[str, Any], gemini_result: Dict[str, Any], target_type: str) -> Dict[str, Any]:
    """
    OpenAI와 Gemini 분석 결과를 통합합니다.
    OpenAI 결과를 기본으로 하고, Gemini 결과로 보완합니다.
    """
    merged = openai_result.copy()
    
    # Executive Summary 통합
    if gemini_result.get("executive_summary") and openai_result.get("executive_summary"):
        # 두 요약을 결합
        merged["executive_summary"] = (
            f"{openai_result['executive_summary']}\n\n"
            f"**Gemini 보완 분석**: {gemini_result['executive_summary']}"
        )
    elif gemini_result.get("executive_summary"):
        merged["executive_summary"] = gemini_result["executive_summary"]
    
    # Key Findings 통합
    if gemini_result.get("key_findings") and openai_result.get("key_findings"):
        merged_key_findings = openai_result["key_findings"].copy()
        
        # Primary Insights 통합 (중복 제거)
        if gemini_result["key_findings"].get("primary_insights"):
            openai_insights = set(openai_result["key_findings"].get("primary_insights", []))
            gemini_insights = gemini_result["key_findings"]["primary_insights"]
            
            # 새로운 인사이트만 추가
            for insight in gemini_insights:
                if insight not in openai_insights:
                    merged_key_findings.setdefault("primary_insights", []).append(insight)
        
        # Quantitative Metrics 통합 (Gemini 값으로 보완)
        if gemini_result["key_findings"].get("quantitative_metrics"):
            merged_metrics = openai_result["key_findings"].get("quantitative_metrics", {}).copy()
            gemini_metrics = gemini_result["key_findings"]["quantitative_metrics"]
            for key, value in gemini_metrics.items():
                if not merged_metrics.get(key) or merged_metrics[key] == "AI API 필요":
                    merged_metrics[key] = value
            merged_key_findings["quantitative_metrics"] = merged_metrics
        
        merged["key_findings"] = merged_key_findings
    elif gemini_result.get("key_findings"):
        merged["key_findings"] = gemini_result["key_findings"]
    
    # Detailed Analysis 통합
    if gemini_result.get("detailed_analysis") and openai_result.get("detailed_analysis"):
        merged_detailed = openai_result["detailed_analysis"].copy()
        gemini_detailed = gemini_result["detailed_analysis"]
        
        # Insights 통합
        if gemini_detailed.get("insights") and merged_detailed.get("insights"):
            merged_insights = merged_detailed["insights"].copy()
            gemini_insights = gemini_detailed["insights"]
            
            # 각 인사이트 섹션 통합
            for key, value in gemini_insights.items():
                if key not in merged_insights or not merged_insights[key]:
                    merged_insights[key] = value
                elif isinstance(value, dict) and isinstance(merged_insights[key], dict):
                    # 딕셔너리인 경우 병합
                    merged_insights[key] = {**merged_insights[key], **value}
                elif isinstance(value, list) and isinstance(merged_insights[key], list):
                    # 리스트인 경우 중복 제거 후 병합
                    existing = set(str(item) for item in merged_insights[key])
                    for item in value:
                        if str(item) not in existing:
                            merged_insights[key].append(item)
            
            merged_detailed["insights"] = merged_insights
        
        merged["detailed_analysis"] = merged_detailed
    elif gemini_result.get("detailed_analysis"):
        merged["detailed_analysis"] = gemini_result["detailed_analysis"]
    
    # Strategic Recommendations 통합
    if gemini_result.get("strategic_recommendations") and openai_result.get("strategic_recommendations"):
        merged_strategic = openai_result["strategic_recommendations"].copy()
        gemini_strategic = gemini_result["strategic_recommendations"]
        
        # 각 전략 섹션 통합
        for key in ["immediate_actions", "short_term_strategies", "long_term_strategies"]:
            if gemini_strategic.get(key):
                openai_list = merged_strategic.get(key, [])
                gemini_list = gemini_strategic[key]
                
                # 중복 제거 후 병합
                existing = set(str(item) for item in openai_list)
                for item in gemini_list:
                    if str(item) not in existing:
                        openai_list.append(item)
                
                merged_strategic[key] = openai_list
        
        # Success Metrics는 Gemini 값으로 보완
        if gemini_strategic.get("success_metrics") and not merged_strategic.get("success_metrics"):
            merged_strategic["success_metrics"] = gemini_strategic["success_metrics"]
        
        merged["strategic_recommendations"] = merged_strategic
    elif gemini_result.get("strategic_recommendations"):
        merged["strategic_recommendations"] = gemini_result["strategic_recommendations"]
    
    # 메타데이터 추가
    merged["analysis_sources"] = ["openai", "gemini"]
    if "target_keyword" not in merged:
        merged["target_keyword"] = openai_result.get("target_keyword") or gemini_result.get("target_keyword")
    if "target_type" not in merged:
        merged["target_type"] = openai_result.get("target_type") or gemini_result.get("target_type")
    
    return merged


def _build_system_message(target_type: str) -> str:
    """시스템 메시지 생성 (프롬프트 엔지니어링 개선)"""
    base_instruction = """You are an expert analyst. Follow these rules strictly:
1. Respond ONLY in valid JSON format (no markdown code blocks)
2. Apply MECE principle: Mutually Exclusive, Collectively Exhaustive
3. Be data-driven: provide evidence, metrics, and sources
4. Be actionable: include specific, implementable recommendations
5. Use Chain-of-Thought reasoning: show your analysis process
6. Ensure accuracy: distinguish facts from estimates clearly"""
    
    if target_type == "audience":
        return f"""Senior digital marketer and customer behavior consultant (15+ years). 
Expertise: audience segmentation, persona development, customer journey mapping, behavioral psychology.
{base_instruction}
Deliver: comprehensive audience analysis with consulting-grade quality, MECE structure, and actionable insights."""
    elif target_type == "keyword":
        return f"""Senior SEO and digital marketing strategist (15+ years).
Expertise: keyword research, search intent analysis, competitive analysis, content strategy.
{base_instruction}
Deliver: comprehensive keyword analysis with search volume estimates, competition analysis, and strategic recommendations."""
    else:  # comprehensive
        return f"""Senior strategic marketing consultant (15+ years).
Expertise: integrated marketing strategy, market research, competitive intelligence, growth strategy.
{base_instruction}
Deliver: comprehensive analysis combining keyword and audience insights with strategic recommendations and execution roadmap."""


def _build_analysis_prompt(
    target_keyword: str,
    target_type: str,
    additional_context: Optional[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> str:
    """분석 프롬프트 생성"""
    
    # 기간 정보 추가 (토큰 최적화)
    period_info = ""
    period_instruction = ""
    if start_date and end_date:
        period_info = f"Period: {start_date} ~ {end_date}"
        period_instruction = f"Analyze trends, changes, and patterns during {start_date} to {end_date}. Include time-series changes, seasonality, events, and market trends."
    elif start_date:
        period_info = f"Start: {start_date}"
        period_instruction = f"Analyze trends and changes after {start_date}. Include time-series changes and market trends."
    elif end_date:
        period_info = f"End: {end_date}"
        period_instruction = f"Analyze data up to {end_date}. Include time-series changes and market trends."
    
    # 오디언스 분석에 특화된 프롬프트 (상세 컨설팅 보고서 형식)
    if target_type == "audience":
        period_display = ""
        if start_date and end_date:
            period_display = f"{start_date}–{end_date}"
        elif start_date:
            period_display = f"{start_date}~"
        elif end_date:
            period_display = f"~{end_date}"
        
        prompt = f"""# [오디언스 분석 보고서] {target_keyword} | 기간: {period_display} | 분석 유형: #2 오디언스 분석(타겟/페르소나)

## 역할 및 전문성
당신은 "디지털 마케터 및 온라인 고객 행동, 마케팅 컨설턴트 업무를 15년 이상 수행한 시니어 마케터"입니다.
전문 분야: 고객 세그먼테이션, 페르소나 개발, 고객 여정 맵핑, 행동 심리학, 데이터 기반 마케팅 전략

## 분석 방법론
아래 입력값을 바탕으로, 해당 기간의 주요 데이터(뉴스/웹/커뮤니티/리뷰/소셜/검색 의도 등)를 '크롤링하여 확보한 것처럼' 폭넓게 리서치하고, 컨설팅 업체 보고서 수준으로 MECE 구조로 오디언스 분석 결과를 작성하세요.

## 데이터 처리 원칙
- 가능한 경우: 최신·관련성 높은 공개 자료를 근거로 분석을 구성하고,
- 불가한 경우: "추정/가정"과 "검증 필요"를 명확히 표기하되, 보고서 품질(논리·구조·실행안)은 유지하세요.
- 모든 주장에는 근거(출처) 또는 산출 방법을 붙이세요.
- Chain-of-Thought: 분석 과정을 단계별로 명시하세요 (데이터 수집 → 패턴 식별 → 인사이트 도출 → 전략 제안)

[입력값]
- 분석 키워드: {target_keyword}
- 분석 기간: {period_display}
- 언어/시장: KR, Korea
"""
        if additional_context:
            prompt += f"- 추가 컨텍스트: {additional_context}\n"
        
        prompt += """
[리서치·데이터 수집 지침(오디언스 관점)]
1) "누가(Who) / 왜(Why) / 어디서(Where) / 어떻게(How)" 프레임으로 데이터를 분류.
2) 커뮤니티/리뷰/댓글/질문글에서 "불만·욕구·장벽·표현(voice of customer)"을 추출.
3) 검색 의도(문제 인식→비교→결정)의 여정 단계별 질문을 도출.
4) 기간 내 사회/정책/기술 변화가 타겟 행동에 미친 영향을 식별.

[분석 범위(반드시 포함)]
A. 타겟 세그먼테이션(고객 분류)
- 세그먼트 기준: (1) 니즈/문제 (2) 구매 동기 (3) 사용 맥락 (4) 예산/민감도 (5) 채널 선호
- 세그먼트별 크기 추정(정성/정량 가능 범위), 성장성, 우선순위

B. 고객 여정 & 의사결정 구조
- Awareness/Consideration/Conversion/Retention 단계별:
  - 핵심 질문(FAQ)
  - 정보 소스(뉴스/유튜브/리뷰/지인/커뮤니티 등)
  - 전환 장벽(리스크·불신·가격·시간·복잡성)
  - 설득 레버(증거·사례·보증·사회적 증거)

C. 페르소나 3~5개(필수)
각 페르소나는 아래 템플릿으로 고정 출력:
- 페르소나 명: 
- 한 줄 요약:
- 배경(직업/라이프스타일/디지털 리터러시):
- 목표/성공 기준:
- Pain Points(상위 3~5개):
- Trigger(행동 촉발 요인):
- Objection(반대/우려):
- 사용 채널 & 콘텐츠 소비 습관:
- 선호 메시지 톤:
- 전환에 필요한 증거(Proof):
- 추천 콘텐츠/오퍼:
- 금지 메시지(브랜드 세이프티 관점):

D. 채널·콘텐츠 전략(페르소나 매핑)
- 페르소나 × 채널 매트릭스(어떤 채널에서 어떤 메시지/포맷이 유효한가)
- 콘텐츠 기획: 토픽 클러스터(문제/해결/비교/사례/FAQ) + 포맷(숏폼/롱폼/리포트/툴)
- 운영 방향: 에디토리얼 캘린더(주간/월간), 리퍼포징(원본→파생), 커뮤니티 운영(가이드/모더레이션)

E. 마케팅 거버넌스(전략 운영 체계)
- 콘텐츠 승인/법무·브랜드 검수 프로세스
- 데이터·측정 거버넌스: KPI 정의, 이벤트 설계, 리포팅 주기
- 리스크 대응: 이슈 발생 시 커뮤니케이션 룰, FAQ/템플릿, escalation 체계

[보고서 출력 포맷(반드시 준수: MECE/프로페셔널)]
1. Executive Summary (핵심 결론 5~10문장)
2. 분석 개요
   2.1 목적/범위
   2.2 기간/시장/소스
   2.3 방법론 + 한계/가정
3. Key Insights (핵심 인사이트 5~7개: 근거→해석→시사점)
4. 오디언스 상세 분석
   4.1 세그먼테이션
   4.2 고객 여정 & 의사결정
   4.3 페르소나(3~5개)
5. 전략 제안
   5.1 페르소나 기반 채널 운영 전략
   5.2 콘텐츠 기획/제작/운영 전략
   5.3 KPI/측정 프레임워크
6. 실행 로드맵
   - 30/60/90일 계획(우선순위, 산출물, R&R)
7. 리스크 & 거버넌스
   - 브랜드 세이프티, FAQ 템플릿, 운영 규정
8. 부록
   8.1 메시지 뱅크(페르소나별 훅/헤드라인/CTA)
   8.2 참고문헌(레퍼런스) — 논문 참고문헌 스타일로 출력

[참고문헌(레퍼런스) 출력 규칙]
- 최소 8개 이상
- 형식 예시:
  [1] Publisher/Org. (Year, Month Day). Title. Source/Website.
  [2] Author. (Year). Title. Journal/Report. Publisher.
- 링크는 가능한 경우 포함하되, 문장 흐름을 깨지 않게 부록에만 정리.

[품질 규칙]
- MECE 유지(세그먼트/페르소나 중복 최소화)
- 추정은 추정으로 표시(검증 체크리스트 포함)
- 실행안 중심(채널/콘텐츠/운영/거버넌스까지 연결)
- 문서에 그대로 붙여넣기 좋은 서식(번호/계층/불릿) 유지
- Chain-of-Thought: 각 결론에 도달한 분석 과정을 명시
- Evidence-based: 모든 주장에 근거와 출처 제공

[분석 프로세스]
1. 데이터 수집: 관련 데이터 소스 식별 및 수집
2. 패턴 분석: 데이터에서 패턴, 트렌드, 이상 징후 식별
3. 인사이트 도출: 패턴에서 비즈니스 인사이트 추출
4. 전략 제안: 인사이트를 바탕으로 실행 가능한 전략 수립
5. 검증: 제안된 전략의 실현 가능성 및 효과 검증

이제 위 포맷으로 보고서를 JSON 형식으로 작성하세요. 반드시 유효한 JSON 형식으로만 응답하세요.

{
  "executive_summary": "핵심 결론 5-10문장 (주요 발견사항, 인사이트, 전략적 권장사항)",
  "analysis_overview": {
    "purpose_scope": "분석 목적 및 범위",
    "period_market_sources": "기간/시장/데이터 소스",
    "methodology": {
      "research_approach": "방법론",
      "limitations_assumptions": "한계 및 가정 사항"
    }
  },
  "key_insights": [
    {
      "insight": "핵심 인사이트 1",
      "evidence": "근거",
      "interpretation": "해석",
      "implication": "시사점"
    }
  ],
  "detailed_audience_analysis": {
    "segmentation": {
      "segmentation_criteria": {
        "needs_problems": "니즈/문제 기준",
        "purchase_motivation": "구매 동기 기준",
        "usage_context": "사용 맥락 기준",
        "budget_sensitivity": "예산/민감도 기준",
        "channel_preference": "채널 선호 기준"
      },
      "segments": [
        {
          "segment_name": "세그먼트명",
          "size_estimate": "크기 추정 (정성/정량)",
          "growth_potential": "성장성",
          "priority": "우선순위"
        }
      ]
    },
    "customer_journey_decision": {
      "awareness": {
        "key_questions": ["Awareness 단계 핵심 질문 (FAQ)"],
        "information_sources": ["정보 소스 (뉴스/유튜브/리뷰/지인/커뮤니티 등)"],
        "conversion_barriers": ["전환 장벽 (리스크·불신·가격·시간·복잡성)"],
        "persuasion_levers": ["설득 레버 (증거·사례·보증·사회적 증거)"]
      },
      "consideration": {
        "key_questions": ["Consideration 단계 핵심 질문"],
        "information_sources": ["정보 소스"],
        "conversion_barriers": ["전환 장벽"],
        "persuasion_levers": ["설득 레버"]
      },
      "conversion": {
        "key_questions": ["Conversion 단계 핵심 질문"],
        "information_sources": ["정보 소스"],
        "conversion_barriers": ["전환 장벽"],
        "persuasion_levers": ["설득 레버"]
      },
      "retention": {
        "key_questions": ["Retention 단계 핵심 질문"],
        "information_sources": ["정보 소스"],
        "conversion_barriers": ["전환 장벽"],
        "persuasion_levers": ["설득 레버"]
      }
    },
    "personas": [
      {
        "persona_name": "페르소나 명",
        "one_line_summary": "한 줄 요약",
        "background": {
          "occupation": "직업",
          "lifestyle": "라이프스타일",
          "digital_literacy": "디지털 리터러시"
        },
        "goals_success_criteria": "목표/성공 기준",
        "pain_points": ["Pain Point 1", "Pain Point 2", "Pain Point 3", "Pain Point 4", "Pain Point 5"],
        "trigger": "행동 촉발 요인",
        "objection": "반대/우려",
        "channels_content_habits": "사용 채널 & 콘텐츠 소비 습관",
        "preferred_message_tone": "선호 메시지 톤",
        "conversion_proof_needed": "전환에 필요한 증거(Proof)",
        "recommended_content_offer": "추천 콘텐츠/오퍼",
        "prohibited_messages": "금지 메시지(브랜드 세이프티 관점)"
      }
    ]
  },
  "strategic_recommendations": {
    "persona_based_channel_strategy": {
      "persona_channel_matrix": [
        {
          "persona_name": "페르소나명",
          "channels": [
            {
              "channel": "채널명",
              "message": "메시지",
              "format": "포맷",
              "effectiveness": "유효성"
            }
          ]
        }
      ]
    },
    "content_strategy": {
      "topic_clusters": {
        "problem": ["문제 관련 토픽"],
        "solution": ["해결 관련 토픽"],
        "comparison": ["비교 관련 토픽"],
        "case_study": ["사례 관련 토픽"],
        "faq": ["FAQ 관련 토픽"]
      },
      "content_formats": {
        "short_form": "숏폼 전략",
        "long_form": "롱폼 전략",
        "report": "리포트 전략",
        "tool": "툴 전략"
      },
      "operational_direction": {
        "editorial_calendar": "에디토리얼 캘린더 (주간/월간)",
        "repurposing": "리퍼포징 전략 (원본→파생)",
        "community_management": "커뮤니티 운영 (가이드/모더레이션)"
      }
    },
    "kpi_measurement_framework": {
      "kpi_definitions": ["KPI 정의"],
      "event_design": "이벤트 설계",
      "reporting_cycle": "리포팅 주기"
    }
  },
  "execution_roadmap": {
    "day_30": {
      "priorities": ["30일 우선순위"],
      "deliverables": ["산출물"],
      "roles_responsibilities": "담당 역할 R&R"
    },
    "day_60": {
      "priorities": ["60일 우선순위"],
      "deliverables": ["산출물"],
      "roles_responsibilities": "담당 역할 R&R"
    },
    "day_90": {
      "priorities": ["90일 우선순위"],
      "deliverables": ["산출물"],
      "roles_responsibilities": "담당 역할 R&R"
    }
  },
  "risk_governance": {
    "brand_safety": {
      "content_approval_process": "콘텐츠 승인/법무·브랜드 검수 프로세스",
      "risk_response_rules": "리스크 대응 룰",
      "escalation_system": "escalation 체계"
    },
    "faq_templates": ["FAQ 템플릿"],
    "operational_regulations": "운영 규정"
  },
  "appendix": {
    "message_bank": [
      {
        "persona_name": "페르소나명",
        "hooks": ["훅 메시지"],
        "headlines": ["헤드라인"],
        "ctas": ["CTA"]
      }
    ],
    "references": [
      {
        "id": 1,
        "citation": "Publisher/Org. (Year, Month Day). Title. Source/Website.",
        "url": "링크 (가능한 경우)"
      }
    ]
  }
}
"""
    elif target_type == "keyword":
        # 키워드 분석 프롬프트 (상세 컨설팅 보고서 형식)
        period_display = ""
        if start_date and end_date:
            period_display = f"{start_date}–{end_date}"
        elif start_date:
            period_display = f"{start_date}~"
        elif end_date:
            period_display = f"~{end_date}"
        
        prompt = f"""# [키워드 분석 보고서] {target_keyword} | 기간: {period_display} | 분석 유형: #1 키워드 분석

## 역할 및 전문성
당신은 "SEO 및 디지털 마케팅 전략가로서 15년 이상의 경력을 가진 시니어 마케터"입니다.
전문 분야: 키워드 리서치, 검색 의도 분석, 경쟁 분석, 콘텐츠 전략, SEO 최적화

## 분석 방법론
아래 입력값을 바탕으로, 해당 기간의 주요 데이터(뉴스/웹/커뮤니티/검색 트렌드 등)를 '크롤링하여 확보한 것처럼' 폭넓게 리서치하고, 컨설팅 업체 보고서 수준으로 MECE 구조로 분석 결과를 작성하세요.

## 데이터 처리 원칙
- 가능한 경우: 최신·관련성 높은 공개 자료를 근거로 분석을 구성하고,
- 불가한 경우: "추정/가정"과 "검증 필요"를 명확히 표기하되, 보고서 품질(논리·구조·실행안)은 유지하세요.
- 모든 수치/주장에는 근거(출처) 또는 산출 방법을 붙이세요.
- Chain-of-Thought: 검색 트렌드 분석 → 경쟁도 평가 → 기회 식별 → 전략 제안의 과정을 명시하세요.

[입력값]
- 분석 키워드: {target_keyword}
- 분석 기간: {period_display}
- 언어/시장: KR, Korea
"""
        if additional_context:
            prompt += f"- 추가 컨텍스트: {additional_context}\n"
        
        prompt += """
[리서치·데이터 수집 지침(보고서 내 반영)]
1) 데이터 소스 범주를 분리해 수집 관점 정리(뉴스/공식 문서/트렌드 도구/커뮤니티/블로그/리뷰/동영상/소셜).
2) 기간 내 이슈/사건/제품출시/정책 변화 등 "스파이크 요인"을 식별.
3) 키워드 의미(정의/의도/동음이의/브랜드 vs 일반명사)를 먼저 정리 후 분석.
4) 가능한 경우, 지역/언어에 따른 SERP 차이와 플랫폼별 추천/노출 맥락을 반영.

[분석 범위(반드시 포함)]
A. 키워드 트렌드 분석
- 기간 내 관심도 변화(상승/하락/급등 구간) 요약
- 급등 원인 Top 3 가설 + 검증 포인트
- 시즌성/이벤트성/뉴스성 분리

B. 연관 키워드/토픽 클러스터
- (1) 동의어/유사어 (2) 문제-해결형 (3) 비교/대안형 (4) 구매/전환형 (5) 브랜드/제품형
- 클러스터별 검색 의도(Informational/Commercial/Transactional/Navigational)
- 각 클러스터별 "추천 콘텐츠 포맷" (가이드/리스트/케이스/FAQ/툴/체크리스트)

C. 감성 분석(긍정/부정/중립)
- 데이터 근거(뉴스 헤드라인/커뮤니티 반응/리뷰/댓글 등) 기반으로 감성 분포 추정
- 긍정·부정의 주요 원인 키워드(Drivers) 및 대표 문장(요약 재구성)
- 리스크(부정 이슈) 조기 경보 키워드 세트 제안

D. 경쟁/대체 키워드 & 차별화 포인트
- 경쟁 주체(브랜드/카테고리/솔루션) 후보군 도출
- 비교 구도(가격/성능/신뢰/편의/지원)에서 우리 포지셔닝 방향 제시

E. 실행 시사점(디지털 마케팅 관점)
- 채널 운영: 어떤 채널에서 어떤 키워드 클러스터를 다뤄야 하는지(우선순위)
- 콘텐츠 기획/제작: 제목/후킹/구조(목차)/FAQ/AEO(답변형)/GEO(지역 맥락) 반영
- 운영 방향: 에디토리얼 캘린더 가이드(주간/월간), 실험 설계(A/B), 리퍼포징 전략
- 마케팅 거버넌스: 승인/검수 프로세스, 브랜드 세이프티, 리스크 대응 룰(가이드라인)

[보고서 출력 포맷(반드시 준수: MECE/프로페셔널)]
1. Executive Summary (5~10문장)
2. 분석 개요
   2.1 목적/범위
   2.2 기간/시장/소스
   2.3 방법론(크롤링/리서치/분석 로직) + 한계/가정
3. Key Findings (핵심 발견 5~7개, 각 발견마다 "근거→해석→의미")
4. 상세 분석
   4.1 트렌드
   4.2 연관 키워드/클러스터
   4.3 감성 분석
   4.4 경쟁/대체 키워드
5. 전략적 시사점
   5.1 채널 운영 제안
   5.2 콘텐츠 전략(TOFU/MOFU/BOFU 매핑)
   5.3 KPI/측정(정의/대시보드 항목/주기)
6. 실행 로드맵
   - 30/60/90일 계획(우선순위, 산출물, 담당 역할 R&R)
7. 리스크 & 대응
   - 부정 이슈 시나리오, Q&A, 브랜드 세이프티 체크리스트
8. 부록
   8.1 키워드 리스트(클러스터별)
   8.2 참고문헌(레퍼런스) — 논문 참고문헌 스타일로 출력

[참고문헌(레퍼런스) 출력 규칙]
- 최소 8개 이상
- 형식 예시:
  [1] Publisher/Org. (Year, Month Day). Title. Source/Website.
  [2] Author. (Year). Title. Journal/Report. Publisher.
- 링크는 가능한 경우 포함하되, 문장 흐름을 깨지 않게 부록에만 정리.

[품질 규칙]
- 과장 금지: 추정은 추정이라고 표시
- 중복 금지: 항목 간 MECE 유지
- 실행 중심: "그래서 무엇을 할 것인가"가 각 섹션에 포함
- 문서에 그대로 붙여넣기 좋은 서식(번호/계층/불릿) 유지

이제 위 포맷으로 보고서를 JSON 형식으로 작성하세요. 반드시 유효한 JSON 형식으로만 응답하세요.

{
  "executive_summary": "5-10문장 요약 (핵심 발견사항, 주요 인사이트, 전략적 권장사항)",
  "analysis_overview": {
    "purpose_scope": "분석 목적 및 범위",
    "period_market_sources": "기간/시장/데이터 소스",
    "methodology": {
      "research_logic": "크롤링/리서치/분석 로직",
      "limitations_assumptions": "한계 및 가정 사항"
    }
  },
  "key_findings": [
    {
      "finding": "핵심 발견 1",
      "evidence": "근거",
      "interpretation": "해석",
      "implication": "의미"
    },
    {
      "finding": "핵심 발견 2",
      "evidence": "근거",
      "interpretation": "해석",
      "implication": "의미"
    }
  ],
  "detailed_analysis": {
    "trend_analysis": {
      "interest_change_summary": "기간 내 관심도 변화 요약 (상승/하락/급등 구간)",
      "spike_causes": [
        {
          "rank": 1,
          "hypothesis": "급등 원인 가설",
          "verification_points": "검증 포인트"
        }
      ],
      "seasonality_event_news": "시즌성/이벤트성/뉴스성 분리 분석"
    },
    "related_keywords_clusters": {
      "synonyms_similar": ["동의어/유사어 키워드 리스트"],
      "problem_solution": ["문제-해결형 키워드 리스트"],
      "comparison_alternative": ["비교/대안형 키워드 리스트"],
      "purchase_conversion": ["구매/전환형 키워드 리스트"],
      "brand_product": ["브랜드/제품형 키워드 리스트"],
      "cluster_intent_mapping": {
        "informational": ["정보성 키워드"],
        "commercial": ["상업성 키워드"],
        "transactional": ["거래성 키워드"],
        "navigational": ["탐색성 키워드"]
      },
      "recommended_content_formats": {
        "guide": "가이드 형식 추천 키워드",
        "list": "리스트 형식 추천 키워드",
        "case_study": "케이스 스터디 형식 추천 키워드",
        "faq": "FAQ 형식 추천 키워드",
        "tool": "툴 형식 추천 키워드",
        "checklist": "체크리스트 형식 추천 키워드"
      }
    },
    "sentiment_analysis": {
      "sentiment_distribution": {
        "positive": "긍정 비율 및 근거",
        "negative": "부정 비율 및 근거",
        "neutral": "중립 비율 및 근거"
      },
      "positive_drivers": {
        "keywords": ["긍정 원인 키워드"],
        "representative_sentences": ["대표 문장"]
      },
      "negative_drivers": {
        "keywords": ["부정 원인 키워드"],
        "representative_sentences": ["대표 문장"]
      },
      "risk_early_warning_keywords": ["리스크 조기 경보 키워드 세트"]
    },
    "competition_alternative_keywords": {
      "competitors": ["경쟁 주체 후보군 (브랜드/카테고리/솔루션)"],
      "positioning_framework": {
        "price": "가격 포지셔닝",
        "performance": "성능 포지셔닝",
        "trust": "신뢰 포지셔닝",
        "convenience": "편의 포지셔닝",
        "support": "지원 포지셔닝"
      },
      "differentiation_points": ["차별화 포인트"]
    }
  },
  "strategic_implications": {
    "channel_operations": {
      "priority_channels": [
        {
          "channel": "채널명",
          "keyword_clusters": ["해당 채널에서 다룰 키워드 클러스터"],
          "priority": "우선순위"
        }
      ]
    },
    "content_strategy": {
      "tofu_mapping": {
        "keywords": ["TOFU 단계 키워드"],
        "content_types": ["콘텐츠 유형"]
      },
      "mofu_mapping": {
        "keywords": ["MOFU 단계 키워드"],
        "content_types": ["콘텐츠 유형"]
      },
      "bofu_mapping": {
        "keywords": ["BOFU 단계 키워드"],
        "content_types": ["콘텐츠 유형"]
      },
      "content_elements": {
        "title_hook": "제목/후킹 전략",
        "structure_outline": "구조(목차) 가이드",
        "faq_aeo": "FAQ/AEO(답변형) 전략",
        "geo_local": "GEO(지역 맥락) 전략"
      }
    },
    "kpi_measurement": {
      "kpi_definitions": ["KPI 정의"],
      "dashboard_items": ["대시보드 항목"],
      "measurement_cycle": "측정 주기"
    }
  },
  "execution_roadmap": {
    "day_30": {
      "priorities": ["30일 우선순위"],
      "deliverables": ["산출물"],
      "roles_responsibilities": "담당 역할 R&R"
    },
    "day_60": {
      "priorities": ["60일 우선순위"],
      "deliverables": ["산출물"],
      "roles_responsibilities": "담당 역할 R&R"
    },
    "day_90": {
      "priorities": ["90일 우선순위"],
      "deliverables": ["산출물"],
      "roles_responsibilities": "담당 역할 R&R"
    },
    "operational_direction": {
      "editorial_calendar": "에디토리얼 캘린더 가이드 (주간/월간)",
      "ab_testing": "실험 설계 (A/B)",
      "repurposing_strategy": "리퍼포징 전략"
    },
    "marketing_governance": {
      "approval_process": "승인/검수 프로세스",
      "brand_safety": "브랜드 세이프티 가이드라인",
      "risk_response_rules": "리스크 대응 룰"
    }
  },
  "risk_response": {
    "negative_issue_scenarios": ["부정 이슈 시나리오"],
    "qa": ["Q&A"],
    "brand_safety_checklist": ["브랜드 세이프티 체크리스트"]
  },
  "appendix": {
    "keyword_list_by_cluster": {
      "synonyms": ["동의어 키워드 리스트"],
      "problem_solution": ["문제-해결형 키워드 리스트"],
      "comparison": ["비교형 키워드 리스트"],
      "purchase": ["구매형 키워드 리스트"],
      "brand": ["브랜드형 키워드 리스트"]
    },
    "references": [
      {
        "id": 1,
        "citation": "Publisher/Org. (Year, Month Day). Title. Source/Website.",
        "url": "링크 (가능한 경우)"
      }
    ]
  }
}
"""
    else:  # comprehensive
        # 종합 분석 프롬프트: 키워드 분석 + 오디언스 분석 핵심 통합 (프롬프트 엔지니어링 개선)
        prompt = f"""# [종합 분석 보고서] {target_keyword} | 기간: {period_info} | 분석 유형: #3 종합 분석

## 역할 및 전문성
당신은 "통합 마케팅 전략 컨설턴트로서 15년 이상의 경력을 가진 시니어 마케터"입니다.
전문 분야: 통합 마케팅 전략, 시장 리서치, 경쟁 인텔리전스, 성장 전략, 데이터 기반 의사결정

## 분석 방법론
키워드 분석과 오디언스 분석을 통합하여 전략적 인사이트를 도출하세요.
{period_instruction}

## 통합 분석 원칙
- 키워드 기회와 오디언스 특성을 연결하여 시너지 효과 식별
- 중복 제거: 키워드와 오디언스 분석에서 중복되는 인사이트는 통합
- 전략 중심: 실행 가능한 통합 마케팅 전략 제안
- Chain-of-Thought: 키워드 분석 → 오디언스 분석 → 통합 인사이트 → 전략 제안의 과정을 명시

"""
        if additional_context:
            prompt += f"**추가 컨텍스트**: {additional_context}\n\n"
        
        prompt += """다음 JSON 구조로 응답하세요 (키워드와 오디언스 인사이트를 통합하고, 중복을 제거하며, 미래 지향적 권장사항에 집중):
{
  "executive_summary": "3-5 paragraph summary integrating keyword opportunities and audience characteristics with strategic recommendations",
  "key_findings": {
    "integrated_insights": [
      "keyword search intent aligned with audience needs",
      "audience demographics matching keyword opportunity",
      "trend convergence between search patterns and audience behavior",
      "market opportunity size and accessibility",
      "unique positioning combining keyword and audience strengths"
    ],
    "quantitative_metrics": {
      "market_size": "estimated market size combining search volume and audience reach",
      "opportunity_score": "1-100 combining keyword opportunity and audience accessibility",
      "growth_potential": "low/medium/high with reason based on trends and audience growth",
      "competition_level": "low/medium/high with reason",
      "success_probability": "low/medium/high with reason"
    }
  },
  "integrated_analysis": {
    "keyword_audience_alignment": {
      "search_intent_match": "how search intent aligns with audience needs and journey stage",
      "keyword_opportunity_for_audience": "which keywords best reach target audience",
      "audience_preferred_keywords": "keywords audience uses based on demographics and behavior",
      "content_gap_analysis": "gaps between available content and audience needs"
    },
    "core_keyword_insights": {
      "primary_search_intent": "Informational/Navigational/Transactional/Commercial",
      "key_opportunity_keywords": ["keyword1 with volume/competition", "keyword2", "keyword3", "keyword4", "keyword5"],
      "trending_keywords": ["trending1 with timing", "trending2", "trending3"],
      "search_volume_trend": "increase/decrease/stable with change rate for period"
    },
    "core_audience_insights": {
      "target_demographics": {
        "age_range": "age range",
        "gender": "gender distribution",
        "location": "regional distribution",
        "income_level": "income range",
        "expected_occupations": ["job1", "job2", "job3", "job4", "job5"]
      },
      "key_behavior_patterns": {
        "purchase_behavior": "purchase patterns and decision factors",
        "media_consumption": "preferred media and platforms",
        "online_activity": "online behavior and platforms"
      },
      "core_values_and_needs": {
        "primary_values": ["value1", "value2", "value3"],
        "main_pain_points": ["pain1", "pain2", "pain3"],
        "key_aspirations": ["aspiration1", "aspiration2", "aspiration3"]
      }
    },
    "trends_and_patterns": {
      "converging_trends": ["trend1 combining keyword and audience patterns", "trend2", "trend3", "trend4", "trend5"],
      "period_analysis": "key changes during period combining search and audience shifts",
      "future_outlook": "6-12 month forecast integrating keyword and audience trends"
    }
  },
  "forward_looking_recommendations": {
    "immediate_actions": [
      "action1 combining keyword targeting and audience messaging",
      "action2 with specific keyword and audience focus",
      "action3 with integrated approach"
    ],
    "content_strategy": {
      "recommended_topics": ["topic1 aligned with keywords and audience needs", "topic2", "topic3", "topic4", "topic5"],
      "content_format": "best content formats for target audience and keyword intent",
      "distribution_channels": ["channel1", "channel2", "channel3"]
    },
    "marketing_strategy": {
      "keyword_targeting": "priority keywords to target based on audience alignment",
      "messaging_framework": "core messages resonating with audience values and keyword intent",
      "channel_strategy": "optimal channels combining keyword opportunities and audience behavior"
    },
    "short_term_goals": [
      "goal1 (3-6 months) with keyword and audience metrics",
      "goal2 with specific targets",
      "goal3 with success criteria"
    ],
    "long_term_vision": [
      "vision1 (6+ months) integrating keyword growth and audience expansion",
      "vision2 with strategic direction",
      "vision3 with market positioning"
    ],
    "success_metrics": {
      "keyword_metrics": "target search rankings, volume, and keyword performance",
      "audience_metrics": "target audience reach, engagement, and conversion",
      "integrated_kpis": "combined metrics showing keyword-audience alignment success"
    }
  }
}
"""
    
    return prompt


def _split_into_sentences(text: str) -> list[str]:
    """텍스트를 문장 단위로 분리 (한국어/영어 지원)"""
    if not text or not text.strip():
        return []
    
    # 문장 종료 패턴: 마침표, 느낌표, 물음표 (한국어/영어/일본어/중국어)
    # 공백이나 줄바꿈이 뒤따르는 경우
    sentence_pattern = re.compile(r'([.!?。！？]\s*|\n\s*\n)')
    
    sentences = []
    last_end = 0
    
    for match in sentence_pattern.finditer(text):
        end_pos = match.end()
        sentence = text[last_end:end_pos].strip()
        if sentence:
            sentences.append(sentence)
        last_end = end_pos
    
    # 마지막 문장 처리
    if last_end < len(text):
        remaining = text[last_end:].strip()
        if remaining:
            sentences.append(remaining)
    
    # 문장이 없으면 원본 텍스트를 그대로 반환
    return sentences if sentences else [text.strip()] if text.strip() else []


async def analyze_target_stream(
    target_keyword: str,
    target_type: str = "keyword",
    additional_context: Optional[str] = None,
    use_gemini: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    progress_tracker: Optional[ProgressTracker] = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    타겟 분석을 스트리밍 방식으로 수행 (문장 단위 출력)
    
    Yields:
        Dict[str, Any]: 문장 단위 분석 결과
    """
    try:
        logger.info(f"타겟 분석 스트리밍 시작: {target_keyword} (타입: {target_type})")
        
        # API 키 확인
        openai_env = os.getenv('OPENAI_API_KEY')
        gemini_env = os.getenv('GEMINI_API_KEY')
        openai_settings = getattr(settings, 'OPENAI_API_KEY', None)
        gemini_settings = getattr(settings, 'GEMINI_API_KEY', None)
        
        openai_key = openai_env or openai_settings
        gemini_key = gemini_env or gemini_settings
        
        has_openai_key = bool(openai_key and len(openai_key.strip()) > 0)
        has_gemini_key = bool(gemini_key and len(gemini_key.strip()) > 0)
        
        if not has_openai_key and not has_gemini_key:
            # 기본 분석 모드로 스트리밍
            if progress_tracker:
                await progress_tracker.update(10, "기본 분석 모드로 진행 중...")
            yield {"type": "progress", "progress": 10, "message": "기본 분석 모드로 진행 중..."}
            
            result = _analyze_basic(target_keyword, target_type, additional_context, start_date, end_date)
            
            if progress_tracker:
                await progress_tracker.update(50, "기본 분석 결과 생성 완료")
            yield {"type": "progress", "progress": 50, "message": "기본 분석 결과 생성 완료"}
            
            # 기본 분석 결과를 문장 단위로 분리하여 스트리밍
            summary = result.get("executive_summary", "")
            if summary:
                sentences = _split_into_sentences(summary)
                for sentence in sentences:
                    if sentence.strip():
                        yield {
                            "type": "sentence",
                            "content": sentence.strip(),
                            "section": "executive_summary"
                        }
            else:
                # executive_summary가 없는 경우 기본 메시지
                yield {
                    "type": "sentence",
                    "content": f"{target_keyword}에 대한 {target_type} 분석을 수행했습니다.",
                    "section": "executive_summary"
                }
            
            if progress_tracker:
                await progress_tracker.update(100, "분석 완료")
            yield {"type": "progress", "progress": 100, "message": "분석 완료"}
            yield {"type": "complete", "data": result}
            return
        
        # OpenAI 스트리밍
        if has_openai_key:
            chunk_received = False
            async for chunk in _analyze_with_openai_stream(
                target_keyword, target_type, additional_context, start_date, end_date, progress_tracker
            ):
                chunk_received = True
                yield chunk
                if chunk.get("type") == "complete":
                    return
                if chunk.get("type") == "error":
                    return
            
            # 청크를 받지 못한 경우 (에러 처리)
            if not chunk_received:
                logger.error("OpenAI 스트리밍: 청크를 받지 못함")
                yield {
                    "type": "error",
                    "message": "OpenAI API 응답을 받지 못했습니다. API 키 및 네트워크 상태를 확인해주세요."
                }
                return
                
        # Gemini 스트리밍
        elif has_gemini_key:
            chunk_received = False
            async for chunk in _analyze_with_gemini_stream(
                target_keyword, target_type, additional_context, start_date, end_date, progress_tracker
            ):
                chunk_received = True
                yield chunk
                if chunk.get("type") == "complete":
                    return
                if chunk.get("type") == "error":
                    return
            
            # 청크를 받지 못한 경우 (에러 처리)
            if not chunk_received:
                logger.error("Gemini 스트리밍: 청크를 받지 못함")
                yield {
                    "type": "error",
                    "message": "Gemini API 응답을 받지 못했습니다. API 키 및 네트워크 상태를 확인해주세요."
                }
                return
                    
    except Exception as e:
        logger.error(f"스트리밍 분석 중 오류: {e}", exc_info=True)
        yield {
            "type": "error",
            "message": str(e)
        }


async def _analyze_with_openai_stream(
    target_keyword: str,
    target_type: str,
    additional_context: Optional[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    progress_tracker: Optional[ProgressTracker] = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """OpenAI API를 사용한 스트리밍 분석"""
    try:
        from openai import AsyncOpenAI
        
        # API 키 확인
        api_key_env = os.getenv('OPENAI_API_KEY')
        api_key_settings = getattr(settings, 'OPENAI_API_KEY', None)
        api_key = api_key_env or api_key_settings
        
        if not api_key or len(api_key.strip()) == 0:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        
        client = AsyncOpenAI(api_key=api_key)
        
        # 프롬프트 생성
        if progress_tracker:
            await progress_tracker.update(20, "프롬프트 생성 중...")
            yield {"type": "progress", "progress": 20, "message": "프롬프트 생성 중..."}
        
        additional_context_optimized = optimize_additional_context(additional_context, max_length=300)
        prompt = _build_analysis_prompt(target_keyword, target_type, additional_context_optimized, start_date, end_date)
        prompt = optimize_prompt(prompt, max_length=4000)
        
        system_message = _build_system_message(target_type)
        full_prompt_tokens = estimate_tokens(system_message) + estimate_tokens(prompt)
        max_output_tokens = get_max_tokens_for_model(settings.OPENAI_MODEL, full_prompt_tokens)
        
        if progress_tracker:
            await progress_tracker.update(30, "OpenAI API 요청 전송 중...")
            yield {"type": "progress", "progress": 30, "message": "OpenAI API 요청 전송 중..."}
        
        # 스트리밍 API 호출
        stream = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=min(max_output_tokens, 4000),
            response_format={"type": "json_object"},
            stream=True
        )
        
        accumulated_text = ""
        current_section = "executive_summary"
        buffer = ""
        
        async for chunk in stream:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta.content:
                    content = delta.content
                    accumulated_text += content
                    buffer += content
                    
                    # 버퍼가 충분히 길어지거나 문장 종료 문자가 있으면 처리
                    # 문장 단위로 분리하여 전송 (최소 길이 체크)
                    if len(buffer) > 50 or any(char in buffer for char in ['.', '!', '?', '。', '！', '？', '\n']):
                        sentences = _split_into_sentences(buffer)
                        if len(sentences) > 1:
                            # 완성된 문장들을 전송
                            for sentence in sentences[:-1]:
                                if sentence.strip():
                                    yield {
                                        "type": "sentence",
                                        "content": sentence.strip(),
                                        "section": current_section
                                    }
                            # 마지막 미완성 문장은 버퍼에 유지
                            buffer = sentences[-1]
        
        # 마지막 버퍼 처리
        if buffer.strip():
            yield {
                "type": "sentence",
                "content": buffer.strip(),
                "section": current_section
            }
        
        if progress_tracker:
            await progress_tracker.update(80, "AI 응답 수신 완료, 결과 파싱 중...")
            yield {"type": "progress", "progress": 80, "message": "AI 응답 수신 완료, 결과 파싱 중..."}
        
        # 최종 결과 파싱 및 반환
        try:
            result = parse_json_with_fallback(accumulated_text)
            if "target_keyword" not in result:
                result["target_keyword"] = target_keyword
            if "target_type" not in result:
                result["target_type"] = target_type
            
            yield {"type": "complete", "data": result}
        except Exception as e:
            logger.error(f"JSON 파싱 실패: {e}")
            yield {
                "type": "complete",
                "data": {
                    "executive_summary": accumulated_text[:500],
                    "target_keyword": target_keyword,
                    "target_type": target_type,
                    "error": "JSON 파싱 실패"
                }
            }
            
    except Exception as e:
        logger.error(f"OpenAI 스트리밍 분석 중 오류: {e}", exc_info=True)
        yield {"type": "error", "message": str(e)}


async def _analyze_with_gemini_stream(
    target_keyword: str,
    target_type: str,
    additional_context: Optional[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    progress_tracker: Optional[ProgressTracker] = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """Gemini API를 사용한 스트리밍 분석"""
    try:
        import asyncio
        
        # API 키 확인
        api_key_env = os.getenv('GEMINI_API_KEY')
        api_key_settings = getattr(settings, 'GEMINI_API_KEY', None)
        api_key = api_key_env or api_key_settings
        
        if not api_key or len(api_key.strip()) == 0:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
        
        if progress_tracker:
            await progress_tracker.update(20, "프롬프트 생성 중...")
            yield {"type": "progress", "progress": 20, "message": "프롬프트 생성 중..."}
        
        additional_context_optimized = optimize_additional_context(additional_context, max_length=300)
        prompt = _build_analysis_prompt(target_keyword, target_type, additional_context_optimized, start_date, end_date)
        prompt = optimize_prompt(prompt, max_length=4000)
        
        system_message = _build_system_message(target_type)
        full_prompt = f"{system_message}\n\n{prompt}\n\nJSON only."
        
        model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash')
        
        if progress_tracker:
            await progress_tracker.update(30, "Gemini API 요청 전송 중...")
            yield {"type": "progress", "progress": 30, "message": "Gemini API 요청 전송 중..."}
        
        # Gemini 스트리밍 (새로운 API 방식 시도)
        try:
            from google import genai
            
            client = genai.Client(api_key=api_key)
            accumulated_text = ""
            buffer = ""
            current_section = "executive_summary"
            
            response_stream = await generate_content_stream_with_fallback(
                client=client,
                model=model_name,
                contents=full_prompt,
                config={
                    "response_mime_type": "application/json",
                    "temperature": 0.5,
                },
                logger=logger,
            )
            
            # 스트리밍 응답 처리
            for chunk in response_stream:
                text = None
                if hasattr(chunk, 'text'):
                    text = chunk.text
                elif isinstance(chunk, str):
                    text = chunk
                
                if text:
                    accumulated_text += text
                    buffer += text
                    
                    # 버퍼가 충분히 길어지거나 문장 종료 문자가 있으면 처리
                    if len(buffer) > 50 or any(char in buffer for char in ['.', '!', '?', '。', '！', '？', '\n']):
                        sentences = _split_into_sentences(buffer)
                        if len(sentences) > 1:
                            for sentence in sentences[:-1]:
                                if sentence.strip():
                                    yield {
                                        "type": "sentence",
                                        "content": sentence.strip(),
                                        "section": current_section
                                    }
                            buffer = sentences[-1]
            
            # 마지막 버퍼 처리
            if buffer.strip():
                yield {
                    "type": "sentence",
                    "content": buffer.strip(),
                    "section": current_section
                }
            
        except ImportError:
            # 기존 방식으로 fallback
            import google.generativeai as genai_old
            genai_old.configure(api_key=api_key)
            model = genai_old.GenerativeModel(model_name)
            
            accumulated_text = ""
            buffer = ""
            current_section = "executive_summary"
            
            loop = asyncio.get_event_loop()
            
            def generate_stream_old():
                return model.generate_content(
                    full_prompt,
                    generation_config={
                        "response_mime_type": "application/json",
                        "temperature": 0.5
                    },
                    stream=True
                )
            
            response_stream = await loop.run_in_executor(None, generate_stream_old)
            
            for chunk in response_stream:
                text = None
                if hasattr(chunk, 'text'):
                    text = chunk.text
                elif isinstance(chunk, str):
                    text = chunk
                
                if text:
                    accumulated_text += text
                    buffer += text
                    
                    # 버퍼가 충분히 길어지거나 문장 종료 문자가 있으면 처리
                    if len(buffer) > 50 or any(char in buffer for char in ['.', '!', '?', '。', '！', '？', '\n']):
                        sentences = _split_into_sentences(buffer)
                        if len(sentences) > 1:
                            for sentence in sentences[:-1]:
                                if sentence.strip():
                                    yield {
                                        "type": "sentence",
                                        "content": sentence.strip(),
                                        "section": current_section
                                    }
                            buffer = sentences[-1]
            
            if buffer.strip():
                yield {
                    "type": "sentence",
                    "content": buffer.strip(),
                    "section": current_section
                }
        
        if progress_tracker:
            await progress_tracker.update(80, "AI 응답 수신 완료, 결과 파싱 중...")
            yield {"type": "progress", "progress": 80, "message": "AI 응답 수신 완료, 결과 파싱 중..."}
        
        # 최종 결과 파싱
        try:
            result = parse_json_with_fallback(accumulated_text)
            if "target_keyword" not in result:
                result["target_keyword"] = target_keyword
            if "target_type" not in result:
                result["target_type"] = target_type
            
            yield {"type": "complete", "data": result}
        except Exception as e:
            logger.error(f"JSON 파싱 실패: {e}")
            yield {
                "type": "complete",
                "data": {
                    "executive_summary": accumulated_text[:500],
                    "target_keyword": target_keyword,
                    "target_type": target_type,
                    "error": "JSON 파싱 실패"
                }
            }
            
    except Exception as e:
        logger.error(f"Gemini 스트리밍 분석 중 오류: {e}", exc_info=True)
        yield {"type": "error", "message": str(e)}
