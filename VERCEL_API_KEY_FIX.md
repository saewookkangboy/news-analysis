# Vercel 배포 환경 API 키 반영 수정 사항

## 문제점
Vercel 배포 환경에서 `OPENAI_API_KEY`와 `GEMINI_API_KEY`가 정상적으로 반영되지 않는 문제가 있었습니다.

## 원인 분석
1. `pydantic-settings`의 `BaseSettings`가 Vercel 환경에서 환경 변수를 제대로 읽지 못할 수 있음
2. Settings 클래스가 모듈 로딩 시점에 인스턴스화되는데, 이때 환경 변수가 아직 설정되지 않았을 수 있음
3. Vercel에서는 환경 변수가 `os.environ`에 직접 설정되므로, `os.getenv()`를 사용하는 것이 더 안전함

## 해결 방법

### 1. backend/config.py 수정
- Settings 클래스의 `__init__` 메서드에서 환경 변수를 직접 읽도록 수정
- Vercel 환경에서 환경 변수를 다시 확인하고 업데이트하는 로직 추가
- 상세한 로깅 추가 (환경 변수와 Settings 값 비교)

### 2. 모든 서비스 파일 수정
다음 파일들에서 API 키를 사용할 때 환경 변수를 직접 확인하도록 수정:
- `backend/services/target_analyzer.py`
- `backend/services/sentiment_analyzer.py`
- `backend/services/keyword_recommender.py`

**수정 패턴:**
```python
# 이전
if settings.OPENAI_API_KEY:
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# 수정 후
import os
api_key = settings.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY')
if api_key:
    client = AsyncOpenAI(api_key=api_key)
```

## 수정된 파일 목록

### 1. backend/config.py
- Settings 클래스에 `__init__` 메서드 추가
- Vercel 환경에서 환경 변수 재확인 로직 추가
- 상세한 로깅 추가

### 2. backend/services/target_analyzer.py
- `analyze_target()` 함수에서 API 키 확인 로직 수정
- `_analyze_with_openai()` 함수에서 API 키 직접 읽기
- `_analyze_with_gemini()` 함수에서 API 키 직접 읽기
- `_analyze_basic()` 함수에서 API 키 상태 확인 로직 수정

### 3. backend/services/sentiment_analyzer.py
- `analyze_sentiment()` 함수에서 API 키 확인 로직 수정
- `analyze_context()` 함수에서 API 키 확인 로직 수정
- `analyze_tone()` 함수에서 API 키 확인 로직 수정
- 모든 OpenAI API 호출에서 API 키 직접 읽기

### 4. backend/services/keyword_recommender.py
- `recommend_keywords()` 함수에서 API 키 확인 로직 수정
- OpenAI API 호출에서 API 키 직접 읽기

## 검증 방법

### 로컬 검증
```bash
python3 scripts/verify_api_keys.py
```

### Vercel 배포 후 검증
1. **배포 로그 확인**
   - Vercel Dashboard > Deployments > 최신 배포 > Logs
   - 다음 메시지 확인:
     ```
     ============================================================
     환경 변수 로딩 상태 확인
     환경: Vercel (배포)
     os.getenv('OPENAI_API_KEY'): ✅ 설정됨
     os.getenv('GEMINI_API_KEY'): ✅ 설정됨
     settings.OPENAI_API_KEY: ✅ 설정됨
     settings.GEMINI_API_KEY: ✅ 설정됨
     ============================================================
     ```

2. **API 테스트**
   ```bash
   curl -X POST https://your-project.vercel.app/api/target/analyze \
     -H "Content-Type: application/json" \
     -d '{
       "target_keyword": "테스트",
       "target_type": "keyword",
       "use_gemini": true
     }'
   ```
   
   응답에서 `api_key_status` 확인:
   ```json
   {
     "api_key_status": {
       "openai_configured": true,
       "gemini_configured": true,
       "message": "✅ 모든 API 키가 설정되어 있습니다."
     }
   }
   ```

## 중요 사항

### Vercel 환경 변수 설정
1. Vercel Dashboard > Project Settings > Environment Variables
2. 다음 변수 설정:
   - `OPENAI_API_KEY` (Production, Preview, Development)
   - `GEMINI_API_KEY` (Production, Preview, Development)
3. **환경 변수 추가/수정 후 반드시 재배포**

### 환경 변수 우선순위
1. `os.getenv()` - 환경 변수 직접 읽기 (최우선)
2. `settings.OPENAI_API_KEY` - Settings 인스턴스 값
3. `.env` 파일 (로컬 개발 환경에서만)

## 테스트 결과

로컬 환경에서 환경 변수 직접 읽기 테스트:
```bash
$ python3 -c "import os; os.environ['OPENAI_API_KEY'] = 'test-key-123'; from backend.config import settings; print(settings.OPENAI_API_KEY)"
test-key-123
```

✅ 환경 변수가 Settings에 정상적으로 반영됨을 확인

## 다음 단계

1. **Vercel Dashboard에서 환경 변수 확인**
   - `OPENAI_API_KEY`, `GEMINI_API_KEY` 설정 여부 확인
   - `.env` 파일의 값과 일치하는지 확인

2. **재배포**
   - 환경 변수 설정/수정 후 재배포

3. **검증**
   - 배포 로그에서 환경 변수 로딩 메시지 확인
   - API 테스트로 실제 동작 확인
