# JavaScript 구문 오류 수정

## 발견된 문제점

브라우저 콘솔에서 다음 오류가 발생했습니다:
```
Uncaught SyntaxError: Invalid or unexpected token
```

## 원인 분석

Python 문자열 내의 JavaScript 템플릿 리터럴(백틱과 `${}`)이 브라우저에서 파싱될 때 문제가 발생할 수 있습니다.

## 수정 사항

### 1. API URL 설정 수정

**파일**: `backend/main.py` (717번째 줄)

**이전**:
```javascript
const apiUrl = `${apiBaseUrl}/api/target/analyze/stream`;
```

**수정 후**:
```javascript
const apiUrl = apiBaseUrl + '/api/target/analyze/stream';
```

## 검증 방법

### 재배포 후 확인 사항

1. **브라우저 콘솔 오류 확인**
   - 브라우저 개발자 도구 콘솔에서 JavaScript 구문 오류가 발생하지 않음
   - `Uncaught SyntaxError` 오류가 사라짐

2. **API 호출 정상 작동**
   - 분석 요청이 정상적으로 작동함
   - API URL이 올바르게 생성됨

## 다음 단계

1. **재배포**
   - 수정 사항 반영 후 Vercel에 재배포

2. **테스트**
   - 브라우저 콘솔에서 오류가 발생하지 않는지 확인
   - 분석 요청이 정상적으로 작동하는지 확인

## 참고 사항

다른 템플릿 리터럴들(`resultText += \`...\``)은 Python 문자열 내에서 이스케이프가 제대로 되어 있어 문제가 없습니다. 하지만 추가 오류가 발생하면 해당 부분도 일반 문자열 연결로 변경할 수 있습니다.
