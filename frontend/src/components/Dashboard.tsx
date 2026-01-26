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
import { DashboardService, CategoryType } from '../services/dashboardService';
import { DashboardOverview, FunnelData, KPITrend, RecentEvent, ScenarioPerformance, CategoryMetrics } from '../services/dashboardService';

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

// 간단한 메모리 캐시 구현
class DataCache {
  private cache: Map<string, CacheEntry<any>> = new Map();
  private readonly TTL = 30000; // 30초 캐시 유지

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
    
    return entry.data as T;
  }

  set<T>(key: string, data: T, category: CategoryType): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      category
    });
  }

  clear(): void {
    this.cache.clear();
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

      // 모든 API 호출을 병렬로 실행
      const [overviewRes, funnelsRes, kpiTrendsRes, recentEventsRes, scenarioPerformanceRes, categoryMetricsRes] = await Promise.all([
        DashboardService.getOverview(category),
        DashboardService.getFunnels(undefined, category),
        DashboardService.getKPITrends(undefined, undefined, category),
        DashboardService.getRecentEvents(undefined, category),
        DashboardService.getScenarioPerformance(category),
        DashboardService.getCategoryMetrics(category)
      ]);

      // 응답 검증
      if (!overviewRes.success || !funnelsRes.success || !kpiTrendsRes.success || 
          !recentEventsRes.success || !scenarioPerformanceRes.success || !categoryMetricsRes.success) {
        throw new Error('일부 데이터를 불러오는데 실패했습니다.');
      }

      const dashboardData: DashboardData = {
        overview: overviewRes.data!,
        funnels: funnelsRes.data!,
        kpi_trends: kpiTrendsRes.data!,
        recent_events: recentEventsRes.data!,
        scenario_performance: scenarioPerformanceRes.data!,
        category_metrics: categoryMetricsRes.data!
      };

      // 캐시에 저장
      cache.set(cacheKey, dashboardData, category);
      setDashboardData(dashboardData);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '대시보드 데이터를 불러오는 중 오류가 발생했습니다.';
      setError(errorMessage);
      console.error('Dashboard data fetch error:', err);
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
    <div className="h-full flex flex-col lg:flex-row bg-white">
      {/* 좌측: 분석 설정 패널 */}
      <div className="w-full lg:w-80 xl:w-96 bg-white border-r border-black p-6 overflow-y-auto custom-scrollbar">
        <AnalysisSettings
          selectedCategory={selectedCategory}
          onCategoryChange={handleCategoryChange}
          showAdminPanel={showAdminPanel}
          onToggleAdminPanel={() => setShowAdminPanel(!showAdminPanel)}
        />
      </div>

      {/* 우측: 분석 결과 패널 */}
      <div className="flex-1 overflow-y-auto p-6 lg:p-8 custom-scrollbar">
        <div className="space-y-6 max-w-7xl mx-auto">
          {/* 페이지 헤더 */}
          <div className="mb-6 animate-fade-in">
            <h1 className="text-2xl font-semibold text-black mb-1 tracking-tight ibm-plex-sans-kr-bold" style={{ letterSpacing: '-1.04px' }}>
              분석 결과
            </h1>
            <p className="text-sm text-black ibm-plex-sans-kr-regular" style={{ letterSpacing: '-0.42px' }}>
              {categoryTitle} 고객 여정과 퍼널 분석을 통한 실시간 인사이트
            </p>
          </div>

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

      {/* 개요 메트릭 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="총 사용자"
          value={dashboardData.overview.total_users.toLocaleString()}
          change="+12.5%"
          changeType="positive"
          icon="users"
        />
        <MetricCard
          title="총 세션"
          value={dashboardData.overview.total_sessions.toLocaleString()}
          change="+8.3%"
          changeType="positive"
          icon="sessions"
        />
        <MetricCard
          title="총 전환"
          value={dashboardData.overview.total_conversions.toLocaleString()}
          change="+15.2%"
          changeType="positive"
          icon="conversions"
        />
        <MetricCard
          title="평균 전환율"
          value={`${dashboardData.overview.average_conversion_rate}%`}
          change="+2.1%"
          changeType="positive"
          icon="conversion-rate"
        />
        {/* 카테고리별 추가 메트릭 */}
        {selectedCategory === 'ecommerce' && dashboardData.overview.total_revenue && (
          <>
            <MetricCard
              title="총 매출"
              value={`₩${dashboardData.overview.total_revenue.toLocaleString()}`}
              change="+18.5%"
              changeType="positive"
              icon="revenue"
            />
            <MetricCard
              title="평균 주문 금액"
              value={`₩${dashboardData.overview.average_order_value?.toLocaleString()}`}
              change="+5.2%"
              changeType="positive"
              icon="order-value"
            />
          </>
        )}
        {selectedCategory === 'lead_generation' && dashboardData.overview.total_leads && (
          <>
            <MetricCard
              title="총 리드"
              value={dashboardData.overview.total_leads.toLocaleString()}
              change="+22.1%"
              changeType="positive"
              icon="leads"
            />
            <MetricCard
              title="리드 전환율"
              value={`${dashboardData.overview.lead_conversion_rate}%`}
              change="+3.8%"
              changeType="positive"
              icon="lead-conversion"
            />
          </>
        )}
        {selectedCategory === 'general_website' && dashboardData.overview.total_page_views && (
          <>
            <MetricCard
              title="총 페이지뷰"
              value={dashboardData.overview.total_page_views.toLocaleString()}
              change="+12.3%"
              changeType="positive"
              icon="page-views"
            />
            <MetricCard
              title="순 방문자"
              value={dashboardData.overview.unique_visitors?.toLocaleString() || '0'}
              change="+8.7%"
              changeType="positive"
              icon="unique-visitors"
            />
          </>
        )}
      </div>

          {/* 차트 섹션 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
          </div>

          {/* 시나리오 비교 및 최근 이벤트 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
          </div>
        </div>
      </div>
    </div>
  );
});

Dashboard.displayName = 'Dashboard';

export default Dashboard; 