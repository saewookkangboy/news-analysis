# Vercel 환경 변수 설정 체크리스트

## ✅ 완료된 항목

### 로컬 환경 (.env 파일)
- ✅ OPENAI_API_KEY: 설정됨 (167 문자)
- ✅ GEMINI_API_KEY: 설정됨 (39 문자)
- ✅ OPENAI_MODEL: gpt-4o-mini
- ✅ GEMINI_MODEL: gemini-2.5-flash-preview (일치 확인됨)
- ✅ Settings 인스턴스: 정상 로딩

## 📋 Vercel Dashboard 설정 체크리스트

### 필수 환경 변수
다음 변수들을 Vercel Dashboard에 설정하세요:

#### 1. OPENAI_API_KEY
- **값**: `.env` 파일의 `OPENAI_API_KEY` 값과 동일
- **형식**: `sk-svcacct-...` (167 문자)
- **환경**: Production, Preview, Development 모두 설정 권장

#### 2. GEMINI_API_KEY
- **값**: `.env` 파일의 `GEMINI_API_KEY` 값과 동일
- **형식**: `AIzaSyCPbp...` (39 문자)
- **환경**: Production, Preview, Development 모두 설정 권장

### 선택적 환경 변수
- `OPENAI_MODEL`: `gpt-4o-mini` (기본값 사용 가능)
- `GEMINI_MODEL`: `gemini-2.5-flash-preview` (기본값 사용 가능)

## 🔍 Vercel 설정 확인 방법

### 1. Vercel Dashboard에서 확인
1. [Vercel Dashboard](https://vercel.com/dashboard) 접속
2. 프로젝트 선택
3. **Settings** 탭 클릭
4. **Environment Variables** 섹션 확인
5. 다음 변수들이 있는지 확인:
   ```
   OPENAI_API_KEY = your_openai_api_key_here
   GEMINI_API_KEY = your_gemini_api_key_here
   ```

### 2. 배포 후 로그 확인
배포 후 Vercel 로그에서 다음 메시지를 확인:

```
============================================================
환경 변수 로딩 상태 확인
환경: Vercel (배포)
OPENAI_API_KEY: ✅ 설정됨
  - 길이: 167 문자
  - 시작: sk-svcacct...
GEMINI_API_KEY: ✅ 설정됨
  - 길이: 39 문자
  - 시작: AIzaSyCPbp...
OPENAI_MODEL: gpt-4o-mini
GEMINI_MODEL: gemini-2.5-flash-preview
============================================================
```

### 3. API 테스트
배포된 사이트에서 분석 요청을 보내고 응답 확인:

```bash
curl -X POST https://your-project.vercel.app/api/target/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "target_keyword": "테스트",
    "target_type": "keyword",
    "use_gemini": true
  }'
```

응답에서 `api_key_status` 확인:
- `openai_configured: true` ✅
- `gemini_configured: true` ✅

## ⚠️ 중요 사항

### 환경 변수 추가 후 필수 작업
1. ✅ 환경 변수 설정
2. ✅ **재배포** (중요!)
3. ✅ 배포 로그 확인
4. ✅ API 테스트

### 주의사항
- 환경 변수 이름은 **대소문자 정확히** 일치해야 함
- `OPENAI_API_KEY` (O, A, K는 대문자)
- `GEMINI_API_KEY` (G, A, K는 대문자)
- 공백이나 특수문자 없이 정확히 입력

## 🔒 보안 확인

- [x] `.env` 파일이 `.gitignore`에 포함됨
- [x] `.env` 파일이 Git에 커밋되지 않음
- [ ] Vercel 환경 변수가 올바르게 설정됨 (확인 필요)
- [ ] API 키가 공개 저장소에 노출되지 않음

## 📊 현재 상태 요약

| 항목 | 로컬 (.env) | Vercel (확인 필요) |
|------|------------|-------------------|
| OPENAI_API_KEY | ✅ 설정됨 | ⚠️ 확인 필요 |
| GEMINI_API_KEY | ✅ 설정됨 | ⚠️ 확인 필요 |
| OPENAI_MODEL | ✅ gpt-4o-mini | ✅ 기본값 사용 |
| GEMINI_MODEL | ✅ gemini-2.5-flash-preview | ✅ 기본값 사용 |

## 다음 단계

1. **Vercel Dashboard 확인**
   - Environment Variables 섹션으로 이동
   - `OPENAI_API_KEY`, `GEMINI_API_KEY` 설정 확인
   - `.env` 파일의 값과 일치하는지 확인

2. **재배포**
   - 환경 변수 설정/수정 후 반드시 재배포

3. **검증**
   - 배포 로그에서 환경 변수 로딩 메시지 확인
   - 분석 요청 테스트
   - `api_key_status` 확인
