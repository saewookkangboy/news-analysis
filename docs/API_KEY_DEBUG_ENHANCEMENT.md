# API 키 디버깅 강화 및 수정 사항

## 문제점
Vercel 배포 환경에서 API 키가 설정되어 있음에도 불구하고 "기본 분석 모드"로 실행되는 문제가 발생했습니다.

## 원인 분석
1. API 키 확인 로직이 단순히 `bool()` 체크만 수행하여 빈 문자열이나 공백만 있는 경우도 True로 판단
2. 환경 변수와 Settings 인스턴스 간의 동기화 문제
3. 상세한 로깅 부족으로 문제 진단이 어려움

## 해결 방법

### 1. API 키 확인 로직 강화
- 빈 문자열 및 공백 체크 추가: `len(api_key.strip()) > 0`
- 여러 소스에서 확인: `os.getenv()` → `settings.OPENAI_API_KEY`
- 상세한 로깅 추가

### 2. 수정된 파일

#### backend/services/target_analyzer.py

**변경 사항:**
1. `analyze_target()` 함수:
   - API 키 확인 로직 강화 (빈 문자열 체크 추가)
   - 상세한 로깅 추가 (환경 변수, Settings 값, 최종 결정 값 모두 로깅)
   
2. `_analyze_with_openai()` 함수:
   - API 키 확인 로직 강화
   - API 키 소스 로깅 추가
   
3. `_analyze_with_gemini()` 함수:
   - API 키 확인 로직 강화
   - API 키 소스 로깅 추가
   
4. `_analyze_basic()` 함수:
   - API 키 상태 확인 로직 강화

**수정 패턴:**
```python
# 이전
openai_key = settings.OPENAI_API_KEY or os.getenv('OPENAI_API_KEY')
has_openai_key = bool(openai_key)

# 수정 후
openai_env = os.getenv('OPENAI_API_KEY')
openai_settings = getattr(settings, 'OPENAI_API_KEY', None)
openai_key = openai_env or openai_settings
has_openai_key = bool(openai_key and len(openai_key.strip()) > 0)
```

## 로깅 개선

### 이전 로깅
```
API 키 상태 - OpenAI: 설정됨, Gemini: 설정됨
```

### 개선된 로깅
```
============================================================
API 키 상태 확인 (상세)
os.getenv('OPENAI_API_KEY'): ✅ 설정됨
  - 길이: 167 문자, 시작: sk-svcacct...
settings.OPENAI_API_KEY: ✅ 설정됨
  - 길이: 167 문자, 시작: sk-svcacct...
최종 openai_key: ✅ 설정됨
os.getenv('GEMINI_API_KEY'): ✅ 설정됨
  - 길이: 39 문자, 시작: AIzaSyCPbp...
settings.GEMINI_API_KEY: ✅ 설정됨
  - 길이: 39 문자, 시작: AIzaSyCPbp...
최종 gemini_key: ✅ 설정됨
============================================================
```

## 검증 방법

### 1. Vercel 배포 후 로그 확인
배포 후 Vercel 로그에서 다음을 확인:

1. **환경 변수 로딩 확인** (backend/config.py에서):
   ```
   ============================================================
   환경 변수 로딩 상태 확인
   환경: Vercel (배포)
   os.getenv('OPENAI_API_KEY'): ✅ 설정됨
   settings.OPENAI_API_KEY: ✅ 설정됨
   ============================================================
   ```

2. **API 키 상태 확인** (target_analyzer.py에서):
   ```
   ============================================================
   API 키 상태 확인 (상세)
   os.getenv('OPENAI_API_KEY'): ✅ 설정됨
   최종 openai_key: ✅ 설정됨
   ============================================================
   ```

3. **API 호출 확인**:
   ```
   OpenAI API 클라이언트 초기화 중... (모델: gpt-4o-mini)
   API 키 소스: 환경 변수, 길이: 167 문자
   ✅ OpenAI API 분석 성공
   ```

### 2. API 테스트
분석 요청 시 응답의 `api_key_status` 확인:
```json
{
  "api_key_status": {
    "openai_configured": true,
    "gemini_configured": true,
    "message": "✅ 모든 API 키가 설정되어 있습니다."
  }
}
```

## 문제 해결 체크리스트

- [ ] Vercel Dashboard에서 환경 변수 설정 확인
- [ ] 배포 후 로그에서 환경 변수 로딩 확인
- [ ] API 키 상태 확인 로그 확인
- [ ] 실제 AI 분석이 수행되는지 확인 (기본 분석 모드가 아닌지)
- [ ] API 응답의 `api_key_status` 확인

## 다음 단계

1. **재배포**
   - 수정 사항 반영 후 재배포

2. **로그 확인**
   - 배포 후 Vercel 로그에서 상세한 API 키 상태 확인
   - 문제가 있으면 로그를 기반으로 추가 수정

3. **테스트**
   - 실제 분석 요청을 보내고 AI 분석이 정상적으로 수행되는지 확인
