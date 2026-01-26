# 배포 환경 API 호출 문제 해결

## 문제
- localhost에서는 정상 작동하지만 배포 환경에서 분석 결과가 출력되지 않음
- 브라우저 콘솔 오류 발생

## 해결 사항

### 1. API URL 자동 감지
- `backend/main.py`의 HTML에서 API 호출 시 `window.location.origin`을 사용하여 현재 도메인 자동 감지
- 배포 환경과 로컬 환경 모두에서 올바르게 작동

### 2. 오류 처리 개선
- API 호출 실패 시 상세한 오류 메시지 표시
- 네트워크 오류, CORS 오류 등 구분하여 처리
- 콘솔 로그 추가로 디버깅 용이

### 3. DashboardService 생성
- `frontend/src/services/dashboardService.ts` 생성
- 배포 환경에서 API URL 자동 감지
- 상세한 오류 처리 및 로깅

### 4. AnalysisService 생성
- `frontend/src/services/analysisService.ts` 생성
- 실제 백엔드 분석 API와 통신
- 타겟 분석, 종합 분석 등 지원

### 5. 오류 핸들러 개선
- 브라우저 확장 프로그램 오류 필터링
- 네트워크 오류, CORS 오류 등 구분 처리
- 사용자 친화적인 오류 메시지

## 주요 변경 사항

### backend/main.py
```javascript
// 변경 전
const response = await fetch('/api/target/analyze', {...});

// 변경 후
const apiBaseUrl = window.location.origin;
const apiUrl = `${apiBaseUrl}/api/target/analyze`;
const response = await fetch(apiUrl, {...});
```

### frontend/src/services/dashboardService.ts
- 배포 환경 자동 감지
- API URL 자동 설정
- 상세한 오류 처리

### frontend/src/utils/errorHandler.ts
- 네트워크 오류 구분
- CORS 오류 처리
- 사용자 친화적인 메시지

## 테스트 방법

1. **로컬 테스트**
   ```bash
   # 백엔드 실행
   cd backend
   uvicorn main:app --reload
   
   # 브라우저에서 http://localhost:8000 접속
   # 분석 기능 테스트
   ```

2. **배포 환경 테스트**
   - Vercel에 배포 후
   - 브라우저 콘솔에서 API 호출 로그 확인
   - 네트워크 탭에서 API 요청/응답 확인

## 디버깅

배포 환경에서 문제가 발생하면:

1. **브라우저 콘솔 확인**
   - `[API Call]` 로그로 API URL 확인
   - `[API Response]` 로그로 응답 상태 확인
   - `[API Error]` 로그로 오류 내용 확인

2. **네트워크 탭 확인**
   - API 요청이 올바른 URL로 전송되는지 확인
   - 응답 상태 코드 확인
   - CORS 오류 여부 확인

3. **Vercel 로그 확인**
   - 서버 사이드 오류 확인
   - 환경 변수 설정 확인

## 추가 개선 사항

- API 호출 재시도 로직 추가 가능
- 오프라인 모드 지원 가능
- 캐싱 전략 개선 가능
