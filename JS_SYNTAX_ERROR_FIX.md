# JavaScript 구문 오류 수정

## 문제점
```
Uncaught SyntaxError: Invalid or unexpected token (at (index):1693:47)
```

## 원인
`backend/main.py`의 1690번 줄에서 Python 문자열 안에 있는 JavaScript 템플릿 리터럴의 백틱이 제대로 이스케이프되지 않았습니다.

**문제 코드**:
```python
const score = kw.score ? ` (점수: ${kw.score})` : '';
```

Python 삼중 따옴표 문자열(`"""`) 안에서 JavaScript 템플릿 리터럴(백틱)을 사용할 때, 백틱과 `${}` 표현식이 제대로 이스케이프되지 않아 브라우저에서 구문 오류가 발생했습니다.

## 해결 방법

### 수정 사항
템플릿 리터럴을 일반 문자열 연결로 변경:

**이전**:
```python
const score = kw.score ? ` (점수: ${kw.score})` : '';
```

**수정 후**:
```python
const score = kw.score ? ' (점수: ' + kw.score + ')' : '';
```

이렇게 하면 백틱 이스케이프 문제를 완전히 피할 수 있습니다.

## 검증

브라우저 콘솔에서 구문 오류가 발생하지 않는지 확인하세요.

## 참고

Python 문자열 안에 JavaScript 코드를 작성할 때:
- 템플릿 리터럴(백틱) 대신 일반 문자열 연결(`+`)을 사용하는 것이 더 안전합니다
- 또는 백틱을 `\\``로 이스케이프하고 `${}`를 `\\$\\{`로 이스케이프해야 합니다
- 하지만 일반 문자열 연결이 더 간단하고 안전합니다
