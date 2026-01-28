/**
 * Dashboard API Service
 * 백엔드 API와 통신하는 서비스
 */

import { ApiResponse, ApiCallOptions } from '../types/api';

// API 기본 URL 설정 (배포 환경 자동 감지)
const getApiBaseUrl = (): string => {
  // 배포 환경에서는 상대 경로 사용 (같은 도메인)
  if (typeof window !== 'undefined') {
    // 프로덕션 환경 (Vercel 배포)
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
      // Vercel에서는 같은 도메인에서 API를 제공하므로 상대 경로 사용
      return window.location.origin + '/api';
    }
    // 로컬 개발 환경
    return 'http://localhost:8000/api';
  }
  return '/api';
};

const API_BASE_URL = getApiBaseUrl();

// 디버깅을 위한 로그
if (typeof window !== 'undefined') {
  console.log('API Base URL:', API_BASE_URL);
}

// API 호출 헬퍼 함수 (타임아웃 및 재시도 로직 포함)
async function apiCall<T>(
    endpoint: string,
    options: ApiCallOptions = {},
    retries: number = options.retries ?? 3
): Promise<ApiResponse<T>> {
  const timeout = options.timeout ?? 30000; // 기본 30초 타임아웃
  const retryDelay = options.retryDelay ?? 1000; // 기본 1초 재시도 지연
  
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    
    console.log(`[API Call] ${options.method || 'GET'} ${url}`);
    
    // AbortController를 사용한 타임아웃 처리
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        // CORS 설정
        credentials: 'same-origin',
      });

      clearTimeout(timeoutId);
      console.log(`[API Response] ${response.status} ${response.statusText}`);

      if (!response.ok) {
        let errorData: any = {};
        try {
          errorData = await response.json();
        } catch {
          errorData = { message: await response.text() };
        }
        
        const errorMessage = errorData.detail || errorData.message || errorData.error || `HTTP ${response.status}: ${response.statusText}`;
        console.error(`[API Error] ${endpoint}:`, errorMessage);
        
        return {
          success: false,
          error: errorMessage,
        };
      }

      const data = await response.json();
      console.log(`[API Success] ${endpoint}:`, data);
      
      // FastAPI 응답 형식에 맞춰 처리
      if (data.success !== undefined) {
        return data as ApiResponse<T>;
      }
      
      // 직접 데이터를 반환하는 경우
      return {
        success: true,
        data: data as T,
      };
    } catch (fetchError) {
      clearTimeout(timeoutId);
      
      // 네트워크 오류 또는 타임아웃인 경우 재시도
      if (retries > 0 && (
        fetchError instanceof TypeError || 
        fetchError instanceof DOMException ||
        (fetchError as any)?.name === 'AbortError'
      )) {
        console.warn(`[API] 재시도 중... (남은 횟수: ${retries - 1})`);
        await new Promise(resolve => setTimeout(resolve, retryDelay * (4 - retries)));
        return apiCall<T>(endpoint, options, retries - 1);
      }
      
      throw fetchError;
    }
  } catch (error) {
    console.error(`[API Exception] ${endpoint}:`, error);
    const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.';
    
    // 네트워크 오류인 경우
    if (error instanceof TypeError && error.message.includes('fetch')) {
      return {
        success: false,
        error: '네트워크 연결을 확인해주세요. API 서버에 연결할 수 없습니다.',
      };
    }
    
    // 타임아웃 오류
    if (error instanceof DOMException || (error as any)?.name === 'AbortError') {
      return {
        success: false,
        error: '요청 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.',
      };
    }
    
    return {
      success: false,
      error: errorMessage,
    };
  }
}

// 타입 정의
export type CategoryType = 'all' | 'ecommerce' | 'lead_generation' | 'general_website';

export interface DashboardOverview {
  total_events: number;
  total_users: number;
  conversion_rate: number;
  revenue?: number;
  total_sessions?: number;
  total_conversions?: number;
  average_conversion_rate?: number;
  total_revenue?: number;
  average_order_value?: number;
  total_leads?: number;
  lead_conversion_rate?: number;
  total_page_views?: number;
  unique_visitors?: number;
}

export interface FunnelData {
  step: string;
  count: number;
  percentage: number;
}

export interface KPITrend {
  date: string;
  value: number;
  metric: string;
}

export interface RecentEvent {
  id: string;
  timestamp: string;
  event_type: string;
  user_id: string;
  properties?: Record<string, any>;
}

export interface ScenarioPerformance {
  scenario_id: string;
  name: string;
  conversion_rate: number;
  total_events: number;
}

export interface CategoryMetrics {
  ecommerce?: {
    revenue: number;
    orders: number;
    average_order_value: number;
  };
  lead_generation?: {
    leads: number;
    conversion_rate: number;
  };
  general_website?: {
    page_views: number;
    unique_visitors: number;
  };
}

// Dashboard Service 클래스
export class DashboardService {
  /**
   * 대시보드 개요 데이터 가져오기
   */
  static async getOverview(category: CategoryType = 'all'): Promise<ApiResponse<DashboardOverview>> {
    return apiCall<DashboardOverview>(`/dashboard/overview?category=${category}`);
  }

  /**
   * 퍼널 데이터 가져오기
   */
  static async getFunnels(
    scenarioId?: string,
    category: CategoryType = 'all'
  ): Promise<ApiResponse<FunnelData[]>> {
    const params = new URLSearchParams();
    if (scenarioId) params.append('scenario_id', scenarioId);
    params.append('category', category);
    return apiCall<FunnelData[]>(`/dashboard/funnels?${params.toString()}`);
  }

  /**
   * KPI 트렌드 데이터 가져오기
   */
  static async getKPITrends(
    metric?: string,
    startDate?: string,
    category: CategoryType = 'all'
  ): Promise<ApiResponse<KPITrend[]>> {
    const params = new URLSearchParams();
    if (metric) params.append('metric', metric);
    if (startDate) params.append('start_date', startDate);
    params.append('category', category);
    return apiCall<KPITrend[]>(`/dashboard/kpi-trends?${params.toString()}`);
  }

  /**
   * 최근 이벤트 가져오기
   */
  static async getRecentEvents(
    limit?: number,
    category: CategoryType = 'all'
  ): Promise<ApiResponse<RecentEvent[]>> {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit.toString());
    params.append('category', category);
    return apiCall<RecentEvent[]>(`/dashboard/recent-events?${params.toString()}`);
  }

  /**
   * 시나리오 성능 데이터 가져오기
   */
  static async getScenarioPerformance(
    category: CategoryType = 'all'
  ): Promise<ApiResponse<ScenarioPerformance[]>> {
    return apiCall<ScenarioPerformance[]>(`/dashboard/scenario-performance?category=${category}`);
  }

  /**
   * 카테고리별 메트릭 가져오기
   */
  static async getCategoryMetrics(
    category: CategoryType = 'all'
  ): Promise<ApiResponse<CategoryMetrics>> {
    return apiCall<CategoryMetrics>(`/dashboard/category-metrics?category=${category}`);
  }
}
