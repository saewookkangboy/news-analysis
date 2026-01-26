# Gemini API 최종 수정 완료

## 발견된 문제점

로그 분석 결과 다음 문제들이 발견되었습니다:

### 1. Gemini API generation_config 오류
```
Models.generate_content() got an unexpected keyword argument 'generation_config'
```
- **원인**: 새로운 Gemini API (`from google import genai`)에서는 `generation_config` 대신 `config` 파라미터를 사용해야 함
- **해결**: `config` 파라미터를 먼저 시도하고, 실패 시 `generation_config` 시도, 그것도 실패하면 일반 모드로 fallback

### 2. JSON 파싱 실패
```
JSON 파싱 최종 실패: Expecting ',' delimiter: line 96 column 2 (char 13748)
```
- **원인**: Gemini 응답이 너무 길거나 잘못된 JSON 형식 (마지막 쉼표 등)
- **해결**: 더 강력한 JSON 파싱 로직 추가 (중괄호 추출, 마지막 쉼표 제거 등)

## 수정 사항

### 1. 새로운 Gemini API 호출 방식 개선

**파일**: `backend/services/target_analyzer.py`, `backend/services/sentiment_analyzer.py`, `backend/services/keyword_recommender.py`

**이전**:
```python
response = await loop.run_in_executor(
    None, 
    lambda: client.models.generate_content(
        model=model_name,
        contents=full_prompt,
        generation_config={
            "response_mime_type": "application/json"
        }
    )
)
```

**수정 후**:
```python
try:
    # config 파라미터 시도 (새로운 API 방식)
    response = await loop.run_in_executor(
        None, 
        lambda: client.models.generate_content(
            model=model_name,
            contents=full_prompt,
            config={
                "response_mime_type": "application/json"
            }
        )
    )
except (TypeError, AttributeError) as config_error:
    # config가 지원되지 않는 경우 generation_config 시도
    try:
        response = await loop.run_in_executor(
            None, 
            lambda: client.models.generate_content(
                model=model_name,
                contents=full_prompt,
                generation_config={
                    "response_mime_type": "application/json"
                }
            )
        )
    except Exception as gen_error:
        # generation_config도 실패하면 일반 모드
        response = await loop.run_in_executor(
            None, 
            lambda: client.models.generate_content(
                model=model_name,
                contents=full_prompt
            )
        )
```

### 2. JSON 파싱 로직 강화

**파일**: `backend/services/target_analyzer.py`

**이전**:
```python
try:
    result = json.loads(clean_text)
except json.JSONDecodeError as e:
    # 중괄호만 추출
    start_idx = clean_text.find("{")
    end_idx = clean_text.rfind("}") + 1
    result = json.loads(clean_text[start_idx:end_idx])
```

**수정 후**:
```python
try:
    result = json.loads(clean_text)
except json.JSONDecodeError as e:
    logger.warning(f"JSON 파싱 실패, 재시도: {e}")
    logger.warning(f"실패 위치: line {e.lineno}, column {e.colno}, char {e.pos}")
    # 중괄호만 추출
    start_idx = clean_text.find("{")
    end_idx = clean_text.rfind("}") + 1
    if start_idx >= 0 and end_idx > start_idx:
        json_text = clean_text[start_idx:end_idx]
        # 마지막 쉼표 제거 시도 (잘못된 JSON 형식 수정)
        json_text = json_text.rstrip().rstrip(',')
        # 닫는 중괄호 다시 추가
        if not json_text.endswith("}"):
            json_text += "}"
        result = json.loads(json_text)
        logger.info("✅ 중괄호 추출 후 JSON 파싱 성공")
```

## 수정된 파일

1. **backend/services/target_analyzer.py**
   - 새로운 Gemini API 호출 방식 개선
   - JSON 파싱 로직 강화

2. **backend/services/sentiment_analyzer.py**
   - 새로운 Gemini API 호출 방식 개선 (감정/맥락/톤 분석)

3. **backend/services/keyword_recommender.py**
   - 새로운 Gemini API 호출 방식 개선

## 검증 방법

### 재배포 후 확인 사항

1. **Gemini API 호출 성공**
   - 로그에서 `✅ Gemini API 응답 수신 완료` 확인
   - `generation_config` 오류가 발생하지 않음

2. **JSON 파싱 성공**
   - 로그에서 `✅ 중괄호 추출 후 JSON 파싱 성공` 확인
   - JSON 파싱 실패 오류가 발생하지 않음

3. **실제 AI 분석 결과 반환**
   - 기본 분석 모드로 fallback되지 않음
   - 실제 AI 분석 결과가 반환됨

## 다음 단계

1. **재배포**
   - 수정 사항 반영 후 Vercel에 재배포

2. **로그 확인**
   - 배포 후 Vercel 로그에서 다음을 확인:
     - Gemini API 호출 성공 로그
     - JSON 파싱 성공 로그
     - 에러가 발생하지 않음

3. **테스트**
   - 실제 분석 요청을 보내고 로그 확인
   - API가 정상적으로 호출되는지 확인
   - 실제 AI 분석 결과가 반환되는지 확인

## 예상 결과

수정 후에는:
- ✅ Gemini API가 정상적으로 호출됨
- ✅ JSON 파싱이 성공적으로 완료됨
- ✅ 실제 AI 분석 결과가 반환됨
- ✅ "기본 분석 모드" 메시지가 나오지 않음
