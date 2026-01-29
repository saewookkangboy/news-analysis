# Backend 비동기 처리 최적화 및 동시성 개선

**날짜**: 2026-01-28  
**역할**: Backend Developer  
**상태**: 완료

## 개요

API 라우트에서 순차 실행되던 분석 호출을 `asyncio.gather`로 병렬화하여 응답 시간을 단축했습니다.

## 변경 사항

### 1. `backend/api/routes.py`

- **import**: `asyncio` 추가
- **analyze_target_endpoint** (POST `/target/analyze`)
  - 정성적 분석: `analyze_sentiment`, `analyze_context`, `analyze_tone`를 **병렬 실행** (`asyncio.gather`)
  - 기존: 감정 → 맥락 → 톤 순차 호출 → **변경**: 3개 동시 호출
- **comprehensive_analysis_endpoint** (POST `/analysis/comprehensive`)
  - 정성적 분석 3종 동일하게 **병렬 실행**
- **compare_keywords_endpoint** (POST `/analysis/compare`)
  - 키워드별 분석을 **병렬 실행**: `analyze_one_keyword(keyword)` 태스크를 `asyncio.gather(*[analyze_one_keyword(kw) for kw in keywords])`로 실행
  - 기존: for 루프로 키워드 하나씩 순차 처리 → **변경**: 키워드 수만큼 동시 처리
- **progress_tracker**: 예외 경로에서 미바인딩 방지를 위해 `progress_tracker = None`을 try 블록 진입 전에 초기화

## 기대 효과

| 구간 | 기존 (순차) | 변경 (병렬) |
|------|-------------|-------------|
| 정성적 분석 3종 | T1 + T2 + T3 | max(T1, T2, T3) |
| 키워드 비교 N개 | N × (분석 시간) | ≈ 1 × (분석 시간) |

- 타겟 분석(정성 포함) 및 종합 분석: 정성적 분석 구간 응답 시간 단축
- 키워드 비교: 키워드 수가 많을수록 체감 시간 단축

## 영향 범위

- 수정 파일: `backend/api/routes.py` only
- 기존 API 스펙·응답 형식 변경 없음
- 서비스 레이어(`analyze_sentiment`, `analyze_context`, `analyze_tone`, `analyze_target`, `recommend_keywords`) 시그니처 변경 없음
