# Vercel 배포 크기 제한 해결 방법

## 문제
Vercel의 Python 함수는 **최대 250MB (압축 해제 후)** 크기 제한이 있습니다.
현재 `sentence-transformers`와 같은 대용량 패키지로 인해 이 제한을 초과하고 있습니다.

## 해결 방법

### 1. 대용량 패키지 제거/주석 처리
`requirements.txt`에서 다음 패키지를 제거했습니다:
- `sentence-transformers` (모델 파일 포함, 수 GB)
- `pandas` (선택적, 필요시만 활성화)
- `numpy` (선택적, 필요시만 활성화)

### 2. 대안 방법

#### sentence-transformers 대신
- OpenAI/Gemini API를 사용하여 임베딩 생성 (현재 코드에서 이미 사용 중)
- 외부 임베딩 서비스 사용
- 필요시 별도의 서버리스 함수로 분리

#### pandas/numpy 대신
- Python 내장 라이브러리 사용
- 필요시 경량 대안 사용

### 3. 배포 크기 확인

배포 전 로컬에서 크기 확인:
```bash
# 가상 환경 생성
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 설치된 패키지 크기 확인
pip list | grep -E "pandas|numpy|sentence|transformers|torch"
```

### 4. 필요시 패키지 추가

특정 기능이 필요하면:
1. 해당 기능이 정말 필요한지 확인
2. 경량 대안 찾기
3. 별도 마이크로서비스로 분리

## 현재 requirements.txt

핵심 패키지만 포함:
- FastAPI 및 웹 프레임워크
- HTTP 요청 (requests, beautifulsoup4)
- AI API 클라이언트 (openai, google-generativeai)
- 기본 유틸리티

## 참고
- Vercel Python 함수 크기 제한: 250MB (압축 해제 후)
- 큰 모델은 Vercel Blob Storage 또는 외부 서비스 사용 권장
