# Vercel 500 Internal Server Error 해결 가이드

## 문제 증상
```
500: INTERNAL_SERVER_ERROR
Code: FUNCTION_INVOCATION_FAILED
ID: icn1::h45mh-1769445235691-3e374d034c5e
```

## 주요 수정 사항

### 1. api/index.py 개선
- ✅ Vercel 환경 변수 명시적 설정
- ✅ 에러 핸들링 추가
- ✅ handler 명시적 export
- ✅ 로깅 추가

**주요 변경점:**
```python
# Vercel 환경 설정
os.environ.setdefault("VERCEL", "1")

# 에러 발생 시 fallback handler 제공
try:
    from backend.main import app
except Exception as e:
    # 에러 발생 시에도 기본 handler 제공
    error_app = FastAPI()
    @error_app.get("/")
    async def error_root():
        return {"error": "Application failed to start", "message": str(e)}
    handler = error_app

# 명시적 export
__all__ = ["handler", "app"]
```

### 2. 디버깅 체크리스트

#### A. Vercel 로그 확인
1. Vercel Dashboard → 프로젝트 → Functions 탭
2. 에러 로그 확인
3. 다음 항목들을 확인:
   - ImportError
   - NameError
   - ModuleNotFoundError
   - 환경 변수 관련 에러

#### B. 환경 변수 확인
Vercel Dashboard → Settings → Environment Variables에서 확인:
- ✅ `OPENAI_API_KEY` 설정됨
- ✅ `GEMINI_API_KEY` 설정됨 (선택사항)
- ✅ `VERCEL=1` (자동 설정됨)

#### C. 의존성 확인
`requirements.txt`에 다음이 포함되어 있는지 확인:
- ✅ `fastapi`
- ✅ `uvicorn`
- ✅ `mangum` (선택사항, 없어도 작동)
- ✅ `openai`
- ✅ `google-generativeai` (선택사항)
- ✅ `pydantic`
- ✅ `pydantic-settings`

### 3. 일반적인 원인 및 해결 방법

#### 원인 1: Import 오류
**증상:** `ModuleNotFoundError` 또는 `ImportError`

**해결:**
- `requirements.txt`에 누락된 패키지 추가
- `api/index.py`에서 경로 설정 확인

#### 원인 2: 환경 변수 미설정
**증상:** API 키 관련 에러

**해결:**
- Vercel Dashboard에서 환경 변수 설정
- 재배포 필수

#### 원인 3: 파일 시스템 접근
**증상:** `PermissionError` 또는 `FileNotFoundError`

**해결:**
- Vercel 환경에서는 파일 쓰기 불가
- `backend/config.py`에서 Vercel 환경 감지 후 파일 시스템 작업 건너뛰기

#### 원인 4: Startup 이벤트 오류
**증상:** 앱 시작 시 크래시

**해결:**
- `backend/main.py`의 startup 이벤트에서 에러 핸들링 추가
- 파일 시스템 접근 제거

### 4. 테스트 방법

#### 로컬에서 Vercel 환경 시뮬레이션
```bash
# 환경 변수 설정
export VERCEL=1
export OPENAI_API_KEY=your_key_here
export GEMINI_API_KEY=your_key_here

# 앱 import 테스트
python3 -c "from api.index import handler; print('Success')"
```

#### Vercel 배포 후 확인
1. **헬스 체크**: `https://newa.allrounder.im/health`
2. **API 문서**: `https://newa.allrounder.im/docs`
3. **루트 엔드포인트**: `https://newa.allrounder.im/`

### 5. 추가 디버깅

#### Vercel 로그에서 확인할 항목
```bash
# Vercel CLI로 로그 확인
vercel logs newa.allrounder.im --follow
```

#### 에러 메시지 패턴
- `NameError: name 'os' is not defined` → import 누락
- `ModuleNotFoundError: No module named 'X'` → requirements.txt 확인
- `KeyError: 'OPENAI_API_KEY'` → 환경 변수 미설정
- `PermissionError` → 파일 시스템 접근 문제

### 6. 다음 단계

1. ✅ `api/index.py` 수정 완료
2. ⏳ 변경사항 커밋 및 푸시
3. ⏳ Vercel 재배포
4. ⏳ 배포 로그 확인
5. ⏳ 사이트 접속 테스트

### 7. 참고 문서
- [Vercel Serverless Functions 문서](https://vercel.com/docs/functions/serverless-functions)
- [FastAPI 배포 가이드](https://fastapi.tiangolo.com/deployment/)
- [Mangum 문서](https://mangum.io/)
