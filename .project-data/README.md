# 프로젝트 데이터

이 디렉토리는 dev-agent-kit의 프로젝트 관리 데이터를 저장합니다.

## 구조

```
.project-data/
├── README.md              # 이 파일
├── todos.json             # To-do 리스트 (Git에 포함되지 않음)
├── role-config.json       # Agent Role 설정
└── config.json            # 프로젝트 설정
```

## 파일 설명

### todos.json
To-do 작업 목록을 저장합니다. 형식:
```json
{
  "todos": [
    {
      "id": "unique-id",
      "title": "작업 제목",
      "description": "상세 설명",
      "priority": "high|medium|low",
      "status": "pending|in_progress|completed",
      "milestone": "마일스톤 이름",
      "dependencies": ["다른 작업 ID"],
      "created_at": "YYYY-MM-DD",
      "updated_at": "YYYY-MM-DD"
    }
  ]
}
```

### role-config.json
현재 활성화된 Agent Role 설정:
```json
{
  "current_role": "backend-developer",
  "roles": {
    "pm": "Project Manager",
    "frontend": "Frontend Developer",
    "backend": "Backend Developer",
    "server-db": "Server/DB Developer",
    "security": "Security Manager",
    "ui-ux": "UI/UX Designer",
    "ai-researcher": "AI Marketing Researcher"
  }
}
```

### config.json
프로젝트 전역 설정:
```json
{
  "project_name": "news-trend-analyzer",
  "version": "1.0.0",
  "description": "AI 기반 뉴스 트렌드 분석 서비스",
  "tech_stack": {
    "backend": "FastAPI",
    "frontend": "React + TypeScript",
    "deployment": "Vercel"
  }
}
```

## 주의사항

- `todos.json`은 개인 작업 목록이므로 `.gitignore`에 포함됩니다.
- `role-config.json`과 `config.json`은 팀 공유를 위해 Git에 포함될 수 있습니다.
