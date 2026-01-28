"""
JSON 복구 유틸리티 테스트
"""
import pytest
import json
from backend.utils.json_repair import (
    repair_json,
    parse_json_with_repair,
    _fix_unterminated_strings,
    _fix_truncated_structures,
    _remove_trailing_commas
)


class TestRepairJson:
    """JSON 복구 함수 테스트"""
    
    def test_repair_json_none(self):
        """None 또는 빈 문자열 처리"""
        assert repair_json(None) is None
        assert repair_json("") is None
        assert repair_json("   ") is None
    
    def test_repair_json_markdown_code_block(self):
        """마크다운 코드 블록 제거"""
        text = "```json\n{\"key\": \"value\"}\n```"
        result = repair_json(text)
        assert result is not None
        assert "```" not in result
        assert json.loads(result) == {"key": "value"}
    
    def test_repair_json_no_braces(self):
        """중괄호가 없는 경우"""
        assert repair_json("just text") is None
        assert repair_json("no json here") is None
    
    def test_repair_json_valid_json(self):
        """유효한 JSON"""
        text = '{"key": "value", "number": 123}'
        result = repair_json(text)
        assert result is not None
        assert json.loads(result) == {"key": "value", "number": 123}
    
    def test_repair_json_with_text_before_after(self):
        """JSON 앞뒤에 텍스트가 있는 경우"""
        text = 'Some text before {"key": "value"} and after'
        result = repair_json(text)
        assert result is not None
        assert json.loads(result) == {"key": "value"}


class TestFixUnterminatedStrings:
    """잘린 문자열 복구 테스트"""
    
    def test_fix_unterminated_strings_complete(self):
        """완전한 문자열"""
        text = '{"key": "value"}'
        result = _fix_unterminated_strings(text)
        assert result == text
    
    def test_fix_unterminated_strings_truncated(self):
        """잘린 문자열"""
        text = '{"key": "incomplete'
        result = _fix_unterminated_strings(text)
        assert '"' in result
        assert result.endswith('"') or '"incomplete"' in result


class TestFixTruncatedStructures:
    """잘린 구조 복구 테스트"""
    
    def test_fix_truncated_structures_complete(self):
        """완전한 구조"""
        text = '{"key": {"nested": "value"}}'
        result = _fix_truncated_structures(text)
        assert result == text
    
    def test_fix_truncated_structures_missing_brace(self):
        """닫는 중괄호 누락"""
        text = '{"key": {"nested": "value"'
        result = _fix_truncated_structures(text)
        assert result.count('{') == result.count('}')
    
    def test_fix_truncated_structures_missing_bracket(self):
        """닫는 대괄호 누락"""
        text = '{"key": [1, 2, 3'
        result = _fix_truncated_structures(text)
        assert result.count('[') == result.count(']')


class TestRemoveTrailingCommas:
    """마지막 쉼표 제거 테스트"""
    
    def test_remove_trailing_commas_object(self):
        """객체의 마지막 쉼표 제거"""
        text = '{"key1": "value1", "key2": "value2",}'
        result = _remove_trailing_commas(text)
        assert result == '{"key1": "value1", "key2": "value2"}'
    
    def test_remove_trailing_commas_array(self):
        """배열의 마지막 쉼표 제거"""
        text = '{"items": [1, 2, 3,]}'
        result = _remove_trailing_commas(text)
        assert result == '{"items": [1, 2, 3]}'
    
    def test_remove_trailing_commas_no_trailing(self):
        """마지막 쉼표가 없는 경우"""
        text = '{"key": "value"}'
        result = _remove_trailing_commas(text)
        assert result == text


class TestParseJsonWithRepair:
    """JSON 파싱 및 복구 테스트"""
    
    def test_parse_json_with_repair_valid(self):
        """유효한 JSON 파싱"""
        text = '{"key": "value", "number": 123}'
        result = parse_json_with_repair(text)
        assert result == {"key": "value", "number": 123}
    
    def test_parse_json_with_repair_markdown(self):
        """마크다운 코드 블록 포함"""
        text = "```json\n{\"key\": \"value\"}\n```"
        result = parse_json_with_repair(text)
        assert result == {"key": "value"}
    
    def test_parse_json_with_repair_trailing_comma(self):
        """마지막 쉼표 포함"""
        text = '{"key": "value",}'
        result = parse_json_with_repair(text)
        assert result == {"key": "value"}
    
    def test_parse_json_with_repair_truncated(self):
        """잘린 JSON"""
        text = '{"key": "value", "nested": {'
        result = parse_json_with_repair(text)
        # 복구 시도 후 최소한 None이 아닌 결과 반환
        assert result is not None
    
    def test_parse_json_with_repair_none(self):
        """None 또는 빈 문자열"""
        assert parse_json_with_repair(None) is None
        assert parse_json_with_repair("") is None
    
    def test_parse_json_with_repair_partial_extraction(self):
        """부분 JSON 추출"""
        text = 'Some text before {"executive_summary": "test"} and more text'
        result = parse_json_with_repair(text)
        assert result is not None
        assert "executive_summary" in result
