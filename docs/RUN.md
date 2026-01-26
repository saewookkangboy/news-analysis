# 실행 방법

## 로컬 개발 환경에서 실행

### 방법 1: 실행 스크립트 사용 (권장)

```bash
cd /Users/chunghyo/news-trend-analyzer
./run.sh
```

스크립트가 포트 충돌을 자동으로 감지하고 처리합니다.

### 방법 2: 프로젝트 루트에서 실행

```bash
cd /Users/chunghyo/news-trend-analyzer
python run.py
```

또는

```bash
cd /Users/chunghyo/news-trend-analyzer
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 포트 충돌 해결

포트 8000이 이미 사용 중인 경우:

1. **기존 프로세스 종료:**
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```

2. **다른 포트 사용:**
   ```bash
   python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001
   ```

### 방법 2: backend 디렉토리에서 실행

```bash
cd /Users/chunghyo/news-trend-analyzer/backend
python main.py
```

(이 방법은 `main.py`에서 자동으로 프로젝트 루트를 경로에 추가합니다)

## 환경 변수 설정

`.env` 파일을 프로젝트 루트에 생성하고 다음 내용을 추가하세요:

```env
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

## API 테스트

서버 실행 후 다음 엔드포인트를 사용할 수 있습니다:

- 타겟 분석 (POST): `http://localhost:8000/api/target/analyze`
- 타겟 분석 (GET): `http://localhost:8000/api/target/analyze?target_keyword=인공지능&target_type=keyword`
- API 문서: `http://localhost:8000/docs`
