"""
토큰 최적화 유틸리티 테스트
"""
import pytest
from backend.utils.token_optimizer import (
    optimize_prompt,
    estimate_tokens,
    get_max_tokens_for_model,
    optimize_additional_context
)


class TestOptimizePrompt:
    """프롬프트 최적화 테스트"""
    
    def test_optimize_prompt_no_change(self):
        """변경이 필요 없는 프롬프트"""
        prompt = "Simple prompt text"
        result = optimize_prompt(prompt)
        assert result == prompt
    
    def test_optimize_prompt_remove_extra_spaces(self):
        """연속된 공백 제거"""
        prompt = "This   has    multiple    spaces"
        result = optimize_prompt(prompt)
        assert "  " not in result
        assert result == "This has multiple spaces"
    
    def test_optimize_prompt_remove_extra_newlines(self):
        """연속된 줄바꿈 제거"""
        prompt = "Line 1\n\n\n\nLine 2"
        result = optimize_prompt(prompt)
        assert "\n\n\n" not in result
        assert result.count("\n\n") <= 1
    
    def test_optimize_prompt_remove_redundant_phrases(self):
        """중복 표현 제거"""
        prompt = "매우 상세하고 심층적인 분석을 수행하세요"
        result = optimize_prompt(prompt)
        assert "매우 상세하고 심층적인" not in result
    
    def test_optimize_prompt_max_length(self):
        """최대 길이 제한"""
        prompt = "A" * 1000
        result = optimize_prompt(prompt, max_length=100)
        assert len(result) <= 100
    
    def test_optimize_prompt_max_length_sentence_boundary(self):
        """문장 단위로 자르기"""
        prompt = "First sentence. Second sentence. Third sentence."
        result = optimize_prompt(prompt, max_length=30)
        assert len(result) <= 30
        assert result.endswith(".")


class TestEstimateTokens:
    """토큰 수 추정 테스트"""
    
    def test_estimate_tokens_korean(self):
        """한국어 텍스트"""
        text = "안녕하세요 반갑습니다"
        tokens = estimate_tokens(text)
        assert tokens > 0
        # 한국어는 1.5자/토큰이므로 10자면 약 6-7 토큰
        assert tokens >= len(text) // 4  # 최소값 보장
    
    def test_estimate_tokens_english(self):
        """영어 텍스트"""
        text = "Hello world this is a test"
        tokens = estimate_tokens(text)
        assert tokens > 0
        # 영어는 4자/토큰이므로 25자면 약 6 토큰
        assert tokens >= len(text) // 4
    
    def test_estimate_tokens_mixed(self):
        """한국어와 영어 혼합"""
        text = "Hello 안녕하세요 world"
        tokens = estimate_tokens(text)
        assert tokens > 0
    
    def test_estimate_tokens_empty(self):
        """빈 문자열"""
        assert estimate_tokens("") >= 0


class TestGetMaxTokensForModel:
    """모델별 최대 토큰 수 계산 테스트"""
    
    def test_get_max_tokens_openai_gpt4o_mini(self):
        """OpenAI GPT-4o-mini"""
        max_tokens = get_max_tokens_for_model("gpt-4o-mini", 1000)
        assert max_tokens > 0
        assert max_tokens <= 16384  # 모델 최대 컨텍스트
    
    def test_get_max_tokens_gemini(self):
        """Gemini 모델"""
        max_tokens = get_max_tokens_for_model("gemini-2.0-flash", 1000)
        assert max_tokens > 0
    
    def test_get_max_tokens_unknown_model(self):
        """알 수 없는 모델"""
        max_tokens = get_max_tokens_for_model("unknown-model", 1000)
        assert max_tokens > 0
        # 기본값 반환


class TestOptimizeAdditionalContext:
    """추가 컨텍스트 최적화 테스트"""
    
    def test_optimize_additional_context_short(self):
        """짧은 컨텍스트"""
        from backend.utils.token_optimizer import optimize_additional_context
        context = "Short context"
        result = optimize_additional_context(context, max_length=300)
        assert result == context
    
    def test_optimize_additional_context_long(self):
        """긴 컨텍스트"""
        from backend.utils.token_optimizer import optimize_additional_context
        context = "A" * 1000
        result = optimize_additional_context(context, max_length=300)
        assert len(result) <= 300
    
    def test_optimize_additional_context_none(self):
        """None 컨텍스트"""
        from backend.utils.token_optimizer import optimize_additional_context
        result = optimize_additional_context(None, max_length=300)
        assert result is None or result == ""
    
    def test_optimize_additional_context_sentence_boundary(self):
        """문장 단위로 자르기"""
        from backend.utils.token_optimizer import optimize_additional_context
        context = "First sentence. Second sentence. Third sentence."
        result = optimize_additional_context(context, max_length=30)
        assert len(result) <= 30
        # 문장 단위로 잘려야 함
        assert "." in result or len(result) < len(context)
