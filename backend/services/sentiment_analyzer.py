"""
정성적 분석 서비스
감정, 맥락, 톤 분석을 수행합니다.
"""
import logging
from typing import Optional, Dict, Any
import json
from datetime import datetime

from backend.config import settings

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
        
        if use_gemini and settings.GEMINI_API_KEY:
            result = await _analyze_sentiment_with_gemini(target_keyword, additional_context)
        elif settings.OPENAI_API_KEY:
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
        
        if use_gemini and settings.GEMINI_API_KEY:
            result = await _analyze_context_with_gemini(target_keyword, additional_context)
        elif settings.OPENAI_API_KEY:
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
        
        if use_gemini and settings.GEMINI_API_KEY:
            result = await _analyze_tone_with_gemini(target_keyword, additional_context)
        elif settings.OPENAI_API_KEY:
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
        
        prompt = _build_sentiment_prompt(target_keyword, additional_context)
        model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash-exp')
        
        try:
            from google import genai
            api_key = settings.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
            client = genai.Client(api_key=api_key) if api_key else genai.Client()
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
            )
            result_text = response.text if hasattr(response, 'text') else str(response)
            
        except ImportError:
            import google.generativeai as genai_old
            genai_old.configure(api_key=settings.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY'))
            model = genai_old.GenerativeModel(model_name)
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: model.generate_content(prompt)
            )
            result_text = response.text if hasattr(response, 'text') else str(response)
        
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            result = {"analysis": result_text}
        
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
        
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        prompt = _build_sentiment_prompt(target_keyword, additional_context)
        
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert sentiment analyst specializing in understanding emotional tones and public sentiment."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        result_text = response.choices[0].message.content
        if not result_text:
            raise ValueError("OpenAI API 응답이 비어있습니다.")
        
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            result = {"analysis": result_text}
        
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
        
        prompt = _build_context_prompt(target_keyword, additional_context)
        model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash-exp')
        
        try:
            from google import genai
            api_key = settings.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
            client = genai.Client(api_key=api_key) if api_key else genai.Client()
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
            )
            result_text = response.text if hasattr(response, 'text') else str(response)
            
        except ImportError:
            import google.generativeai as genai_old
            genai_old.configure(api_key=settings.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY'))
            model = genai_old.GenerativeModel(model_name)
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: model.generate_content(prompt)
            )
            result_text = response.text if hasattr(response, 'text') else str(response)
        
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            result = {"analysis": result_text}
        
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
        
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        prompt = _build_context_prompt(target_keyword, additional_context)
        
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert context analyst specializing in understanding social, cultural, and temporal contexts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        result_text = response.choices[0].message.content
        if not result_text:
            raise ValueError("OpenAI API 응답이 비어있습니다.")
        
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            result = {"analysis": result_text}
        
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
        
        prompt = _build_tone_prompt(target_keyword, additional_context)
        model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash-exp')
        
        try:
            from google import genai
            api_key = settings.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
            client = genai.Client(api_key=api_key) if api_key else genai.Client()
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
            )
            result_text = response.text if hasattr(response, 'text') else str(response)
            
        except ImportError:
            import google.generativeai as genai_old
            genai_old.configure(api_key=settings.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY'))
            model = genai_old.GenerativeModel(model_name)
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: model.generate_content(prompt)
            )
            result_text = response.text if hasattr(response, 'text') else str(response)
        
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            result = {"analysis": result_text}
        
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
        
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        prompt = _build_tone_prompt(target_keyword, additional_context)
        
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert tone analyst specializing in analyzing communication tone and style."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        result_text = response.choices[0].message.content
        if not result_text:
            raise ValueError("OpenAI API 응답이 비어있습니다.")
        
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            result = {"analysis": result_text}
        
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
            "distribution": {
                "positive": 33,
                "neutral": 34,
                "negative": 33
            },
            "trend": "유지",
            "key_emotional_drivers": ["AI API를 설정하면 더 상세한 분석이 가능합니다."]
        }
    }


def _analyze_context_basic(
    target_keyword: str,
    additional_context: Optional[str]
) -> Dict[str, Any]:
    """기본 맥락 분석"""
    return {
        "context": {
            "social_relevance": "중간",
            "current_issues": ["AI API를 설정하면 더 상세한 분석이 가능합니다."],
            "cultural_context": "기본 분석 모드",
            "temporal_factors": datetime.now().strftime("%Y년 %m월")
        }
    }


def _analyze_tone_basic(
    target_keyword: str,
    additional_context: Optional[str]
) -> Dict[str, Any]:
    """기본 톤 분석"""
    return {
        "tone": {
            "professional": 0.5,
            "positive": 0.5,
            "objective": 0.5,
            "formal": 0.5
        }
    }


def _build_sentiment_prompt(
    target_keyword: str,
    additional_context: Optional[str]
) -> str:
    """감정 분석 프롬프트 생성"""
    current_date = datetime.now().strftime("%Y년 %m월 %d일")
    
    prompt = f"""
당신은 전문적인 감정 분석가입니다. 다음 키워드에 대한 대중의 감정을 분석해주세요.

**분석 대상**: {target_keyword}
**현재 시점**: {current_date}
"""
    if additional_context:
        prompt += f"""
**추가 컨텍스트**:
{additional_context}

"""
    
    prompt += """
다음 형식의 JSON으로 응답해주세요:

{
  "sentiment": {
    "overall": "긍정적/부정적/중립적",
    "score": 72,  // 0-100 점수 (0: 매우 부정적, 100: 매우 긍정적)
    "distribution": {
      "positive": 65,  // 긍정적 비율 (%)
      "neutral": 25,   // 중립적 비율 (%)
      "negative": 10   // 부정적 비율 (%)
    },
    "trend": "향상 중/악화 중/유지",  // 최근 감정 변화 추세
    "key_emotional_drivers": [
      "감정을 이끄는 주요 요인 1",
      "감정을 이끄는 주요 요인 2",
      "감정을 이끄는 주요 요인 3"
    ],
    "emotional_intensity": "높음/중간/낮음",  // 감정 강도
    "sentiment_details": {
      "positive_aspects": ["긍정적 측면 1", "긍정적 측면 2"],
      "negative_aspects": ["부정적 측면 1", "부정적 측면 2"],
      "neutral_aspects": ["중립적 측면 1", "중립적 측면 2"]
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
당신은 전문적인 맥락 분석가입니다. 다음 키워드의 사회적, 문화적, 시기적 맥락을 분석해주세요.

**분석 대상**: {target_keyword}
**현재 시점**: {current_date}
"""
    if additional_context:
        prompt += f"""
**추가 컨텍스트**:
{additional_context}

"""
    
    prompt += """
다음 형식의 JSON으로 응답해주세요:

{
  "context": {
    "social_relevance": "높음/중간/낮음",  // 사회적 관련성
    "current_issues": [
      "현재 사회적 이슈와의 연관성 1",
      "현재 사회적 이슈와의 연관성 2"
    ],
    "cultural_context": "문화적 맥락 설명",
    "temporal_factors": "시기적 특성 설명",
    "regional_context": "지역적 맥락 (한국 시장 중심)",
    "industry_context": "산업적 맥락",
    "related_movements": [
      "관련된 사회적 움직임 1",
      "관련된 사회적 움직임 2"
    ]
  }
}
"""
    return prompt


def _build_tone_prompt(
    target_keyword: str,
    additional_context: Optional[str]
) -> str:
    """톤 분석 프롬프트 생성"""
    
    prompt = f"""
당신은 전문적인 톤 분석가입니다. 다음 키워드와 관련된 언론 및 미디어의 톤을 분석해주세요.

**분석 대상**: {target_keyword}
"""
    if additional_context:
        prompt += f"""
**추가 컨텍스트**:
{additional_context}

"""
    
    prompt += """
다음 형식의 JSON으로 응답해주세요:

{
  "tone": {
    "professional": 0.85,  // 전문성 (0-1)
    "positive": 0.72,      // 긍정성 (0-1)
    "objective": 0.68,     // 객관성 (0-1)
    "formal": 0.75,        // 공식성 (0-1)
    "technical": 0.80,     // 기술성 (0-1)
    "accessible": 0.65,    // 접근성 (0-1)
    "tone_description": "톤에 대한 종합적 설명",
    "primary_tone": "주요 톤 (예: 전문적이고 긍정적)",
    "tone_consistency": "높음/중간/낮음"  // 톤 일관성
  }
}
"""
    return prompt
