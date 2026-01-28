# Railway 배포 가이드

이 문서는 뉴스 트렌드 분석 서비스를 Railway에 배포하는 방법을 설명합니다.

## 사전 준비

1. [Railway 계정](https://railway.app) 생성
2. GitHub 저장소 준비 (또는 Railway CLI 사용)

## 배포 방법

### 방법 1: Railway 웹 대시보드 사용 (권장)

1. **프로젝트 생성**
   - Railway 대시보드에서 "New Project" 클릭
   - "Deploy from GitHub repo" 선택
   - 저장소 선택 및 연결

2. **환경 변수 설정**
   - 프로젝트 설정 → Variables 탭
   - 다음 환경 변수 추가:

```env
# 필수: AI API 키 (최소 하나는 필요)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# 선택사항: Gemini API
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash

# 서버 설정 (Railway가 자동으로 설정)
PORT=8000
HOST=0.0.0.0

# 선택사항: 로깅
LOG_LEVEL=INFO
DEBUG=False
```

3. **배포 확인**
   - Railway가 자동으로 빌드 및 배포를 시작합니다
   - Deployments 탭에서 배포 상태 확인
   - 배포 완료 후 제공되는 URL로 접속 테스트

### 방법 2: Railway CLI 사용

```bash
# Railway CLI 설치
npm i -g @railway/cli

# 로그인
railway login

# 프로젝트 초기화
railway init

# 환경 변수 설정
railway variables set OPENAI_API_KEY=your_key_here
railway variables set GEMINI_API_KEY=your_key_here

# 배포
railway up
```

## 설정 파일 설명

### Procfile
Railway가 애플리케이션을 시작하는 명령어를 정의합니다:
```
web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### runtime.txt
Python 버전을 명시합니다:
```
python-3.11.9
```

### railway.json
Railway 배포 설정을 정의합니다:
- `startCommand`: 애플리케이션 시작 명령어
- `restartPolicyType`: 재시작 정책
- `restartPolicyMaxRetries`: 최대 재시작 횟수

## 환경 변수 필수 목록

### 필수 변수
- `OPENAI_API_KEY` 또는 `GEMINI_API_KEY` (최소 하나는 필수)

### 선택 변수
- `OPENAI_MODEL`: OpenAI 모델 (기본값: `gpt-4o-mini`)
- `GEMINI_API_KEY`: Gemini API 키
- `GEMINI_MODEL`: Gemini 모델 (기본값: `gemini-2.0-flash`)
- `LOG_LEVEL`: 로그 레벨 (기본값: `INFO`)
- `DEBUG`: 디버그 모드 (기본값: `False`)

## 배포 후 확인 사항

1. **헬스 체크**
   ```bash
   curl https://your-app.railway.app/
   ```

2. **API 문서 확인**
   - Swagger UI: `https://your-app.railway.app/docs`
   - ReDoc: `https://your-app.railway.app/redoc`

3. **API 테스트**
   ```bash
   curl -X POST https://your-app.railway.app/api/target/analyze \
     -H "Content-Type: application/json" \
     -d '{
       "target_keyword": "인공지능",
       "target_type": "keyword",
       "start_date": "2025-01-01",
       "end_date": "2025-01-28"
     }'
   ```

## 트러블슈팅

### "No start command was found" 오류

이 오류는 Railway가 시작 명령어를 찾지 못했을 때 발생합니다. 해결 방법:

1. **Procfile 확인**
   - 프로젝트 루트에 `Procfile`이 있는지 확인
   - 내용이 올바른지 확인: `web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

2. **railway.json 확인**
   - `startCommand`가 올바르게 설정되어 있는지 확인

3. **재배포**
   - 설정 파일 수정 후 Railway에서 재배포

### 포트 바인딩 오류

Railway는 `$PORT` 환경 변수를 제공합니다. 코드에서 이 포트를 사용하도록 설정되어 있는지 확인:

- `Procfile`에서 `--port $PORT` 사용
- `backend/config.py`에서 `PORT` 환경 변수 읽기

### 의존성 설치 실패

`requirements.txt`에 모든 필수 패키지가 포함되어 있는지 확인:

```bash
pip install -r requirements.txt
```

### 환경 변수 누락

Railway 대시보드에서 모든 필수 환경 변수가 설정되어 있는지 확인:

1. 프로젝트 → Settings → Variables
2. 필수 변수 목록 확인
3. 누락된 변수 추가

## 모니터링

Railway 대시보드에서 다음을 모니터링할 수 있습니다:

- **Deployments**: 배포 이력 및 상태
- **Metrics**: CPU, 메모리 사용량
- **Logs**: 실시간 로그 확인
- **Variables**: 환경 변수 관리

## 비용 최적화

1. **자동 슬립 모드**: 사용하지 않을 때 자동으로 슬립
2. **리소스 제한**: 필요한 만큼만 리소스 할당
3. **캐싱 활용**: 분석 결과 캐싱으로 API 호출 감소

## 추가 리소스

- [Railway 공식 문서](https://docs.railway.app)
- [Railway Discord 커뮤니티](https://discord.gg/railway)
- [FastAPI 배포 가이드](https://fastapi.tiangolo.com/deployment/)
