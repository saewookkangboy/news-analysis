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
    use_gemini: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    타겟 분석 수행
    
    Args:
        target_keyword: 분석할 타겟 키워드 또는 주제
        target_type: 분석 유형 (keyword, audience, competitor)
        additional_context: 추가 컨텍스트 정보
        use_gemini: Gemini API 사용 여부
        start_date: 분석 시작일 (YYYY-MM-DD 형식)
        end_date: 분석 종료일 (YYYY-MM-DD 형식)
        
    Returns:
        분석 결과 딕셔너리
    """
    try:
        logger.info(f"타겟 분석 시작: {target_keyword} (타입: {target_type})")
        
        # AI API 선택
        if use_gemini and settings.GEMINI_API_KEY:
            result = await _analyze_with_gemini(
                target_keyword, target_type, additional_context, start_date, end_date
            )
        elif settings.OPENAI_API_KEY:
            result = await _analyze_with_openai(
                target_keyword, target_type, additional_context, start_date, end_date
            )
        else:
            # AI API가 없으면 기본 분석 수행
            result = _analyze_basic(target_keyword, target_type, additional_context, start_date, end_date)
        
        logger.info(f"타겟 분석 완료: {target_keyword}")
        return result
        
    except Exception as e:
        logger.error(f"타겟 분석 중 오류: {e}")
        raise


async def _analyze_with_gemini(
    target_keyword: str,
    target_type: str,
    additional_context: Optional[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """Gemini API를 사용한 분석"""
    try:
        import asyncio
        import os
        
        # 프롬프트 생성
        prompt = _build_analysis_prompt(target_keyword, target_type, additional_context, start_date, end_date)
        
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
        if not result_text:
            raise ValueError("Gemini API 응답이 비어있습니다.")
        
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
        return _analyze_basic(target_keyword, target_type, additional_context, start_date, end_date)
    except Exception as e:
        logger.error(f"Gemini API 호출 실패: {e}")
        return _analyze_basic(target_keyword, target_type, additional_context, start_date, end_date)


async def _analyze_with_openai(
    target_keyword: str,
    target_type: str,
    additional_context: Optional[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """OpenAI API를 사용한 분석"""
    try:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # 프롬프트 생성
        prompt = _build_analysis_prompt(target_keyword, target_type, additional_context, start_date, end_date)
        
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
            # result_text가 문자열인지 확인
            if isinstance(result_text, str):
                result = json.loads(result_text)
            else:
                result = {"analysis": str(result_text), "target_keyword": target_keyword, "target_type": target_type}
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
        return _analyze_basic(target_keyword, target_type, additional_context, start_date, end_date)
    except Exception as e:
        logger.error(f"OpenAI API 호출 실패: {e}")
        return _analyze_basic(target_keyword, target_type, additional_context, start_date, end_date)


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
    
    result = {
        "target_keyword": target_keyword,
        "target_type": target_type,
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


def _build_analysis_prompt(
    target_keyword: str,
    target_type: str,
    additional_context: Optional[str],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> str:
    """분석 프롬프트 생성"""
    
    # 기간 정보 추가
    period_info = ""
    period_instruction = ""
    if start_date and end_date:
        period_info = f"""
**분석 기간**: {start_date} ~ {end_date}
"""
        period_instruction = f"""
**중요**: 반드시 {start_date}부터 {end_date}까지의 기간 동안의 데이터, 트렌드, 변화, 패턴을 중심으로 분석해주세요. 
이 기간 동안의 시계열 변화, 계절성, 이벤트, 뉴스, 시장 동향 등을 반드시 포함하여 매우 상세하게 분석해야 합니다.
"""
    elif start_date:
        period_info = f"""
**시작일**: {start_date}
"""
        period_instruction = f"""
**중요**: 반드시 {start_date} 이후의 트렌드와 변화를 중심으로 분석해주세요. 
이 날짜 이후의 시계열 변화, 뉴스, 시장 동향 등을 반드시 포함하여 매우 상세하게 분석해야 합니다.
"""
    elif end_date:
        period_info = f"""
**종료일**: {end_date}
"""
        period_instruction = f"""
**중요**: 반드시 {end_date}까지의 데이터를 기반으로 분석해주세요. 
이 날짜까지의 시계열 변화, 뉴스, 시장 동향 등을 반드시 포함하여 매우 상세하게 분석해야 합니다.
"""
    
    # 오디언스 분석에 특화된 프롬프트
    if target_type == "audience":
        prompt = f"""
당신은 전문적인 마케팅 및 소비자 행동 분석가입니다. 다음 타겟 오디언스에 대한 매우 상세하고 심층적인 분석을 수행해주세요.

**분석 대상**: {target_keyword}
{period_info}
{period_instruction}
"""
        if additional_context:
            prompt += f"""
**추가 컨텍스트**:
{additional_context}

"""
        prompt += """
다음 항목들을 매우 상세하게 분석하여 JSON 형식으로 응답해주세요. 각 항목은 구체적이고 실용적인 정보를 포함해야 합니다. 
특히 지정된 기간 동안의 변화, 트렌드, 패턴을 반드시 포함하여 분석해주세요:

{
  "summary": "오디언스에 대한 종합적인 요약 (3-5문단, 인구통계, 심리적 특성, 행동 패턴, 니즈, 기회 등을 포괄적으로 설명)",
  "key_points": [
    "인구통계학적 특성의 핵심 요약 (연령대, 성별, 지역, 소득 수준 등)",
    "심리적 특성 및 라이프스타일의 주요 특징",
    "주요 행동 패턴 및 미디어 소비 습관의 특징",
    "핵심 니즈 및 페인 포인트 (3-5개 구체적 사례)",
    "이 오디언스의 고유한 특성과 차별점"
  ],
  "insights": {
    "demographics": {
      "age_range": "주요 연령대 (예: 25-35세) 및 각 연령대별 특성",
      "gender": "성별 분포 (예: 남성 60%, 여성 40%) 및 성별별 특성",
      "location": "주요 지역 (도시/지역별 분포 및 특성)",
      "income_level": "소득 수준 (구체적 금액 범위 및 소비 패턴)",
      "education_level": "교육 수준 및 직업군 분포",
      "family_status": "가족 구성 (1인 가구, 기혼, 자녀 유무 등)",
      "expected_occupations": ["예상 직업 1 (상세 설명 포함)", "예상 직업 2", "예상 직업 3", "예상 직업 4", "예상 직업 5"]
    },
    "psychographics": {
      "lifestyle": "라이프스타일 특성 (일상 패턴, 여가 활동, 생활 방식 등 상세 설명)",
      "values": "가치관 및 신념 (중요하게 생각하는 가치 5-7개)",
      "interests": "주요 관심 분야 (구체적인 관심사 및 취미)",
      "personality_traits": "성격 특성 (MBTI 유형 추정, 주요 성격 특성)",
      "aspirations": "열망 및 목표 (이 오디언스가 추구하는 것)",
      "fears_concerns": "우려사항 및 두려움 (이 오디언스가 걱정하는 것)"
    },
    "behavior": {
      "purchase_behavior": "구매 행동 패턴 (구매 주기, 구매 채널, 구매 결정 요인, 가격 민감도 등 상세 설명)",
      "media_consumption": "미디어 소비 패턴 (선호하는 미디어, 소비 시간, 콘텐츠 선호도 등)",
      "online_activity": "온라인 활동 특성 (주로 사용하는 플랫폼, 온라인 쇼핑 패턴, SNS 사용 등)",
      "brand_loyalty": "브랜드 충성도 (브랜드 선호도, 전환 가능성 등)",
      "decision_making": "의사결정 프로세스 (구매 결정에 영향을 미치는 요소, 결정 시간 등)"
    },
    "trends": ["지정된 기간 동안의 트렌드 1 (상세 설명 및 시계열 변화 포함)", "트렌드 2", "트렌드 3", "트렌드 4", "트렌드 5"],
    "opportunities": ["마케팅 기회 1 (구체적 전략 포함)", "마케팅 기회 2", "마케팅 기회 3", "마케팅 기회 4", "마케팅 기회 5"],
    "challenges": ["마케팅 도전 과제 1 (해결 방안 포함)", "마케팅 도전 과제 2", "마케팅 도전 과제 3", "마케팅 도전 과제 4"]
  },
  "recommendations": [
    "타겟 오디언스에 효과적인 마케팅 전략 1 (구체적 실행 방안 포함)",
    "타겟 오디언스에 효과적인 마케팅 전략 2",
    "타겟 오디언스에 효과적인 마케팅 전략 3",
    "타겟 오디언스에 효과적인 마케팅 전략 4",
    "타겟 오디언스에 효과적인 마케팅 전략 5"
  ],
  "metrics": {
    "estimated_volume": "예상 오디언스 규모 (구체적 숫자 또는 범위)",
    "engagement_level": "참여 수준 (낮음/중간/높음) 및 근거",
    "growth_potential": "성장 잠재력 (낮음/중간/높음) 및 근거",
    "market_value": "시장 가치 추정 (구매력, 소비 규모 등)",
    "accessibility": "접근 난이도 (이 오디언스에 도달하기 어려운 정도)"
  }
}
"""
    elif target_type == "keyword":
        # 키워드 분석에 특화된 매우 상세한 프롬프트
        prompt = f"""
당신은 전문적인 SEO 및 키워드 분석가입니다. 다음 키워드에 대한 매우 상세하고 심층적인 분석을 수행해주세요.

**분석 대상 키워드**: {target_keyword}
{period_info}
{period_instruction}
"""
        if additional_context:
            prompt += f"""
**추가 컨텍스트**:
{additional_context}

"""
        prompt += """
다음 항목들을 매우 상세하게 분석하여 JSON 형식으로 응답해주세요. 각 항목은 구체적이고 실용적인 정보를 포함해야 합니다.
특히 지정된 기간 동안의 검색량 변화, 트렌드, 계절성, 이벤트 등을 반드시 포함하여 분석해주세요:

{
  "summary": "키워드에 대한 종합적인 요약 (3-5문단, 검색 의도, 경쟁 환경, 트렌드, 기회 등을 포괄적으로 설명)",
  "key_points": [
    "검색 의도 및 사용자 목적의 핵심 요약",
    "경쟁 환경 및 시장 상황의 주요 특징",
    "검색 트렌드 및 시계열 변화 패턴",
    "관련 키워드 및 롱테일 키워드 기회",
    "이 키워드의 고유한 특성과 차별점"
  ],
  "insights": {
    "search_intent": {
      "primary_intent": "주요 검색 의도 (Informational/Navigational/Transactional/Commercial) 및 근거",
      "intent_breakdown": "의도별 분포 (예: 정보성 60%, 거래성 30%, 탐색성 10%)",
      "user_journey_stage": "사용자 여정 단계 (인지/고려/구매/유지) 및 각 단계별 특성",
      "search_context": "검색 맥락 (언제, 왜, 어떻게 검색하는지)"
    },
    "competition": {
      "competition_level": "경쟁 수준 (낮음/중간/높음) 및 구체적 근거",
      "top_competitors": ["주요 경쟁 페이지/사이트 1", "주요 경쟁 페이지/사이트 2", "주요 경쟁 페이지/사이트 3", "주요 경쟁 페이지/사이트 4", "주요 경쟁 페이지/사이트 5"],
      "competitor_analysis": "경쟁자들의 강점과 약점 분석",
      "market_gap": "시장 공백 및 차별화 기회"
    },
    "trends": {
      "search_volume_trend": "지정된 기간 동안의 검색량 트렌드 (증가/감소/안정) 및 구체적 변화율, 예상 검색량 범위",
      "seasonal_patterns": "지정된 기간 동안의 계절성 패턴 (특정 시기에 검색량이 증가/감소하는지, 구체적 날짜 및 이유)",
      "trending_topics": ["지정된 기간 동안의 관련 트렌딩 토픽 1 (발생 시기 및 이유 포함)", "트렌딩 토픽 2", "트렌딩 토픽 3", "트렌딩 토픽 4", "트렌딩 토픽 5"],
      "period_analysis": "지정된 기간 동안의 검색량 변화 상세 분석 (월별/주별 변화, 피크 시기, 하락 시기 등)",
      "future_outlook": "향후 전망 (지정된 기간의 패턴을 기반으로 한 향후 6개월-1년간의 예상 트렌드)"
    },
    "related_keywords": {
      "semantic_keywords": ["의미적으로 관련된 키워드 1", "의미적으로 관련된 키워드 2", "의미적으로 관련된 키워드 3", "의미적으로 관련된 키워드 4", "의미적으로 관련된 키워드 5"],
      "long_tail_keywords": ["롱테일 키워드 1 (검색량 및 경쟁도 포함)", "롱테일 키워드 2", "롱테일 키워드 3", "롱테일 키워드 4", "롱테일 키워드 5"],
      "question_keywords": ["질문형 키워드 1", "질문형 키워드 2", "질문형 키워드 3", "질문형 키워드 4", "질문형 키워드 5"],
      "comparison_keywords": ["비교형 키워드 1", "비교형 키워드 2", "비교형 키워드 3"]
    },
    "opportunities": ["SEO 기회 1 (구체적 실행 방안 포함)", "SEO 기회 2", "SEO 기회 3", "SEO 기회 4", "SEO 기회 5"],
    "challenges": ["SEO 도전 과제 1 (해결 방안 포함)", "SEO 도전 과제 2", "SEO 도전 과제 3", "SEO 도전 과제 4"]
  },
  "recommendations": [
    "키워드 최적화 전략 1 (구체적 실행 방안 포함)",
    "키워드 최적화 전략 2",
    "키워드 최적화 전략 3",
    "키워드 최적화 전략 4",
    "키워드 최적화 전략 5"
  ],
  "metrics": {
    "estimated_volume": "예상 검색량 (월간 검색량 범위 또는 추정치)",
    "competition_level": "경쟁 수준 (낮음/중간/높음) 및 구체적 근거",
    "growth_potential": "성장 잠재력 (낮음/중간/높음) 및 근거",
    "difficulty_score": "난이도 점수 (1-100) 및 근거",
    "opportunity_score": "기회 점수 (1-100) 및 근거"
  },
  "target_audience": {
    "expected_occupations": ["이 키워드와 관련된 주요 직업군 1", "직업군 2", "직업군 3", "직업군 4", "직업군 5"]
  }
}
"""
    else:  # competitor
        # 경쟁자 분석에 특화된 매우 상세한 프롬프트
        prompt = f"""
당신은 전문적인 경쟁 분석 및 시장 조사 전문가입니다. 다음 경쟁사 또는 경쟁 키워드에 대한 매우 상세하고 심층적인 분석을 수행해주세요.

**분석 대상**: {target_keyword}
{period_info}
{period_instruction}
"""
        if additional_context:
            prompt += f"""
**추가 컨텍스트**:
{additional_context}

"""
        prompt += """
다음 항목들을 매우 상세하게 분석하여 JSON 형식으로 응답해주세요. 각 항목은 구체적이고 실용적인 정보를 포함해야 합니다.
특히 지정된 기간 동안의 시장 변화, 경쟁자 움직임, 시장 점유율 변화 등을 반드시 포함하여 분석해주세요:

{
  "summary": "경쟁 환경에 대한 종합적인 요약 (3-5문단, 주요 경쟁자, 시장 구조, 경쟁 강도, 기회 등을 포괄적으로 설명)",
  "key_points": [
    "경쟁 환경의 핵심 요약 (시장 구조, 경쟁 강도 등)",
    "주요 경쟁자의 강점과 약점",
    "시장 포지셔닝 및 차별화 포인트",
    "경쟁 우위 확보 기회",
    "이 시장의 고유한 특성과 차별점"
  ],
  "insights": {
    "competitive_environment": {
      "main_competitors": ["주요 경쟁자 1 (상세 정보 포함)", "주요 경쟁자 2", "주요 경쟁자 3", "주요 경쟁자 4", "주요 경쟁자 5"],
      "competition_intensity": "경쟁 강도 (낮음/중간/높음) 및 구체적 근거",
      "market_structure": "시장 구조 (과점/독점/완전경쟁 등) 및 특성",
      "market_positioning": "시장 포지셔닝 맵 (가격-품질, 기능-서비스 등)",
      "barriers_to_entry": "진입 장벽 (기술적, 자본적, 규제적 등)",
      "market_size": "시장 규모 추정 및 성장률"
    },
    "competitor_analysis": {
      "strengths": ["경쟁자의 주요 강점 1 (구체적 사례 포함)", "강점 2", "강점 3", "강점 4", "강점 5"],
      "weaknesses": ["경쟁자의 약점 1 (구체적 사례 포함)", "약점 2", "약점 3", "약점 4", "약점 5"],
      "differentiation_points": ["차별화 포인트 1 (구체적 전략 포함)", "차별화 포인트 2", "차별화 포인트 3", "차별화 포인트 4", "차별화 포인트 5"],
      "market_share": "시장 점유율 추정 (주요 경쟁자별)",
      "pricing_strategy": "경쟁자의 가격 전략 분석",
      "marketing_strategy": "경쟁자의 마케팅 전략 분석",
      "technology_stack": "경쟁자의 기술 스택 및 혁신 수준"
    },
    "trends": {
      "market_trends": ["지정된 기간 동안의 시장 트렌드 1 (상세 설명 및 시계열 변화 포함)", "시장 트렌드 2", "시장 트렌드 3", "시장 트렌드 4", "시장 트렌드 5"],
      "competitor_movements": ["지정된 기간 동안의 경쟁자 움직임 1 (구체적 시기 및 내용)", "경쟁자 움직임 2", "경쟁자 움직임 3"],
      "industry_changes": "지정된 기간 동안의 산업 전반의 변화 및 영향 (구체적 시기 및 사건 포함)",
      "period_analysis": "지정된 기간 동안의 시장 점유율, 경쟁 강도, 진입/퇴출 등의 변화 상세 분석"
    },
    "opportunities": ["경쟁 우위 확보 기회 1 (구체적 실행 방안 포함)", "기회 2", "기회 3", "기회 4", "기회 5"],
    "challenges": ["경쟁 도전 과제 1 (해결 방안 포함)", "도전 과제 2", "도전 과제 3", "도전 과제 4"]
  },
  "strategic_recommendations": {
    "competitive_advantages": ["경쟁 우위 확보 방안 1 (구체적 전략 포함)", "방안 2", "방안 3", "방안 4", "방안 5"],
    "market_entry_strategy": "시장 진입 전략 (신규 진입 시) 또는 시장 확대 전략 (기존 진입 시)",
    "content_differentiation": ["콘텐츠 차별화 전략 1 (구체적 실행 방안)", "전략 2", "전략 3", "전략 4", "전략 5"],
    "pricing_strategy": "가격 전략 제안 (경쟁자 대비)",
    "partnership_opportunities": "파트너십 기회 및 협력 방안"
  },
  "recommendations": [
    "경쟁 전략 1 (구체적 실행 방안 포함)",
    "경쟁 전략 2",
    "경쟁 전략 3",
    "경쟁 전략 4",
    "경쟁 전략 5"
  ],
  "metrics": {
    "competition_level": "경쟁 수준 (낮음/중간/높음) 및 구체적 근거",
    "market_opportunity": "시장 기회 크기 (낮음/중간/높음) 및 근거",
    "differentiation_potential": "차별화 가능성 (낮음/중간/높음) 및 근거",
    "risk_level": "위험 수준 (낮음/중간/높음) 및 주요 위험 요소",
    "success_probability": "성공 확률 추정 (낮음/중간/높음) 및 근거"
  }
}
"""
    
    return prompt
