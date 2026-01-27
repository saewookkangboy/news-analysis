"""
정성적 분석 서비스
감정, 맥락, 톤 분석을 수행합니다.
"""
import logging
from typing import Optional, Dict, Any
import json
from datetime import datetime

from backend.config import settings
from backend.utils.token_optimizer import (
    optimize_prompt, estimate_tokens, get_max_tokens_for_model, optimize_additional_context,
    parse_json_with_fallback
)
from backend.utils.gemini_utils import (
    generate_content_with_fallback,
    build_model_candidates,
    is_model_not_found_error,
)

logger = logging.getLogger(__name__)


async def analyze_sentiment(
    target_keyword: str,
    additional_context: Optional[str] = None,
    use_gemini: bool = False
) -> Dict[str, Any]:
    """
    감정 분석 수행
    
    Args:
        target_keyword: 분석할 키워드
        additional_context: 추가 컨텍스트
        use_gemini: Gemini API 사용 여부
        
    Returns:
        감정 분석 결과
    """
    try:
        logger.info(f"감정 분석 시작: {target_keyword}")
        
        # API 키 확인 (환경 변수에서 직접 확인 - Vercel 호환성)
        import os
        from backend.config import settings
        gemini_key = settings.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
        openai_key = settings.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY')
        
        if use_gemini and gemini_key:
            result = await _analyze_sentiment_with_gemini(target_keyword, additional_context)
        elif openai_key:
            result = await _analyze_sentiment_with_openai(target_keyword, additional_context)
        else:
            result = _analyze_sentiment_basic(target_keyword, additional_context)
        
        logger.info(f"감정 분석 완료: {target_keyword}")
        return result
        
    except Exception as e:
        logger.error(f"감정 분석 중 오류: {e}")
        raise


async def analyze_context(
    target_keyword: str,
    additional_context: Optional[str] = None,
    use_gemini: bool = False
) -> Dict[str, Any]:
    """
    맥락 분석 수행
    
    Args:
        target_keyword: 분석할 키워드
        additional_context: 추가 컨텍스트
        use_gemini: Gemini API 사용 여부
        
    Returns:
        맥락 분석 결과
    """
    try:
        logger.info(f"맥락 분석 시작: {target_keyword}")
        
        # API 키 확인 (환경 변수에서 직접 확인 - Vercel 호환성)
        import os
        from backend.config import settings
        gemini_key = settings.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
        openai_key = settings.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY')
        
        if use_gemini and gemini_key:
            result = await _analyze_context_with_gemini(target_keyword, additional_context)
        elif openai_key:
            result = await _analyze_context_with_openai(target_keyword, additional_context)
        else:
            result = _analyze_context_basic(target_keyword, additional_context)
        
        logger.info(f"맥락 분석 완료: {target_keyword}")
        return result
        
    except Exception as e:
        logger.error(f"맥락 분석 중 오류: {e}")
        raise


async def analyze_tone(
    target_keyword: str,
    additional_context: Optional[str] = None,
    use_gemini: bool = False
) -> Dict[str, Any]:
    """
    톤 분석 수행
    
    Args:
        target_keyword: 분석할 키워드
        additional_context: 추가 컨텍스트
        use_gemini: Gemini API 사용 여부
        
    Returns:
        톤 분석 결과
    """
    try:
        logger.info(f"톤 분석 시작: {target_keyword}")
        
        # API 키 확인 (환경 변수에서 직접 확인 - Vercel 호환성)
        import os
        from backend.config import settings
        gemini_key = settings.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
        openai_key = settings.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY')
        
        if use_gemini and gemini_key:
            result = await _analyze_tone_with_gemini(target_keyword, additional_context)
        elif openai_key:
            result = await _analyze_tone_with_openai(target_keyword, additional_context)
        else:
            result = _analyze_tone_basic(target_keyword, additional_context)
        
        logger.info(f"톤 분석 완료: {target_keyword}")
        return result
        
    except Exception as e:
        logger.error(f"톤 분석 중 오류: {e}")
        raise


async def _analyze_sentiment_with_gemini(
    target_keyword: str,
    additional_context: Optional[str]
) -> Dict[str, Any]:
    """Gemini API를 사용한 감정 분석"""
    try:
        import asyncio
        import os
        
        # 추가 컨텍스트 최적화
        additional_context_optimized = optimize_additional_context(additional_context, max_length=300)
        prompt = _build_sentiment_prompt(target_keyword, additional_context_optimized)
        prompt = optimize_prompt(prompt, max_length=5000)  # 프롬프트 최적화
        
        model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash')
        
        # 시스템 메시지와 프롬프트 결합 (최적화)
        system_message = "You are a senior sentiment analyst. Respond ONLY in valid JSON format."
        full_prompt = f"{system_message}\n\n{prompt}\n\nJSON 형식으로만 응답하세요."
        
        # 토큰 수 계산
        full_prompt_tokens = estimate_tokens(full_prompt)
        max_output_tokens = get_max_tokens_for_model(model_name, full_prompt_tokens)
        
        try:
            from google import genai
            api_key = settings.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
            client = genai.Client(api_key=api_key) if api_key else genai.Client()
            
            response = await generate_content_with_fallback(
                client=client,
                model=model_name,
                contents=full_prompt,
                config={
                    "response_mime_type": "application/json",
                    "max_output_tokens": max_output_tokens,
                },
                logger=logger,
            )
            result_text = response.text if hasattr(response, 'text') else str(response)
            
        except ImportError:
            import google.generativeai as genai_old
            genai_old.configure(api_key=settings.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY'))
            
            # 시스템 메시지와 프롬프트 결합 (최적화)
            system_message = "You are a senior sentiment analyst. Respond ONLY in valid JSON format."
            full_prompt_old = f"{system_message}\n\n{prompt}\n\nJSON 형식으로만 응답하세요."
            
            # 토큰 수 계산
            full_prompt_tokens_old = estimate_tokens(full_prompt_old)
            max_output_tokens_old = get_max_tokens_for_model(model_name, full_prompt_tokens_old)
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: model.generate_content(
                    full_prompt_old,
                    generation_config={
                        "max_output_tokens": max_output_tokens_old
                    }
                )
            )
            result_text = response.text if hasattr(response, 'text') else str(response)
        
        # 강화된 JSON 파싱 사용
        try:
            result = parse_json_with_fallback(result_text)
        except ValueError as e:
            logger.error(f"JSON 파싱 최종 실패: {e}")
            result = {"sentiment": {"error": "JSON 파싱 실패", "raw_response": result_text[:1000] if len(result_text) > 1000 else result_text}}
        
        return result
        
    except Exception as e:
        logger.error(f"Gemini 감정 분석 실패: {e}")
        return _analyze_sentiment_basic(target_keyword, additional_context)


async def _analyze_sentiment_with_openai(
    target_keyword: str,
    additional_context: Optional[str]
) -> Dict[str, Any]:
    """OpenAI API를 사용한 감정 분석"""
    try:
        from openai import AsyncOpenAI
        import os
        
        # API 키 확인 (환경 변수에서 직접 읽기 - Vercel 호환성)
        api_key = settings.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        
        client = AsyncOpenAI(api_key=api_key)
        
        # 추가 컨텍스트 최적화
        additional_context_optimized = optimize_additional_context(additional_context, max_length=300)
        prompt = _build_sentiment_prompt(target_keyword, additional_context_optimized)
        prompt = optimize_prompt(prompt, max_length=5000)  # 프롬프트 최적화
        
        system_message = """You are a senior sentiment analyst. Provide comprehensive sentiment analysis in JSON format.
Your analysis must be data-driven, structured, and actionable."""
        system_message = optimize_prompt(system_message, max_length=300)  # 시스템 메시지 최적화
        
        # 토큰 수 계산
        full_prompt_tokens = estimate_tokens(system_message) + estimate_tokens(prompt)
        max_output_tokens = get_max_tokens_for_model(settings.OPENAI_MODEL, full_prompt_tokens)
        
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=max_output_tokens,  # 최대 출력 토큰 설정
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content
        if not result_text:
            raise ValueError("OpenAI API 응답이 비어있습니다.")
        
        # 강화된 JSON 파싱 사용
        try:
            result = parse_json_with_fallback(result_text)
        except ValueError as e:
            logger.error(f"JSON 파싱 최종 실패: {e}")
            result = {"sentiment": {"error": "JSON 파싱 실패", "raw_response": result_text[:1000] if len(result_text) > 1000 else result_text}}
        
        return result
        
    except Exception as e:
        logger.error(f"OpenAI 감정 분석 실패: {e}")
        return _analyze_sentiment_basic(target_keyword, additional_context)


async def _analyze_context_with_gemini(
    target_keyword: str,
    additional_context: Optional[str]
) -> Dict[str, Any]:
    """Gemini API를 사용한 맥락 분석"""
    try:
        import asyncio
        import os
        
        # 추가 컨텍스트 최적화
        additional_context_optimized = optimize_additional_context(additional_context, max_length=300)
        prompt = _build_context_prompt(target_keyword, additional_context_optimized)
        prompt = optimize_prompt(prompt, max_length=5000)  # 프롬프트 최적화
        
        model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash')
        
        # 시스템 메시지와 프롬프트 결합 (최적화)
        system_message = "You are a senior context analyst. Respond ONLY in valid JSON format."
        full_prompt = f"{system_message}\n\n{prompt}\n\nJSON 형식으로만 응답하세요."
        
        # 토큰 수 계산
        full_prompt_tokens = estimate_tokens(full_prompt)
        max_output_tokens = get_max_tokens_for_model(model_name, full_prompt_tokens)
        
        try:
            from google import genai
            api_key = settings.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
            client = genai.Client(api_key=api_key) if api_key else genai.Client()
            
            response = await generate_content_with_fallback(
                client=client,
                model=model_name,
                contents=full_prompt,
                config={
                    "response_mime_type": "application/json",
                    "max_output_tokens": max_output_tokens,
                },
                logger=logger,
            )
            result_text = response.text if hasattr(response, 'text') else str(response)
            
        except ImportError:
            import google.generativeai as genai_old
            genai_old.configure(api_key=settings.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY'))
            
            # 시스템 메시지와 프롬프트 결합
            system_message = "You are a senior context analyst. Respond ONLY in valid JSON format without markdown code blocks."
            full_prompt_old = f"{system_message}\n\n{prompt}\n\n**중요**: 반드시 유효한 JSON 형식으로만 응답하세요. 마크다운 코드 블록을 사용하지 마세요."
            
            loop = asyncio.get_event_loop()
            response = None
            last_error = None
            for candidate in build_model_candidates(model_name):
                try:
                    if candidate != model_name:
                        logger.warning(f"GEMINI_MODEL fallback 사용: {candidate}")
                    model = genai_old.GenerativeModel(candidate)
                    response = await loop.run_in_executor(
                        None,
                        lambda: model.generate_content(full_prompt_old)
                    )
                    break
                except Exception as e:
                    last_error = e
                    if not is_model_not_found_error(e):
                        raise
            if response is None:
                raise ValueError(f"Gemini API 호출 실패: {str(last_error)}")
            result_text = response.text if hasattr(response, 'text') else str(response)
        
        # 강화된 JSON 파싱 사용
        if not result_text:
            raise ValueError("Gemini API 응답이 비어있습니다.")
        
        try:
            result = parse_json_with_fallback(result_text)
        except ValueError as e:
            logger.error(f"JSON 파싱 최종 실패: {e}")
            result = {"context": {"error": "JSON 파싱 실패", "raw_response": result_text[:1000] if len(result_text) > 1000 else result_text}}
        
        return result
        
    except Exception as e:
        logger.error(f"Gemini 맥락 분석 실패: {e}")
        return _analyze_context_basic(target_keyword, additional_context)


async def _analyze_context_with_openai(
    target_keyword: str,
    additional_context: Optional[str]
) -> Dict[str, Any]:
    """OpenAI API를 사용한 맥락 분석"""
    try:
        from openai import AsyncOpenAI
        import os
        
        # API 키 확인 (환경 변수에서 직접 읽기 - Vercel 호환성)
        api_key = settings.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        
        client = AsyncOpenAI(api_key=api_key)
        # 추가 컨텍스트 최적화
        additional_context_optimized = optimize_additional_context(additional_context, max_length=300)
        prompt = _build_context_prompt(target_keyword, additional_context_optimized)
        prompt = optimize_prompt(prompt, max_length=5000)  # 프롬프트 최적화
        
        system_message = """You are a senior context analyst. Provide comprehensive context analysis in JSON format.
Your analysis must be culturally sensitive, data-driven, and actionable."""
        system_message = optimize_prompt(system_message, max_length=300)  # 시스템 메시지 최적화
        
        # 토큰 수 계산
        full_prompt_tokens = estimate_tokens(system_message) + estimate_tokens(prompt)
        max_output_tokens = get_max_tokens_for_model(settings.OPENAI_MODEL, full_prompt_tokens)
        
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=max_output_tokens,  # 최대 출력 토큰 설정
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content
        if not result_text:
            raise ValueError("OpenAI API 응답이 비어있습니다.")
        
        # 마크다운 코드 블록 제거
        clean_text = result_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()
        
        try:
            result = json.loads(clean_text)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON 파싱 실패, 재시도: {e}")
            try:
                start_idx = clean_text.find("{")
                end_idx = clean_text.rfind("}") + 1
                if start_idx >= 0 and end_idx > start_idx:
                    result = json.loads(clean_text[start_idx:end_idx])
                else:
                    raise ValueError("유효한 JSON을 찾을 수 없습니다.")
            except Exception as e2:
                logger.error(f"JSON 파싱 최종 실패: {e2}")
                result = {"context": {"error": "JSON 파싱 실패", "raw_response": clean_text[:500]}}
        
        return result
        
    except Exception as e:
        logger.error(f"OpenAI 맥락 분석 실패: {e}")
        return _analyze_context_basic(target_keyword, additional_context)


async def _analyze_tone_with_gemini(
    target_keyword: str,
    additional_context: Optional[str]
) -> Dict[str, Any]:
    """Gemini API를 사용한 톤 분석"""
    try:
        import asyncio
        import os
        
        # 추가 컨텍스트 최적화
        additional_context_optimized = optimize_additional_context(additional_context, max_length=300)
        prompt = _build_tone_prompt(target_keyword, additional_context_optimized)
        prompt = optimize_prompt(prompt, max_length=5000)  # 프롬프트 최적화
        
        model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash')
        
        # 시스템 메시지와 프롬프트 결합 (최적화)
        system_message = "You are a senior tone analyst. Respond ONLY in valid JSON format."
        full_prompt = f"{system_message}\n\n{prompt}\n\nJSON 형식으로만 응답하세요."
        
        # 토큰 수 계산
        full_prompt_tokens = estimate_tokens(full_prompt)
        max_output_tokens = get_max_tokens_for_model(model_name, full_prompt_tokens)
        
        try:
            from google import genai
            api_key = settings.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
            client = genai.Client(api_key=api_key) if api_key else genai.Client()
            
            response = await generate_content_with_fallback(
                client=client,
                model=model_name,
                contents=full_prompt,
                config={
                    "response_mime_type": "application/json",
                    "max_output_tokens": max_output_tokens,
                },
                logger=logger,
            )
            result_text = response.text if hasattr(response, 'text') else str(response)
            
        except ImportError:
            import google.generativeai as genai_old
            genai_old.configure(api_key=settings.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY'))
            model = genai_old.GenerativeModel(model_name)
            
            # 시스템 메시지와 프롬프트 결합 (최적화)
            system_message = "You are a senior sentiment analyst. Respond ONLY in valid JSON format."
            full_prompt_old = f"{system_message}\n\n{prompt}\n\nJSON 형식으로만 응답하세요."
            
            # 토큰 수 계산
            full_prompt_tokens_old = estimate_tokens(full_prompt_old)
            max_output_tokens_old = get_max_tokens_for_model(model_name, full_prompt_tokens_old)
            
            loop = asyncio.get_event_loop()
            response = None
            last_error = None
            for candidate in build_model_candidates(model_name):
                try:
                    if candidate != model_name:
                        logger.warning(f"GEMINI_MODEL fallback 사용: {candidate}")
                    model = genai_old.GenerativeModel(candidate)
                    response = await loop.run_in_executor(
                        None,
                        lambda: model.generate_content(
                            full_prompt_old,
                            generation_config={
                                "max_output_tokens": max_output_tokens_old
                            }
                        )
                    )
                    break
                except Exception as e:
                    last_error = e
                    if not is_model_not_found_error(e):
                        raise
            if response is None:
                raise ValueError(f"Gemini API 호출 실패: {str(last_error)}")
            result_text = response.text if hasattr(response, 'text') else str(response)
        
        # 마크다운 코드 블록 제거
        if not result_text:
            raise ValueError("Gemini API 응답이 비어있습니다.")
        
        clean_text = result_text.strip() if isinstance(result_text, str) else str(result_text).strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()
        
        try:
            result = json.loads(clean_text)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON 파싱 실패, 재시도: {e}")
            try:
                start_idx = clean_text.find("{")
                end_idx = clean_text.rfind("}") + 1
                if start_idx >= 0 and end_idx > start_idx:
                    result = json.loads(clean_text[start_idx:end_idx])
                else:
                    raise ValueError("유효한 JSON을 찾을 수 없습니다.")
            except Exception as e2:
                logger.error(f"JSON 파싱 최종 실패: {e2}")
                result = {"tone": {"error": "JSON 파싱 실패", "raw_response": clean_text[:500]}}
        
        return result
        
    except Exception as e:
        logger.error(f"Gemini 톤 분석 실패: {e}")
        return _analyze_tone_basic(target_keyword, additional_context)


async def _analyze_tone_with_openai(
    target_keyword: str,
    additional_context: Optional[str]
) -> Dict[str, Any]:
    """OpenAI API를 사용한 톤 분석"""
    try:
        from openai import AsyncOpenAI
        import os
        
        # API 키 확인 (환경 변수에서 직접 읽기 - Vercel 호환성)
        api_key = settings.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        
        client = AsyncOpenAI(api_key=api_key)
        
        # 추가 컨텍스트 최적화
        additional_context_optimized = optimize_additional_context(additional_context, max_length=300)
        prompt = _build_tone_prompt(target_keyword, additional_context_optimized)
        prompt = optimize_prompt(prompt, max_length=5000)  # 프롬프트 최적화
        
        system_message = """You are a senior tone analyst. Provide comprehensive tone analysis in JSON format.
Your analysis must be multi-dimensional, channel-specific, and actionable."""
        system_message = optimize_prompt(system_message, max_length=300)  # 시스템 메시지 최적화
        
        # 토큰 수 계산
        full_prompt_tokens = estimate_tokens(system_message) + estimate_tokens(prompt)
        max_output_tokens = get_max_tokens_for_model(settings.OPENAI_MODEL, full_prompt_tokens)
        
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=max_output_tokens,  # 최대 출력 토큰 설정
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content
        if not result_text:
            raise ValueError("OpenAI API 응답이 비어있습니다.")
        
        # 강화된 JSON 파싱 사용
        try:
            result = parse_json_with_fallback(result_text)
        except ValueError as e:
            logger.error(f"JSON 파싱 최종 실패: {e}")
            result = {"tone": {"error": "JSON 파싱 실패", "raw_response": result_text[:1000] if len(result_text) > 1000 else result_text}}
        
        return result
        
    except Exception as e:
        logger.error(f"OpenAI 톤 분석 실패: {e}")
        return _analyze_tone_basic(target_keyword, additional_context)


def _analyze_sentiment_basic(
    target_keyword: str,
    additional_context: Optional[str]
) -> Dict[str, Any]:
    """기본 감정 분석"""
    return {
        "sentiment": {
            "overall": "중립적",
            "score": 50,
            "confidence": 0.3,
            "distribution": {
                "very_positive": 10,
                "positive": 23,
                "neutral": 34,
                "negative": 23,
                "very_negative": 10
            },
            "trend": {
                "direction": "유지",
                "change_rate": "안정",
                "period": "기본 분석 모드",
                "trend_description": "AI API를 설정하면 더 상세한 트렌드 분석이 가능합니다."
            },
            "key_emotional_drivers": [
                {
                    "driver": "AI API 미설정",
                    "impact": "높음",
                    "sentiment": "중립적",
                    "description": "AI API를 설정하면 더 상세한 감정 분석이 가능합니다."
                }
            ],
            "emotional_intensity": {
                "level": "중간",
                "score": 0.5,
                "description": "기본 분석 모드입니다."
            },
            "sentiment_details": {
                "positive_aspects": [
                    {
                        "aspect": "기본 분석 모드",
                        "evidence": "AI API 설정 필요",
                        "impact": "중간"
                    }
                ],
                "negative_aspects": [],
                "neutral_aspects": [
                    {
                        "aspect": "기본 분석 모드",
                        "description": "AI API를 설정하면 더 상세한 분석이 가능합니다."
                    }
                ]
            },
            "recommendations": {
                "immediate_actions": [
                    "OpenAI 또는 Gemini API 키를 환경 변수에 설정하세요.",
                    "API 키 설정 후 서버를 재시작하고 다시 분석을 시도하세요."
                ],
                "long_term_strategies": [
                    "AI API를 통한 정량적 감정 데이터 수집",
                    "지속적인 감정 모니터링 시스템 구축"
                ]
            }
        }
    }


def _analyze_context_basic(
    target_keyword: str,
    additional_context: Optional[str]
) -> Dict[str, Any]:
    """기본 맥락 분석"""
    current_date = datetime.now()
    return {
        "context": {
            "social_relevance": {
                "level": "중간",
                "score": 0.5,
                "description": "기본 분석 모드입니다. AI API를 설정하면 더 상세한 분석이 가능합니다.",
                "indicators": ["AI API 설정 필요"]
            },
            "current_issues": [
                {
                    "issue": "AI API 미설정",
                    "relevance": "높음",
                    "connection": "AI API를 설정하면 더 상세한 맥락 분석이 가능합니다.",
                    "impact": "높음"
                }
            ],
            "cultural_context": {
                "korean_cultural_factors": "기본 분석 모드입니다. AI API를 설정하면 한국 문화적 특성과의 연관성을 상세히 분석할 수 있습니다.",
                "generational_differences": "AI API 설정 필요",
                "regional_variations": "AI API 설정 필요",
                "cultural_trends": ["AI API 설정 필요"]
            },
            "temporal_factors": {
                "current_period": f"{current_date.strftime('%Y년 %m월')} - 기본 분석 모드",
                "seasonal_patterns": "AI API 설정 필요",
                "timing_opportunities": ["AI API 설정 필요"],
                "timing_risks": []
            },
            "regional_context": {
                "korean_market": {
                    "market_size": "AI API 설정 필요",
                    "market_maturity": "AI API 설정 필요",
                    "competitive_landscape": "AI API 설정 필요",
                    "consumer_behavior": "AI API 설정 필요"
                },
                "global_context": {
                    "international_relevance": "AI API 설정 필요",
                    "comparison": "AI API 설정 필요"
                }
            },
            "industry_context": {
                "industry": "AI API 설정 필요",
                "industry_trends": ["AI API 설정 필요"],
                "industry_challenges": ["AI API 설정 필요"],
                "industry_opportunities": ["AI API 설정 필요"]
            },
            "related_movements": [
                {
                    "movement": "AI API 설정 필요",
                    "type": "기술",
                    "connection": "AI API를 설정하면 관련 사회적 움직임을 분석할 수 있습니다.",
                    "influence": "중간"
                }
            ],
            "media_landscape": {
                "coverage_level": "AI API 설정 필요",
                "media_sentiment": "AI API 설정 필요",
                "key_media_outlets": ["AI API 설정 필요"],
                "coverage_quality": "AI API 설정 필요"
            },
            "recommendations": {
                "messaging_strategy": [
                    "AI API를 설정하여 맥락 기반 메시징 전략을 수립하세요."
                ],
                "timing_strategy": [
                    "AI API를 설정하여 최적의 타이밍을 분석하세요."
                ],
                "channel_strategy": [
                    "AI API를 설정하여 맥락에 맞는 채널을 선택하세요."
                ]
            }
        }
    }


def _analyze_tone_basic(
    target_keyword: str,
    additional_context: Optional[str]
) -> Dict[str, Any]:
    """기본 톤 분석"""
    return {
        "tone": {
            "overall_tone": {
                "primary_tone": "기본 분석 모드",
                "tone_description": "AI API를 설정하면 더 상세한 톤 분석이 가능합니다.",
                "tone_category": "일반적"
            },
            "tone_dimensions": {
                "professional": {
                    "score": 0.5,
                    "description": "기본 분석 모드입니다.",
                    "evidence": "AI API 설정 필요"
                },
                "positive": {
                    "score": 0.5,
                    "description": "기본 분석 모드입니다.",
                    "evidence": "AI API 설정 필요"
                },
                "objective": {
                    "score": 0.5,
                    "description": "기본 분석 모드입니다.",
                    "evidence": "AI API 설정 필요"
                },
                "formal": {
                    "score": 0.5,
                    "description": "기본 분석 모드입니다.",
                    "evidence": "AI API 설정 필요"
                },
                "technical": {
                    "score": 0.5,
                    "description": "기본 분석 모드입니다.",
                    "evidence": "AI API 설정 필요"
                },
                "accessible": {
                    "score": 0.5,
                    "description": "기본 분석 모드입니다.",
                    "evidence": "AI API 설정 필요"
                },
                "authoritative": {
                    "score": 0.5,
                    "description": "기본 분석 모드입니다.",
                    "evidence": "AI API 설정 필요"
                },
                "empathetic": {
                    "score": 0.5,
                    "description": "기본 분석 모드입니다.",
                    "evidence": "AI API 설정 필요"
                }
            },
            "tone_consistency": {
                "level": "중간",
                "score": 0.5,
                "description": "기본 분석 모드입니다.",
                "variations": []
            },
            "channel_analysis": {
                "traditional_media": {
                    "tone": "AI API 설정 필요",
                    "characteristics": ["AI API 설정 필요"]
                },
                "digital_media": {
                    "tone": "AI API 설정 필요",
                    "characteristics": ["AI API 설정 필요"]
                },
                "social_media": {
                    "tone": "AI API 설정 필요",
                    "characteristics": ["AI API 설정 필요"]
                }
            },
            "tone_trends": {
                "recent_changes": "AI API 설정 필요",
                "trend_direction": "유지",
                "key_events": ["AI API 설정 필요"]
            },
            "tone_recommendations": {
                "optimal_tone": "AI API를 설정하면 최적의 톤을 추천할 수 있습니다.",
                "tone_guidelines": [
                    "AI API를 설정하여 톤 가이드라인을 수립하세요.",
                    "채널별 톤 전략을 수립하세요."
                ],
                "tone_risks": [],
                "channel_specific_recommendations": {
                    "traditional_media": "AI API 설정 필요",
                    "digital_media": "AI API 설정 필요",
                    "social_media": "AI API 설정 필요"
                }
            }
        }
    }


def _build_sentiment_prompt(
    target_keyword: str,
    additional_context: Optional[str]
) -> str:
    """감정 분석 프롬프트 생성"""
    current_date = datetime.now().strftime("%Y년 %m월 %d일")
    
    prompt = f"""
당신은 15년 이상의 경력을 가진 전문 감정 분석가이자 소셜 리스닝 전문가입니다.
다음 키워드에 대한 대중의 감정을 매우 상세하고 심층적으로 분석해주세요.

**분석 대상**: {target_keyword}
**현재 시점**: {current_date}

**분석 목적**: 이 감정 분석은 마케팅 전략, 위기 관리, 브랜드 관리, PR 전략 수립에 활용됩니다.
따라서 모든 분석은 실행 가능한 인사이트와 구체적인 권장사항을 포함해야 합니다.
"""
    if additional_context:
        prompt += f"""
**추가 컨텍스트**:
{additional_context}

"""
    
    prompt += """
**중요 지시사항**:
1. 반드시 유효한 JSON 형식으로만 응답해야 합니다. 마크다운 코드 블록(```json)을 사용하지 마세요.
2. MECE 원칙을 엄격히 준수하여 각 섹션이 상호 배타적이면서 완전 포괄적이어야 합니다.
3. 정량적 데이터(점수, 비율, 강도 등)와 정성적 분석(감정 요인, 세부 측면 등)을 모두 포함해야 합니다.
4. 최근 3개월간의 감정 변화 추세를 반드시 포함해야 합니다.
5. 감정을 이끄는 구체적인 사건, 뉴스, 이슈를 명시해야 합니다.

다음 JSON 구조를 정확히 따르면서 각 필드를 매우 상세하게 작성해주세요:

{
  "sentiment": {
    "overall": "긍정적/부정적/중립적/복합적",
    "score": 72,  // 0-100 점수 (0: 매우 부정적, 50: 중립적, 100: 매우 긍정적)
    "confidence": 0.85,  // 분석 신뢰도 (0-1)
    "distribution": {
      "very_positive": 25,  // 매우 긍정적 비율 (%)
      "positive": 40,       // 긍정적 비율 (%)
      "neutral": 20,        // 중립적 비율 (%)
      "negative": 12,       // 부정적 비율 (%)
      "very_negative": 3    // 매우 부정적 비율 (%)
    },
    "trend": {
      "direction": "향상 중/악화 중/유지/변동",  // 최근 감정 변화 추세
      "change_rate": "급격/점진/안정",  // 변화 속도
      "period": "최근 3개월",  // 분석 기간
      "trend_description": "구체적인 추세 설명 (예: 지난 3개월간 긍정적 감정이 15%p 증가)"
    },
    "key_emotional_drivers": [
      {
        "driver": "감정을 이끄는 주요 요인 1",
        "impact": "높음/중간/낮음",
        "sentiment": "긍정적/부정적/중립적",
        "description": "구체적인 설명 및 근거"
      },
      {
        "driver": "감정을 이끄는 주요 요인 2",
        "impact": "높음/중간/낮음",
        "sentiment": "긍정적/부정적/중립적",
        "description": "구체적인 설명 및 근거"
      },
      {
        "driver": "감정을 이끄는 주요 요인 3",
        "impact": "높음/중간/낮음",
        "sentiment": "긍정적/부정적/중립적",
        "description": "구체적인 설명 및 근거"
      },
      {
        "driver": "감정을 이끄는 주요 요인 4",
        "impact": "높음/중간/낮음",
        "sentiment": "긍정적/부정적/중립적",
        "description": "구체적인 설명 및 근거"
      },
      {
        "driver": "감정을 이끄는 주요 요인 5",
        "impact": "높음/중간/낮음",
        "sentiment": "긍정적/부정적/중립적",
        "description": "구체적인 설명 및 근거"
      }
    ],
    "emotional_intensity": {
      "level": "높음/중간/낮음",
      "score": 0.75,  // 0-1 (1: 매우 강함)
      "description": "감정 강도에 대한 상세 설명"
    },
    "sentiment_details": {
      "positive_aspects": [
        {
          "aspect": "긍정적 측면 1",
          "evidence": "근거 또는 사례",
          "impact": "높음/중간/낮음"
        },
        {
          "aspect": "긍정적 측면 2",
          "evidence": "근거 또는 사례",
          "impact": "높음/중간/낮음"
        },
        {
          "aspect": "긍정적 측면 3",
          "evidence": "근거 또는 사례",
          "impact": "높음/중간/낮음"
        }
      ],
      "negative_aspects": [
        {
          "aspect": "부정적 측면 1",
          "evidence": "근거 또는 사례",
          "impact": "높음/중간/낮음",
          "mitigation": "완화 방안"
        },
        {
          "aspect": "부정적 측면 2",
          "evidence": "근거 또는 사례",
          "impact": "높음/중간/낮음",
          "mitigation": "완화 방안"
        }
      ],
      "neutral_aspects": [
        {
          "aspect": "중립적 측면 1",
          "description": "상세 설명"
        },
        {
          "aspect": "중립적 측면 2",
          "description": "상세 설명"
        }
      ]
    },
    "demographic_sentiment": {
      "age_groups": {
        "20s": {"sentiment": "긍정적/부정적/중립적", "score": 75},
        "30s": {"sentiment": "긍정적/부정적/중립적", "score": 68},
        "40s": {"sentiment": "긍정적/부정적/중립적", "score": 72},
        "50s+": {"sentiment": "긍정적/부정적/중립적", "score": 70}
      },
      "gender": {
        "male": {"sentiment": "긍정적/부정적/중립적", "score": 70},
        "female": {"sentiment": "긍정적/부정적/중립적", "score": 74}
      }
    },
    "recommendations": {
      "immediate_actions": [
        "즉시 실행 가능한 감정 관리 전략 1 (구체적 실행 방안)",
        "즉시 실행 가능한 감정 관리 전략 2",
        "즉시 실행 가능한 감정 관리 전략 3"
      ],
      "long_term_strategies": [
        "장기 감정 관리 전략 1",
        "장기 감정 관리 전략 2"
      ]
    }
  }
}
"""
    return prompt


def _build_context_prompt(
    target_keyword: str,
    additional_context: Optional[str]
) -> str:
    """맥락 분석 프롬프트 생성"""
    current_date = datetime.now().strftime("%Y년 %m월 %d일")
    
    prompt = f"""
당신은 15년 이상의 경력을 가진 전문 맥락 분석가이자 문화 인류학자입니다.
다음 키워드의 사회적, 문화적, 시기적, 산업적 맥락을 매우 상세하고 심층적으로 분석해주세요.

**분석 대상**: {target_keyword}
**현재 시점**: {current_date}

**분석 목적**: 이 맥락 분석은 마케팅 메시징, 타겟팅, 채널 선택, 콘텐츠 전략 수립에 활용됩니다.
따라서 모든 분석은 실행 가능한 인사이트와 구체적인 전략 제안을 포함해야 합니다.
"""
    if additional_context:
        prompt += f"""
**추가 컨텍스트**:
{additional_context}

"""
    
    prompt += """
**중요 지시사항**:
1. 반드시 유효한 JSON 형식으로만 응답해야 합니다. 마크다운 코드 블록(```json)을 사용하지 마세요.
2. MECE 원칙을 엄격히 준수하여 각 섹션이 상호 배타적이면서 완전 포괄적이어야 합니다.
3. 한국 시장과 문화에 특화된 맥락 분석을 제공해야 합니다.
4. 최근 3개월간의 맥락 변화를 반드시 포함해야 합니다.
5. 구체적인 사건, 뉴스, 트렌드를 명시해야 합니다.

다음 JSON 구조를 정확히 따르면서 각 필드를 매우 상세하게 작성해주세요:

{
  "context": {
    "social_relevance": {
      "level": "높음/중간/낮음",
      "score": 0.75,  // 0-1
      "description": "사회적 관련성에 대한 상세 설명",
      "indicators": [
        "관련성 지표 1 (예: 언론 보도 빈도, SNS 언급량 등)",
        "관련성 지표 2",
        "관련성 지표 3"
      ]
    },
    "current_issues": [
      {
        "issue": "현재 사회적 이슈와의 연관성 1",
        "relevance": "높음/중간/낮음",
        "connection": "연관성 설명",
        "impact": "영향도 설명"
      },
      {
        "issue": "현재 사회적 이슈와의 연관성 2",
        "relevance": "높음/중간/낮음",
        "connection": "연관성 설명",
        "impact": "영향도 설명"
      },
      {
        "issue": "현재 사회적 이슈와의 연관성 3",
        "relevance": "높음/중간/낮음",
        "connection": "연관성 설명",
        "impact": "영향도 설명"
      }
    ],
    "cultural_context": {
      "korean_cultural_factors": "한국 문화적 특성과의 연관성 (가치관, 관습, 사회적 규범 등)",
      "generational_differences": "세대별 인식 차이",
      "regional_variations": "지역별 차이 (서울/지방, 도시/농촌 등)",
      "cultural_trends": [
        "관련 문화 트렌드 1",
        "관련 문화 트렌드 2",
        "관련 문화 트렌드 3"
      ]
    },
    "temporal_factors": {
      "current_period": "현재 시기의 특성 (계절, 이벤트, 사회적 분위기 등)",
      "seasonal_patterns": "계절성 패턴 (있는 경우)",
      "timing_opportunities": [
        "타이밍 기회 1 (예: 특정 시기에 강조할 수 있는 측면)",
        "타이밍 기회 2"
      ],
      "timing_risks": [
        "타이밍 리스크 1 (예: 피해야 할 시기나 이벤트)",
        "타이밍 리스크 2"
      ]
    },
    "regional_context": {
      "korean_market": {
        "market_size": "한국 시장 규모 추정",
        "market_maturity": "시장 성숙도 (초기/성장/성숙/쇠퇴)",
        "competitive_landscape": "경쟁 환경",
        "consumer_behavior": "한국 소비자 행동 특성"
      },
      "global_context": {
        "international_relevance": "국제적 관련성",
        "comparison": "해외 시장과의 비교"
      }
    },
    "industry_context": {
      "industry": "관련 산업",
      "industry_trends": [
        "산업 트렌드 1",
        "산업 트렌드 2",
        "산업 트렌드 3"
      ],
      "industry_challenges": [
        "산업 도전 과제 1",
        "산업 도전 과제 2"
      ],
      "industry_opportunities": [
        "산업 기회 1",
        "산업 기회 2"
      ]
    },
    "related_movements": [
      {
        "movement": "관련된 사회적 움직임 1",
        "type": "사회운동/트렌드/이슈",
        "connection": "연관성 설명",
        "influence": "영향도"
      },
      {
        "movement": "관련된 사회적 움직임 2",
        "type": "사회운동/트렌드/이슈",
        "connection": "연관성 설명",
        "influence": "영향도"
      },
      {
        "movement": "관련된 사회적 움직임 3",
        "type": "사회운동/트렌드/이슈",
        "connection": "연관성 설명",
        "influence": "영향도"
      }
    ],
    "media_landscape": {
      "coverage_level": "미디어 보도 수준 (높음/중간/낮음)",
      "media_sentiment": "미디어 감정 (긍정적/부정적/중립적)",
      "key_media_outlets": [
        "주요 보도 매체 1",
        "주요 보도 매체 2"
      ],
      "coverage_quality": "보도 품질 평가"
    },
    "recommendations": {
      "messaging_strategy": [
        "맥락 기반 메시징 전략 1",
        "맥락 기반 메시징 전략 2"
      ],
      "timing_strategy": [
        "타이밍 전략 1",
        "타이밍 전략 2"
      ],
      "channel_strategy": [
        "채널 전략 1 (맥락에 맞는 채널 선택)",
        "채널 전략 2"
      ]
    }
  }
}
"""
    return prompt


def _build_tone_prompt(
    target_keyword: str,
    additional_context: Optional[str]
) -> str:
    """톤 분석 프롬프트 생성"""
    current_date = datetime.now().strftime("%Y년 %m월 %d일")
    
    prompt = f"""
당신은 15년 이상의 경력을 가진 전문 톤 분석가이자 커뮤니케이션 스타일 전문가입니다.
다음 키워드와 관련된 언론, 미디어, 소셜 미디어의 톤을 매우 상세하고 심층적으로 분석해주세요.

**분석 대상**: {target_keyword}
**현재 시점**: {current_date}

**분석 목적**: 이 톤 분석은 브랜드 메시징, 콘텐츠 톤 설정, 커뮤니케이션 전략 수립에 활용됩니다.
따라서 모든 분석은 실행 가능한 인사이트와 구체적인 톤 가이드라인을 포함해야 합니다.
"""
    if additional_context:
        prompt += f"""
**추가 컨텍스트**:
{additional_context}

"""
    
    prompt += """
**중요 지시사항**:
1. 반드시 유효한 JSON 형식으로만 응답해야 합니다. 마크다운 코드 블록(```json)을 사용하지 마세요.
2. MECE 원칙을 엄격히 준수하여 각 섹션이 상호 배타적이면서 완전 포괄적이어야 합니다.
3. 다양한 톤 차원을 정량적으로 측정하고 정성적으로 설명해야 합니다.
4. 언론, 미디어, 소셜 미디어 등 채널별 톤 차이를 분석해야 합니다.
5. 최근 3개월간의 톤 변화를 반드시 포함해야 합니다.

다음 JSON 구조를 정확히 따르면서 각 필드를 매우 상세하게 작성해주세요:

{
  "tone": {
    "overall_tone": {
      "primary_tone": "주요 톤 (예: 전문적이고 긍정적이며 객관적)",
      "tone_description": "톤에 대한 종합적이고 상세한 설명 (3-5문단)",
      "tone_category": "전문적/친근한/공식적/캐주얼/기술적/일반적"
    },
    "tone_dimensions": {
      "professional": {
        "score": 0.85,  // 전문성 (0-1)
        "description": "전문성에 대한 상세 설명",
        "evidence": "근거 또는 사례"
      },
      "positive": {
        "score": 0.72,  // 긍정성 (0-1)
        "description": "긍정성에 대한 상세 설명",
        "evidence": "근거 또는 사례"
      },
      "objective": {
        "score": 0.68,  // 객관성 (0-1)
        "description": "객관성에 대한 상세 설명",
        "evidence": "근거 또는 사례"
      },
      "formal": {
        "score": 0.75,  // 공식성 (0-1)
        "description": "공식성에 대한 상세 설명",
        "evidence": "근거 또는 사례"
      },
      "technical": {
        "score": 0.80,  // 기술성 (0-1)
        "description": "기술성에 대한 상세 설명",
        "evidence": "근거 또는 사례"
      },
      "accessible": {
        "score": 0.65,  // 접근성 (0-1)
        "description": "접근성에 대한 상세 설명",
        "evidence": "근거 또는 사례"
      },
      "authoritative": {
        "score": 0.78,  // 권위성 (0-1)
        "description": "권위성에 대한 상세 설명",
        "evidence": "근거 또는 사례"
      },
      "empathetic": {
        "score": 0.60,  // 공감성 (0-1)
        "description": "공감성에 대한 상세 설명",
        "evidence": "근거 또는 사례"
      }
    },
    "tone_consistency": {
      "level": "높음/중간/낮음",
      "score": 0.82,  // 0-1
      "description": "톤 일관성에 대한 상세 설명",
      "variations": [
        "톤 변동 사례 1 (있는 경우)",
        "톤 변동 사례 2"
      ]
    },
    "channel_analysis": {
      "traditional_media": {
        "tone": "전통 미디어의 톤",
        "characteristics": ["특성 1", "특성 2"]
      },
      "digital_media": {
        "tone": "디지털 미디어의 톤",
        "characteristics": ["특성 1", "특성 2"]
      },
      "social_media": {
        "tone": "소셜 미디어의 톤",
        "characteristics": ["특성 1", "특성 2"]
      }
    },
    "tone_trends": {
      "recent_changes": "최근 3개월간의 톤 변화",
      "trend_direction": "향상/악화/유지",
      "key_events": [
        "톤 변화에 영향을 준 주요 사건 1",
        "톤 변화에 영향을 준 주요 사건 2"
      ]
    },
    "tone_recommendations": {
      "optimal_tone": "권장 톤",
      "tone_guidelines": [
        "톤 가이드라인 1 (구체적 실행 방안)",
        "톤 가이드라인 2",
        "톤 가이드라인 3"
      ],
      "tone_risks": [
        "톤 관련 리스크 1 (피해야 할 톤)",
        "톤 관련 리스크 2"
      ],
      "channel_specific_recommendations": {
        "traditional_media": "전통 미디어용 톤 권장사항",
        "digital_media": "디지털 미디어용 톤 권장사항",
        "social_media": "소셜 미디어용 톤 권장사항"
      }
    }
  }
}
"""
    return prompt
