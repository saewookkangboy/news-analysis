# 타겟 분석 기능 스펙

## 개요
AI 기반 키워드, 오디언스, 경쟁자 분석 기능입니다. OpenAI GPT-4o-mini 또는 Google Gemini 2.0 Flash 모델을 사용하여 마케팅 및 비즈니스 인사이트를 제공합니다.

## 요구사항

### 기능 요구사항
1. **키워드 분석**
   - 검색 트렌드 분석
   - 검색량 추정
   - 경쟁도 분석
   - 관련 키워드 추천

2. **오디언스 분석**
   - 인구통계학적 특성 분석
   - 심리적 특성 분석
   - 행동 패턴 분석
   - 마케팅 전략 제안

3. **경쟁자 분석**
   - 주요 경쟁자 식별
   - 경쟁 우위 분석
   - 차별화 포인트 도출
   - 시장 점유율 추정

### 비기능 요구사항
- 응답 시간: 평균 5초 이내
- 캐싱: 동일 키워드 재요청 시 캐시 활용
- 에러 핸들링: API 실패 시 적절한 에러 메시지
- 확장성: 다양한 AI 모델 지원

## 설계

### 아키텍처
```
Frontend (React)
    ↓
API Layer (FastAPI)
    ↓
Service Layer (target_analyzer.py)
    ↓
AI Model (OpenAI / Gemini)
```

### 데이터 흐름
1. 사용자 입력 (키워드, 분석 유형)
2. API 요청 처리
3. 캐시 확인
4. AI 모델 호출
5. 결과 파싱 및 반환
6. 캐시 저장

### API 엔드포인트
- `POST /api/target/analyze`
- `GET /api/target/analyze` (쿼리 파라미터)

## 구현

### 주요 컴포넌트
- `backend/services/target_analyzer.py`: 분석 로직
- `backend/api/routes.py`: API 라우팅
- `backend/middleware/cache_middleware.py`: 캐싱

### AI 모델 통합
- OpenAI API: `gpt-4o-mini`
- Gemini API: `gemini-2.0-flash`

### 응답 형식
MECE 원칙에 따른 구조화된 JSON 응답:
```json
{
  "executive_summary": "...",
  "key_findings": {...},
  "detailed_analysis": {...},
  "strategic_recommendations": {...}
}
```

## 테스트

### 단위 테스트
- 키워드 분석 로직
- 오디언스 분석 로직
- 경쟁자 분석 로직
- 캐싱 동작

### 통합 테스트
- API 엔드포인트
- AI 모델 통합
- 에러 핸들링

### 성능 테스트
- 응답 시간 측정
- 캐시 효과 검증
- 동시 요청 처리

## 변경 이력
- 2026-01-28: 초기 스펙 작성
- 2026-01-26: MECE 구조 적용
