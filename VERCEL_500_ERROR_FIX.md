# Vercel 500 에러 수정 사항

## 발생한 에러

1. **SyntaxWarning**: `invalid escape sequence '\`'`
   - `backend/main.py`의 JavaScript 코드에서 백틱 이스케이프 문제

2. **TypeError**: `issubclass() arg 1 must be a class`
   - Vercel 핸들러 인식 문제

## 수정 사항

### 1. 백틱 이스케이프 문제 수정

**파일**: `backend/main.py` (1770번 줄)

**이전**:
```python
resultText += `\`\`\`json\\n${JSON.stringify(...)}\\n\`\`\`\\n\\n`;
```

**수정 후**:
```python
resultText += `\\\`\\\`\\\`json\\\\n${JSON.stringify(...)}\\\\n\\\`\\\`\\\`\\\\n\\\\n`;
```

Python 문자열에서 백틱을 이스케이프할 때는 `\\\``를 사용해야 합니다.

### 2. Vercel 설정 단순화

**파일**: `vercel.json`

**이전**:
```json
{
  "version": 2,
  "builds": [...],
  "routes": [...],
  "functions": {...}
}
```

**수정 후**:
```json
{
  "version": 2,
  "functions": {
    "api/index.py": {
      "maxDuration": 60,
      "memory": 1024
    }
  }
}
```

최신 Vercel은 자동으로 `api/index.py`를 감지하므로 `builds`와 `routes`를 제거했습니다.

### 3. api/index.py 개선

**변경 사항**:
- 불필요한 `__all__` 제거
- 에러 처리 개선
- 로깅 개선

**핵심**:
- `handler` 변수를 export하면 Vercel이 자동으로 인식합니다
- Mangum을 사용하여 FastAPI 앱을 Lambda 핸들러로 변환합니다

## 검증

로컬에서 import 테스트:
```bash
python3 -c "import sys; sys.path.insert(0, '.'); from api.index import handler; print('Handler import 성공')"
```

## 다음 단계

1. **재배포**
   - 수정 사항 반영 후 Vercel에 재배포

2. **확인**
   - 배포 후 사이트 접속하여 500 에러가 해결되었는지 확인
   - Vercel 로그에서 에러가 없는지 확인
   - API 키가 정상적으로 로딩되는지 확인

## 참고

- Vercel은 `api/` 디렉토리의 Python 파일을 자동으로 Serverless Function으로 인식합니다
- `handler` 변수를 export하면 Vercel이 자동으로 Lambda 핸들러로 사용합니다
- Mangum은 FastAPI (ASGI) 앱을 AWS Lambda 핸들러로 변환합니다
