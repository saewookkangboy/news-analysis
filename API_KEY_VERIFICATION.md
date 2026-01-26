# API 키 검증 가이드

## 검증 결과 요약

### 로컬 환경 (.env 파일)
- ✅ **OPENAI_API_KEY**: 설정됨 (167 문자)
- ✅ **GEMINI_API_KEY**: 설정됨 (39 문자)
- ✅ **Settings 인스턴스**: 정상 로딩 확인

### Vercel 배포 환경 확인 방법

#### 1. Vercel Dashboard에서 확인
1. [Vercel Dashboard](https://vercel.com/dashboard) 접속
2. 프로젝트 선택
3. **Settings** > **Environment Variables** 이동
4. 다음 변수들이 설정되어 있는지 확인:
   - `OPENAI_API_KEY` (Production, Preview, Development)
   - `GEMINI_API_KEY` (Production, Preview, Development)

#### 2. 배포 후 로그 확인
배포 후 Vercel 로그에서 다음 메시지를 확인하세요:

```
============================================================
환경 변수 로딩 상태 확인
OPENAI_API_KEY: 설정됨
GEMINI_API_KEY: 설정됨
OPENAI_MODEL: gpt-4o-mini
GEMINI_MODEL: gemini-2.5-flash-preview
============================================================
```

#### 3. API 엔드포인트로 확인
배포된 사이트에서 다음 엔드포인트를 호출하여 확인:

```bash
# 헬스 체크
curl https://your-project.vercel.app/health

# API 키 상태 확인 (분석 요청 시 자동으로 포함됨)
curl -X POST https://your-project.vercel.app/api/target/analyze \
  -H "Content-Type: application/json" \
  -d '{"target_keyword": "테스트", "target_type": "keyword"}'
```

응답의 `api_key_status` 필드를 확인:
```json
{
  "success": true,
  "data": {
    "api_key_status": {
      "openai_configured": true,
      "gemini_configured": true,
      "message": "✅ 모든 API 키가 설정되어 있습니다."
    }
  }
}
```

## 환경 변수 설정 체크리스트

### Vercel Dashboard 설정
- [ ] `OPENAI_API_KEY` 설정됨
- [ ] `GEMINI_API_KEY` 설정됨
- [ ] Production 환경에 설정됨
- [ ] Preview 환경에 설정됨 (선택사항)
- [ ] Development 환경에 설정됨 (선택사항)

### .env 파일 설정 (로컬)
- [ ] `OPENAI_API_KEY` 설정됨
- [ ] `GEMINI_API_KEY` 설정됨
- [ ] `.env` 파일이 `.gitignore`에 포함되어 있음 (보안)

## 문제 해결

### 문제 1: Vercel에서 API 키가 로딩되지 않음

**원인:**
- 환경 변수가 설정되지 않음
- 환경 변수 이름이 잘못됨
- 배포 후 환경 변수를 추가했지만 재배포하지 않음

**해결:**
1. Vercel Dashboard에서 환경 변수 확인
2. 환경 변수 추가/수정 후 **재배포** 필수
3. 변수 이름 확인: `OPENAI_API_KEY`, `GEMINI_API_KEY` (대소문자 구분)

### 문제 2: 로컬에서는 작동하지만 Vercel에서는 작동하지 않음

**원인:**
- Vercel 환경 변수가 설정되지 않음
- `.env` 파일은 Vercel에서 사용되지 않음

**해결:**
1. Vercel Dashboard에서 환경 변수 설정
2. 재배포

### 문제 3: API 키가 설정되었는데도 "기본 분석 모드"로 실행됨

**원인:**
- 환경 변수가 제대로 로딩되지 않음
- Settings 인스턴스가 환경 변수를 읽지 못함

**해결:**
1. Vercel 로그에서 환경 변수 로딩 메시지 확인
2. `backend/config.py`의 로깅 확인
3. 환경 변수 이름 확인 (대소문자, 언더스코어)

## 검증 스크립트 사용

로컬에서 검증:
```bash
python3 scripts/verify_api_keys.py
```

이 스크립트는 다음을 확인합니다:
1. 환경 변수 직접 확인
2. Settings 인스턴스 확인
3. .env 파일 확인
4. Vercel 환경 확인
5. API 키 일치 여부

## Vercel 배포 후 확인

배포 후 다음을 확인하세요:

1. **Vercel 로그 확인**
   - Deployments > 최신 배포 > Logs
   - 환경 변수 로딩 메시지 확인

2. **API 테스트**
   - 분석 요청 시 `api_key_status` 확인
   - 실제 AI 분석이 수행되는지 확인

3. **응답 확인**
   - "기본 분석 모드" 메시지가 없어야 함
   - 상세한 분석 결과가 표시되어야 함

## 보안 주의사항

⚠️ **중요**: 
- `.env` 파일은 절대 Git에 커밋하지 마세요
- `.gitignore`에 `.env`가 포함되어 있는지 확인하세요
- API 키는 공개 저장소에 노출되지 않도록 주의하세요
