# JavaScript 따옴표 이스케이프 수정

## 발견된 문제점

브라우저 콘솔에서 다음 오류가 발생했습니다:
```
Uncaught SyntaxError: Invalid or unexpected token (at (index):683:46)
```

## 원인 분석

Python 삼중 따옴표 문자열(`"""`) 내의 JavaScript 코드에서 작은따옴표(`'`)를 사용하면, 브라우저에서 파싱할 때 문제가 발생할 수 있습니다. 특히 Python 문자열 내에서 작은따옴표가 잘못 이스케이프되거나 파싱될 수 있습니다.

## 수정 사항

### 모든 `getElementById` 호출의 작은따옴표를 큰따옴표로 변경

**파일**: `backend/main.py`

**이전**:
```javascript
const startDate = document.getElementById('start_date').value;
const endDate = document.getElementById('end_date').value;
```

**수정 후**:
```javascript
const startDate = document.getElementById("start_date").value;
const endDate = document.getElementById("end_date").value;
```

### 수정된 모든 위치

1. **URL 파라미터 처리 부분** (582-587번째 줄)
   - `getElementById('target_keyword')` → `getElementById("target_keyword")`
   - `getElementById('target_type')` → `getElementById("target_type")`
   - `getElementById('start_date')` → `getElementById("start_date")`
   - `getElementById('end_date')` → `getElementById("end_date")`
   - `getElementById('additional_context')` → `getElementById("additional_context")`
   - `getElementById('use_gemini')` → `getElementById("use_gemini")`

2. **URL 파라미터 읽기 부분** (590-615번째 줄)
   - `urlParams.has('target_keyword')` → `urlParams.has("target_keyword")`
   - `urlParams.get('target_keyword')` → `urlParams.get("target_keyword")`
   - 모든 파라미터의 작은따옴표를 큰따옴표로 변경

3. **폼 데이터 수집 부분** (679-680, 700-703번째 줄)
   - 모든 `getElementById` 호출의 작은따옴표를 큰따옴표로 변경

4. **기타 함수들**
   - `copyToClipboard()` 함수의 `getElementById` 호출
   - `addEventListener` 함수의 `getElementById` 호출
   - 진행률 표시 관련 `getElementById` 호출

## 검증 방법

### 재배포 후 확인 사항

1. **브라우저 콘솔 오류 확인**
   - 브라우저 개발자 도구 콘솔에서 JavaScript 구문 오류가 발생하지 않음
   - `Uncaught SyntaxError` 오류가 사라짐

2. **폼 기능 정상 작동**
   - 폼 입력이 정상적으로 작동함
   - URL 파라미터로 폼이 자동으로 채워짐
   - 분석 요청이 정상적으로 작동함

## 다음 단계

1. **재배포**
   - 수정 사항 반영 후 Vercel에 재배포

2. **테스트**
   - 브라우저 콘솔에서 오류가 발생하지 않는지 확인
   - URL 파라미터가 포함된 URL로 접속하여 폼이 자동으로 채워지는지 확인
   - 분석 요청이 정상적으로 작동하는지 확인

## 참고 사항

- Python 삼중 따옴표 문자열(`"""`) 내에서 JavaScript 코드를 작성할 때는 큰따옴표(`"`)를 사용하는 것이 안전합니다.
- 작은따옴표(`'`)를 사용해야 하는 경우에는 이스케이프(`\'`)를 사용하거나, 큰따옴표로 변경하는 것이 좋습니다.
