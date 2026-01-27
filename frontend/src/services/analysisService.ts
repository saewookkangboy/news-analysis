/**
 * Analysis API Service
 * 실제 백엔드 분석 API와 통신하는 서비스
 */

// API 기본 URL 설정 (배포 환경 자동 감지)
const getApiBaseUrl = (): string => {
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

// 공통 응답 타입
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  detail?: string;
  message?: string;
}

// API 호출 헬퍼 함수
async function apiCall<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    
    console.log(`[Analysis API] ${options.method || 'GET'} ${url}`);
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      credentials: 'same-origin',
    });

    console.log(`[Analysis API Response] ${response.status} ${response.statusText}`);

    if (!response.ok) {
      let errorData: any = {};
      try {
        errorData = await response.json();
      } catch {
        errorData = { message: await response.text() };
      }
      
      const errorMessage = errorData.detail || errorData.message || errorData.error || `HTTP ${response.status}: ${response.statusText}`;
      console.error(`[Analysis API Error] ${endpoint}:`, errorMessage);
      
      return {
        success: false,
        error: errorMessage,
        detail: errorMessage,
      };
    }

    const data = await response.json();
    console.log(`[Analysis API Success] ${endpoint}:`, data);
    
    // FastAPI 응답 형식에 맞춰 처리
    if (data.success !== undefined) {
      return data as ApiResponse<T>;
    }
    
    // 직접 데이터를 반환하는 경우
    return {
      success: true,
      data: data as T,
    };
  } catch (error) {
    console.error(`[Analysis API Exception] ${endpoint}:`, error);
    const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.';
    
    // 네트워크 오류인 경우
    if (error instanceof TypeError && error.message.includes('fetch')) {
      return {
        success: false,
        error: '네트워크 연결을 확인해주세요. API 서버에 연결할 수 없습니다.',
        detail: '네트워크 연결을 확인해주세요. API 서버에 연결할 수 없습니다.',
      };
    }
    
    return {
      success: false,
      error: errorMessage,
      detail: errorMessage,
    };
  }
}

// 분석 결과 타입
export interface TargetAnalysisResult {
  target_keyword: string;
  target_type: string;
  analysis: {
    overview?: any;
    insights?: any;
    recommendations?: any;
  };
  sentiment?: any;
  context?: any;
  tone?: any;
  recommendations?: any;
  progress_info?: {
    current_step?: string;
    progress?: number;
  };
}

export interface AnalysisRequest {
  target_keyword: string;
  target_type?: 'keyword' | 'audience' | 'competitor';
  additional_context?: string;
  use_gemini?: boolean;
  start_date?: string;
  end_date?: string;
  include_sentiment?: boolean;
  include_recommendations?: boolean;
}

/**
 * Analysis Service 클래스
 */
export class AnalysisService {
  /**
   * 타겟 분석 수행
   */
  static async analyzeTarget(
    request: AnalysisRequest
  ): Promise<ApiResponse<TargetAnalysisResult>> {
    return apiCall<TargetAnalysisResult>('/target/analyze', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * 타겟 분석 수행 (GET 방식)
   */
  static async analyzeTargetGet(
    target_keyword: string,
    target_type: string = 'keyword',
    additional_context?: string,
    use_gemini: boolean = false
  ): Promise<ApiResponse<TargetAnalysisResult>> {
    const params = new URLSearchParams({
      target_keyword,
      target_type,
      use_gemini: use_gemini.toString(),
    });
    if (additional_context) {
      params.append('additional_context', additional_context);
    }
    
    return apiCall<TargetAnalysisResult>(`/target/analyze?${params.toString()}`);
  }

  /**
   * 종합 분석 수행
   */
  static async comprehensiveAnalysis(
    target_keyword: string,
    target_type: string = 'keyword',
    additional_context?: string,
    use_gemini: boolean = false,
    analysis_depth: string = 'standard'
  ): Promise<ApiResponse<TargetAnalysisResult>> {
    return apiCall<TargetAnalysisResult>('/analysis/comprehensive', {
      method: 'POST',
      body: JSON.stringify({
        target_keyword,
        target_type,
        additional_context,
        use_gemini,
        analysis_depth,
      }),
    });
  }

  /**
   * 타겟 분석 수행 (스트리밍 방식 - 문장 단위 실시간 출력)
   */
  static async analyzeTargetStream(
    request: AnalysisRequest,
    onSentence: (sentence: string, section: string) => void,
    onProgress?: (progress: number, message: string) => void,
    onComplete?: (data: TargetAnalysisResult) => void,
    onError?: (error: string) => void
  ): Promise<void> {
    try {
      const url = `${API_BASE_URL}/target/analyze/stream`;
      
      console.log(`[Analysis API Stream] POST ${url}`);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorText = await response.text();
        let errorData: any = {};
        try {
          errorData = JSON.parse(errorText);
        } catch {
          errorData = { message: errorText };
        }
        
        const errorMessage = errorData.detail || errorData.message || errorData.error || `HTTP ${response.status}: ${response.statusText}`;
        console.error(`[Analysis API Stream Error]:`, errorMessage);
        
        if (onError) {
          onError(errorMessage);
        }
        return;
      }

      // 스트리밍 응답 읽기
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      if (!reader) {
        throw new Error('스트리밍 응답을 읽을 수 없습니다.');
      }

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }

        // 디코딩 및 버퍼에 추가
        buffer += decoder.decode(value, { stream: true });
        
        // 줄 단위로 분리하여 처리
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // 마지막 불완전한 줄은 버퍼에 유지

        for (const line of lines) {
          if (!line.trim()) {
            continue;
          }

          try {
            const chunk = JSON.parse(line);
            
            // 문장 타입 처리
            if (chunk.type === 'sentence') {
              onSentence(chunk.content, chunk.section || 'executive_summary');
            }
            // 진행 상황 처리
            else if (chunk.type === 'progress' && onProgress) {
              onProgress(chunk.progress || 0, chunk.message || '');
            }
            // 완료 처리
            else if (chunk.type === 'complete') {
              if (onComplete && chunk.data) {
                onComplete(chunk.data);
              }
              return;
            }
            // 오류 처리
            else if (chunk.type === 'error') {
              if (onError) {
                onError(chunk.message || '알 수 없는 오류가 발생했습니다.');
              }
              return;
            }
          } catch (parseError) {
            console.warn(`[Analysis API Stream] JSON 파싱 실패:`, line, parseError);
          }
        }
      }

      // 버퍼에 남은 데이터 처리
      if (buffer.trim()) {
        try {
          const chunk = JSON.parse(buffer);
          if (chunk.type === 'sentence') {
            onSentence(chunk.content, chunk.section || 'executive_summary');
          } else if (chunk.type === 'complete' && onComplete && chunk.data) {
            onComplete(chunk.data);
          }
        } catch (parseError) {
          console.warn(`[Analysis API Stream] 버퍼 파싱 실패:`, buffer, parseError);
        }
      }

    } catch (error) {
      console.error(`[Analysis API Stream Exception]:`, error);
      const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.';
      
      if (onError) {
        onError(errorMessage);
      }
    }
  }
}
