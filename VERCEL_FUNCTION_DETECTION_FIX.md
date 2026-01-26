# Vercel Serverless Function 감지 문제 해결

## 문제점
```
Error: The pattern "api/index.py" defined in `functions` doesn't match any Serverless Functions inside the `api` directory.
```

## 원인
Vercel은 `api/` 디렉토리의 Python 파일을 자동으로 Serverless Function으로 감지합니다. `vercel.json`에서 `functions`를 명시적으로 지정할 때는 특정 형식이 필요하지만, 최신 Vercel은 자동 감지를 사용하는 것이 권장됩니다.

## 해결 방법

### vercel.json 수정

**이전**:
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

**수정 후**:
```json
{
  "version": 2
}
```

Vercel이 자동으로 `api/index.py`를 감지하고 Serverless Function으로 처리합니다.

## Vercel의 자동 감지 규칙

1. **`api/` 디렉토리**: `api/` 디렉토리의 모든 파일이 자동으로 Serverless Function으로 인식됩니다.
2. **Python 파일**: `.py` 확장자를 가진 파일은 자동으로 Python 런타임으로 실행됩니다.
3. **Handler 변수**: `handler` 변수를 export하면 Vercel이 자동으로 Lambda 핸들러로 사용합니다.

## 함수 설정 (필요한 경우)

만약 함수별로 다른 설정이 필요하다면, Vercel Dashboard에서 설정하거나 `vercel.json`에 다음과 같이 추가할 수 있습니다:

```json
{
  "version": 2,
  "functions": {
    "api/**/*.py": {
      "maxDuration": 60,
      "memory": 1024
    }
  }
}
```

하지만 단일 함수(`api/index.py`)만 있는 경우에는 자동 감지가 더 간단하고 안정적입니다.

## 검증

배포 후 다음을 확인하세요:

1. **Vercel 로그**: `api/index.py`가 Serverless Function으로 인식되는지 확인
2. **배포 성공**: 에러 없이 배포가 완료되는지 확인
3. **사이트 접속**: 정상적으로 작동하는지 확인

## 참고

- Vercel은 `api/` 디렉토리의 파일을 자동으로 감지합니다
- `handler` 변수를 export하면 Vercel이 자동으로 Lambda 핸들러로 사용합니다
- Mangum을 사용하여 FastAPI 앱을 Lambda 핸들러로 변환합니다
