"""
JSON 복구 유틸리티
잘린 JSON이나 특수 문자가 포함된 JSON을 복구합니다.
"""
import re
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def repair_json(text: str) -> Optional[str]:
    """
    잘린 JSON이나 오류가 있는 JSON을 복구 시도합니다.
    
    Args:
        text: 복구할 JSON 텍스트
        
    Returns:
        복구된 JSON 텍스트 또는 None
    """
    if not text:
        return None
    
    # 1. 마크다운 코드 블록 제거
    clean_text = text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    if clean_text.startswith("```"):
        clean_text = clean_text[3:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    clean_text = clean_text.strip()
    
    # 2. 중괄호로 감싸진 부분만 추출
    start_idx = clean_text.find("{")
    if start_idx < 0:
        return None
    
    # 3. 닫는 중괄호 찾기 (마지막 유효한 중괄호)
    end_idx = clean_text.rfind("}")
    if end_idx <= start_idx:
        return None
    
    json_text = clean_text[start_idx:end_idx + 1]
    
    # 4. 잘린 문자열 복구 시도
    json_text = _fix_unterminated_strings(json_text)
    
    # 5. 잘린 배열/객체 복구 시도
    json_text = _fix_truncated_structures(json_text)
    
    # 6. 마지막 쉼표 제거
    json_text = _remove_trailing_commas(json_text)
    
    return json_text


def _fix_unterminated_strings(text: str) -> str:
    """잘린 문자열을 복구합니다."""
    # 문자열 내부의 따옴표를 찾아서 이스케이프 처리
    # 단순한 방법: 마지막 문자열이 잘렸다면 닫기
    
    # 따옴표로 시작하는 문자열 패턴 찾기
    # 마지막에 따옴표 없이 끝나는 문자열 찾기
    lines = text.split('\n')
    fixed_lines = []
    
    in_string = False
    escape_next = False
    
    for i, line in enumerate(lines):
        fixed_line = line
        for j, char in enumerate(line):
            if escape_next:
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                continue
            
            if char == '"' and not escape_next:
                in_string = not in_string
            
            # 마지막 줄이고 문자열이 열려있으면 닫기
            if i == len(lines) - 1 and j == len(line) - 1 and in_string:
                fixed_line += '"'
                in_string = False
        
        fixed_lines.append(fixed_line)
    
    return '\n'.join(fixed_lines)


def _fix_truncated_structures(text: str) -> str:
    """잘린 배열이나 객체를 복구합니다."""
    # 열린 중괄호/대괄호 개수 세기
    open_braces = text.count('{')
    close_braces = text.count('}')
    open_brackets = text.count('[')
    close_brackets = text.count(']')
    
    # 닫는 중괄호/대괄호 추가
    result = text
    for _ in range(open_braces - close_braces):
        result += '}'
    for _ in range(open_brackets - close_brackets):
        result += ']'
    
    return result


def _remove_trailing_commas(text: str) -> str:
    """마지막 쉼표를 제거합니다."""
    # JSON에서 유효하지 않은 마지막 쉼표 제거
    # 예: { "key": "value", } -> { "key": "value" }
    
    # 객체/배열 내부의 마지막 쉼표 제거
    # 정규식으로 패턴 찾기: ,\s*[}\]]
    text = re.sub(r',\s*([}\]])', r'\1', text)
    
    return text


def parse_json_with_repair(text: str) -> Optional[Dict[str, Any]]:
    """
    JSON을 파싱하고 실패 시 복구를 시도합니다.
    
    Args:
        text: 파싱할 JSON 텍스트
        
    Returns:
        파싱된 JSON 객체 또는 None
    """
    if not text:
        return None
    
    # 1차 시도: 직접 파싱
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # 2차 시도: 마크다운 제거 후 파싱
    try:
        clean_text = text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()
        
        return json.loads(clean_text)
    except json.JSONDecodeError:
        pass
    
    # 3차 시도: 중괄호 추출 후 파싱
    try:
        start_idx = clean_text.find("{")
        end_idx = clean_text.rfind("}") + 1
        if start_idx >= 0 and end_idx > start_idx:
            json_text = clean_text[start_idx:end_idx]
            return json.loads(json_text)
    except (json.JSONDecodeError, ValueError):
        pass
    
    # 4차 시도: JSON 복구 후 파싱
    try:
        repaired = repair_json(text)
        if repaired:
            return json.loads(repaired)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON 복구 후 파싱 실패: {e}")
    
    # 5차 시도: 부분 JSON 추출 (최소한의 구조라도)
    try:
        return _extract_partial_json(clean_text)
    except Exception as e:
        logger.warning(f"부분 JSON 추출 실패: {e}")
    
    return None


def _extract_partial_json(text: str) -> Dict[str, Any]:
    """부분적으로라도 JSON 구조를 추출합니다."""
    result = {}
    
    # executive_summary 추출
    exec_match = re.search(r'"executive_summary"\s*:\s*"([^"]*(?:\\.[^"]*)*)"', text, re.DOTALL)
    if exec_match:
        result["executive_summary"] = exec_match.group(1).replace('\\"', '"')
    else:
        # 더 관대한 패턴 시도
        exec_match = re.search(r'"executive_summary"\s*:\s*"([^"]*)"', text[:2000])
        if exec_match:
            result["executive_summary"] = exec_match.group(1)
    
    # key_findings 추출 시도
    if '"key_findings"' in text:
        result["key_findings"] = {
            "primary_insights": ["JSON 파싱 중 부분 추출"],
            "quantitative_metrics": {}
        }
    
    # detailed_analysis 추출 시도
    if '"detailed_analysis"' in text:
        result["detailed_analysis"] = {
            "insights": {
                "note": "JSON이 완전하지 않아 부분 추출되었습니다."
            }
        }
    
    # strategic_recommendations 추출 시도
    if '"strategic_recommendations"' in text:
        result["strategic_recommendations"] = {
            "immediate_actions": ["JSON 파싱 오류로 인해 완전한 추출이 불가능했습니다."]
        }
    
    # 최소한의 구조라도 반환
    if not result:
        result = {
            "executive_summary": "JSON 파싱에 실패했지만 응답은 수신되었습니다.",
            "key_findings": {
                "primary_insights": ["원본 응답 확인 필요"],
                "quantitative_metrics": {}
            },
            "error": "JSON 파싱 실패",
            "raw_response_preview": text[:500] if len(text) > 500 else text
        }
    
    return result
