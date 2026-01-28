"""
보안 유틸리티 테스트
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from backend.utils.security import (
    validate_api_key,
    get_api_key_safely,
    check_api_keys_status,
    log_api_key_status_safely,
    mask_api_key
)


class TestValidateApiKey:
    """API 키 검증 테스트"""
    
    def test_validate_api_key_none(self):
        """None 값 검증"""
        assert validate_api_key(None) is False
    
    def test_validate_api_key_empty_string(self):
        """빈 문자열 검증"""
        assert validate_api_key("") is False
        assert validate_api_key("   ") is False
    
    def test_validate_openai_key_valid(self):
        """유효한 OpenAI API 키 검증"""
        valid_key = "sk-" + "a" * 20
        assert validate_api_key(valid_key, "OPENAI_API_KEY") is True
    
    def test_validate_openai_key_invalid_prefix(self):
        """잘못된 접두사의 OpenAI API 키"""
        invalid_key = "invalid-" + "a" * 20
        assert validate_api_key(invalid_key, "OPENAI_API_KEY") is False
    
    def test_validate_openai_key_too_short(self):
        """너무 짧은 OpenAI API 키"""
        short_key = "sk-123"
        assert validate_api_key(short_key, "OPENAI_API_KEY") is False
    
    def test_validate_gemini_key_valid(self):
        """유효한 Gemini API 키 검증"""
        valid_key = "a" * 25
        assert validate_api_key(valid_key, "GEMINI_API_KEY") is True
    
    def test_validate_gemini_key_too_short(self):
        """너무 짧은 Gemini API 키"""
        short_key = "a" * 10
        assert validate_api_key(short_key, "GEMINI_API_KEY") is False
    
    def test_validate_other_key_valid(self):
        """기타 API 키 검증 (최소 20자)"""
        valid_key = "a" * 25
        assert validate_api_key(valid_key, "OTHER_API_KEY") is True
    
    def test_validate_other_key_too_short(self):
        """너무 짧은 기타 API 키"""
        short_key = "a" * 10
        assert validate_api_key(short_key, "OTHER_API_KEY") is False


class TestGetApiKeySafely:
    """안전한 API 키 가져오기 테스트"""
    
    def test_get_api_key_from_env(self, mock_openai_key):
        """환경 변수에서 API 키 가져오기"""
        key = get_api_key_safely("OPENAI_API_KEY")
        assert key is not None
        assert key.startswith("sk-")
    
    def test_get_api_key_not_found(self, no_api_keys):
        """API 키가 없는 경우"""
        key = get_api_key_safely("OPENAI_API_KEY")
        assert key is None
    
    def test_get_api_key_invalid(self):
        """유효하지 않은 API 키"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "invalid"}):
            key = get_api_key_safely("OPENAI_API_KEY")
            assert key is None


class TestCheckApiKeysStatus:
    """API 키 상태 확인 테스트"""
    
    def test_check_api_keys_both_configured(self, mock_both_keys):
        """두 API 키 모두 설정된 경우"""
        status = check_api_keys_status()
        assert status["openai_configured"] is True
        assert status["gemini_configured"] is True
        assert "모든 API 키가 설정되었습니다" in status["message"]
    
    def test_check_api_keys_only_openai(self, mock_openai_key):
        """OpenAI 키만 설정된 경우"""
        with patch.dict(os.environ, {}, clear=True):
            with patch("backend.config.settings.GEMINI_API_KEY", None):
                status = check_api_keys_status()
                assert status["openai_configured"] is True
                assert status["gemini_configured"] is False
                assert "Gemini API 키가 설정되지 않았습니다" in status["message"]
    
    def test_check_api_keys_none(self, no_api_keys):
        """API 키가 없는 경우"""
        status = check_api_keys_status()
        assert status["openai_configured"] is False
        assert status["gemini_configured"] is False
        assert "모두 설정되지 않았습니다" in status["message"]


class TestMaskApiKey:
    """API 키 마스킹 테스트"""
    
    def test_mask_api_key_none(self):
        """None 값 마스킹"""
        assert mask_api_key(None) == "None"
    
    def test_mask_api_key_short(self):
        """짧은 키 마스킹"""
        assert mask_api_key("short") == "***"
    
    def test_mask_api_key_normal(self):
        """일반 키 마스킹"""
        key = "sk-test123456789012345678901234567890"
        masked = mask_api_key(key)
        assert masked.startswith("sk-t")
        assert masked.endswith("7890")
        assert "..." in masked
    
    def test_mask_api_key_with_length(self):
        """길이 정보 포함 마스킹"""
        key = "sk-test123456789012345678901234567890"
        masked = mask_api_key(key, show_length=True)
        assert "길이:" in masked
        assert "문자" in masked
