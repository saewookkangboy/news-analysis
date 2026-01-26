# 프로젝트 구조 가이드

## 📁 디렉토리 구조

```
news-trend-analyzer/
├── backend/                    # 백엔드 코드
│   ├── api/                   # API 라우터
│   │   ├── __init__.py
│   │   ├── routes.py          # 메인 API 엔드포인트
│   │   └── cache_stats.py     # 캐시 통계
│   ├── middleware/            # 미들웨어
│   │   ├── __init__.py
│   │   └── cache_middleware.py
│   ├── services/              # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── target_analyzer.py      # 타겟 분석 서비스
│   │   ├── sentiment_analyzer.py   # 감정 분석 서비스
│   │   ├── keyword_recommender.py  # 키워드 추천 서비스
│   │   └── progress_tracker.py     # 진행 상황 추적
│   ├── config.py              # 설정 관리
│   └── main.py                # FastAPI 앱 진입점
│
├── frontend/                  # 프론트엔드 코드
│   └── src/
│       ├── components/        # React 컴포넌트
│       │   ├── Dashboard.tsx
│       │   ├── AnalysisSettings.tsx
│       │   ├── ScenarioManager.tsx
│       │   ├── CustomerJourneyMap.tsx
│       │   ├── KPIAnalytics.tsx
│       │   ├── Settings.tsx
│       │   ├── Navigation.tsx
│       │   ├── Footer.tsx
│       │   ├── ErrorBoundary.tsx
│       │   └── NetworkStatus.tsx
│       ├── services/          # API 서비스
│       │   ├── analysisService.ts
│       │   └── dashboardService.ts
│       ├── utils/             # 유틸리티
│       │   └── errorHandler.ts
│       ├── App.tsx            # 메인 앱 컴포넌트
│       ├── App.css
│       └── index.css
│
├── api/                       # Vercel Serverless Functions
│   └── index.py              # Vercel 진입점
│
├── scripts/                   # 유틸리티 스크립트
│   ├── verify_api_keys.py    # API 키 검증
│   └── test_api_keys_vercel.py
│
├── docs/                      # 문서 파일
│   ├── PROJECT_STRUCTURE.md   # 이 파일
│   └── ...                    # 기타 문서들
│
├── data/                      # 데이터 저장소 (로컬 개발용)
│   ├── raw/                   # 원시 데이터
│   ├── processed/             # 처리된 데이터
│   ├── cache/                 # 캐시 데이터
│   └── stopwords.txt          # 불용어 목록
│
├── logs/                      # 로그 파일 (로컬 개발용)
│
├── exports/                   # 분석 결과 내보내기 (로컬 개발용)
│
├── .env                       # 환경 변수 (로컬 개발용, git에 포함되지 않음)
├── .env.example              # 환경 변수 템플릿
├── .gitignore
├── .vercelignore
├── requirements.txt           # Python 의존성
├── vercel.json               # Vercel 배포 설정
├── run.py                    # 로컬 실행 스크립트
├── run.sh                    # 로컬 실행 스크립트 (쉘)
├── index.py                  # Vercel 루트 진입점 (선택사항)
└── README.md                 # 프로젝트 메인 문서
```

## 🔗 데이터 연결 구조

### 1. 설정 관리
- **위치**: `backend/config.py`
- **역할**: 모든 설정을 중앙에서 관리
- **환경 변수**: `.env` 파일 또는 시스템 환경 변수에서 로드
- **템플릿**: `.env.example` 참고

### 2. API 라우팅
- **백엔드**: `backend/api/routes.py` - 모든 API 엔드포인트 정의
- **Vercel**: `api/index.py` - Serverless Function 진입점
- **로컬**: `backend/main.py` - FastAPI 앱 직접 실행

### 3. 서비스 계층
- **target_analyzer.py**: 타겟 분석 메인 로직
- **sentiment_analyzer.py**: 감정/맥락/톤 분석
- **keyword_recommender.py**: 키워드 추천
- **progress_tracker.py**: 비동기 작업 진행 상황 추적

### 4. 프론트엔드 연결
- **analysisService.ts**: 백엔드 API와 통신
- **자동 환경 감지**: 로컬/프로덕션 환경 자동 구분
- **API Base URL**: 
  - 로컬: `http://localhost:8000/api`
  - 프로덕션: `window.location.origin/api`

### 5. 데이터 저장
- **로컬 개발**: `data/` 디렉토리 사용
- **Vercel 배포**: 임시 저장소 또는 외부 스토리지 사용
- **캐시**: 메모리 기반 (Vercel에서는 제한적)

## 🚀 실행 방법

### 로컬 개발
```bash
# 방법 1: 스크립트 사용
./run.sh

# 방법 2: Python 직접 실행
python run.py

# 방법 3: Uvicorn 직접 실행
python -m uvicorn backend.main:app --reload
```

### Vercel 배포
- `api/index.py`가 자동으로 진입점으로 사용됨
- 환경 변수는 Vercel 대시보드에서 설정

## 📝 유지보수 가이드

### 새로운 API 엔드포인트 추가
1. `backend/api/routes.py`에 새 라우트 추가
2. 필요한 서비스 로직은 `backend/services/`에 추가
3. 프론트엔드에서 `frontend/src/services/analysisService.ts` 업데이트

### 설정 변경
1. `backend/config.py`의 `Settings` 클래스 수정
2. `.env.example` 업데이트
3. 문서 업데이트

### 데이터 구조 변경
1. `backend/config.py`의 디렉토리 경로 확인
2. 필요한 디렉토리 자동 생성 확인
3. 마이그레이션 스크립트 작성 (필요시)

## 🔧 환경별 차이점

### 로컬 개발
- 파일 시스템 사용 가능
- 로그 파일 생성
- 정적 파일 서빙
- 데이터 디렉토리 사용

### Vercel 배포
- Serverless Function 환경
- 파일 시스템 제한적
- 환경 변수만 사용
- 캐시는 메모리 기반 (제한적)
