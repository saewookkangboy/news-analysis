"""
키워드 추천 서비스
관련 키워드, 유사 주제, 경쟁 키워드를 추천합니다.
"""
import logging
from typing import Optional, Dict, Any, List
import json

from backend.config import settings

logger = logging.getLogger(__name__)


async def recommend_keywords(
    target_keyword: str,
    recommendation_type: str = "all",
    max_results: int = 10,
    additional_context: Optional[str] = None,
    use_gemini: bool = False
) -> Dict[str, Any]:
    """
    키워드 추천 수행
    
    Args:
        target_keyword: 기준 키워드
        recommendation_type: 추천 유형 (all, semantic, co_occurring, hierarchical, trending, alternative)
        max_results: 최대 결과 수
        additional_context: 추가 컨텍스트
        use_gemini: Gemini API 사용 여부
        
    Returns:
        추천 키워드 결과
    """
    try:
        logger.info(f"키워드 추천 시작: {target_keyword} (유형: {recommendation_type})")
        
        if use_gemini and settings.GEMINI_API_KEY:
            result = await _recommend_with_gemini(
                target_keyword, recommendation_type, max_results, additional_context
            )
        elif settings.OPENAI_API_KEY:
            result = await _recommend_with_openai(
                target_keyword, recommendation_type, max_results, additional_context
            )
        else:
            result = _recommend_basic(target_keyword, recommendation_type, max_results)
        
        logger.info(f"키워드 추천 완료: {target_keyword}")
        return result
        
    except Exception as e:
        logger.error(f"키워드 추천 중 오류: {e}")
        raise


async def _recommend_with_gemini(
    target_keyword: str,
    recommendation_type: str,
    max_results: int,
    additional_context: Optional[str]
) -> Dict[str, Any]:
    """Gemini API를 사용한 키워드 추천"""
    try:
        import asyncio
        import os
        
        prompt = _build_recommendation_prompt(
            target_keyword, recommendation_type, max_results, additional_context
        )
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
            result = {"recommendations": result_text}
        
        return result
        
    except Exception as e:
        logger.error(f"Gemini 키워드 추천 실패: {e}")
        return _recommend_basic(target_keyword, recommendation_type, max_results)


async def _recommend_with_openai(
    target_keyword: str,
    recommendation_type: str,
    max_results: int,
    additional_context: Optional[str]
) -> Dict[str, Any]:
    """OpenAI API를 사용한 키워드 추천"""
    try:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        prompt = _build_recommendation_prompt(
            target_keyword, recommendation_type, max_results, additional_context
        )
        
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert keyword researcher and SEO specialist who recommends relevant keywords based on semantic similarity, co-occurrence, and market trends."},
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
            result = {"recommendations": result_text}
        
        return result
        
    except Exception as e:
        logger.error(f"OpenAI 키워드 추천 실패: {e}")
        return _recommend_basic(target_keyword, recommendation_type, max_results)


def _recommend_basic(
    target_keyword: str,
    recommendation_type: str,
    max_results: int
) -> Dict[str, Any]:
    """기본 키워드 추천"""
    return {
        "related_keywords": {
            "semantic_similar": [
                {"keyword": f"{target_keyword} 관련 1", "relevance": 0.8},
                {"keyword": f"{target_keyword} 관련 2", "relevance": 0.7}
            ],
            "note": "AI API를 설정하면 더 상세한 추천이 가능합니다."
        }
    }


def _build_recommendation_prompt(
    target_keyword: str,
    recommendation_type: str,
    max_results: int,
    additional_context: Optional[str]
) -> str:
    """키워드 추천 프롬프트 생성"""
    
    type_descriptions = {
        "all": "모든 유형의 관련 키워드",
        "semantic": "의미적으로 유사한 키워드",
        "co_occurring": "동시에 자주 출현하는 키워드",
        "hierarchical": "계층적 관계의 키워드 (상위/하위 개념)",
        "trending": "최근 트렌드가 있는 관련 키워드",
        "alternative": "대안이 될 수 있는 키워드"
    }
    
    prompt = f"""
당신은 전문적인 키워드 연구 및 SEO 전문가입니다. 다음 키워드와 관련된 다양한 키워드를 추천해주세요.

**기준 키워드**: {target_keyword}
**추천 유형**: {type_descriptions.get(recommendation_type, recommendation_type)}
**최대 결과 수**: {max_results}
"""
    if additional_context:
        prompt += f"""
**추가 컨텍스트**:
{additional_context}

"""
    
    if recommendation_type == "all":
        prompt += """
다음 형식의 JSON으로 응답해주세요. 다양한 관점에서 관련 키워드를 추천해주세요:

{
  "related_keywords": {
    "semantic_similar": [
      {"keyword": "의미적으로 유사한 키워드 1", "relevance": 0.92, "description": "유사성 설명"},
      {"keyword": "의미적으로 유사한 키워드 2", "relevance": 0.88, "description": "유사성 설명"}
    ],
    "co_occurring": [
      {"keyword": "동시 출현 키워드 1", "frequency": 0.75, "description": "출현 패턴 설명"},
      {"keyword": "동시 출현 키워드 2", "frequency": 0.68, "description": "출현 패턴 설명"}
    ],
    "hierarchical": {
      "broader": [
        {"keyword": "상위 개념 키워드 1", "level": "상위", "description": "관계 설명"},
        {"keyword": "상위 개념 키워드 2", "level": "상위", "description": "관계 설명"}
      ],
      "narrower": [
        {"keyword": "하위 개념 키워드 1", "level": "하위", "description": "관계 설명"},
        {"keyword": "하위 개념 키워드 2", "level": "하위", "description": "관계 설명"}
      ]
    }
  },
  "trending_related": [
    {"keyword": "트렌드 관련 키워드 1", "trend": "상승", "growth_rate": "높음", "description": "트렌드 설명"},
    {"keyword": "트렌드 관련 키워드 2", "trend": "상승", "growth_rate": "중간", "description": "트렌드 설명"}
  ],
  "alternative_keywords": [
    {"keyword": "대안 키워드 1", "similarity": 0.85, "use_case": "사용 사례 설명"},
    {"keyword": "대안 키워드 2", "similarity": 0.80, "use_case": "사용 사례 설명"}
  ],
  "long_tail_keywords": [
    {"keyword": "롱테일 키워드 1", "search_intent": "검색 의도", "competition": "낮음"},
    {"keyword": "롱테일 키워드 2", "search_intent": "검색 의도", "competition": "낮음"}
  ],
  "recommendation_summary": "추천 키워드에 대한 종합 요약"
}
"""
    elif recommendation_type == "semantic":
        prompt += """
다음 형식의 JSON으로 응답해주세요. 의미적으로 유사한 키워드만 추천해주세요:

{
  "semantic_similar": [
    {"keyword": "의미적으로 유사한 키워드 1", "relevance": 0.92, "description": "유사성 설명"},
    {"keyword": "의미적으로 유사한 키워드 2", "relevance": 0.88, "description": "유사성 설명"}
  ]
}
"""
    elif recommendation_type == "co_occurring":
        prompt += """
다음 형식의 JSON으로 응답해주세요. 동시에 자주 출현하는 키워드만 추천해주세요:

{
  "co_occurring": [
    {"keyword": "동시 출현 키워드 1", "frequency": 0.75, "description": "출현 패턴 설명"},
    {"keyword": "동시 출현 키워드 2", "frequency": 0.68, "description": "출현 패턴 설명"}
  ]
}
"""
    elif recommendation_type == "hierarchical":
        prompt += """
다음 형식의 JSON으로 응답해주세요. 계층적 관계의 키워드만 추천해주세요:

{
  "hierarchical": {
    "broader": [
      {"keyword": "상위 개념 키워드 1", "level": "상위", "description": "관계 설명"},
      {"keyword": "상위 개념 키워드 2", "level": "상위", "description": "관계 설명"}
    ],
    "narrower": [
      {"keyword": "하위 개념 키워드 1", "level": "하위", "description": "관계 설명"},
      {"keyword": "하위 개념 키워드 2", "level": "하위", "description": "관계 설명"}
    ]
  }
}
"""
    elif recommendation_type == "trending":
        prompt += """
다음 형식의 JSON으로 응답해주세요. 최근 트렌드가 있는 관련 키워드만 추천해주세요:

{
  "trending_related": [
    {"keyword": "트렌드 관련 키워드 1", "trend": "상승", "growth_rate": "높음", "description": "트렌드 설명"},
    {"keyword": "트렌드 관련 키워드 2", "trend": "상승", "growth_rate": "중간", "description": "트렌드 설명"}
  ]
}
"""
    elif recommendation_type == "alternative":
        prompt += """
다음 형식의 JSON으로 응답해주세요. 대안이 될 수 있는 키워드만 추천해주세요:

{
  "alternative_keywords": [
    {"keyword": "대안 키워드 1", "similarity": 0.85, "use_case": "사용 사례 설명"},
    {"keyword": "대안 키워드 2", "similarity": 0.80, "use_case": "사용 사례 설명"}
  ]
}
"""
    else:
        prompt += """
다음 형식의 JSON으로 응답해주세요:

{
  "related_keywords": {
    "semantic_similar": [
      {"keyword": "관련 키워드 1", "relevance": 0.92},
      {"keyword": "관련 키워드 2", "relevance": 0.88}
    ]
  }
}
"""
    
    return prompt
