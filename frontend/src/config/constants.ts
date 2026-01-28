/**
 * 프론트엔드 상수 설정
 * 하드코딩된 값들을 중앙 관리
 */

export const CACHE_CONFIG = {
  TTL: 30000, // 30초 캐시 유지 시간 (밀리초)
  MAX_SIZE: 100, // 최대 캐시 항목 수
} as const;

export const API_CONFIG = {
  TIMEOUT: 30000, // 30초 타임아웃 (밀리초)
  MAX_RETRIES: 3, // 최대 재시도 횟수
  RETRY_DELAY: 1000, // 재시도 지연 시간 (밀리초)
} as const;
