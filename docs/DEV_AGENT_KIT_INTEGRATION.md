# Dev Agent Kit 통합 가이드

이 문서는 dev-agent-kit의 기능을 news-trend-analyzer 프로젝트에 통합한 내용을 설명합니다.

## 📋 개요

dev-agent-kit은 다음 기능들을 제공하는 통합 개발 에이전트 패키지입니다:
- Spec-kit: 사양 문서 관리
- To-do Management: 작업 관리
- Agent Roles: 역할 기반 개발
- AI 강화학습: Agent Lightning 통합
- SEO/AI SEO/GEO 최적화
- FastAPI 백엔드 개발 지원
- API 키 관리

## 🗂️ 프로젝트 구조

### Spec-kit 디렉토리 (`.spec-kit/`)
사양 문서를 관리하는 디렉토리입니다.

```
.spec-kit/
├── README.md              # Spec-kit 사용 가이드
├── requirements/          # 요구사항 문서
├── api/                   # API 스펙
├── architecture/          # 아키텍처 문서
├── features/              # 기능 스펙
└── changelog/             # 변경 이력
```

### 프로젝트 데이터 디렉토리 (`.project-data/`)
프로젝트 관리 데이터를 저장하는 디렉토리입니다.

```
.project-data/
├── README.md              # 데이터 구조 설명
├── todos.json             # To-do 리스트 (Git 제외)
├── role-config.json       # Agent Role 설정
└── config.json            # 프로젝트 설정
```

### Cursor 서브에이전트 (`.cursor/agents/`)
Cursor에서 사용할 서브에이전트 정의입니다.

```
.cursor/agents/
└── dev-agent-kit.md       # Dev Agent Kit 통합 에이전트
```

## 🚀 사용 방법

### 1. Cursor 서브에이전트 사용

Cursor에서 dev-agent-kit 서브에이전트를 사용하려면:

```
dev-agent-kit 서브에이전트를 사용하여 [작업 설명]
```

또는 자동으로 활성화됩니다:
- 프로젝트 관리 및 계획 수립
- 코드 리뷰 및 품질 개선
- SEO/최적화 작업
- 문서화 및 사양 정리
- 보안 감사 및 API 키 관리
- 역할별 전문 작업

### 2. Spec-kit으로 사양 문서 관리

#### 새 사양 문서 생성
```bash
# .spec-kit/features/ 디렉토리에 새 기능 스펙 작성
# .spec-kit/api/ 디렉토리에 API 스펙 작성
```

#### 표준 템플릿 사용
모든 사양 문서는 다음 구조를 따릅니다:
- 개요
- 요구사항
- 설계
- 구현
- 테스트
- 변경 이력

### 3. To-do 관리

`.project-data/todos.json` 파일을 직접 편집하거나, Cursor 서브에이전트를 통해 관리할 수 있습니다.

#### To-do 추가 예시
```json
{
  "id": "unique-id",
  "title": "작업 제목",
  "description": "상세 설명",
  "priority": "high",
  "status": "pending",
  "milestone": "phase-2",
  "dependencies": [],
  "created_at": "2026-01-28",
  "updated_at": "2026-01-28"
}
```

### 4. Agent Role 설정

`.project-data/role-config.json`에서 현재 역할을 확인하고 변경할 수 있습니다.

#### 사용 가능한 역할
- **pm**: Project Manager - 프로젝트 관리 및 조율
- **frontend**: Frontend Developer - React/TypeScript 개발
- **backend**: Backend Developer - FastAPI 백엔드 개발
- **server-db**: Server/DB Developer - 인프라 및 데이터베이스
- **security**: Security Manager - 보안 관리
- **ui-ux**: UI/UX Designer - 사용자 인터페이스 설계
- **ai-researcher**: AI Marketing Researcher - AI 기반 리서치

## 📝 워크플로우

### 새 기능 개발 시
1. Spec-kit에 기능 스펙 작성 (`.spec-kit/features/`)
2. To-do 항목 생성 (`.project-data/todos.json`)
3. 적절한 Agent Role 설정
4. 개발 진행
5. 문서 업데이트

### API 변경 시
1. API 스펙 업데이트 (`.spec-kit/api/`)
2. 변경 이력 기록 (`.spec-kit/changelog/`)
3. 코드 구현
4. 문서 동기화

### 코드 리뷰 시
1. dev-agent-kit 서브에이전트 활성화
2. 코드 분석 및 리뷰
3. 개선 사항 제안
4. To-do에 후속 작업 추가

## 🔧 통합 기능

### SEO/AI SEO/GEO 최적화
dev-agent-kit 서브에이전트를 통해 다음 최적화 작업을 수행할 수 있습니다:
- SEO 분석 및 최적화
- AI 기반 키워드 리서치
- 생성형 AI 검색 엔진 최적화 (GEO)
- 종합 최적화 리포트 (AIO)

### API 키 관리
- 안전한 API 키 저장 및 관리
- 토큰 캐싱 및 재사용 최적화
- 사용량 추적 및 모니터링

### FastAPI 백엔드 개발
- RESTful API 설계 및 구현
- 비동기 처리 최적화
- 자동 API 문서 생성

## 📚 관련 문서

- [프로젝트 구조](./PROJECT_STRUCTURE.md)
- [서비스 기능](./SERVICE_FEATURES.md)
- [배포 가이드](./VERCEL_DEPLOY.md)

## 🔗 참고 리소스

- [dev-agent-kit GitHub](https://github.com/saewookkangboy/dev-agent-kit)
- [Spec-kit](https://github.com/github/spec-kit)
- [Agent Lightning](https://github.com/microsoft/agent-lightning)

## 💡 팁

1. **자동 활성화**: dev-agent-kit 서브에이전트는 관련 작업 시 자동으로 활성화됩니다.
2. **문서 우선**: 새 기능 개발 전에 항상 Spec-kit에 문서를 작성하세요.
3. **To-do 추적**: 모든 작업을 To-do에 기록하여 진행 상황을 추적하세요.
4. **역할 전환**: 작업 유형에 따라 적절한 Agent Role을 설정하세요.

---

**Last Updated**: 2026-01-28
