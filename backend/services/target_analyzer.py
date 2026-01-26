"""
타겟 분석 서비스
AI를 사용하여 키워드, 오디언스, 경쟁자 분석을 수행합니다.
"""
import logging
from typing import Optional, Dict, Any
import json

from backend.config import settings

logger = logging.getLogger(__name__)


async def analyze_target(
    target_keyword: str,
    target_type: str = "keyword",
    additional_context: Optional[str] = None,
    use_gemini: bool = False
) -> Dict[str, Any]:
    """
    타겟 분석 수행
    
    Args:
        target_keyword: 분석할 타겟 키워드 또는 주제
        target_type: 분석 유형 (keyword, audience, competitor)
        additional_context: 추가 컨텍스트 정보
        use_gemini: Gemini API 사용 여부
        
    Returns:
        분석 결과 딕셔너리
    """
    try:
        logger.info(f"타겟 분석 시작: {target_keyword} (타입: {target_type})")
        
        # AI API 선택
        if use_gemini and settings.GEMINI_API_KEY:
            result = await _analyze_with_gemini(
                target_keyword, target_type, additional_context
            )
        elif settings.OPENAI_API_KEY:
            result = await _analyze_with_openai(
                target_keyword, target_type, additional_context
            )
        else:
            # AI API가 없으면 기본 분석 수행
            result = _analyze_basic(target_keyword, target_type, additional_context)
        
        logger.info(f"타겟 분석 완료: {target_keyword}")
        return result
        
    except Exception as e:
        logger.error(f"타겟 분석 중 오류: {e}")
        raise


async def _analyze_with_gemini(
    target_keyword: str,
    target_type: str,
    additional_context: Optional[str]
) -> Dict[str, Any]:
    """Gemini API를 사용한 분석"""
    try:
        import asyncio
        import os
        
        # 프롬프트 생성
        prompt = _build_analysis_prompt(target_keyword, target_type, additional_context)
        
        # 모델 설정 (기본값: gemini-2.5-flash-preview)
        model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash-preview')
        
        # 새로운 Gemini API 방식 시도 (from google import genai)
        try:
            from google import genai
            
            # API 키 설정 (환경 변수 또는 설정에서)
            api_key = settings.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
            if api_key:
                client = genai.Client(api_key=api_key)
            else:
                # 환경 변수에서 자동으로 가져오기
                client = genai.Client()
            
            # API 호출 (비동기 실행을 위해 run_in_executor 사용)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
            )
            
            # 응답 파싱
            result_text = response.text if hasattr(response, 'text') else str(response)
            
        except ImportError:
            # 새로운 방식이 없으면 기존 방식 시도
            import google.generativeai as genai_old
            
            genai_old.configure(api_key=settings.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY'))
            model = genai_old.GenerativeModel(model_name)
            
            # API 호출 (비동기 실행을 위해 run_in_executor 사용)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: model.generate_content(prompt)
            )
            
            # 응답 파싱
            result_text = response.text if hasattr(response, 'text') else str(response)
        
        # JSON 형식으로 파싱 시도
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            # JSON이 아니면 텍스트로 반환
            result = {
                "analysis": result_text,
                "target_keyword": target_keyword,
                "target_type": target_type
            }
        
        return result
        
    except ImportError as e:
        logger.warning(f"Gemini API 패키지가 설치되지 않았습니다: {e}")
        logger.warning("'pip install google-genai' 또는 'pip install google-generativeai'를 실행해주세요.")
        return _analyze_basic(target_keyword, target_type, additional_context)
    except Exception as e:
        logger.error(f"Gemini API 호출 실패: {e}")
        return _analyze_basic(target_keyword, target_type, additional_context)


async def _analyze_with_openai(
    target_keyword: str,
    target_type: str,
    additional_context: Optional[str]
) -> Dict[str, Any]:
    """OpenAI API를 사용한 분석"""
    try:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # 프롬프트 생성
        prompt = _build_analysis_prompt(target_keyword, target_type, additional_context)
        
        # API 호출
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes targets for marketing and business purposes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        result_text = response.choices[0].message.content
        
        if not result_text:
            raise ValueError("OpenAI API 응답이 비어있습니다.")
        
        # JSON 형식으로 파싱 시도
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            # JSON이 아니면 텍스트로 반환
            result = {
                "analysis": result_text,
                "target_keyword": target_keyword,
                "target_type": target_type
            }
        
        return result
        
    except ImportError:
        logger.warning("openai 패키지가 설치되지 않았습니다.")
        return _analyze_basic(target_keyword, target_type, additional_context)
    except Exception as e:
        logger.error(f"OpenAI API 호출 실패: {e}")
        return _analyze_basic(target_keyword, target_type, additional_context)


def _analyze_basic(
    target_keyword: str,
    target_type: str,
    additional_context: Optional[str]
) -> Dict[str, Any]:
    """기본 분석 (AI API 없이)"""
    logger.info("기본 분석 모드 사용")
    
    result = {
        "target_keyword": target_keyword,
        "target_type": target_type,
        "analysis": {
            "summary": f"{target_keyword}에 대한 {target_type} 분석 결과입니다.",
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
    
    return result


def _build_analysis_prompt(
    target_keyword: str,
    target_type: str,
    additional_context: Optional[str]
) -> str:
    """분석 프롬프트 생성"""
    
    type_descriptions = {
        "keyword": "키워드 분석: 검색 트렌드, 검색량, 경쟁도, 관련 키워드 등을 분석해주세요.",
        "audience": """오디언스 분석: 타겟 고객층의 다음 항목들을 상세히 분석해주세요:
- 인구통계학적 특성 (연령, 성별, 지역, 소득 수준 등)
- 심리적 특성 (라이프스타일, 가치관, 관심사 등)
- 행동 패턴 (구매 행동, 미디어 소비 패턴, 온라인 활동 등)
- 니즈와 페인 포인트
- 선호하는 브랜드 및 서비스
- 마케팅 접근 방법""",
        "competitor": "경쟁자 분석: 주요 경쟁자, 경쟁 우위, 차별화 포인트, 시장 점유율 등을 분석해주세요."
    }
    
    # 오디언스 분석에 특화된 프롬프트
    if target_type == "audience":
        prompt = f"""
다음 타겟 오디언스에 대한 상세한 분석을 수행해주세요.

타겟 오디언스: {target_keyword}
"""
        if additional_context:
            prompt += f"""
추가 컨텍스트:
{additional_context}

"""
        prompt += """
다음 형식의 JSON으로 응답해주세요. 오디언스 분석에 특화된 정보를 포함해주세요:
{
  "summary": "오디언스에 대한 종합적인 요약 (인구통계, 심리적 특성, 행동 패턴 포함)",
  "key_points": [
    "인구통계학적 특성 (연령대, 성별, 지역 등)",
    "심리적 특성 및 라이프스타일",
    "주요 행동 패턴 및 미디어 소비 습관",
    "핵심 니즈 및 페인 포인트"
  ],
  "insights": {
    "demographics": {
      "age_range": "주요 연령대",
      "gender": "성별 분포",
      "location": "주요 지역",
      "income_level": "소득 수준",
      "expected_occupations": ["예상 직업 1", "예상 직업 2", "예상 직업 3"]
    },
    "psychographics": {
      "lifestyle": "라이프스타일 특성",
      "values": "가치관 및 관심사",
      "interests": "주요 관심 분야"
    },
    "behavior": {
      "purchase_behavior": "구매 행동 패턴",
      "media_consumption": "미디어 소비 패턴",
      "online_activity": "온라인 활동 특성"
    },
    "trends": ["트렌드 1", "트렌드 2", ...],
    "opportunities": ["마케팅 기회 1", "마케팅 기회 2", ...],
    "challenges": ["마케팅 도전 과제 1", "마케팅 도전 과제 2", ...]
  },
  "recommendations": [
    "타겟 오디언스에 효과적인 마케팅 전략 1",
    "타겟 오디언스에 효과적인 마케팅 전략 2",
    "타겟 오디언스에 효과적인 마케팅 전략 3"
  ],
  "metrics": {
    "estimated_volume": "예상 오디언스 규모",
    "engagement_level": "참여 수준 (낮음/중간/높음)",
    "growth_potential": "성장 잠재력 (낮음/중간/높음)"
  }
}
"""
    else:
        # 키워드 및 경쟁자 분석용 기본 프롬프트
        prompt = f"""
다음에 대한 {type_descriptions.get(target_type, "분석")}을 수행해주세요.

타겟: {target_keyword}
분석 유형: {target_type}

"""
        if additional_context:
            prompt += f"""
추가 컨텍스트:
{additional_context}

"""
        prompt += """
다음 형식의 JSON으로 응답해주세요:
{
  "summary": "분석 요약",
  "key_points": ["주요 포인트 1", "주요 포인트 2", ...],
  "insights": {
    "trends": ["트렌드 1", "트렌드 2", ...],
    "opportunities": ["기회 1", "기회 2", ...],
    "challenges": ["도전 과제 1", "도전 과제 2", ...]
  },
  "recommendations": ["권장사항 1", "권장사항 2", ...],
  "metrics": {
    "estimated_volume": "예상 검색량/시장 규모",
    "competition_level": "경쟁 수준 (낮음/중간/높음)",
    "growth_potential": "성장 잠재력 (낮음/중간/높음)"
  },
  "target_audience": {
    "expected_occupations": ["이 키워드와 관련된 주요 직업군 1", "직업군 2", "직업군 3"]
  }
}
"""
    
    return prompt
