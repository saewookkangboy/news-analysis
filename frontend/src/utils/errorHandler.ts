/**
 * 브라우저 콘솔 오류 처리 유틸리티
 * Chrome 확장 프로그램이나 서비스 워커 관련 오류를 필터링
 */

// 무시해도 되는 오류 패턴
const IGNORED_ERROR_PATTERNS = [
  /message channel closed/i,
  /asynchronous response/i,
  /Extension context invalidated/i,
  /Receiving end does not exist/i,
];

/**
 * 오류가 무시해도 되는 오류인지 확인
 */
export function isIgnorableError(error: Error | string): boolean {
  const errorMessage = typeof error === 'string' ? error : error.message;
  return IGNORED_ERROR_PATTERNS.some(pattern => pattern.test(errorMessage));
}

/**
 * 전역 오류 핸들러 설정
 * 브라우저 확장 프로그램 관련 오류를 필터링
 */
export function setupGlobalErrorHandler(): void {
  // Promise rejection 핸들러
  window.addEventListener('unhandledrejection', (event) => {
    const error = event.reason;
    const errorMessage = error?.message || error?.toString() || '';
    
    // 무시해도 되는 오류는 콘솔에 표시하지 않음
    if (isIgnorableError(errorMessage)) {
      event.preventDefault();
      return;
    }
    
    // 다른 오류는 기본 동작 유지
    console.error('Unhandled promise rejection:', error);
  });

  // 일반 오류 핸들러
  const originalErrorHandler = window.onerror;
  window.onerror = (message, source, lineno, colno, error) => {
    const errorMessage = message?.toString() || '';
    
    // 무시해도 되는 오류는 콘솔에 표시하지 않음
    if (isIgnorableError(errorMessage)) {
      return true; // 오류 처리 완료 표시
    }
    
    // 다른 오류는 기본 핸들러 호출
    if (originalErrorHandler) {
      return originalErrorHandler(message, source, lineno, colno, error);
    }
    
    return false;
  };
}

/**
 * API 호출 오류 처리
 */
export function handleApiError(error: unknown): string {
  if (error instanceof Error) {
    // 무시해도 되는 오류는 사용자에게 표시하지 않음
    if (isIgnorableError(error)) {
      return '';
    }
    
    // 네트워크 오류
    if (error.message.includes('fetch') || error.message.includes('network')) {
      return '네트워크 연결을 확인해주세요.';
    }
    
    // 타임아웃 오류
    if (error.message.includes('timeout')) {
      return '요청 시간이 초과되었습니다. 다시 시도해주세요.';
    }
    
    return error.message || '알 수 없는 오류가 발생했습니다.';
  }
  
  return '알 수 없는 오류가 발생했습니다.';
}
