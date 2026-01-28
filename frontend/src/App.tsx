import React, { useEffect, Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import Footer from './components/Footer';
import ErrorBoundary from './components/ErrorBoundary';
import NetworkStatus from './components/NetworkStatus';
import SEOHead from './components/SEOHead';
import LoadingSpinner from './components/LoadingSpinner';
import { setupGlobalErrorHandler } from './utils/errorHandler';
/* Flat Design을 최우선으로 적용 */
import './styles/flat-design.css';
import './styles/flat-design-override.css';
import './App.css';

// 코드 스플리팅: 라우트별 컴포넌트를 지연 로딩
const Dashboard = lazy(() => import('./components/Dashboard'));
const ScenarioManager = lazy(() => import('./components/ScenarioManager'));
const CustomerJourneyMap = lazy(() => import('./components/CustomerJourneyMap'));
const KPIAnalytics = lazy(() => import('./components/KPIAnalytics'));
const Settings = lazy(() => import('./components/Settings'));

function App() {
  useEffect(() => {
    // 전역 오류 핸들러 설정 (브라우저 확장 프로그램 오류 필터링)
    setupGlobalErrorHandler();
  }, []);

  return (
    <ErrorBoundary>
      <SEOHead />
      <Router>
        <div className="min-h-screen flex flex-col bg-white">
          <NetworkStatus />
          <Navigation />
          <main className="flex-1 overflow-y-auto">
            <Suspense fallback={
              <div className="flex items-center justify-center h-64">
                <LoadingSpinner size="large" text="페이지를 불러오는 중..." />
              </div>
            }>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/scenarios" element={<ScenarioManager />} />
                <Route path="/journey-map" element={<CustomerJourneyMap />} />
                <Route path="/kpi" element={<KPIAnalytics />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </Suspense>
          </main>
          <Footer />
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
