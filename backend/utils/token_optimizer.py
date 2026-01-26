"""
토큰 최적화 유틸리티
프롬프트를 압축하고 토큰 사용량을 최적화합니다.
"""
import re
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def optimize_prompt(prompt: str, max_length: Optional[int] = None) -> str:
    """
    프롬프트를 최적화하여 토큰 사용량을 줄입니다.
    
    Args:
        prompt: 원본 프롬프트
        max_length: 최대 길이 (문자 수, None이면 압축만 수행)
        
    Returns:
        최적화된 프롬프트
    """
    optimized = prompt
    
    # 1. 연속된 공백 제거
    optimized = re.sub(r' +', ' ', optimized)
    
    # 2. 연속된 줄바꿈 제거 (최대 2개까지)
    optimized = re.sub(r'\n{3,}', '\n\n', optimized)
    
    # 3. 불필요한 설명 제거 (예: "매우 상세하게", "심층적으로" 등 중복 표현)
    redundant_phrases = [
        r'매우 상세하고 심층적인',
        r'매우 상세하게',
        r'심층적으로',
        r'구체적이고 실용적인',
        r'구체적인',
        r'실용적인',
    ]
    for phrase in redundant_phrases:
        optimized = re.sub(phrase, '', optimized, flags=re.IGNORECASE)
    
    # 4. 반복되는 지시사항 정리
    optimized = re.sub(
        r'반드시\s+유효한\s+JSON\s+형식으로만\s+응답해야\s+합니다\.?\s*마크다운\s+코드\s+블록.*?사용하지\s+마세요\.?',
        'JSON 형식으로만 응답하세요.',
        optimized,
        flags=re.IGNORECASE | re.DOTALL
    )
    
    # 5. 길이 제한 적용
    if max_length and len(optimized) > max_length:
        # 문장 단위로 자르기
        sentences = optimized.split('. ')
        result = []
        current_length = 0
        
        for sentence in sentences:
            if current_length + len(sentence) + 2 <= max_length:
                result.append(sentence)
                current_length += len(sentence) + 2
            else:
                break
        
        optimized = '. '.join(result)
        if optimized and not optimized.endswith('.'):
            optimized += '.'
    
    return optimized.strip()


def estimate_tokens(text: str) -> int:
    """
    텍스트의 대략적인 토큰 수를 추정합니다.
    (한국어: 약 1.5자/토큰, 영어: 약 4자/토큰)
    
    Args:
        text: 텍스트
        
    Returns:
        추정 토큰 수
    """
    # 간단한 추정: 한국어와 영어 혼합 기준
    korean_chars = len(re.findall(r'[가-힣]', text))
    other_chars = len(text) - korean_chars
    
    # 한국어는 1.5자/토큰, 영어는 4자/토큰으로 추정
    estimated = int(korean_chars / 1.5 + other_chars / 4)
    return max(estimated, len(text) // 4)  # 최소값 보장


def get_max_tokens_for_model(model: str, prompt_tokens: int) -> int:
    """
    모델별 최대 출력 토큰 수를 계산합니다.
    
    Args:
        model: 모델 이름
        prompt_tokens: 프롬프트 토큰 수
        
    Returns:
        최대 출력 토큰 수
    """
    # 모델별 컨텍스트 윈도우 크기
    model_limits = {
        'gpt-4o-mini': 128000,
        'gpt-4o': 128000,
        'gpt-4': 8192,
        'gpt-3.5-turbo': 16385,
        'gemini-2.5-flash': 1000000,
        'gemini-2.0-flash-exp': 1000000,
        'gemini-1.5-pro': 2000000,
        'gemini-1.5-flash': 1000000,
    }
    
    # 기본값
    context_window = model_limits.get(model, 16385)
    
    # 프롬프트 + 출력 토큰이 컨텍스트 윈도우를 초과하지 않도록
    # 출력 토큰은 최대 8000으로 제한 (분석 결과가 충분히 길 수 있음)
    max_output = min(8000, context_window - prompt_tokens - 1000)  # 1000 토큰 여유
    
    # 최소값 보장
    return max(max_output, 2000)


def optimize_additional_context(context: Optional[str], max_length: int = 500) -> Optional[str]:
    """
    추가 컨텍스트를 최적화합니다.
    
    Args:
        context: 추가 컨텍스트
        max_length: 최대 길이
        
    Returns:
        최적화된 컨텍스트
    """
    if not context:
        return None
    
    if len(context) <= max_length:
        return context
    
    # 문장 단위로 자르기
    sentences = context.split('. ')
    result = []
    current_length = 0
    
    for sentence in sentences:
        if current_length + len(sentence) + 2 <= max_length:
            result.append(sentence)
            current_length += len(sentence) + 2
        else:
            break
    
    optimized = '. '.join(result)
    if optimized and not optimized.endswith('.'):
        optimized += '.'
    
    return optimized if optimized else context[:max_length]
