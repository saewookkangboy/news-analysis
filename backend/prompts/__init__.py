"""
프롬프트 모듈: 분석·리포트용 메타 프롬프트 및 역할 정의
"""
from backend.prompts.marketing_consultant_meta import (
    get_meta_prompt_report_role,
    get_report_output_instructions,
)

__all__ = [
    "get_meta_prompt_report_role",
    "get_report_output_instructions",
]
