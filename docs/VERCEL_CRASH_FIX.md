# Vercel 서버리스 함수 크래시 해결 방법

## 수정 사항

### 1. `index.py` 수정
- Vercel 환경 감지 추가
- FastAPI 앱을 직접 export (Vercel이 자동으로 처리)

### 2. `backend/config.py` 수정
- Vercel 환경에서는 디렉토리 생성 건너뛰기
- 파일 시스템 접근 오류 방지

### 3. `backend/main.py` 수정
- Vercel 환경에서는 파일 로깅 비활성화
- 정적 파일 마운트를 Vercel 환경에서 건너뛰기
- 모든 파일 시스템 작업을 try-except로 보호

## 주요 변경점

### Vercel 환경 감지
```python
IS_VERCEL = os.environ.get("VERCEL") == "1"
```

### 파일 시스템 작업 보호
- 디렉토리 생성: Vercel 환경에서는 건너뛰기
- 파일 로깅: Vercel 환경에서는 비활성화
- 정적 파일: Vercel 환경에서는 마운트하지 않음

## 테스트

로컬에서 테스트:
```bash
# 환경 변수 설정
export VERCEL=1

# 앱 import 테스트
python3 -c "from index import app; print('Success')"
```

## 배포 후 확인

1. **헬스 체크**: `https://your-project.vercel.app/health`
2. **API 문서**: `https://your-project.vercel.app/docs`
3. **루트 엔드포인트**: `https://your-project.vercel.app/`

## 추가 디버깅

만약 여전히 오류가 발생한다면:
1. Vercel 로그 확인
2. 환경 변수 설정 확인
3. `requirements.txt`의 모든 패키지가 설치되는지 확인
