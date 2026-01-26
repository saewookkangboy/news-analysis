# Vercel Handler TypeError 완전 수정

## 문제점
```
TypeError: issubclass() arg 1 must be a class
Python process exited with exit status: 1
```

## 원인 분석

웹 검색 결과에 따르면, 이 오류는 주로 다음과 같은 원인으로 발생합니다:

1. **`typing` 패키지 충돌**: Python 3.5+에서는 `typing`이 내장 모듈인데, `requirements.txt`에 `typing` 패키지가 포함되어 있으면 충돌 발생
2. **순환 import 문제**: FastAPI의 타입 검증 중 순환 import로 인한 문제
3. **Handler 형식 문제**: Vercel이 handler를 클래스로 인식하려고 시도

## 해결 방법

### 1. api/index.py 수정

**핵심 변경 사항**:
- Mangum import를 try-except에서 제거하고 직접 import
- Vercel에서는 Mangum이 필수이므로 ImportError 처리를 제거

**이전**:
```python
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except ImportError:
    handler = app
```

**수정 후**:
```python
from mangum import Mangum

# handler를 함수로 정의 (Vercel이 기대하는 형식)
handler = Mangum(app, lifespan="off")
```

### 2. requirements.txt 확인

`typing` 패키지가 포함되어 있지 않은지 확인:
- ✅ `typing` 패키지가 없음 (Python 3.5+에서는 내장 모듈)
- ✅ `mangum==0.17.0` 포함됨

## 검증

로컬에서 handler import 테스트:
```bash
python3 -c "import sys; sys.path.insert(0, '.'); from api.index import handler; print('Handler type:', type(handler))"
```

**예상 결과**:
- `<class 'mangum.adapter.Mangum'>`

## 다음 단계

1. **재배포**
   - 수정 사항 반영 후 Vercel에 재배포

2. **확인**
   - 배포 후 Vercel 로그에서 TypeError가 발생하지 않는지 확인
   - 사이트가 정상적으로 작동하는지 확인

## 참고

- Vercel에서는 Mangum이 필수입니다 (`requirements.txt`에 포함되어야 함)
- Mangum은 FastAPI (ASGI) 앱을 AWS Lambda 핸들러로 변환합니다
- `handler` 변수는 모듈 레벨에서 정의되어야 Vercel이 인식합니다
- `typing` 패키지를 `requirements.txt`에 추가하지 마세요 (Python 3.5+에서는 내장 모듈)
