# Vercel 배포 가이드 - News Trend Analyzer

## 📋 프로젝트 구조

이 프로젝트는 Python FastAPI 백엔드와 React/TypeScript 프론트엔드로 구성되어 있습니다.

```
news-trend-analyzer/
├── api/
│   └── index.py          # Vercel Serverless Function 진입점
├── backend/
│   ├── main.py           # FastAPI 앱
│   ├── config.py         # 설정 관리
│   ├── api/              # API 라우트
│   ├── services/         # 비즈니스 로직
│   └── middleware/       # 미들웨어
├── frontend/             # React 프론트엔드 (정적 파일)
├── vercel.json           # Vercel 설정
├── requirements.txt      # Python 의존성
└── .vercelignore         # 배포 제외 파일
```

## ⚠️ 중요: Vercel 제한사항

### 1. 파일 시스템 제한
- Vercel Serverless Functions는 **읽기 전용** 파일 시스템을 사용합니다
- `data/` 폴더에 파일을 쓰는 작업은 **작동하지 않습니다**
- 로그 파일 쓰기도 제한될 수 있습니다

**해결 방법:**
- 파일 저장이 필요한 경우: Vercel Blob, AWS S3, 또는 다른 클라우드 스토리지 사용
- 로그는 Vercel의 로그 시스템 사용 (파일 로깅 비활성화)

### 2. 디렉토리 생성 제한
- `backend/config.py`에서 디렉토리를 생성하려고 시도하지만, Vercel에서는 실패할 수 있습니다
- 디렉토리 생성 코드는 try-except로 감싸져 있어 에러가 발생해도 계속 진행됩니다

### 3. 캐시 저장소
- 현재 메모리 기반 캐시를 사용하므로, 서버리스 환경에서도 작동합니다
- 다만 각 함수 인스턴스마다 별도의 캐시를 가지므로, 분산 캐시(Redis 등)를 고려하세요

## 🚀 배포 방법

### 방법 1: Vercel CLI 사용

```bash
# Vercel CLI 설치
npm i -g vercel

# 프로젝트 디렉토리로 이동
cd news-trend-analyzer

# 배포
vercel

# 프로덕션 배포
vercel --prod
```

### 방법 2: GitHub 연동

1. GitHub에 프로젝트 푸시
2. [Vercel Dashboard](https://vercel.com/dashboard) 접속
3. "Add New Project" 클릭
4. GitHub 저장소 선택
5. 프로젝트 설정:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (기본값)
   - **Build Command**: (비워두기)
   - **Output Directory**: (비워두기)
   - **Install Command**: `pip install -r requirements.txt`

## 🔧 환경 변수 설정

Vercel Dashboard → Project Settings → Environment Variables에서 다음 변수를 설정하세요:

### 필수 환경 변수
```
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key
```

### 선택적 환경 변수
```
DEBUG=False
LOG_LEVEL=INFO
CACHE_ENABLED=True
CACHE_TTL=3600
OPENAI_MODEL=gpt-4o-mini
GEMINI_MODEL=gemini-2.0-flash
NEWS_API_KEY=your-news-api-key
NAVER_CLIENT_ID=your-naver-client-id
NAVER_CLIENT_SECRET=your-naver-secret
```

## 📝 현재 설정

### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/index.py"
    },
    {
      "src": "/health",
      "dest": "api/index.py"
    },
    {
      "src": "/docs",
      "dest": "api/index.py"
    },
    {
      "src": "/",
      "dest": "api/index.py"
    }
  ],
  "functions": {
    "api/index.py": {
      "maxDuration": 30,
      "memory": 1024
    }
  }
}
```

### api/index.py
- Mangum을 사용하여 FastAPI 앱을 AWS Lambda 핸들러로 변환
- 프로젝트 루트를 Python 경로에 추가하여 모듈 import 가능

## ✅ 배포 후 확인 사항

배포가 완료되면 다음을 확인하세요:

1. **헬스 체크**
   ```bash
   curl https://your-project.vercel.app/health
   ```

2. **API 문서**
   - 브라우저에서 `https://your-project.vercel.app/docs` 접속
   - Swagger UI가 표시되어야 합니다

3. **API 엔드포인트 테스트**
   ```bash
   # 타겟 분석 API 테스트
   curl -X POST https://your-project.vercel.app/api/target/analyze \
     -H "Content-Type: application/json" \
     -d '{"target_keyword": "인공지능", "target_type": "keyword"}'
   ```

4. **캐시 통계 확인**
   ```bash
   curl https://your-project.vercel.app/api/cache/stats
   ```

## 🐛 문제 해결

### 빌드 실패: 의존성 설치 오류

```bash
# 로컬에서 테스트
pip install -r requirements.txt
```

### 런타임 오류: 모듈을 찾을 수 없음

- `api/index.py`에서 `sys.path`에 프로젝트 루트가 추가되어 있는지 확인
- 모든 import 경로가 올바른지 확인

### 파일 시스템 접근 오류

- 파일 쓰기 작업을 제거하거나 외부 스토리지로 변경
- 로그 파일 대신 Vercel 로그 사용

### 캐시가 작동하지 않음

- 서버리스 환경에서는 각 함수 인스턴스마다 별도의 메모리를 가집니다
- 분산 캐시(Redis, Vercel KV) 사용을 고려하세요

## 🔄 Vercel 배포 전 수정 권장 사항

### 1. 파일 쓰기 제거

`backend/config.py`에서 디렉토리 생성 코드를 Vercel 환경에서는 건너뛰도록 수정:

```python
# Vercel 환경 확인
import os
IS_VERCEL = os.environ.get("VERCEL") == "1"

if not IS_VERCEL:
    # 디렉토리 생성 코드
    for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, CACHE_DIR, ASSETS_DIR, LOGS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
```

### 2. 로그 파일 비활성화

Vercel 환경에서는 파일 로깅을 비활성화:

```python
# backend/main.py
if not os.environ.get("VERCEL"):
    # 파일 로깅 활성화
    handlers.append(logging.FileHandler(settings.LOG_FILE))
```

### 3. 정적 파일 서빙

프론트엔드가 React 앱인 경우, 빌드된 정적 파일을 서빙해야 합니다:
- Vite/Webpack으로 빌드 후 `dist/` 또는 `build/` 폴더를 서빙
- 또는 프론트엔드를 별도로 배포 (Vercel, Netlify 등)

## 📚 추가 리소스

- [Vercel Python 문서](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [FastAPI 배포 가이드](https://fastapi.tiangolo.com/deployment/)
- [Mangum 문서](https://mangum.io/)

## 🎯 대안 배포 플랫폼

Vercel의 제한사항이 문제가 되는 경우 다음 플랫폼을 고려하세요:

1. **Railway** - Python 애플리케이션에 최적화
2. **Render** - 무료 티어 제공, 파일 시스템 지원
3. **Fly.io** - 글로벌 배포, 파일 시스템 지원
4. **Heroku** - 전통적인 PaaS, 파일 시스템 지원
