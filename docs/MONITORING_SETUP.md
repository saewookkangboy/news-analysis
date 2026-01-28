# 성능 모니터링 설정 가이드

## 개요

이 프로젝트는 기본적인 성능 모니터링 기능을 포함하고 있습니다. 프로덕션 환경에서는 외부 모니터링 도구 연동을 권장합니다.

## 현재 구현

### 기본 메트릭 수집
- API 호출 수 추적
- 응답 시간 측정
- 에러율 계산
- 최근 에러 목록

### 메트릭 API 엔드포인트
- `GET /api/metrics/summary`: 메트릭 요약 조회
- `POST /api/metrics/reset`: 메트릭 초기화 (개발용)

## 사용 방법

### 메트릭 조회
```bash
curl http://localhost:8000/api/metrics/summary
```

### 응답 예시
```json
{
  "success": true,
  "data": {
    "total_calls": 150,
    "total_errors": 3,
    "error_rate": 2.0,
    "avg_response_time": 1.234,
    "min_response_time": 0.123,
    "max_response_time": 5.678,
    "recent_errors": [...]
  }
}
```

## 프로덕션 모니터링 도구 연동

### 권장 도구

#### 1. Sentry (에러 추적)
```python
# requirements.txt에 추가
sentry-sdk[fastapi]==1.38.0

# backend/main.py에 추가
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

#### 2. DataDog (APM)
```python
# requirements.txt에 추가
ddtrace==2.0.0

# 실행 시
ddtrace-run uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

#### 3. Prometheus + Grafana
```python
# requirements.txt에 추가
prometheus-fastapi-instrumentator==6.1.0

# backend/main.py에 추가
from prometheus_fastapi_instrumentator import Instrumentator

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)
```

#### 4. Redis (메트릭 저장소)
```python
# requirements.txt에 추가
redis==5.0.1

# backend/utils/monitoring.py 수정
# 메모리 저장소 대신 Redis 사용
```

## 모니터링 지표

### 필수 지표
- API 응답 시간 (P50, P95, P99)
- 에러율 (4xx, 5xx)
- 요청 처리량 (RPS)
- API 키 사용량

### 선택 지표
- 캐시 히트율
- 데이터베이스 쿼리 시간
- 외부 API 호출 시간
- 메모리 사용량

## 알림 설정

### 권장 알림 조건
- 에러율 > 5%
- 평균 응답 시간 > 3초
- P95 응답 시간 > 5초
- 연속 에러 발생 (5분 내 10건 이상)

## 대시보드 구성

### 권장 대시보드 항목
1. **API 성능**
   - 응답 시간 트렌드
   - 요청 처리량
   - 에러율

2. **리소스 사용량**
   - CPU 사용률
   - 메모리 사용률
   - 네트워크 트래픽

3. **비즈니스 메트릭**
   - 일일 활성 사용자
   - 분석 요청 수
   - API 키 사용량

## 다음 단계

1. [ ] Sentry 연동 (에러 추적)
2. [ ] Prometheus 메트릭 수집
3. [ ] Grafana 대시보드 구성
4. [ ] 알림 규칙 설정
5. [ ] 로그 집계 시스템 연동 (예: ELK Stack)

---

**작성일**: 2026-01-28  
**버전**: 1.0.0
