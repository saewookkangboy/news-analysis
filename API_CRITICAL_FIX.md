# API 호출 크리티컬 버그 수정

## 발견된 문제점

로그 분석 결과 다음 문제들이 발견되었습니다:

### 1. OpenAI API 오류
```
OpenAI API 호출 실패: AsyncClient.__init__() got an unexpected keyword argument 'proxies'
```
- **원인**: OpenAI 라이브러리 버전 문제 (1.3.0에서 `proxies` 인자 미지원)
- **해결**: `openai>=1.12.0`으로 업데이트

### 2. Gemini 모델 이름 오류
```
404 NOT_FOUND. models/gemini-2.5-flash-preview is not found
```
- **원인**: 존재하지 않는 모델 이름 사용
- **해결**: `gemini-1.5-flash`로 변경 (안정적인 모델)

### 3. Gemini API generation_config 오류
```
Models.generate_content() got an unexpected keyword argument 'generation_config'
```
- **원인**: 새로운 Gemini API에서는 `config` 파라미터 사용
- **해결**: `config` 딕셔너리로 변경

## 수정 사항

### 1. OpenAI 라이브러리 버전 업데이트
**파일**: `requirements.txt`
```diff
- openai==1.3.0
+ openai>=1.12.0  # 최신 버전 사용 (proxies 오류 수정)
```

### 2. Gemini 모델 이름 수정
**파일**: `backend/config.py`
```diff
- GEMINI_MODEL: str = "gemini-2.5-flash-preview"
+ GEMINI_MODEL: str = "gemini-1.5-flash"  # 안정적인 모델 사용
```

**파일**: `backend/services/target_analyzer.py`
```diff
- model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash-preview')
+ model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-1.5-flash')
```

**파일**: `backend/services/keyword_recommender.py`
```diff
- model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash-exp')
+ model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-1.5-flash')
```

**파일**: `backend/services/sentiment_analyzer.py`
```diff
- model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash-exp')
+ model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-1.5-flash')
```

### 3. Gemini API 호출 방식 수정
**파일**: `backend/services/target_analyzer.py`

**새로운 API 방식** (`from google import genai`):
```python
# 이전
generation_config={
    "response_mime_type": "application/json"
}

# 수정 후
config={
    "response_mime_type": "application/json"
}
```

**기존 API 방식** (`import google.generativeai`):
```python
# GenerationConfig 객체 사용 시도, 실패 시 딕셔너리 사용
try:
    response = await loop.run_in_executor(
        None, 
        lambda: model.generate_content(
            full_prompt,
            generation_config=genai_old.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )
    )
except (AttributeError, TypeError):
    # GenerationConfig가 없거나 지원하지 않는 경우 딕셔너리 사용
    response = await loop.run_in_executor(
        None, 
        lambda: model.generate_content(
            full_prompt,
            generation_config={
                "response_mime_type": "application/json"
            }
        )
    )
```

## 검증 방법

### 재배포 후 확인 사항

1. **OpenAI API 호출 성공**
   - 로그에서 `✅ OpenAI API 응답 수신 완료` 확인
   - `proxies` 오류가 발생하지 않음

2. **Gemini API 호출 성공**
   - 로그에서 `✅ Gemini API 응답 수신 완료` 확인
   - `404 NOT_FOUND` 오류가 발생하지 않음
   - `generation_config` 오류가 발생하지 않음

3. **실제 AI 분석 결과 반환**
   - 기본 분석 모드로 fallback되지 않음
   - 실제 AI 분석 결과가 반환됨

## 다음 단계

1. **재배포**
   - 수정 사항 반영 후 Vercel에 재배포

2. **로그 확인**
   - 배포 후 Vercel 로그에서 다음을 확인:
     - OpenAI API 호출 성공 로그
     - Gemini API 호출 성공 로그
     - 에러가 발생하지 않음

3. **테스트**
   - 실제 분석 요청을 보내고 로그 확인
   - API가 정상적으로 호출되는지 확인
   - 실제 AI 분석 결과가 반환되는지 확인

## 예상 결과

수정 후에는:
- ✅ OpenAI API가 정상적으로 호출됨
- ✅ Gemini API가 정상적으로 호출됨
- ✅ 실제 AI 분석 결과가 반환됨
- ✅ "기본 분석 모드" 메시지가 나오지 않음
