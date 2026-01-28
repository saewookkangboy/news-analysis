# 📊 뉴스 트렌드 분석 서비스

AI 기반 키워드, 오디언스, 경쟁자 분석 플랫폼입니다. OpenAI 또는 Google Gemini API를 활용하여 마케팅 및 비즈니스 인사이트를 제공합니다.

## ✨ 주요 기능

### 1. 타겟 분석
- **키워드 분석**: 검색 트렌드, 검색량, 경쟁도, 관련 키워드 분석
- **오디언스 분석**: 타겟 고객층의 인구통계학적 특성, 심리적 특성, 행동 패턴 분석
- **경쟁자 분석**: 주요 경쟁자, 경쟁 우위, 차별화 포인트, 시장 점유율 분석

### 2. 인터랙티브 웹 인터페이스
- 브라우저에서 직접 키워드 입력 및 분석 실행
- 실시간 분석 결과 표시
- 다양한 분석 유형 선택 가능
- 결과 복사 및 공유 기능

### 3. AI 모델 지원
- OpenAI GPT-4o-mini
- Google Gemini 2.0 Flash
- 사용자가 원하는 AI 모델 선택 가능

### 4. 성능 최적화
- 캐싱 미들웨어를 통한 응답 속도 향상
- 비동기 처리로 동시 요청 지원
- 효율적인 데이터 처리

## 🛠 기술 스택

### Backend
- **FastAPI**: 고성능 비동기 웹 프레임워크
- **Uvicorn**: ASGI 서버
- **OpenAI API**: GPT 모델 기반 분석
- **Google Gemini API**: Gemini 모델 기반 분석
- **Pydantic**: 데이터 검증 및 설정 관리

### Frontend
- **React**: 사용자 인터페이스 구축
- **TypeScript**: 타입 안정성
- **Tailwind CSS**: 스타일링

### 기타
- **Python 3.8+**: 백엔드 언어
- **Docker**: 컨테이너화 (선택사항)
- **Vercel**: 배포 플랫폼 지원

## 📦 설치 및 실행

### 사전 요구사항
- Python 3.8 이상
- pip 패키지 관리자
- OpenAI API 키 또는 Gemini API 키 (선택사항)

### 1. 저장소 클론
```bash
git clone https://github.com/saewookkangboy/news-analysis.git
cd news-trend-analyzer
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```bash
# .env.example 파일을 복사하여 사용
cp .env.example .env
```

그리고 `.env` 파일을 열어 실제 API 키를 입력하세요:

```env
# AI API 설정 (최소 하나는 필요)
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# 서버 설정 (선택사항)
HOST=0.0.0.0
PORT=8000
DEBUG=True

# 캐싱 설정 (선택사항)
CACHE_ENABLED=True
CACHE_TTL=3600
```

모든 설정 옵션은 `.env.example` 파일을 참고하세요.

### 4. 서버 실행

#### 방법 1: 실행 스크립트 사용 (권장)
```bash
./run.sh
```

#### 방법 2: Python 스크립트 사용
```bash
python run.py
```

#### 방법 3: Uvicorn 직접 실행
```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 접속
브라우저에서 다음 주소로 접속하세요:
```
http://localhost:8000
```

## 🚀 사용 방법

### 웹 인터페이스 사용

1. **분석할 키워드 입력**
   - 예: "인공지능", "스마트폰", "삼성전자"

2. **분석 유형 선택**
   - 키워드 분석: 검색 트렌드 및 경쟁도
   - 오디언스 분석: 타겟 고객층 특성
   - 경쟁자 분석: 경쟁 우위 분석

3. **추가 컨텍스트 입력** (선택사항)
   - 추가로 제공할 컨텍스트 정보

4. **AI 모델 선택** (선택사항)
   - 체크 시 Gemini API 사용 (기본값: OpenAI)

5. **분석 시작** 버튼 클릭

### API 사용

#### POST /api/target/analyze
```bash
curl -X POST "http://localhost:8000/api/target/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "target_keyword": "인공지능",
    "target_type": "keyword",
    "additional_context": "최신 기술 트렌드",
    "use_gemini": false
  }'
```

#### GET /api/target/analyze
```bash
curl "http://localhost:8000/api/target/analyze?target_keyword=인공지능&target_type=keyword"
```

## 📁 프로젝트 구조

```
news-trend-analyzer/
├── backend/                    # 백엔드 코드
│   ├── api/                   # API 라우터
│   │   ├── routes.py          # 메인 API 엔드포인트
│   │   └── cache_stats.py     # 캐시 통계
│   ├── middleware/            # 미들웨어
│   │   └── cache_middleware.py
│   ├── services/              # 비즈니스 로직
│   │   ├── target_analyzer.py      # 타겟 분석 서비스
│   │   ├── sentiment_analyzer.py   # 감정 분석 서비스
│   │   ├── keyword_recommender.py  # 키워드 추천 서비스
│   │   └── progress_tracker.py     # 진행 상황 추적
│   ├── config.py              # 설정 관리 (중앙화)
│   └── main.py                # FastAPI 앱 진입점
├── frontend/                  # 프론트엔드 코드
│   └── src/
│       ├── components/        # React 컴포넌트
│       ├── services/          # API 서비스
│       ├── utils/             # 유틸리티
│       ├── App.tsx            # 메인 앱 컴포넌트
│       └── index.css          # 스타일
├── api/                       # Vercel Serverless Functions
│   └── index.py              # Vercel 진입점
├── scripts/                   # 유틸리티 스크립트
│   ├── verify_api_keys.py    # API 키 검증
│   └── test_api_keys_vercel.py
├── docs/                      # 문서 파일
│   └── PROJECT_STRUCTURE.md  # 상세 구조 가이드
├── data/                      # 데이터 저장소 (로컬 개발용)
│   ├── raw/                   # 원시 데이터
│   ├── processed/             # 처리된 데이터
│   └── cache/                 # 캐시 데이터
├── .env.example              # 환경 변수 템플릿
├── requirements.txt          # Python 의존성
├── vercel.json              # Vercel 배포 설정
├── run.py                   # 로컬 실행 스크립트
└── README.md                # 프로젝트 문서
```

자세한 구조는 [docs/PROJECT_STRUCTURE.md](./docs/PROJECT_STRUCTURE.md)를 참고하세요.

## 🔌 API 엔드포인트

### 타겟 분석
- `POST /api/target/analyze` - 타겟 분석 실행
- `GET /api/target/analyze` - 타겟 분석 실행 (쿼리 파라미터)

### 헬스 체크
- `GET /health` - 서비스 상태 확인

### API 문서
- `GET /docs` - Swagger UI (인터랙티브 API 문서)
- `GET /openapi.json` - OpenAPI 스펙

### 캐시 통계
- `GET /api/cache/stats` - 캐시 통계 정보

## 📊 분석 결과 형식

### 키워드/경쟁자 분석
```json
{
  "summary": "분석 요약",
  "key_points": ["주요 포인트 1", "주요 포인트 2"],
  "insights": {
    "trends": ["트렌드 1", "트렌드 2"],
    "opportunities": ["기회 1", "기회 2"],
    "challenges": ["도전 과제 1", "도전 과제 2"]
  },
  "recommendations": ["권장사항 1", "권장사항 2"],
  "metrics": {
    "estimated_volume": "예상 검색량/시장 규모",
    "competition_level": "경쟁 수준",
    "growth_potential": "성장 잠재력"
  }
}
```

### 오디언스 분석
```json
{
  "summary": "오디언스 요약",
  "key_points": ["주요 포인트"],
  "insights": {
    "demographics": {
      "age_range": "주요 연령대",
      "gender": "성별 분포",
      "location": "주요 지역",
      "income_level": "소득 수준",
      "expected_occupations": ["직업 1", "직업 2"]
    },
    "psychographics": {
      "lifestyle": "라이프스타일",
      "values": "가치관",
      "interests": "관심사"
    },
    "behavior": {
      "purchase_behavior": "구매 행동",
      "media_consumption": "미디어 소비",
      "online_activity": "온라인 활동"
    }
  },
  "recommendations": ["마케팅 전략"],
  "metrics": {
    "estimated_volume": "예상 규모",
    "engagement_level": "참여 수준",
    "growth_potential": "성장 잠재력"
  }
}
```

## 🚢 배포

### Vercel 배포
1. Vercel 계정 생성 및 프로젝트 연결
2. 환경 변수 설정 (Vercel 대시보드)
3. 자동 배포 또는 수동 배포

자세한 내용은 [VERCEL_DEPLOY.md](./VERCEL_DEPLOY.md)를 참고하세요.

### Docker 배포
```bash
docker build -t news-trend-analyzer .
docker run -p 8000:8000 --env-file .env news-trend-analyzer
```

## 🔧 설정 옵션

환경 변수 또는 `.env` 파일을 통해 다음 설정을 변경할 수 있습니다:

- `HOST`: 서버 호스트 (기본값: 0.0.0.0)
- `PORT`: 서버 포트 (기본값: 8000)
- `DEBUG`: 디버그 모드 (기본값: True)
- `CACHE_ENABLED`: 캐싱 활성화 (기본값: True)
- `CACHE_TTL`: 캐시 TTL (초 단위, 기본값: 3600)
- `OPENAI_MODEL`: OpenAI 모델명 (기본값: gpt-4o-mini)
- `GEMINI_MODEL`: Gemini 모델명 (기본값: gemini-2.0-flash)

## 🐛 문제 해결

### 분석이 실행되지 않는 경우
1. 서버가 정상 실행 중인지 확인 (`/health` 엔드포인트 확인)
2. 브라우저 콘솔에서 에러 메시지 확인
3. API 키가 설정되어 있는지 확인 (`.env` 파일)

### 결과가 표시되지 않는 경우
1. 네트워크 연결 확인
2. 서버 로그 확인
3. API 응답 형식 확인

### 포트 충돌
포트 8000이 이미 사용 중인 경우:
```bash
# 기존 프로세스 종료
lsof -ti:8000 | xargs kill -9

# 또는 다른 포트 사용
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8001
```

## 📝 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 🤝 기여

기여를 환영합니다! 이슈를 열거나 풀 리퀘스트를 제출해주세요.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해주세요.

## 🤖 Dev Agent Kit 통합

이 프로젝트는 [dev-agent-kit](https://github.com/saewookkangboy/dev-agent-kit)의 기능을 통합하여 개발 워크플로우를 향상시킵니다.

### 주요 기능
- **Spec-kit**: 사양 문서 관리 (`.spec-kit/`)
- **To-do Management**: 작업 관리 (`.project-data/todos.json`)
- **Agent Roles**: 역할 기반 개발 지원
- **SEO/AI SEO/GEO 최적화**: 웹 최적화 도구
- **Cursor 서브에이전트**: 통합 개발 에이전트 (`.cursor/agents/dev-agent-kit.md`)

자세한 내용은 [Dev Agent Kit 통합 가이드](./docs/DEV_AGENT_KIT_INTEGRATION.md)를 참고하세요.

## 🔮 향후 개선 사항

- [ ] 분석 결과 시각화 (차트, 그래프)
- [ ] 분석 히스토리 저장
- [ ] 결과 다운로드 기능
- [ ] 분석 결과 비교 기능
- [ ] 워드 클라우드 생성
- [ ] 다국어 지원
- [ ] 사용자 인증 및 세션 관리

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-28
