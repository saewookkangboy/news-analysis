# 메인 API 스펙

## 개요
news-trend-analyzer의 주요 API 엔드포인트 스펙입니다.

## 엔드포인트 목록

### 1. 타겟 분석
#### POST /api/target/analyze
타겟 키워드, 오디언스, 경쟁자 분석을 수행합니다.

**Request Body:**
```json
{
  "target_keyword": "string (required)",
  "target_type": "keyword|audience|competitor (required)",
  "additional_context": "string (optional)",
  "use_gemini": "boolean (optional, default: false)",
  "start_date": "string (optional, YYYY-MM-DD)",
  "end_date": "string (optional, YYYY-MM-DD)"
}
```

**Response:**
```json
{
  "executive_summary": "string",
  "key_findings": {
    "primary_insights": ["string"],
    "quantitative_metrics": {}
  },
  "detailed_analysis": {},
  "strategic_recommendations": {
    "immediate_actions": ["string"],
    "short_term_strategies": ["string"],
    "long_term_strategies": ["string"],
    "success_metrics": "string"
  }
}
```

#### GET /api/target/analyze
쿼리 파라미터를 통한 타겟 분석 (POST와 동일한 기능)

**Query Parameters:**
- `target_keyword` (required)
- `target_type` (required)
- `additional_context` (optional)
- `use_gemini` (optional)
- `start_date` (optional)
- `end_date` (optional)

### 2. 헬스 체크
#### GET /health
서비스 상태를 확인합니다.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-28T00:00:00Z"
}
```

### 3. 캐시 통계
#### GET /api/cache/stats
캐시 통계 정보를 조회합니다.

**Response:**
```json
{
  "cache_enabled": true,
  "cache_hits": 100,
  "cache_misses": 50,
  "hit_rate": 0.67
}
```

### 4. API 문서
#### GET /docs
Swagger UI 인터랙티브 API 문서

#### GET /openapi.json
OpenAPI 스펙 JSON

## 에러 응답

모든 에러는 다음 형식을 따릅니다:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "에러 메시지",
    "details": {}
  }
}
```

### 에러 코드
- `VALIDATION_ERROR`: 요청 데이터 검증 실패
- `API_KEY_ERROR`: API 키 오류
- `MODEL_ERROR`: AI 모델 호출 실패
- `INTERNAL_ERROR`: 내부 서버 오류

## 인증

현재는 API 키 기반 인증을 사용합니다:
- OpenAI API 키: 환경 변수 `OPENAI_API_KEY`
- Gemini API 키: 환경 변수 `GEMINI_API_KEY`

## 레이트 리미팅

현재 레이트 리미팅은 구현되지 않았습니다. 향후 추가 예정입니다.

## 버전 관리

API 버전 관리는 URL 경로에 포함되지 않습니다. 
주요 변경사항은 `.spec-kit/changelog/`에 기록됩니다.

## 변경 이력
- 2026-01-28: 초기 API 스펙 작성
