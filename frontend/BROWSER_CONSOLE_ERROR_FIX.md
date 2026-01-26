# 브라우저 콘솔 오류 해결 방법

## 문제
```
Uncaught (in promise) Error: A listener indicated an asynchronous response by returning true, but the message channel closed before a response was received
```

## 원인
이 오류는 일반적으로 **Chrome 확장 프로그램**이나 **서비스 워커**와 관련된 문제입니다. 
- 브라우저 확장 프로그램이 페이지와 통신하려고 할 때 발생
- 서비스 워커가 메시지를 보내려고 할 때 발생
- 브라우저의 내부 통신 문제

**이 오류는 앱 코드의 문제가 아니라 브라우저 확장 프로그램의 문제입니다.**

## 해결 방법

### 1. 전역 오류 핸들러 추가
`frontend/src/utils/errorHandler.ts` 파일을 생성하여 무시해도 되는 오류를 필터링합니다.

### 2. App.tsx에서 오류 핸들러 설정
앱 시작 시 전역 오류 핸들러를 설정하여 브라우저 확장 프로그램 관련 오류를 필터링합니다.

### 3. API 오류 처리 개선
`handleApiError` 함수를 사용하여 실제 앱 오류와 브라우저 확장 프로그램 오류를 구분합니다.

## 무시해도 되는 오류 패턴
- `message channel closed`
- `asynchronous response`
- `Extension context invalidated`
- `Receiving end does not exist`

## 사용자 안내
이 오류는 앱 기능에 영향을 주지 않으며, 브라우저 확장 프로그램과의 통신 문제입니다.
- 앱은 정상적으로 작동합니다
- 콘솔에 오류가 표시되더라도 기능에는 문제가 없습니다
- 필요시 브라우저 확장 프로그램을 비활성화하여 확인할 수 있습니다

## 추가 디버깅
만약 실제 앱 기능에 문제가 있다면:
1. 브라우저 확장 프로그램을 모두 비활성화하고 테스트
2. 시크릿 모드에서 테스트
3. 다른 브라우저에서 테스트
4. 네트워크 탭에서 API 호출 확인
