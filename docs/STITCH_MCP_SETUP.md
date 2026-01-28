# Stitch MCP 서버 설정 가이드

Google Stitch를 MCP (Model Context Protocol) 형태로 Cursor에 연결하는 가이드입니다.

## 개요

Stitch는 Google Labs의 실험적인 AI 기반 디자인 도구로, 자연어 설명이나 이미지/와이어프레임으로부터 UI를 생성할 수 있습니다. 이 가이드는 dev-agent-kit 서브에이전트를 사용하여 Stitch를 MCP 서버로 연결하는 방법을 설명합니다.

## 사전 요구사항

1. **Google Cloud 계정**: Google Cloud 프로젝트가 필요합니다
2. **Node.js**: npx 명령어를 사용하기 위해 Node.js가 설치되어 있어야 합니다
3. **Google Cloud CLI**: gcloud 명령어 도구

## 설정 단계

### 1. Google Cloud 프로젝트 설정

```bash
# Google Cloud에 로그인
gcloud auth login

# 프로젝트 설정 (YOUR_PROJECT_ID를 실제 프로젝트 ID로 변경)
gcloud config set project YOUR_PROJECT_ID
gcloud auth application-default set-quota-project YOUR_PROJECT_ID

# Stitch API 활성화
gcloud beta services mcp enable stitch.googleapis.com
```

### 2. Application Default Credentials 설정

MCP 서버가 Google Cloud API에 접근할 수 있도록 인증 정보를 설정합니다:

```bash
gcloud auth application-default login
```

이 명령어는 브라우저를 열어 Google 계정으로 로그인하고, 애플리케이션 기본 인증 정보를 설정합니다.

### 3. 프로젝트 MCP 설정

프로젝트 루트의 `.cursor/mcp.json` 파일이 이미 생성되어 있습니다. 다음 내용을 확인하고 `YOUR_PROJECT_ID`를 실제 Google Cloud 프로젝트 ID로 변경하세요:

```json
{
  "mcpServers": {
    "stitch": {
      "command": "npx",
      "args": ["-y", "stitch-mcp"],
      "env": {
        "GOOGLE_CLOUD_PROJECT": "YOUR_PROJECT_ID"
      }
    }
  }
}
```

### 4. Cursor 재시작

MCP 설정을 적용하려면 Cursor를 재시작해야 합니다.

## 사용 방법

### 기본 워크플로우

1. **프로젝트 목록 조회**
   ```
   Stitch 프로젝트 목록을 보여줘
   ```

2. **디자인 컨텍스트 추출**
   ```
   Home Screen에서 디자인 컨텍스트를 추출해줘
   ```

3. **새 화면 생성**
   ```
   추출한 컨텍스트를 사용해서 Chat Screen을 생성해줘
   ```

### 사용 가능한 도구

#### 디자인 컨텍스트 & 생성
- `extract_design_context`: 화면에서 "Design DNA" (폰트, 색상, 레이아웃) 추출
- `generate_screen_from_text`: 프롬프트를 기반으로 새 화면 생성
- `fetch_screen_code`: 화면의 HTML/프론트엔드 코드 다운로드
- `fetch_screen_image`: 화면의 고해상도 스크린샷 다운로드

#### 프로젝트 관리
- `create_project`: 새로운 워크스페이스/프로젝트 폴더 생성
- `list_projects`: 사용 가능한 모든 Stitch 프로젝트 목록 조회
- `get_project`: 특정 프로젝트의 상세 정보 조회

#### 화면 관리
- `list_screens`: 특정 프로젝트 내의 모든 화면 목록 조회
- `get_screen`: 특정 화면의 메타데이터 조회

## 디자이너 플로우 (Pro Tip)

일관된 UI를 생성하기 위한 2단계 플로우:

1. **추출 (Extract)**: "Home Screen에서 디자인 컨텍스트를 가져와줘..."
2. **생성 (Generate)**: "그 컨텍스트를 사용해서 Chat Screen을 생성해줘..."

이렇게 하면 새 화면이 기존 디자인 시스템과 완벽하게 일치합니다.

## 문제 해결

### MCP 서버가 연결되지 않는 경우

1. **Google Cloud 프로젝트 ID 확인**
   - `.cursor/mcp.json` 파일에서 `GOOGLE_CLOUD_PROJECT` 환경 변수가 올바른지 확인

2. **인증 정보 확인**
   ```bash
   gcloud auth application-default print-access-token
   ```
   이 명령어가 토큰을 반환하면 인증이 정상적으로 설정된 것입니다.

3. **Stitch API 활성화 확인**
   ```bash
   gcloud services list --enabled | grep stitch
   ```

4. **Cursor 재시작**
   - MCP 설정 변경 후에는 반드시 Cursor를 재시작해야 합니다

### npx 명령어 오류

Node.js가 설치되어 있는지 확인:
```bash
node --version
npm --version
```

## 참고 자료

- [Stitch 공식 사이트](https://stitch.withgoogle.com/)
- [stitch-mcp GitHub 저장소](https://github.com/Kargatharaakash/stitch-mcp)
- [Google Cloud MCP 문서](https://docs.cloud.google.com/mcp/overview)
- [Model Context Protocol 문서](https://modelcontextprotocol.io/)

## 라이선스

stitch-mcp는 Apache 2.0 라이선스 하에 배포됩니다.
