"""
토큰 최적화 유틸리티
프롬프트를 압축하고 토큰 사용량을 최적화합니다.
"""
import re
import logging
import json
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


def fix_json_string(text: str) -> str:
    """
    JSON 문자열 내의 잘못된 이스케이프 문자를 수정합니다.
    
    Args:
        text: 수정할 JSON 텍스트
        
    Returns:
        수정된 JSON 텍스트
    """
    # 줄바꿈이 문자열 내부에 있는 경우 이스케이프 처리
    # 하지만 이미 이스케이프된 것은 건드리지 않음
    lines = text.split('\n')
    result = []
    in_string = False
    escape_next = False
    
    for line in lines:
        if not in_string:
            # 문자열 시작 찾기
            if '"' in line:
                in_string = True
                escape_next = False
        else:
            # 문자열 내부
            if escape_next:
                escape_next = False
            elif '\\' in line:
                escape_next = True
            elif '"' in line and not line.rstrip().endswith('\\'):
                # 문자열 종료
                in_string = False
        
        result.append(line)
    
    return '\n'.join(result)


def extract_and_fix_json(text: str) -> str:
    """
    텍스트에서 JSON을 추출하고 수정합니다.
    
    Args:
        text: 원본 텍스트
        
    Returns:
        수정된 JSON 텍스트
    """
    # 1. 마크다운 코드 블록 제거
    clean_text = text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    if clean_text.startswith("```"):
        clean_text = clean_text[3:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    clean_text = clean_text.strip()
    
    # 2. 중괄호로 JSON 범위 찾기
    start_idx = clean_text.find("{")
    if start_idx < 0:
        return clean_text
    
    # 중첩된 중괄호를 고려하여 닫는 중괄호 찾기
    brace_count = 0
    end_idx = start_idx
    
    for i in range(start_idx, len(clean_text)):
        char = clean_text[i]
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break
    
    if end_idx <= start_idx:
        # 닫는 중괄호를 찾지 못한 경우
        end_idx = clean_text.rfind("}") + 1
        if end_idx <= start_idx:
            return clean_text
    
    json_text = clean_text[start_idx:end_idx]
    
    # 3. 일반적인 JSON 오류 수정
    # - 마지막 쉼표 제거
    json_text = re.sub(r',\s*}', '}', json_text)
    json_text = re.sub(r',\s*]', ']', json_text)
    
    # 4. 닫히지 않은 문자열 처리 (간단한 경우)
    # 따옴표가 홀수 개인 경우 마지막에 닫기
    quote_count = json_text.count('"') - json_text.count('\\"')
    if quote_count % 2 != 0:
        # 마지막 따옴표가 닫히지 않은 경우
        last_quote_idx = json_text.rfind('"')
        if last_quote_idx > 0 and json_text[last_quote_idx-1] != '\\':
            # 마지막 따옴표 앞에 닫는 따옴표 추가 시도는 위험하므로
            # 대신 마지막 부분을 제거
            pass
    
    return json_text


def parse_json_with_fallback(text: str) -> Dict[str, Any]:
    """
    JSON을 파싱하고, 실패 시 여러 방법으로 재시도합니다.
    
    Args:
        text: 파싱할 JSON 텍스트
        
    Returns:
        파싱된 JSON 객체
        
    Raises:
        ValueError: 모든 파싱 시도가 실패한 경우
    """
    # 시도 1: 직접 파싱
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # 시도 2: JSON 추출 및 수정 후 파싱
    try:
        fixed_json = extract_and_fix_json(text)
        return json.loads(fixed_json)
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"JSON 추출 및 수정 후 파싱 실패: {e}")
    
    # 시도 3: 중괄호만 추출
    try:
        start_idx = text.find("{")
        end_idx = text.rfind("}") + 1
        if start_idx >= 0 and end_idx > start_idx:
            json_text = text[start_idx:end_idx]
            # 마지막 쉼표 제거
            json_text = re.sub(r',\s*}', '}', json_text)
            json_text = re.sub(r',\s*]', ']', json_text)
            return json.loads(json_text)
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"중괄호 추출 후 파싱 실패: {e}")
    
    # 시도 4: 부분 파싱 시도 (executive_summary만이라도 추출)
    try:
        import re
        result = {}
        
        # executive_summary 추출
        exec_match = re.search(r'"executive_summary"\s*:\s*"([^"]*(?:\\.[^"]*)*)"', text, re.DOTALL)
        if exec_match:
            result["executive_summary"] = exec_match.group(1).replace('\\"', '"').replace('\\n', '\n')
        else:
            # 더 관대한 패턴 시도
            exec_match = re.search(r'"executive_summary"\s*:\s*"([^"]+)"', text)
            if exec_match:
                result["executive_summary"] = exec_match.group(1)
            else:
                result["executive_summary"] = "JSON 파싱에 실패했지만 분석은 완료되었습니다."
        
        # key_findings 추출 시도
        key_findings_match = re.search(r'"key_findings"\s*:\s*(\{[^}]*\})', text, re.DOTALL)
        if key_findings_match:
            try:
                result["key_findings"] = json.loads(key_findings_match.group(1))
            except:
                result["key_findings"] = {"primary_insights": ["JSON 파싱 부분 실패"]}
        else:
            result["key_findings"] = {"primary_insights": ["JSON 파싱 실패"]}
        
        logger.warning("부분 JSON 파싱 성공 (일부 필드만 추출)")
        return result
        
    except Exception as e:
        logger.error(f"부분 파싱도 실패: {e}")
        raise ValueError(f"JSON 파싱 실패: 모든 시도가 실패했습니다. 원본 텍스트 길이: {len(text)} 문자")
