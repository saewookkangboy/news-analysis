"""
키워드 추천 서비스
관련 키워드, 유사 주제, 경쟁 키워드를 추천합니다.
"""
import logging
from typing import Optional, Dict, Any, List
import json

from backend.config import settings
from backend.utils.token_optimizer import (
    optimize_prompt, estimate_tokens, get_max_tokens_for_model, optimize_additional_context
)

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
        
        # API 키 확인 (환경 변수에서 직접 확인 - Vercel 호환성)
        import os
        from backend.config import settings
        gemini_key = settings.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
        openai_key = settings.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY')
        
        if use_gemini and gemini_key:
            result = await _recommend_with_gemini(
                target_keyword, recommendation_type, max_results, additional_context
            )
        elif openai_key:
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
        
        # 추가 컨텍스트 최적화
        additional_context_optimized = optimize_additional_context(additional_context, max_length=300)
        prompt = _build_recommendation_prompt(
            target_keyword, recommendation_type, max_results, additional_context_optimized
        )
        prompt = optimize_prompt(prompt, max_length=5000)  # 프롬프트 최적화
        
        model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash')
        
        # 시스템 메시지와 프롬프트 결합 (최적화)
        system_message = "You are a senior keyword researcher. Respond ONLY in valid JSON format."
        full_prompt = f"{system_message}\n\n{prompt}\n\nJSON 형식으로만 응답하세요."
        
        # 토큰 수 계산
        full_prompt_tokens = estimate_tokens(full_prompt)
        max_output_tokens = get_max_tokens_for_model(model_name, full_prompt_tokens)
        
        try:
            from google import genai
            api_key = settings.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
            client = genai.Client(api_key=api_key) if api_key else genai.Client()
            
            loop = asyncio.get_event_loop()
            try:
                # JSON 응답 강제 시도 (새로운 API)
                try:
                    # config 파라미터 시도
                    response = await loop.run_in_executor(
                        None,
                        lambda: client.models.generate_content(
                            model=model_name,
                            contents=full_prompt,
                            config={
                                "response_mime_type": "application/json",
                                "max_output_tokens": max_output_tokens
                            }
                        )
                    )
                except (TypeError, AttributeError) as e:
                    # config가 지원되지 않는 경우 generation_config 시도
                    logger.warning(f"config 파라미터 미지원, generation_config 시도: {e}")
                    try:
                        from google.genai.types import GenerationConfig
                        gen_config = GenerationConfig(
                            response_mime_type="application/json",
                            max_output_tokens=max_output_tokens
                        )
                        response = await loop.run_in_executor(
                            None,
                            lambda: client.models.generate_content(
                                model=model_name,
                                contents=full_prompt,
                                generation_config=gen_config
                            )
                        )
                    except (TypeError, AttributeError, ImportError) as e2:
                        # generation_config도 실패하면 일반 모드로 재시도
                        logger.warning(f"generation_config도 실패, 일반 모드로 재시도: {e2}")
                        response = await loop.run_in_executor(
                            None,
                            lambda: client.models.generate_content(
                                model=model_name,
                                contents=full_prompt,
                                config={
                                    "max_output_tokens": max_output_tokens
                                }
                            )
                        )
            except Exception as e:
                logger.warning(f"JSON 응답 강제 실패, 일반 모드로 재시도: {e}")
                response = await loop.run_in_executor(
                    None,
                    lambda: client.models.generate_content(
                        model=model_name,
                        contents=full_prompt
                    )
                )
            result_text = response.text if hasattr(response, 'text') else str(response)
            
        except ImportError:
            import google.generativeai as genai_old
            genai_old.configure(api_key=settings.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY'))
            model = genai_old.GenerativeModel(model_name)
            
            # 시스템 메시지와 프롬프트 결합 (최적화)
            system_message = "You are a senior keyword researcher. Respond ONLY in valid JSON format."
            full_prompt_old = f"{system_message}\n\n{prompt}\n\nJSON 형식으로만 응답하세요."
            
            # 토큰 수 계산
            full_prompt_tokens = estimate_tokens(full_prompt_old)
            max_output_tokens = get_max_tokens_for_model(model_name, full_prompt_tokens)
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: model.generate_content(full_prompt_old)
            )
            result_text = response.text if hasattr(response, 'text') else str(response)
        
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
                result = {"related_keywords": {"error": "JSON 파싱 실패", "raw_response": clean_text[:500]}}
        
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
        import os
        
        # API 키 확인 (환경 변수에서 직접 읽기 - Vercel 호환성)
        api_key = settings.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        
        client = AsyncOpenAI(api_key=api_key)
        
        # 추가 컨텍스트 최적화
        additional_context_optimized = optimize_additional_context(additional_context, max_length=300)
        prompt = _build_recommendation_prompt(
            target_keyword, recommendation_type, max_results, additional_context_optimized
        )
        prompt = optimize_prompt(prompt, max_length=5000)  # 프롬프트 최적화
        
        system_message = """You are a senior keyword researcher and SEO strategy consultant.
Provide comprehensive keyword recommendations in JSON format.
Your recommendations must be data-driven, market-specific (Korean market), and actionable."""
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
                result = {"related_keywords": {"error": "JSON 파싱 실패", "raw_response": clean_text[:500]}}
        
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
                {
                    "keyword": f"{target_keyword} 관련 1",
                    "relevance": 0.8,
                    "description": "기본 추천 모드입니다.",
                    "estimated_volume": "AI API 설정 필요",
                    "competition": "중간",
                    "search_intent": "정보성",
                    "use_case": "AI API를 설정하면 더 상세한 추천이 가능합니다."
                },
                {
                    "keyword": f"{target_keyword} 관련 2",
                    "relevance": 0.7,
                    "description": "기본 추천 모드입니다.",
                    "estimated_volume": "AI API 설정 필요",
                    "competition": "중간",
                    "search_intent": "정보성",
                    "use_case": "AI API를 설정하면 더 상세한 추천이 가능합니다."
                }
            ],
            "co_occurring": [
                {
                    "keyword": f"{target_keyword} 동시 출현 1",
                    "frequency": 0.6,
                    "description": "기본 추천 모드입니다.",
                    "co_occurrence_context": "AI API 설정 필요",
                    "estimated_volume": "AI API 설정 필요",
                    "competition": "중간",
                    "use_case": "AI API를 설정하면 더 상세한 추천이 가능합니다."
                }
            ],
            "hierarchical": {
                "broader": [
                    {
                        "keyword": f"{target_keyword} 상위 개념",
                        "level": "상위",
                        "description": "기본 추천 모드입니다.",
                        "estimated_volume": "AI API 설정 필요",
                        "competition": "중간",
                        "use_case": "AI API를 설정하면 더 상세한 추천이 가능합니다."
                    }
                ],
                "narrower": [
                    {
                        "keyword": f"{target_keyword} 하위 개념",
                        "level": "하위",
                        "description": "기본 추천 모드입니다.",
                        "estimated_volume": "AI API 설정 필요",
                        "competition": "중간",
                        "use_case": "AI API를 설정하면 더 상세한 추천이 가능합니다."
                    }
                ]
            }
        },
        "trending_related": [
            {
                "keyword": f"{target_keyword} 트렌드 1",
                "trend": "유지",
                "growth_rate": "중간",
                "description": "기본 추천 모드입니다.",
                "trend_period": "AI API 설정 필요",
                "estimated_volume": "AI API 설정 필요",
                "competition": "중간",
                "opportunity_score": 0.6,
                "use_case": "AI API를 설정하면 더 상세한 추천이 가능합니다."
            }
        ],
        "alternative_keywords": [
            {
                "keyword": f"{target_keyword} 대안 1",
                "similarity": 0.75,
                "use_case": "기본 추천 모드입니다.",
                "estimated_volume": "AI API 설정 필요",
                "competition": "중간",
                "advantage": "AI API 설정 필요",
                "disadvantage": "AI API 설정 필요"
            }
        ],
        "long_tail_keywords": [
            {
                "keyword": f"{target_keyword} 롱테일",
                "search_intent": "정보성",
                "competition": "낮음",
                "estimated_volume": "AI API 설정 필요",
                "conversion_potential": "중간",
                "description": "기본 추천 모드입니다.",
                "use_case": "AI API를 설정하면 더 상세한 추천이 가능합니다."
            }
        ],
        "question_keywords": [
            {
                "keyword": f"{target_keyword} 질문형",
                "question_type": "무엇",
                "estimated_volume": "AI API 설정 필요",
                "competition": "낮음",
                "answer_opportunity": "AI API 설정 필요",
                "use_case": "AI API를 설정하면 더 상세한 추천이 가능합니다."
            }
        ],
        "recommendation_summary": {
            "total_keywords": "기본 추천 모드",
            "top_opportunities": [
                "AI API를 설정하여 최고 기회 키워드를 발견하세요."
            ],
            "strategic_recommendations": [
                "OpenAI 또는 Gemini API 키를 환경 변수에 설정하세요.",
                "API 키 설정 후 서버를 재시작하고 다시 추천을 시도하세요."
            ],
            "priority_keywords": [
                {
                    "keyword": "AI API 설정",
                    "priority": "높음",
                    "reason": "더 상세한 키워드 추천을 받기 위해 필수입니다.",
                    "action": "환경 변수에 OPENAI_API_KEY 또는 GEMINI_API_KEY 설정"
                }
            ]
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
당신은 15년 이상의 경력을 가진 전문 키워드 연구 및 SEO 전략 컨설턴트입니다.
다음 키워드와 관련된 다양한 키워드를 매우 상세하고 심층적으로 추천해주세요.

**기준 키워드**: {target_keyword}
**추천 유형**: {type_descriptions.get(recommendation_type, recommendation_type)}
**최대 결과 수**: {max_results}

**분석 목적**: 이 키워드 추천은 SEO 전략, 콘텐츠 기획, 키워드 타겟팅, 경쟁 분석에 활용됩니다.
따라서 모든 추천은 실행 가능한 인사이트와 구체적인 사용 가이드를 포함해야 합니다.
"""
    if additional_context:
        prompt += f"""
**추가 컨텍스트**:
{additional_context}

"""
    
    if recommendation_type == "all":
        prompt += """
**중요 지시사항**:
1. 반드시 유효한 JSON 형식으로만 응답해야 합니다. 마크다운 코드 블록(```json)을 사용하지 마세요.
2. MECE 원칙을 엄격히 준수하여 각 키워드 카테고리가 상호 배타적이면서 완전 포괄적이어야 합니다.
3. 각 키워드에 대해 검색량 추정, 경쟁도, 검색 의도, 사용 사례 등 상세 정보를 제공해야 합니다.
4. 한국 시장에 특화된 키워드를 우선 추천해야 합니다.
5. 최근 트렌드를 반영한 키워드를 포함해야 합니다.

다음 JSON 구조를 정확히 따르면서 각 필드를 매우 상세하게 작성해주세요:

{
  "related_keywords": {
    "semantic_similar": [
      {
        "keyword": "의미적으로 유사한 키워드 1",
        "relevance": 0.92,
        "description": "유사성에 대한 상세 설명",
        "estimated_volume": "월간 검색량 추정 (예: 1,000-5,000)",
        "competition": "낮음/중간/높음",
        "search_intent": "정보성/거래성/탐색성",
        "use_case": "사용 사례 및 활용 방안"
      },
      {
        "keyword": "의미적으로 유사한 키워드 2",
        "relevance": 0.88,
        "description": "유사성에 대한 상세 설명",
        "estimated_volume": "월간 검색량 추정",
        "competition": "낮음/중간/높음",
        "search_intent": "정보성/거래성/탐색성",
        "use_case": "사용 사례 및 활용 방안"
      },
      {
        "keyword": "의미적으로 유사한 키워드 3",
        "relevance": 0.85,
        "description": "유사성에 대한 상세 설명",
        "estimated_volume": "월간 검색량 추정",
        "competition": "낮음/중간/높음",
        "search_intent": "정보성/거래성/탐색성",
        "use_case": "사용 사례 및 활용 방안"
      }
    ],
    "co_occurring": [
      {
        "keyword": "동시 출현 키워드 1",
        "frequency": 0.75,
        "description": "출현 패턴에 대한 상세 설명",
        "co_occurrence_context": "동시 출현 맥락",
        "estimated_volume": "월간 검색량 추정",
        "competition": "낮음/중간/높음",
        "use_case": "사용 사례 및 활용 방안"
      },
      {
        "keyword": "동시 출현 키워드 2",
        "frequency": 0.68,
        "description": "출현 패턴에 대한 상세 설명",
        "co_occurrence_context": "동시 출현 맥락",
        "estimated_volume": "월간 검색량 추정",
        "competition": "낮음/중간/높음",
        "use_case": "사용 사례 및 활용 방안"
      }
    ],
    "hierarchical": {
      "broader": [
        {
          "keyword": "상위 개념 키워드 1",
          "level": "상위",
          "description": "계층 관계에 대한 상세 설명",
          "estimated_volume": "월간 검색량 추정",
          "competition": "낮음/중간/높음",
          "use_case": "사용 사례 및 활용 방안"
        },
        {
          "keyword": "상위 개념 키워드 2",
          "level": "상위",
          "description": "계층 관계에 대한 상세 설명",
          "estimated_volume": "월간 검색량 추정",
          "competition": "낮음/중간/높음",
          "use_case": "사용 사례 및 활용 방안"
        }
      ],
      "narrower": [
        {
          "keyword": "하위 개념 키워드 1",
          "level": "하위",
          "description": "계층 관계에 대한 상세 설명",
          "estimated_volume": "월간 검색량 추정",
          "competition": "낮음/중간/높음",
          "use_case": "사용 사례 및 활용 방안"
        },
        {
          "keyword": "하위 개념 키워드 2",
          "level": "하위",
          "description": "계층 관계에 대한 상세 설명",
          "estimated_volume": "월간 검색량 추정",
          "competition": "낮음/중간/높음",
          "use_case": "사용 사례 및 활용 방안"
        }
      ]
    }
  },
  "trending_related": [
    {
      "keyword": "트렌드 관련 키워드 1",
      "trend": "상승/하락/유지",
      "growth_rate": "높음/중간/낮음",
      "description": "트렌드에 대한 상세 설명",
      "trend_period": "트렌드 기간 (예: 최근 3개월)",
      "estimated_volume": "월간 검색량 추정",
      "competition": "낮음/중간/높음",
      "opportunity_score": 0.85,
      "use_case": "사용 사례 및 활용 방안"
    },
    {
      "keyword": "트렌드 관련 키워드 2",
      "trend": "상승/하락/유지",
      "growth_rate": "높음/중간/낮음",
      "description": "트렌드에 대한 상세 설명",
      "trend_period": "트렌드 기간",
      "estimated_volume": "월간 검색량 추정",
      "competition": "낮음/중간/높음",
      "opportunity_score": 0.80,
      "use_case": "사용 사례 및 활용 방안"
    }
  ],
  "alternative_keywords": [
    {
      "keyword": "대안 키워드 1",
      "similarity": 0.85,
      "use_case": "사용 사례 및 활용 방안",
      "estimated_volume": "월간 검색량 추정",
      "competition": "낮음/중간/높음",
      "advantage": "기준 키워드 대비 장점",
      "disadvantage": "기준 키워드 대비 단점"
    },
    {
      "keyword": "대안 키워드 2",
      "similarity": 0.80,
      "use_case": "사용 사례 및 활용 방안",
      "estimated_volume": "월간 검색량 추정",
      "competition": "낮음/중간/높음",
      "advantage": "기준 키워드 대비 장점",
      "disadvantage": "기준 키워드 대비 단점"
    }
  ],
  "long_tail_keywords": [
    {
      "keyword": "롱테일 키워드 1",
      "search_intent": "정보성/거래성/탐색성",
      "competition": "낮음/중간/높음",
      "estimated_volume": "월간 검색량 추정 (일반적으로 낮음)",
      "conversion_potential": "높음/중간/낮음",
      "description": "키워드에 대한 상세 설명",
      "use_case": "사용 사례 및 활용 방안"
    },
    {
      "keyword": "롱테일 키워드 2",
      "search_intent": "정보성/거래성/탐색성",
      "competition": "낮음/중간/높음",
      "estimated_volume": "월간 검색량 추정",
      "conversion_potential": "높음/중간/낮음",
      "description": "키워드에 대한 상세 설명",
      "use_case": "사용 사례 및 활용 방안"
    }
  ],
  "question_keywords": [
    {
      "keyword": "질문형 키워드 1",
      "question_type": "무엇/어떻게/왜/언제/어디서",
      "estimated_volume": "월간 검색량 추정",
      "competition": "낮음/중간/높음",
      "answer_opportunity": "답변 콘텐츠 기회 설명",
      "use_case": "사용 사례 및 활용 방안"
    },
    {
      "keyword": "질문형 키워드 2",
      "question_type": "무엇/어떻게/왜/언제/어디서",
      "estimated_volume": "월간 검색량 추정",
      "competition": "낮음/중간/높음",
      "answer_opportunity": "답변 콘텐츠 기회 설명",
      "use_case": "사용 사례 및 활용 방안"
    }
  ],
  "recommendation_summary": {
    "total_keywords": "추천된 총 키워드 수",
    "top_opportunities": [
      "최고 기회 키워드 1 (이유 포함)",
      "최고 기회 키워드 2 (이유 포함)",
      "최고 기회 키워드 3 (이유 포함)"
    ],
    "strategic_recommendations": [
      "전략적 권장사항 1 (구체적 실행 방안)",
      "전략적 권장사항 2",
      "전략적 권장사항 3"
    ],
    "priority_keywords": [
      {
        "keyword": "우선순위 키워드 1",
        "priority": "높음/중간/낮음",
        "reason": "우선순위 이유",
        "action": "권장 행동"
      },
      {
        "keyword": "우선순위 키워드 2",
        "priority": "높음/중간/낮음",
        "reason": "우선순위 이유",
        "action": "권장 행동"
      }
    ]
  }
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
