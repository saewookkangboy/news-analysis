"""
pytest 설정 및 공통 픽스처
"""
import os
import pytest
from unittest.mock import patch, MagicMock

# 테스트 환경 변수 설정
os.environ.setdefault("LOG_LEVEL", "WARNING")
os.environ.setdefault("CACHE_ENABLED", "false")


@pytest.fixture
def mock_openai_key():
    """OpenAI API 키 모킹"""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test123456789012345678901234567890"}):
        yield


@pytest.fixture
def mock_gemini_key():
    """Gemini API 키 모킹"""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test123456789012345678901234567890"}):
        yield


@pytest.fixture
def mock_both_keys(mock_openai_key, mock_gemini_key):
    """두 API 키 모두 모킹"""
    yield


@pytest.fixture
def no_api_keys():
    """API 키 없는 환경 모킹"""
    with patch.dict(os.environ, {}, clear=True):
        # Settings도 모킹
        with patch("backend.config.settings.OPENAI_API_KEY", None), \
             patch("backend.config.settings.GEMINI_API_KEY", None):
            yield
