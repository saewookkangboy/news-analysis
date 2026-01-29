# 마케팅 컨설턴트 Serveagent Role 및 분석 결과 리포트 고도화

**날짜**: 2026-01-28  
**역할**: Marketing Consultant (Serveagent) + dev-agent-kit 역할별 품질 체크  
**상태**: 완료

## 개요

'분석 결과'를 **정성적 리포트**로 출력하기 위해 **마케팅 컨설턴트 Serveagent Role** 메타 프롬프트를 추가하고, 분석 유형(keyword / audience / comprehensive)별 **리포트 출력 지침**을 적용했습니다. 이후 역할별 품질 체크리스트와 단위 테스트를 추가해 완성도를 검증했습니다.

## 변경 사항

### 1. 신규: `backend/prompts/` 모듈

- **`backend/prompts/__init__.py`**  
  - `get_meta_prompt_report_role`, `get_report_output_instructions` export.

- **`backend/prompts/marketing_consultant_meta.py`**  
  - **`get_meta_prompt_report_role()`**: 공통 메타 프롬프트 (마케팅 컨설턴트 Serveagent 역할, 리포트 품질 원칙 7조).  
  - **`get_report_output_instructions(target_type)`**: 분석 유형별 리포트 출력 지침.  
    - **keyword**: Executive Summary 스토리, Key Findings 근거→해석→시사점, 전략적 시사점 단계별 서술.  
    - **audience**: 타겟 스토리, 페르소나 서술, 고객 여정·전략 제안 연결.  
    - **comprehensive**: 키워드·오디언스 통합 스토리, 통합 인사이트, 다음 액션·성공 지표 해석.

### 2. 수정: `backend/services/target_analyzer.py`

- **Import**: `get_meta_prompt_report_role`, `get_report_output_instructions` 추가.  
- **`_build_system_message(target_type)`**:  
  - 기존 역할·규칙 앞에 **메타 역할 블록**(`get_meta_prompt_report_role()`)을 항상 포함.  
  - keyword/audience/comprehensive 공통으로 "마케팅 컨설턴트 Serveagent" 역할 적용.  
- **`_build_analysis_prompt(...)`**:  
  - **audience**: "[분석 프로세스]" 다음에 `get_report_output_instructions("audience")` 삽입 후 JSON 스키마 안내.  
  - **keyword**: "[품질 규칙]" 다음에 `get_report_output_instructions("keyword")` 삽입 후 JSON 스키마 안내.  
  - **comprehensive**: "추가 컨텍스트" 다음에 `get_report_output_instructions("comprehensive")` 삽입 후 JSON 구조 안내.

### 3. 테스트: `tests/test_target_analyzer.py`

- **Import**: `_build_system_message`, `_build_analysis_prompt`, `get_meta_prompt_report_role`, `get_report_output_instructions` 추가.  
- **`TestMarketingConsultantMeta`** 클래스 추가:  
  - `test_system_message_includes_meta_role`: 시스템 메시지에 "마케팅 컨설턴트"/"Serveagent", "리포트"/"보고서" 포함.  
  - `test_analysis_prompt_includes_report_instructions_keyword`: 키워드 프롬프트에 Executive Summary/Key Findings 및 리포트 지침 반영.  
  - `test_analysis_prompt_includes_report_instructions_audience`: 오디언스 프롬프트에 executive_summary, 페르소나, 고객 여정 관련 내용 포함.  
  - `test_analysis_prompt_includes_report_instructions_comprehensive`: 종합 프롬프트에 executive_summary, 통합 관련 내용 포함.  
  - `test_meta_prompt_module_returns_non_empty`: 메타 프롬프트·유형별 지침이 비어 있지 않은 문자열 반환.

### 4. 문서: `docs/ANALYSIS_REPORT_QUALITY_CHECK.md`

- **역할별 품질 체크리스트**: PM, Security, Backend, Frontend, UI/UX, AI Researcher, Server/DB, Marketing Consultant 8개 역할별 체크 항목·확인 방법·통과 기준.  
- **디버깅·테스트 실행 요약**: 단위 테스트 명령, API 수동 검증(기본 분석 모드), 실제 AI 분석 품질 확인(선택) 방법.  
- **완료 상태**: 메타 프롬프트 적용·테스트·문서화 완료, E2E/수동 최종 확인은 선택 사항으로 명시.

## 기대 효과

- **정성적 리포트**: Executive Summary가 5~10문장 스토리로, Key Findings/Insights가 근거→해석→시사점 구조로 출력되도록 유도.  
- **유형별 최적화**: 키워드(기회·우선순위), 오디언스(페르소나·여정), 종합(통합 스토리·다음 액션)에 맞는 서술 톤과 구조.  
- **품질 검증**: 역할별 체크리스트와 단위 테스트로 메타 프롬프트 적용 여부 및 기본 구조를 자동·수동으로 확인 가능.

## 영향 범위

- **수정 파일**: `backend/services/target_analyzer.py`  
- **신규 파일**: `backend/prompts/__init__.py`, `backend/prompts/marketing_consultant_meta.py`, `docs/ANALYSIS_REPORT_QUALITY_CHECK.md`, `tests/test_target_analyzer.py` (클래스·테스트 추가)  
- **API 스펙**: 변경 없음. 기존 분석 API 응답 구조 유지, 출력 **내용** 품질만 메타 프롬프트로 고도화.
