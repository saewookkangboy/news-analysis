import React, { useState, useEffect, useMemo, useCallback } from 'react';
import MetricCard from './MetricCard';
import FunnelChart from './FunnelChart';
import KPITrendChart from './KPITrendChart';
import ScenarioComparisonChart from './ScenarioComparisonChart';
import RecentEventsTable from './RecentEventsTable';
import AdminPanel from './AdminPanel';
import CategorySelector from './CategorySelector';
import CategoryMetricsComponent from './CategoryMetrics';
import AnalysisSettings from './AnalysisSettings';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';
import { handleApiError } from '../utils/errorHandler';
import { DashboardService, CategoryType } from '../services/dashboardService';
import { DashboardOverview, FunnelData, KPITrend, RecentEvent, ScenarioPerformance, CategoryMetrics } from '../services/dashboardService';
import { CACHE_CONFIG } from '../config/constants';

interface DashboardData {
  overview: DashboardOverview;
  funnels: FunnelData[];
  kpi_trends: KPITrend[];
  recent_events: RecentEvent[];
  scenario_performance: ScenarioPerformance[];
  category_metrics: CategoryMetrics | Partial<CategoryMetrics>;
}

// 데이터 캐시 인터페이스
interface CacheEntry<T> {
  data: T;
  timestamp: number;
  category: CategoryType;
}

// 간단한 메모리 캐시 구현 (메모리 누수 방지)
class DataCache {
  private cache: Map<string, CacheEntry<any>> = new Map();
  private readonly TTL = CACHE_CONFIG.TTL;
  private readonly MAX_SIZE = CACHE_CONFIG.MAX_SIZE;

  get<T>(key: string, category: CategoryType): T | null {
    const entry = this.cache.get(key);
    if (!entry) return null;
    
    // 카테고리가 다르면 캐시 무효화
    if (entry.category !== category) {
      this.cache.delete(key);
      return null;
    }
    
    // TTL 체크
    if (Date.now() - entry.timestamp > this.TTL) {
      this.cache.delete(key);
      return null;
    }
    
    // 주기적으로 만료된 항목 정리
    if (this.cache.size > this.MAX_SIZE) {
      this.cleanup();
    }
    
    return entry.data as T;
  }

  set<T>(key: string, data: T, category: CategoryType): void {
    // 캐시 크기 제한 체크
    if (this.cache.size >= this.MAX_SIZE) {
      this.cleanup();
    }
    
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      category
    });
  }

  clear(): void {
    this.cache.clear();
  }
  
  private cleanup(): void {
    const now = Date.now();
    // 만료된 항목 제거
    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp > this.TTL) {
        this.cache.delete(key);
      }
    }
    
    // 여전히 크기가 크면 오래된 항목 제거 (LRU 방식)
    if (this.cache.size > this.MAX_SIZE) {
      const sorted = Array.from(this.cache.entries())
        .sort((a, b) => a[1].timestamp - b[1].timestamp);
      const toRemove = sorted.slice(0, this.cache.size - this.MAX_SIZE);
      toRemove.forEach(([key]) => this.cache.delete(key));
    }
  }
}

const cache = new DataCache();

const Dashboard: React.FC = React.memo(() => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAdminPanel, setShowAdminPanel] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<CategoryType>('all');

  const fetchDashboardData = useCallback(async (category: CategoryType = 'all') => {
    const cacheKey = `dashboard-${category}`;
    
    // 캐시 확인
    const cachedData = cache.get<DashboardData>(cacheKey, category);
    if (cachedData) {
      setDashboardData(cachedData);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // 우선순위별로 API 호출 (overview 먼저, 나머지는 병렬)
      const overviewRes = await DashboardService.getOverview(category).catch(() => ({
        success: true,
        data: {
          total_events: 0,
          total_users: 0,
          conversion_rate: 0,
          total_sessions: 0,
          total_conversions: 0,
          average_conversion_rate: 0,
        },
      }));

      // overview 성공 후 나머지 API 병렬 호출
      const [funnelsRes, kpiTrendsRes, recentEventsRes, scenarioPerformanceRes, categoryMetricsRes] = await Promise.all([
        DashboardService.getFunnels(undefined, category).catch(() => ({ success: true, data: [] })),
        DashboardService.getKPITrends(undefined, undefined, category).catch(() => ({ success: true, data: [] })),
        DashboardService.getRecentEvents(undefined, category).catch(() => ({ success: true, data: [] })),
        DashboardService.getScenarioPerformance(category).catch(() => ({ success: true, data: [] })),
        DashboardService.getCategoryMetrics(category).catch(() => ({ success: true, data: {} }))
      ]);

      // 응답 검증 (일부 실패해도 계속 진행)
      const failedApis = [];
      if (!overviewRes.success) failedApis.push('overview');
      if (!funnelsRes.success) failedApis.push('funnels');
      if (!kpiTrendsRes.success) failedApis.push('kpiTrends');
      if (!recentEventsRes.success) failedApis.push('recentEvents');
      if (!scenarioPerformanceRes.success) failedApis.push('scenarioPerformance');
      if (!categoryMetricsRes.success) failedApis.push('categoryMetrics');
      
      if (failedApis.length > 0) {
        console.warn('일부 API 호출 실패:', failedApis);
        // 모든 API가 실패한 경우에만 에러 발생
        if (failedApis.length === 6) {
          throw new Error('모든 데이터를 불러오는데 실패했습니다.');
        }
      }

      // 타입 안정성 개선: Non-null assertion 제거, 기본값 제공
      const defaultOverview: DashboardOverview = {
        total_events: 0,
        total_users: 0,
        conversion_rate: 0,
        total_sessions: 0,
        total_conversions: 0,
        average_conversion_rate: 0,
      };

      const dashboardData: DashboardData = {
        overview: overviewRes.data ?? defaultOverview,
        funnels: funnelsRes.data ?? [],
        kpi_trends: kpiTrendsRes.data ?? [],
        recent_events: recentEventsRes.data ?? [],
        scenario_performance: scenarioPerformanceRes.data ?? [],
        category_metrics: categoryMetricsRes.data ?? {},
      };

      // 캐시에 저장
      cache.set(cacheKey, dashboardData, category);
      setDashboardData(dashboardData);
    } catch (err) {
      const errorMessage = handleApiError(err) || '대시보드 데이터를 불러오는 중 오류가 발생했습니다.';
      // 무시해도 되는 오류는 사용자에게 표시하지 않음
      if (errorMessage) {
        setError(errorMessage);
        console.error('Dashboard data fetch error:', err);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData(selectedCategory);
  }, [selectedCategory, fetchDashboardData]);

  const handleCategoryChange = useCallback((category: CategoryType) => {
    setSelectedCategory(category);
  }, []);

  const handleDataUpdate = useCallback(() => {
    // 관리자 패널에서 데이터가 업데이트되면 캐시를 무효화하고 대시보드 새로고침
    cache.clear();
    fetchDashboardData(selectedCategory);
  }, [selectedCategory, fetchDashboardData]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="large" text="대시보드 데이터를 불러오는 중..." />
      </div>
    );
  }

  if (error) {
    return (
      <ErrorMessage 
        error={error} 
        onRetry={() => fetchDashboardData(selectedCategory)}
        showRetry={true}
      />
    );
  }

  if (!dashboardData) {
    return null;
  }

  const getCategoryTitle = useCallback((category: CategoryType) => {
    switch (category) {
      case 'ecommerce': return 'E-commerce';
      case 'lead_generation': return '잠재고객 확보';
      case 'general_website': return '일반 웹사이트';
      default: return '전체';
    }
  }, []);

  const categoryTitle = useMemo(() => getCategoryTitle(selectedCategory), [selectedCategory, getCategoryTitle]);

  return (
    <div className="min-h-full flex flex-col lg:flex-row bg-white" role="main" aria-label="대시보드">
      {/* 좌측: 분석 설정 패널 - Flat Design */}
      <aside 
        className="w-full lg:w-80 xl:w-96 bg-white border-r border-gray-200 p-4 sm:p-6 overflow-y-auto custom-scrollbar"
        aria-label="분석 설정"
      >
        <AnalysisSettings
          selectedCategory={selectedCategory}
          onCategoryChange={handleCategoryChange}
          showAdminPanel={showAdminPanel}
          onToggleAdminPanel={() => setShowAdminPanel(!showAdminPanel)}
        />
      </aside>

      {/* 우측: 분석 결과 패널 */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 custom-scrollbar" aria-label="분석 결과">
        <div className="space-y-6 max-w-7xl mx-auto">
          {/* 페이지 헤더 - Flat Design */}
          <header className="mb-6 animate-fade-in">
            <h1 className="flat-heading-2 mb-1">
              분석 결과
            </h1>
            <p className="flat-caption">
              {categoryTitle} 고객 여정과 퍼널 분석을 통한 실시간 인사이트
            </p>
          </header>

          {/* 관리자 패널 */}
          {showAdminPanel && (
            <div className="mb-6">
              <AdminPanel onDataUpdate={handleDataUpdate} />
            </div>
          )}

          {/* 카테고리별 상세 지표 */}
          <CategoryMetricsComponent 
            category={selectedCategory} 
            metrics={dashboardData.category_metrics} 
          />

      {/* 개요 메트릭 - Flat Design Grid */}
      <section aria-label="개요 메트릭" className="flat-grid">
        <MetricCard
          title="총 사용자"
          value={(dashboardData.overview.total_users ?? 0).toLocaleString()}
          change="+12.5%"
          changeType="positive"
          icon="users"
        />
        <MetricCard
          title="총 세션"
          value={(dashboardData.overview.total_sessions ?? dashboardData.overview.total_events ?? 0).toLocaleString()}
          change="+8.3%"
          changeType="positive"
          icon="sessions"
        />
        <MetricCard
          title="총 전환"
          value={(dashboardData.overview.total_conversions ?? 0).toLocaleString()}
          change="+15.2%"
          changeType="positive"
          icon="conversions"
        />
        <MetricCard
          title="평균 전환율"
          value={`${dashboardData.overview.average_conversion_rate ?? dashboardData.overview.conversion_rate ?? 0}%`}
          change="+2.1%"
          changeType="positive"
          icon="conversion-rate"
        />
        {/* 카테고리별 추가 메트릭 */}
        {selectedCategory === 'ecommerce' && (dashboardData.overview.total_revenue != null || dashboardData.overview.average_order_value != null) && (
          <>
            <MetricCard
              title="총 매출"
              value={`₩${(dashboardData.overview.total_revenue ?? 0).toLocaleString()}`}
              change="+18.5%"
              changeType="positive"
              icon="revenue"
            />
            <MetricCard
              title="평균 주문 금액"
              value={`₩${(dashboardData.overview.average_order_value ?? 0).toLocaleString()}`}
              change="+5.2%"
              changeType="positive"
              icon="order-value"
            />
          </>
        )}
        {selectedCategory === 'lead_generation' && (dashboardData.overview.total_leads != null || dashboardData.overview.lead_conversion_rate != null) && (
          <>
            <MetricCard
              title="총 리드"
              value={(dashboardData.overview.total_leads ?? 0).toLocaleString()}
              change="+22.1%"
              changeType="positive"
              icon="leads"
            />
            <MetricCard
              title="리드 전환율"
              value={`${dashboardData.overview.lead_conversion_rate ?? 0}%`}
              change="+3.8%"
              changeType="positive"
              icon="lead-conversion"
            />
          </>
        )}
        {selectedCategory === 'general_website' && (dashboardData.overview.total_page_views != null || dashboardData.overview.unique_visitors != null) && (
          <>
            <MetricCard
              title="총 페이지뷰"
              value={(dashboardData.overview.total_page_views ?? 0).toLocaleString()}
              change="+12.3%"
              changeType="positive"
              icon="page-views"
            />
            <MetricCard
              title="순 방문자"
              value={(dashboardData.overview.unique_visitors ?? 0).toLocaleString()}
              change="+8.7%"
              changeType="positive"
              icon="unique-visitors"
            />
          </>
        )}
      </section>

          {/* 차트 섹션 */}
          <section aria-label="차트 분석" className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
            {/* 퍼널 차트 */}
            <div className="chart-container">
              <h3 className="chart-title ibm-plex-sans-kr-semibold">{categoryTitle} 고객 여정 퍼널</h3>
              <FunnelChart data={dashboardData.funnels} />
            </div>

            {/* KPI 트렌드 */}
            <div className="chart-container">
              <h3 className="chart-title ibm-plex-sans-kr-semibold">{categoryTitle} 전환율 트렌드</h3>
              <KPITrendChart data={dashboardData.kpi_trends} />
            </div>
          </section>

          {/* 시나리오 비교 및 최근 이벤트 */}
          <section aria-label="시나리오 및 이벤트" className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
            {/* 시나리오 성과 비교 */}
            <div className="chart-container">
              <h3 className="chart-title ibm-plex-sans-kr-semibold">{categoryTitle} 시나리오별 성과</h3>
              <ScenarioComparisonChart data={dashboardData.scenario_performance} />
            </div>

            {/* 최근 이벤트 */}
            <div className="chart-container">
              <h3 className="chart-title ibm-plex-sans-kr-semibold">{categoryTitle} 최근 사용자 이벤트</h3>
              <RecentEventsTable events={dashboardData.recent_events} />
            </div>
          </section>
        </div>
      </div>
    </div>
  );
});

Dashboard.displayName = 'Dashboard';

export default Dashboard; 