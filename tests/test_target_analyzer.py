"""
타겟 분석 서비스 테스트 (Mock 기반)
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from backend.services.target_analyzer import analyze_target, _analyze_basic


class TestAnalyzeTarget:
    """타겟 분석 함수 테스트"""
    
    @pytest.mark.asyncio
    async def test_analyze_target_no_api_keys(self):
        """API 키가 없는 경우 기본 분석 모드"""
        with patch('backend.services.target_analyzer.get_api_key_safely', return_value=None):
            result = await analyze_target(
                target_keyword="테스트",
                target_type="keyword"
            )
            assert result is not None
            assert "target_keyword" in result
            assert result["target_keyword"] == "테스트"
            assert "api_key_status" in result
    
    async def test_analyze_target_with_openai_mock(self):
        """OpenAI API Mock 테스트"""
        mock_result = {
            "executive_summary": "테스트 요약",
            "key_findings": {
                "primary_insights": ["인사이트 1"],
                "quantitative_metrics": {}
            },
            "target_keyword": "테스트",
            "target_type": "keyword"
        }
        
        with patch('backend.services.target_analyzer.get_api_key_safely') as mock_key, \
             patch('backend.services.target_analyzer._analyze_with_openai', new_callable=AsyncMock) as mock_openai:
            
            mock_key.side_effect = lambda x: "sk-test123..." if x == "OPENAI_API_KEY" else None
            mock_openai.return_value = mock_result
            
            result = await analyze_target(
                target_keyword="테스트",
                target_type="keyword"
            )
            
            assert result is not None
            assert result["target_keyword"] == "테스트"
            mock_openai.assert_called_once()
    
    async def test_analyze_target_openai_fallback_to_gemini(self):
        """OpenAI 실패 시 Gemini로 재시도"""
        mock_gemini_result = {
            "executive_summary": "Gemini 요약",
            "target_keyword": "테스트",
            "target_type": "keyword"
        }
        
        with patch('backend.services.target_analyzer.get_api_key_safely') as mock_key, \
             patch('backend.services.target_analyzer._analyze_with_openai', new_callable=AsyncMock) as mock_openai, \
             patch('backend.services.target_analyzer._analyze_with_gemini', new_callable=AsyncMock) as mock_gemini:
            
            mock_key.side_effect = lambda x: "test-key" if x in ["OPENAI_API_KEY", "GEMINI_API_KEY"] else None
            mock_openai.side_effect = Exception("OpenAI API 실패")
            mock_gemini.return_value = mock_gemini_result
            
            result = await analyze_target(
                target_keyword="테스트",
                target_type="keyword"
            )
            
            assert result is not None
            assert mock_gemini.called
    
    async def test_analyze_target_invalid_type(self):
        """잘못된 타겟 타입 - routes.py에서 검증되므로 여기서는 경고만 발생"""
        # target_analyzer는 직접 검증하지 않고, routes.py에서 검증함
        # 따라서 여기서는 기본 분석 모드로 진행됨
        with patch('backend.services.target_analyzer.get_api_key_safely', return_value=None):
            result = await analyze_target(
                target_keyword="테스트",
                target_type="invalid"
            )
            # 기본 분석 모드로 진행되므로 결과는 반환됨
            assert result is not None


class TestAnalyzeBasic:
    """기본 분석 함수 테스트"""
    
    def test_analyze_basic_keyword(self):
        """키워드 기본 분석"""
        result = _analyze_basic(
            target_keyword="테스트 키워드",
            target_type="keyword",
            additional_context=None
        )
        assert result is not None
        assert result["target_keyword"] == "테스트 키워드"
        assert result["target_type"] == "keyword"
        assert "executive_summary" in result
        assert "key_findings" in result
    
    def test_analyze_basic_audience(self):
        """오디언스 기본 분석"""
        result = _analyze_basic(
            target_keyword="테스트",
            target_type="audience",
            additional_context=None
        )
        assert result is not None
        assert result["target_type"] == "audience"
    
    def test_analyze_basic_with_dates(self):
        """날짜 포함 기본 분석"""
        result = _analyze_basic(
            target_keyword="테스트",
            target_type="keyword",
            additional_context=None,
            start_date="2025-01-01",
            end_date="2025-01-31"
        )
        assert result is not None
        assert "2025-01-01" in result.get("executive_summary", "") or "2025-01-31" in result.get("executive_summary", "")
    
    def test_analyze_basic_with_context(self):
        """추가 컨텍스트 포함 기본 분석"""
        result = _analyze_basic(
            target_keyword="테스트",
            target_type="keyword",
            additional_context="추가 정보"
        )
        assert result is not None
        assert "additional_context" in result
