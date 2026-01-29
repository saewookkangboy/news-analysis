"""
타겟 분석 서비스 테스트 (Mock 기반)
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from backend.services.target_analyzer import (
    analyze_target,
    _analyze_basic,
    _build_system_message,
    _build_analysis_prompt,
)
from backend.prompts.marketing_consultant_meta import (
    get_meta_prompt_report_role,
    get_report_output_instructions,
)


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


class TestMarketingConsultantMeta:
    """마케팅 컨설턴트 메타 프롬프트 통합 검증"""

    def test_system_message_includes_meta_role(self):
        """시스템 메시지에 마케팅 컨설턴트 Serveagent 역할 포함"""
        for target_type in ("keyword", "audience", "comprehensive"):
            msg = _build_system_message(target_type)
            assert "마케팅 컨설턴트" in msg or "Serveagent" in msg
            assert "리포트" in msg or "보고서" in msg

    def test_analysis_prompt_includes_report_instructions_keyword(self):
        """키워드 분석 프롬프트에 리포트 출력 지침 포함"""
        prompt = _build_analysis_prompt("테스트", "keyword", None, None, None)
        instr = get_report_output_instructions("keyword")
        assert "Executive Summary" in prompt or "executive_summary" in prompt
        assert "Key Findings" in prompt or "key_findings" in prompt
        assert instr.strip()[:30] in prompt or "근거" in prompt

    def test_analysis_prompt_includes_report_instructions_audience(self):
        """오디언스 분석 프롬프트에 리포트 출력 지침 포함"""
        prompt = _build_analysis_prompt("테스트", "audience", None, None, None)
        assert "executive_summary" in prompt or "Executive Summary" in prompt
        assert "페르소나" in prompt
        assert "고객 여정" in prompt or "customer_journey" in prompt

    def test_analysis_prompt_includes_report_instructions_comprehensive(self):
        """종합 분석 프롬프트에 리포트 출력 지침 포함"""
        prompt = _build_analysis_prompt("테스트", "comprehensive", None, None, None)
        assert "executive_summary" in prompt
        assert "integrated" in prompt.lower() or "통합" in prompt

    def test_meta_prompt_module_returns_non_empty(self):
        """메타 프롬프트 모듈이 비어 있지 않은 문자열 반환"""
        assert len(get_meta_prompt_report_role()) > 100
        assert len(get_report_output_instructions("keyword")) > 50
        assert len(get_report_output_instructions("audience")) > 50
        assert len(get_report_output_instructions("comprehensive")) > 50
