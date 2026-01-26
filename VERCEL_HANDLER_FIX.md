# Vercel Handler TypeError 수정

## 문제점
```
TypeError: issubclass() arg 1 must be a class
Python process exited with exit status: 1
```

## 원인
Vercel의 Python 런타임이 handler를 클래스로 인식하려고 시도하는데, handler가 인스턴스(객체)이기 때문에 발생하는 오류입니다.

## 해결 방법

### api/index.py 구조 개선

**핵심 변경 사항**:
1. 에러 처리를 더 명확하게 분리
2. handler가 항상 정의되도록 보장
3. Mangum을 우선적으로 사용 (Vercel에서 권장)

**수정된 구조**:
```python
# FastAPI 앱 import
try:
    from backend.main import app
except Exception as e:
    # 에러 발생 시 기본 앱 생성
    from fastapi import FastAPI
    app = FastAPI()
    @app.get("/")
    async def error_root():
        return {"error": "Application failed to start", "message": str(e)}

# Mangum을 사용하여 ASGI 앱을 Lambda 핸들러로 변환
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except ImportError:
    # Mangum이 없으면 app을 직접 사용
    handler = app
```

## 검증

로컬에서 handler import 테스트:
```bash
python3 -c "import sys; sys.path.insert(0, '.'); from api.index import handler; print('Handler type:', type(handler))"
```

**예상 결과**:
- Mangum이 있으면: `<class 'mangum.adapter.Mangum'>`
- Mangum이 없으면: `<class 'fastapi.applications.FastAPI'>`

## 다음 단계

1. **재배포**
   - 수정 사항 반영 후 Vercel에 재배포

2. **확인**
   - 배포 후 Vercel 로그에서 TypeError가 발생하지 않는지 확인
   - 사이트가 정상적으로 작동하는지 확인

## 참고

- Vercel에서는 Mangum이 `requirements.txt`에 포함되어 있어야 합니다
- Mangum은 FastAPI (ASGI) 앱을 AWS Lambda 핸들러로 변환합니다
- `handler` 변수는 모듈 레벨에서 정의되어야 Vercel이 인식합니다
