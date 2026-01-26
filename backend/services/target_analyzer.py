"""
타겟 분석 서비스
AI를 사용하여 키워드, 오디언스, 경쟁자 분석을 수행합니다.
"""
import logging
from typing import Optional, Dict, Any
import json

from backend.config import settings
from backend.services.progress_tracker import ProgressTracker

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
        target_type: 분석 유형 (keyword, audience, competitor)
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
        
        # API 키 상태 확인 및 로깅 (환경 변수에서 직접 확인 - Vercel 호환성)
        # 여러 소스에서 API 키 확인 (우선순위: 환경 변수 > Settings)
        openai_env = os.getenv('OPENAI_API_KEY')
        gemini_env = os.getenv('GEMINI_API_KEY')
        openai_settings = getattr(settings, 'OPENAI_API_KEY', None)
        gemini_settings = getattr(settings, 'GEMINI_API_KEY', None)
        
        openai_key = openai_env or openai_settings
        gemini_key = gemini_env or gemini_settings
        
        has_openai_key = bool(openai_key and len(openai_key.strip()) > 0)
        has_gemini_key = bool(gemini_key and len(gemini_key.strip()) > 0)
        
        # 상세 로깅
        logger.info("=" * 60)
        logger.info("API 키 상태 확인 (상세)")
        logger.info(f"os.getenv('OPENAI_API_KEY'): {'✅ 설정됨' if openai_env else '❌ 미설정'}")
        if openai_env:
            logger.info(f"  - 길이: {len(openai_env)} 문자, 시작: {openai_env[:10]}...")
        logger.info(f"settings.OPENAI_API_KEY: {'✅ 설정됨' if openai_settings else '❌ 미설정'}")
        if openai_settings:
            logger.info(f"  - 길이: {len(openai_settings)} 문자, 시작: {openai_settings[:10]}...")
        logger.info(f"최종 openai_key: {'✅ 설정됨' if has_openai_key else '❌ 미설정'}")
        
        logger.info(f"os.getenv('GEMINI_API_KEY'): {'✅ 설정됨' if gemini_env else '❌ 미설정'}")
        if gemini_env:
            logger.info(f"  - 길이: {len(gemini_env)} 문자, 시작: {gemini_env[:10]}...")
        logger.info(f"settings.GEMINI_API_KEY: {'✅ 설정됨' if gemini_settings else '❌ 미설정'}")
        if gemini_settings:
            logger.info(f"  - 길이: {len(gemini_settings)} 문자, 시작: {gemini_settings[:10]}...")
        logger.info(f"최종 gemini_key: {'✅ 설정됨' if has_gemini_key else '❌ 미설정'}")
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
            logger.info("OpenAI API로 기본 분석 수행 중...")
            try:
                result = await _analyze_with_openai(
                    target_keyword, target_type, additional_context, start_date, end_date, progress_tracker
                )
                logger.info("✅ OpenAI API 분석 성공")
            except Exception as e:
                logger.error(f"❌ OpenAI API 호출 실패: {e}", exc_info=True)
                # OpenAI 실패 시 Gemini로 재시도
                if has_gemini_key:
                    logger.info("Gemini API로 재시도 중...")
                    try:
                        if progress_tracker:
                            await progress_tracker.update(50, "OpenAI 실패, Gemini로 재시도 중...")
                        result = await _analyze_with_gemini(
                            target_keyword, target_type, additional_context, start_date, end_date, progress_tracker
                        )
                        logger.info("✅ Gemini API 분석 성공 (OpenAI 실패 후 재시도)")
                    except Exception as e2:
                        logger.error(f"❌ Gemini API 재시도도 실패: {e2}", exc_info=True)
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
                    logger.info("Gemini API로 결과 보완 중...")
                    gemini_result = await _analyze_with_gemini(
                        target_keyword, target_type, additional_context, start_date, end_date, progress_tracker
                    )
                    # OpenAI와 Gemini 결과 통합
                    if progress_tracker:
                        await progress_tracker.update(85, "OpenAI + Gemini 결과 통합 중...")
                    result = _merge_analysis_results(result, gemini_result, target_type)
                    logger.info("OpenAI + Gemini 결과 통합 완료")
                except Exception as e:
                    logger.warning(f"Gemini API 보완 중 오류 발생 (OpenAI 결과만 사용): {e}")
                    # Gemini 실패해도 OpenAI 결과는 유지
                    if progress_tracker:
                        await progress_tracker.update(90, "Gemini 보완 실패, OpenAI 결과만 사용")
        elif use_gemini and has_gemini_key:
            # OpenAI가 없고 Gemini만 있는 경우
            if progress_tracker:
                await progress_tracker.update(10, "Gemini API로 분석 시작...")
            logger.info("Gemini API로 분석 수행 중...")
            try:
                result = await _analyze_with_gemini(
                    target_keyword, target_type, additional_context, start_date, end_date, progress_tracker
                )
                logger.info("✅ Gemini API 분석 성공")
            except Exception as e:
                logger.error(f"❌ Gemini API 호출 실패: {e}", exc_info=True)
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
        return result
        
    except Exception as e:
        logger.error(f"❌ 타겟 분석 중 치명적 오류: {e}", exc_info=True)
        # 예외 발생 시에도 기본 분석 결과라도 반환
        logger.warning("기본 분석 모드로 fallback 시도")
        try:
            return _analyze_basic(target_keyword, target_type, additional_context, start_date, end_date)
        except Exception as e2:
            logger.error(f"기본 분석 모드도 실패: {e2}")
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
        import os
        
        # API 키 확인 (환경 변수에서 직접 읽기 - Vercel 호환성)
        # 여러 소스에서 API 키 확인 (우선순위: 환경 변수 > Settings)
        api_key_env = os.getenv('GEMINI_API_KEY')
        api_key_settings = getattr(settings, 'GEMINI_API_KEY', None)
        api_key = api_key_env or api_key_settings
        
        if not api_key or len(api_key.strip()) == 0:
            logger.error(f"GEMINI_API_KEY 미설정 - env: {bool(api_key_env)}, settings: {bool(api_key_settings)}")
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
        
        logger.info(f"Gemini API 키 소스: {'환경 변수' if api_key_env else 'Settings'}, 길이: {len(api_key)} 문자")
        
        # 프롬프트 생성
        prompt = _build_analysis_prompt(target_keyword, target_type, additional_context, start_date, end_date)
        
        # 모델 설정 (기본값: gemini-2.5-flash-preview)
        model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash-preview')
        logger.info(f"Gemini API 클라이언트 초기화 중... (모델: {model_name})")
        
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
            
            # 시스템 메시지와 프롬프트 결합
            system_message = _build_system_message(target_type)
            full_prompt = f"{system_message}\n\n{prompt}\n\n**중요**: 반드시 유효한 JSON 형식으로만 응답하세요. 마크다운 코드 블록을 사용하지 마세요."
            
            # API 호출 (비동기 실행을 위해 run_in_executor 사용)
            loop = asyncio.get_event_loop()
            try:
                # JSON 응답 강제 시도
                response = await loop.run_in_executor(
                    None, 
                    lambda: client.models.generate_content(
                        model=model_name,
                        contents=full_prompt,
                        generation_config={
                            "response_mime_type": "application/json"
                        }
                    )
                )
            except Exception as e:
                logger.warning(f"JSON 응답 강제 실패, 일반 모드로 재시도: {e}")
                # JSON 응답 강제가 실패하면 일반 모드로 재시도
                response = await loop.run_in_executor(
                    None, 
                    lambda: client.models.generate_content(
                        model=model_name,
                        contents=full_prompt
                    )
                )
            
            # 응답 파싱
            result_text = response.text if hasattr(response, 'text') else str(response)
            
        except ImportError:
            # 새로운 방식이 없으면 기존 방식 시도
            import google.generativeai as genai_old
            
            genai_old.configure(api_key=settings.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY'))
            model = genai_old.GenerativeModel(model_name)
            
            # 시스템 메시지와 프롬프트 결합
            system_message = _build_system_message(target_type)
            full_prompt = f"{system_message}\n\n{prompt}\n\n**중요**: 반드시 유효한 JSON 형식으로만 응답하세요. 마크다운 코드 블록을 사용하지 마세요."
            
            # API 호출 (비동기 실행을 위해 run_in_executor 사용)
            loop = asyncio.get_event_loop()
            try:
                # JSON 응답 강제 시도
                response = await loop.run_in_executor(
                    None, 
                    lambda: model.generate_content(
                        full_prompt,
                        generation_config={
                            "response_mime_type": "application/json"
                        }
                    )
                )
            except Exception as e:
                logger.warning(f"JSON 응답 강제 실패, 일반 모드로 재시도: {e}")
                # JSON 응답 강제가 실패하면 일반 모드로 재시도
                response = await loop.run_in_executor(
                    None, 
                    lambda: model.generate_content(full_prompt)
                )
            
            # 응답 파싱
            result_text = response.text if hasattr(response, 'text') else str(response)
        
        if progress_tracker:
            await progress_tracker.update(80, "AI 응답 수신 완료, 결과 파싱 중...")
        
        # JSON 형식으로 파싱 시도
        if not result_text:
            raise ValueError("Gemini API 응답이 비어있습니다.")
        
        # 마크다운 코드 블록 제거
        clean_text = result_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]  # ```json 제거
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]  # ``` 제거
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]  # 끝의 ``` 제거
        clean_text = clean_text.strip()
        
        try:
                result = json.loads(clean_text)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON 파싱 실패, 재시도: {e}")
            # 한 번 더 시도: 중괄호만 추출
            try:
                start_idx = clean_text.find("{")
                end_idx = clean_text.rfind("}") + 1
                if start_idx >= 0 and end_idx > start_idx:
                    result = json.loads(clean_text[start_idx:end_idx])
                else:
                    raise ValueError("유효한 JSON을 찾을 수 없습니다.")
            except Exception as e2:
                logger.error(f"JSON 파싱 최종 실패: {e2}, 원본 텍스트: {clean_text[:200]}")
                # JSON이 아니면 텍스트로 반환
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
                            "raw_response": result_text[:500]  # 처음 500자만
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
    end_date: Optional[str] = None,
    progress_tracker: Optional[ProgressTracker] = None
) -> Dict[str, Any]:
    """OpenAI API를 사용한 분석"""
    try:
        from openai import AsyncOpenAI
        
        # API 키 확인 (환경 변수에서 직접 읽기 - Vercel 호환성)
        # 여러 소스에서 API 키 확인 (우선순위: 환경 변수 > Settings)
        api_key_env = os.getenv('OPENAI_API_KEY')
        api_key_settings = getattr(settings, 'OPENAI_API_KEY', None)
        api_key = api_key_env or api_key_settings
        
        if not api_key or len(api_key.strip()) == 0:
            logger.error(f"OPENAI_API_KEY 미설정 - env: {bool(api_key_env)}, settings: {bool(api_key_settings)}")
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        
        logger.info(f"OpenAI API 클라이언트 초기화 중... (모델: {settings.OPENAI_MODEL})")
        logger.info(f"API 키 소스: {'환경 변수' if api_key_env else 'Settings'}, 길이: {len(api_key)} 문자")
        client = AsyncOpenAI(api_key=api_key)
        
        # 프롬프트 생성
        if progress_tracker:
            await progress_tracker.update(20, "프롬프트 생성 중...")
        prompt = _build_analysis_prompt(target_keyword, target_type, additional_context, start_date, end_date)
        
        # 시스템 메시지 생성
        system_message = _build_system_message(target_type)
        
        if progress_tracker:
            await progress_tracker.update(30, "OpenAI API 요청 전송 중...")
        
        # API 호출
        logger.info("OpenAI API 요청 전송 중...")
        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}  # JSON 응답 강제
            )
            logger.info("OpenAI API 응답 수신 완료")
        except Exception as api_error:
            logger.error(f"OpenAI API 호출 중 오류 발생: {api_error}", exc_info=True)
            raise ValueError(f"OpenAI API 호출 실패: {str(api_error)}")
        
        result_text = response.choices[0].message.content
        
        if not result_text:
            raise ValueError("OpenAI API 응답이 비어있습니다.")
        
        logger.info(f"OpenAI 응답 길이: {len(result_text)} 문자")
        
        if progress_tracker:
            await progress_tracker.update(80, "AI 응답 수신 완료, 결과 파싱 중...")
        
        # JSON 형식으로 파싱 시도
        try:
            # result_text가 문자열인지 확인
            if isinstance(result_text, str):
                # 마크다운 코드 블록 제거
                clean_text = result_text.strip()
                if clean_text.startswith("```json"):
                    clean_text = clean_text[7:]  # ```json 제거
                if clean_text.startswith("```"):
                    clean_text = clean_text[3:]  # ``` 제거
                if clean_text.endswith("```"):
                    clean_text = clean_text[:-3]  # 끝의 ``` 제거
                clean_text = clean_text.strip()
                
                result = json.loads(clean_text)
                if progress_tracker:
                    await progress_tracker.update(90, "JSON 파싱 완료, 결과 정리 중...")
            else:
                # 문자열 응답인 경우
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
                            "raw_response": str(result_text)[:500]  # 처음 500자만
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
        except json.JSONDecodeError as e:
            logger.warning(f"JSON 파싱 실패, 재시도: {e}")
            # 한 번 더 시도: 중괄호만 추출
            try:
                if isinstance(result_text, str):
                    clean_text = result_text.strip()
                    start_idx = clean_text.find("{")
                    end_idx = clean_text.rfind("}") + 1
                    if start_idx >= 0 and end_idx > start_idx:
                        result = json.loads(clean_text[start_idx:end_idx])
                    else:
                        raise ValueError("유효한 JSON을 찾을 수 없습니다.")
                else:
                    raise ValueError("응답이 문자열이 아닙니다.")
            except Exception as e2:
                logger.error(f"JSON 파싱 최종 실패: {e2}")
                # JSON이 아니면 구조화된 오류 응답 반환
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
                            "raw_response": str(result_text)[:500] if isinstance(result_text, str) else str(result_text)
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
    
    # MECE 구조로 기본 분석 결과 반환
    # API 키 상태 확인 (환경 변수에서 직접 확인 - Vercel 호환성)
    import os
    openai_env = os.getenv('OPENAI_API_KEY')
    gemini_env = os.getenv('GEMINI_API_KEY')
    openai_settings = getattr(settings, 'OPENAI_API_KEY', None)
    gemini_settings = getattr(settings, 'GEMINI_API_KEY', None)
    
    openai_key = openai_env or openai_settings
    gemini_key = gemini_env or gemini_settings
    
    has_openai = bool(openai_key and len(openai_key.strip()) > 0)
    has_gemini = bool(gemini_key and len(gemini_key.strip()) > 0)
    
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
    """시스템 메시지 생성"""
    mece_instruction = """
CRITICAL: Your analysis MUST follow MECE (Mutually Exclusive, Collectively Exhaustive) principles:
- Mutually Exclusive: Each section and category must be distinct with no overlap
- Collectively Exhaustive: All relevant aspects must be covered comprehensively
- Logical Structure: Follow a clear, hierarchical, and logical flow
- Professional Format: Present findings in a structured, consulting-grade document format
"""
    
    if target_type == "audience":
        return f"""You are a senior marketing research and consulting analyst with 15+ years of experience at top-tier consulting firms (McKinsey, BCG, Bain, Deloitte, PwC).
Your role is to provide comprehensive, structured, and actionable audience analysis reports for C-level executives and marketing decision-makers.
{mece_instruction}
You MUST respond ONLY in valid JSON format without any markdown code blocks or additional text.
Your analysis must be:
- Data-driven with specific quantitative metrics and qualitative insights
- Structured in a logical, hierarchical manner following MECE principles
- Professional consulting-grade quality suitable for board presentations
- Actionable with clear strategic recommendations"""
    elif target_type == "keyword":
        return f"""You are a senior SEO and digital marketing strategy consultant with 15+ years of experience at top-tier consulting firms.
Your role is to provide comprehensive, structured, and actionable keyword analysis reports for digital marketing executives.
{mece_instruction}
You MUST respond ONLY in valid JSON format without any markdown code blocks or additional text.
Your analysis must be:
- Data-driven with specific quantitative metrics and qualitative insights
- Structured in a logical, hierarchical manner following MECE principles
- Professional consulting-grade quality suitable for strategic planning
- Actionable with clear SEO and marketing recommendations"""
    else:  # competitor
        return f"""You are a senior competitive intelligence and market research consultant with 15+ years of experience at top-tier consulting firms.
Your role is to provide comprehensive, structured, and actionable competitive analysis reports for strategic planning executives.
{mece_instruction}
You MUST respond ONLY in valid JSON format without any markdown code blocks or additional text.
Your analysis must be:
- Data-driven with specific quantitative metrics and qualitative insights
- Structured in a logical, hierarchical manner following MECE principles
- Professional consulting-grade quality suitable for board-level decisions
- Actionable with clear strategic recommendations and competitive positioning"""


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
당신은 10년 이상의 경력을 가진 전문 마케팅 및 소비자 행동 분석가입니다. 
다음 타겟 오디언스에 대한 매우 상세하고 심층적인 마케팅 관점의 분석을 수행해주세요.

**분석 대상**: {target_keyword}
{period_info}
{period_instruction}

**분석 목적**: 이 분석은 마케팅 전략 수립, 타겟팅, 메시징, 채널 선택, 예산 배분 등의 의사결정에 활용됩니다.
따라서 모든 분석은 실행 가능한 마케팅 인사이트와 구체적인 전략 제안을 포함해야 합니다.
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
  "executive_summary": "Executive Summary: 오디언스에 대한 종합적인 요약 (3-5문단, 핵심 발견사항, 주요 인사이트, 전략적 권장사항 요약)",
  "key_findings": {
    "primary_insights": [
      "인구통계학적 특성의 핵심 요약 (연령대, 성별, 지역, 소득 수준 등)",
      "심리적 특성 및 라이프스타일의 주요 특징",
      "주요 행동 패턴 및 미디어 소비 습관의 특징",
      "핵심 니즈 및 페인 포인트 (3-5개 구체적 사례)",
      "이 오디언스의 고유한 특성과 차별점"
    ],
    "quantitative_metrics": {
      "estimated_volume": "예상 오디언스 규모 (구체적 숫자 또는 범위)",
      "engagement_level": "참여 수준 (낮음/중간/높음) 및 근거",
      "growth_potential": "성장 잠재력 (낮음/중간/높음) 및 근거",
      "market_value": "시장 가치 추정 (구매력, 소비 규모 등)",
      "accessibility": "접근 난이도 (이 오디언스에 도달하기 어려운 정도)"
    }
  },
  "detailed_analysis": {
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
  "strategic_recommendations": {
    "immediate_actions": [
      "즉시 실행 가능한 마케팅 전략 1 (구체적 실행 방안, 예상 효과, 필요 리소스 포함)",
      "즉시 실행 가능한 마케팅 전략 2",
      "즉시 실행 가능한 마케팅 전략 3"
    ],
    "short_term_strategies": [
      "단기 마케팅 전략 1 (3-6개월, 구체적 실행 방안 포함)",
      "단기 마케팅 전략 2",
      "단기 마케팅 전략 3"
    ],
    "long_term_strategies": [
      "장기 마케팅 전략 1 (6개월 이상, 구체적 실행 방안 포함)",
      "장기 마케팅 전략 2",
      "장기 마케팅 전략 3"
    ],
    "success_metrics": "성공 지표 및 측정 방법 (KPI, 측정 주기, 목표 수치 등)"
  }
}
"""
    elif target_type == "keyword":
        # 키워드 분석에 특화된 매우 상세한 프롬프트
        prompt = f"""
당신은 글로벌 컨설팅 그룹의 시니어 SEO 및 디지털 마케팅 전략 컨설턴트입니다.
다음 키워드에 대한 MECE 원칙에 기반한 구조화된 컨설팅 수준의 분석 보고서를 작성해주세요.

**분석 대상 키워드**: {target_keyword}
{period_info}
{period_instruction}

**분석 목적**: 이 분석은 디지털 마케팅 전략 수립, SEO 최적화, 콘텐츠 기획, 키워드 타겟팅, 경쟁 분석 등의 의사결정에 활용됩니다.
따라서 모든 분석은 실행 가능한 SEO 인사이트와 구체적인 최적화 전략을 포함해야 합니다.

**MECE 구조 요구사항**:
1. Mutually Exclusive (상호 배타적): 각 섹션과 카테고리는 명확히 구분되어 중복이 없어야 합니다.
2. Collectively Exhaustive (완전 포괄적): 키워드 분석에 필요한 모든 측면을 포괄해야 합니다.
3. 논리적 계층 구조: Executive Summary → Key Findings → Detailed Analysis → Strategic Recommendations 순서로 구성
4. 컨설팅 문서 형식: 명확한 구조, 데이터 기반 결론, 실행 가능한 권장사항
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
3. 정량적 데이터(검색량, 경쟁도 점수, 예상 수치, 시장 규모 등)와 정성적 분석(전략, 기회 등)을 모두 포함해야 합니다.
4. 지정된 기간 동안의 검색량 변화, 트렌드, 계절성, 이벤트 등을 반드시 포함하여 분석해주세요.
5. 컨설팅 수준의 전문성: 논리적 근거, 데이터 기반 결론, 실행 가능한 SEO 전략을 제시해야 합니다.
6. 문서 구조: Executive Summary → Key Findings → Detailed Analysis (MECE 구조) → Strategic Recommendations

다음 JSON 구조를 정확히 따르면서 각 필드를 매우 상세하게 작성해주세요. 각 섹션은 MECE 원칙에 따라 명확히 구분되어야 합니다:

{
  "executive_summary": "Executive Summary: 키워드에 대한 종합적인 요약 (3-5문단, 핵심 발견사항, 주요 인사이트, 전략적 권장사항 요약)",
  "key_findings": {
    "primary_insights": [
      "검색 의도 및 사용자 목적의 핵심 요약",
      "경쟁 환경 및 시장 상황의 주요 특징",
      "검색 트렌드 및 시계열 변화 패턴",
      "관련 키워드 및 롱테일 키워드 기회",
      "이 키워드의 고유한 특성과 차별점"
    ],
    "quantitative_metrics": {
      "estimated_volume": "예상 검색량 (월간 검색량 범위 또는 추정치)",
      "competition_level": "경쟁 수준 (낮음/중간/높음) 및 구체적 근거",
      "growth_potential": "성장 잠재력 (낮음/중간/높음) 및 근거",
      "difficulty_score": "난이도 점수 (1-100) 및 근거",
      "opportunity_score": "기회 점수 (1-100) 및 근거"
    }
  },
  "detailed_analysis": {
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
  "strategic_recommendations": {
    "immediate_actions": [
      "즉시 실행 가능한 SEO 전략 1 (구체적 실행 방안, 예상 효과, 필요 리소스 포함)",
      "즉시 실행 가능한 SEO 전략 2",
      "즉시 실행 가능한 SEO 전략 3"
    ],
    "short_term_strategies": [
      "단기 SEO 전략 1 (3-6개월, 구체적 실행 방안 포함)",
      "단기 SEO 전략 2",
      "단기 SEO 전략 3"
    ],
    "long_term_strategies": [
      "장기 SEO 전략 1 (6개월 이상, 구체적 실행 방안 포함)",
      "장기 SEO 전략 2",
      "장기 SEO 전략 3"
    ],
    "success_metrics": "성공 지표 및 측정 방법 (KPI, 측정 주기, 목표 수치 등)"
  },
  "target_audience": {
    "expected_occupations": ["이 키워드와 관련된 주요 직업군 1", "직업군 2", "직업군 3", "직업군 4", "직업군 5"]
  }
}
"""
    else:  # competitor
        # 경쟁자 분석에 특화된 매우 상세한 프롬프트
        prompt = f"""
당신은 글로벌 컨설팅 그룹의 시니어 경쟁 인텔리전스 및 시장 조사 컨설턴트입니다.
다음 경쟁사 또는 경쟁 키워드에 대한 MECE 원칙에 기반한 구조화된 컨설팅 수준의 분석 보고서를 작성해주세요.

**분석 대상**: {target_keyword}
{period_info}
{period_instruction}

**분석 목적**: 이 분석은 경쟁 전략 수립, 시장 포지셔닝, 차별화 전략, 가격 전략, 시장 진입/확대 전략 등의 의사결정에 활용됩니다.
따라서 모든 분석은 실행 가능한 경쟁 전략 인사이트와 구체적인 차별화 방안을 포함해야 합니다.

**MECE 구조 요구사항**:
1. Mutually Exclusive (상호 배타적): 각 섹션과 카테고리는 명확히 구분되어 중복이 없어야 합니다.
2. Collectively Exhaustive (완전 포괄적): 경쟁 분석에 필요한 모든 측면을 포괄해야 합니다.
3. 논리적 계층 구조: Executive Summary → Key Findings → Detailed Analysis → Strategic Recommendations 순서로 구성
4. 컨설팅 문서 형식: 명확한 구조, 데이터 기반 결론, 실행 가능한 권장사항
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
3. 정량적 데이터(시장 점유율, 경쟁 점수, 예상 수치, 시장 규모 등)와 정성적 분석(전략, 기회 등)을 모두 포함해야 합니다.
4. 지정된 기간 동안의 시장 변화, 경쟁자 움직임, 시장 점유율 변화 등을 반드시 포함하여 분석해주세요.
5. 컨설팅 수준의 전문성: 논리적 근거, 데이터 기반 결론, 실행 가능한 경쟁 전략을 제시해야 합니다.
6. 문서 구조: Executive Summary → Key Findings → Detailed Analysis (MECE 구조) → Strategic Recommendations

다음 JSON 구조를 정확히 따르면서 각 필드를 매우 상세하게 작성해주세요. 각 섹션은 MECE 원칙에 따라 명확히 구분되어야 합니다:

{
  "executive_summary": "Executive Summary: 경쟁 환경에 대한 종합적인 요약 (3-5문단, 핵심 발견사항, 주요 인사이트, 전략적 권장사항 요약)",
  "key_findings": {
    "primary_insights": [
      "경쟁 환경의 핵심 요약 (시장 구조, 경쟁 강도 등)",
      "주요 경쟁자의 강점과 약점",
      "시장 포지셔닝 및 차별화 포인트",
      "경쟁 우위 확보 기회",
      "이 시장의 고유한 특성과 차별점"
    ],
    "quantitative_metrics": {
      "competition_level": "경쟁 수준 (낮음/중간/높음) 및 구체적 근거",
      "market_opportunity": "시장 기회 크기 (낮음/중간/높음) 및 근거",
      "differentiation_potential": "차별화 가능성 (낮음/중간/높음) 및 근거",
      "risk_level": "위험 수준 (낮음/중간/높음) 및 주요 위험 요소",
      "success_probability": "성공 확률 추정 (낮음/중간/높음) 및 근거"
    }
  },
  "detailed_analysis": {
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
    "immediate_actions": [
      "즉시 실행 가능한 경쟁 전략 1 (구체적 실행 방안, 예상 효과, 필요 리소스 포함)",
      "즉시 실행 가능한 경쟁 전략 2",
      "즉시 실행 가능한 경쟁 전략 3"
    ],
    "short_term_strategies": [
      "단기 경쟁 전략 1 (3-6개월, 구체적 실행 방안 포함)",
      "단기 경쟁 전략 2",
      "단기 경쟁 전략 3"
    ],
    "long_term_strategies": [
      "장기 경쟁 전략 1 (6개월 이상, 구체적 실행 방안 포함)",
      "장기 경쟁 전략 2",
      "장기 경쟁 전략 3"
    ],
    "competitive_advantages": ["경쟁 우위 확보 방안 1 (구체적 전략 포함)", "방안 2", "방안 3"],
    "market_entry_strategy": "시장 진입 전략 (신규 진입 시) 또는 시장 확대 전략 (기존 진입 시)",
    "content_differentiation": ["콘텐츠 차별화 전략 1 (구체적 실행 방안)", "전략 2", "전략 3"],
    "pricing_strategy": "가격 전략 제안 (경쟁자 대비)",
    "partnership_opportunities": "파트너십 기회 및 협력 방안",
    "success_metrics": "성공 지표 및 측정 방법 (KPI, 측정 주기, 목표 수치 등)"
  }
}
"""
    
    return prompt
