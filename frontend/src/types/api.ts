/**
 * 공통 API 타입 정의
 * 모든 서비스에서 공유하는 타입
 */

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  detail?: string;
  message?: string;
}

/**
 * API 호출 옵션
 */
export interface ApiCallOptions extends RequestInit {
  timeout?: number; // 타임아웃 (밀리초, 기본값: 30000)
  retries?: number; // 재시도 횟수 (기본값: 3)
  retryDelay?: number; // 재시도 지연 시간 (밀리초, 기본값: 1000)
}
