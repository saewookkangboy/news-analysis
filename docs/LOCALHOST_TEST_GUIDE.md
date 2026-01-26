# Localhost 테스트 가이드

## 진단 및 수정 사항

### 발견된 문제점

1. **프론트엔드 정적 파일 마운트 순서 문제**
   - 문제: 프론트엔드 정적 파일을 루트(`/`)에 마운트하여 `/`와 `/health` API 엔드포인트가 가려짐
   - 원인: FastAPI에서 정적 파일 마운트가 라우터보다 우선순위가 높음
   - 해결: API 엔드포인트를 정적 파일 마운트 전에 등록하고, 프론트엔드를 `/app` 경로로 마운트

2. **루트 엔드포인트 접근 불가**
   - 문제: `/` 엔드포인트가 404 반환
   - 해결: API 엔드포인트를 정적 파일 마운트 전에 등록

3. **헬스 체크 엔드포인트 접근 불가**
   - 문제: `/health` 엔드포인트가 404 반환
   - 해결: API 엔드포인트를 정적 파일 마운트 전에 등록

### 수정 내용

#### `backend/main.py` 수정 사항

1. **엔드포인트 등록 순서 변경**
   - API 라우터 등록
   - `/` 및 `/health` 엔드포인트 등록
   - 정적 파일 마운트 (마지막에)

2. **프론트엔드 마운트 경로 변경**
   - 루트(`/`) → `/app` 경로로 변경
   - 빌드된 파일이 있는 경우에만 마운트

3. **루트 엔드포인트 개선**
   - API 정보와 주요 엔드포인트 링크 제공

## 테스트 결과

### ✅ 정상 작동하는 엔드포인트

1. **헬스 체크**
   ```bash
   curl http://localhost:8000/health
   ```
   응답:
   ```json
   {
       "status": "healthy",
       "service": "news-trend-analyzer"
   }
   ```

2. **루트 엔드포인트**
   ```bash
   curl http://localhost:8000/
   ```
   응답:
   ```json
   {
       "message": "뉴스 트렌드 분석 서비스 API",
       "version": "1.0.0",
       "docs": "/docs",
       "health": "/health",
       "api": "/api"
   }
   ```

3. **API 문서**
   ```bash
   # 브라우저에서 접근
   http://localhost:8000/docs
   ```

4. **타겟 분석 API (POST)**
   ```bash
   curl -X POST http://localhost:8000/api/target/analyze \
     -H "Content-Type: application/json" \
     -d '{"target_keyword":"AI","target_type":"keyword"}'
   ```

5. **타겟 분석 API (GET)**
   ```bash
   curl "http://localhost:8000/api/target/analyze?target_keyword=인공지능&target_type=keyword"
   ```

6. **캐시 통계**
   ```bash
   curl http://localhost:8000/api/cache/stats
   ```

## 서비스 실행 방법

### 방법 1: 실행 스크립트 사용 (권장)
```bash
cd /Users/chunghyo/news-trend-analyzer
./run.sh
```

### 방법 2: Python 직접 실행
```bash
cd /Users/chunghyo/news-trend-analyzer
python run.py
```

### 방법 3: Uvicorn 직접 실행
```bash
cd /Users/chunghyo/news-trend-analyzer
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## 포트 충돌 해결

포트 8000이 이미 사용 중인 경우:

```bash
# 기존 프로세스 종료
lsof -ti:8000 | xargs kill -9

# 또는 다른 포트 사용
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001
```

## 주요 엔드포인트 목록

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/` | GET | API 정보 및 주요 엔드포인트 링크 |
| `/health` | GET | 헬스 체크 |
| `/docs` | GET | Swagger UI API 문서 |
| `/openapi.json` | GET | OpenAPI 스펙 |
| `/api/target/analyze` | GET/POST | 타겟 분석 |
| `/api/cache/stats` | GET | 캐시 통계 |

## 프론트엔드 접근

프론트엔드가 빌드된 경우:
- 프론트엔드: `http://localhost:8000/app`
- 루트에서 자동 리다이렉트 (향후 구현 가능)

프론트엔드가 빌드되지 않은 경우:
- 루트(`/`)에서 API 정보 제공
- 프론트엔드 빌드 후 `/app` 경로에서 접근 가능

## 테스트 체크리스트

- [x] 서버 정상 시작
- [x] `/health` 엔드포인트 정상 작동
- [x] `/` 엔드포인트 정상 작동
- [x] `/docs` API 문서 정상 표시
- [x] POST `/api/target/analyze` 정상 작동
- [x] GET `/api/target/analyze` 정상 작동
- [x] `/api/cache/stats` 정상 작동
- [x] 에러 처리 정상 작동

## 추가 개선 사항

1. **프론트엔드 빌드 자동화**
   - 프론트엔드 빌드 스크립트 추가
   - 빌드 후 자동 서빙

2. **환경별 설정**
   - 개발/프로덕션 환경 분리
   - 환경 변수 관리 개선

3. **로깅 개선**
   - 요청/응답 로깅
   - 에러 추적 개선
