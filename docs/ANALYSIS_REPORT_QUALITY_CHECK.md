# 분석 결과 품질 체크 — 역할별 체크리스트

**목적**: 마케팅 컨설턴트 메타 프롬프트 적용 후, dev-agent-kit 각 업무 역할별로 '분석 결과' 품질을 점검하고 완성도 확인.

**대상**: 타겟 분석 API 응답 (키워드 / 오디언스 / 종합 분석)

---

## 1. PM (프로젝트 관리)

| 체크 항목 | 확인 방법 | 통과 기준 |
|-----------|------------|-----------|
| 분석 유형별 결과 구조 일관성 | keyword/audience/comprehensive 각각 1회 요청 후 응답 JSON 검사 | `executive_summary`, `key_findings` 또는 `key_insights`, `detailed_analysis`, `strategic_recommendations`(또는 유형별 동일 필드) 존재 |
| 마일스톤 반영 | 메타 프롬프트 적용 여부 | 시스템 메시지에 "마케팅 컨설턴트 Serveagent" 포함, 프롬프트에 "리포트 출력 지침" 포함 |
| 문서화 | `.spec-kit/changelog`, `docs/` | 메타 프롬프트 추가·변경 이력 문서화 완료 |

---

## 2. Security Manager (보안)

| 체크 항목 | 확인 방법 | 통과 기준 |
|-----------|------------|-----------|
| API 키 노출 여부 | 분석 요청/응답 로그 및 클라이언트 노출 필드 검사 | 응답 본문·로그에 API 키 값 미포함 |
| 환경 변수 의존성 | API 키 없이 요청 시 | 기본 분석 모드로 정상 응답, 에러 메시지에 키 값 미포함 |

---

## 3. Backend Developer (백엔드)

| 체크 항목 | 확인 방법 | 통과 기준 |
|-----------|------------|-----------|
| 에러 핸들링 | 잘못된 `target_type`, 잘못된 날짜 형식 등 | 400/422 응답, 일관된 에러 스키마 |
| 응답 스키마 | `result_normalizer`, `ensure_result_structure` | 필수 필드(`executive_summary`, `target_keyword`, `target_type` 등) 누락 없음 |
| 메타 프롬프트 주입 | `_build_system_message`, `_build_analysis_prompt` | `get_meta_prompt_report_role()`, `get_report_output_instructions(target_type)` 호출 및 반영 |
| 테스트 | `pytest tests/test_target_analyzer.py` | TestMarketingConsultantMeta 포함 전체 통과 |

---

## 4. Frontend Developer (프론트엔드)

| 체크 항목 | 확인 방법 | 통과 기준 |
|-----------|------------|-----------|
| 분석 결과 표시 | 대시보드/분석 결과 영역에서 `executive_summary`, `key_findings` 등 렌더링 | 섹션별 제목·본문 표시, 스트리밍 시 문장 단위 표시 |
| 로딩/에러 상태 | API 실패·타임아웃 시 | 에러 메시지 노출, 재시도 또는 안내 문구 |
| 스트리밍 | `/target/analyze/stream` 응답 | NDJSON 파싱, `sentence`/`progress`/`complete`/`error` 타입 처리 |

---

## 5. UI/UX Designer (UI/UX)

| 체크 항목 | 확인 방법 | 통과 기준 |
|-----------|------------|-----------|
| 리포트 가독성 | Executive Summary, Key Findings 블록 표시 | 계층(번호/불릿), 줄바꿈, 강조가 읽기 쉽게 적용 |
| 반응형 | 모바일/태블릿에서 분석 결과 영역 | 레이아웃 깨짐 없음, 스크롤·접기 등 동작 |
| 접근성 | 스크린 리더, 키보드 포커스 | 섹션 제목·랜드마크, 포커스 순서 적절 |

---

## 6. AI Marketing Researcher (AI 리서치)

| 체크 항목 | 확인 방법 | 통과 기준 |
|-----------|------------|-----------|
| 정성적 서술 | Executive Summary, Key Findings/Insights 내용 | 수치 나열만이 아닌 "무엇이 중요한지·왜·그래서 무엇을 할지" 문장으로 서술 |
| 유형별 스토리 | keyword / audience / comprehensive | 키워드: 기회·리스크·우선순위 서술 / 오디언스: 페르소나·여정 서술 / 종합: 통합 스토리·다음 액션 |
| MECE·근거 | 각 섹션 내용 | 항목 간 중복 최소화, 추정 시 "추정" 표기, 근거/출처 언급 |

---

## 7. Server/DB Developer (서버/배포)

| 체크 항목 | 확인 방법 | 통과 기준 |
|-----------|------------|-----------|
| 헬스/메트릭 | `/health`, `/metrics` | 200 응답, 서비스 상태·API 키 상태(값 미노출) 확인 가능 |
| 타임아웃·리소스 | 장시간 분석 요청 | Vercel/배포 환경에서 설정된 maxDuration 내 응답 또는 스트리밍 유지 |
| 로그 | 프로덕션 로그 | API 키·개인정보 미포함, 에러 시 추적 가능한 식별자 |

---

## 8. Marketing Consultant (마케팅 컨설턴트 — Serveagent)

| 체크 항목 | 확인 방법 | 통과 기준 |
|-----------|------------|-----------|
| 메타 역할 반영 | 시스템 메시지 | "마케팅 컨설턴트 Serveagent", "리포트", "정성적 서술" 등 포함 |
| 유형별 리포트 지침 | 사용자 프롬프트 | keyword/audience/comprehensive 각각 "리포트 출력 지침" 블록 포함 |
| 출력 품질 | 샘플 분석 1회 이상 (API 키 있을 때) | Executive Summary가 5~10문장 스토리, Key Findings에 근거→해석→시사점 구조, 실행 가능한 권장사항 포함 |

---

## 디버깅·테스트 실행 요약

1. **단위 테스트**  
   ```bash
   python -m pytest tests/test_target_analyzer.py -v
   ```  
   - `TestMarketingConsultantMeta` 5개 + 기존 테스트 전부 통과 확인.

2. **API 수동 검증 (기본 분석 모드)**  
   - API 키 없이 `POST /api/target/analyze` body: `{"target_keyword": "전기차", "target_type": "keyword"}`  
   - 응답에 `executive_summary`, `key_findings`, `target_keyword`, `target_type`, `api_key_status` 존재 확인.

3. **실제 AI 분석 품질 (선택)**  
   - OPENAI_API_KEY 또는 GEMINI_API_KEY 설정 후 동일 요청.  
   - Executive Summary가 문장 단위 스토리인지, Key Findings에 근거·해석·시사점이 드러나는지 확인.

---

## 완료 상태

- [x] 마케팅 컨설턴트 메타 프롬프트 설계 및 적용  
- [x] 분석 유형별(keyword/audience/comprehensive) 리포트 출력 지침 적용  
- [x] 역할별 품질 체크리스트 문서화  
- [x] 메타 프롬프트 통합 단위 테스트 추가 및 통과  
- [ ] 필요 시 E2E/수동 테스트로 실제 AI 출력 품질 최종 확인
