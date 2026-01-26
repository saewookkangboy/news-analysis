import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  ChartBarIcon, 
  MapIcon, 
  PresentationChartLineIcon,
  CogIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline';

const Navigation: React.FC = () => {
  const location = useLocation();

  const navigation = [
    { name: '대시보드', href: '/', icon: ChartBarIcon },
    { name: '시나리오 관리', href: '/scenarios', icon: MapIcon },
    { name: '고객 여정 맵', href: '/journey-map', icon: UserGroupIcon },
    { name: 'KPI 분석', href: '/kpi', icon: PresentationChartLineIcon },
    { name: '설정', href: '/settings', icon: CogIcon },
  ];

  return (
    <nav className="bg-white border-b border-black flex-shrink-0 sticky top-0 z-50 backdrop-blur-sm bg-white/95">
      <div className="px-6">
        <div className="flex justify-between items-center h-16">
          {/* 로고 */}
          <div className="flex items-center">
            <h1 className="text-xl font-semibold text-black tracking-tight ibm-plex-sans-kr-semibold" style={{ letterSpacing: '-0.8px' }}>
              고객 행동 분석
            </h1>
          </div>

          {/* 네비게이션 메뉴 */}
          <div className="hidden md:block">
            <div className="flex items-center space-x-2">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ibm-plex-sans-kr-medium ${
                      isActive
                        ? 'bg-black text-white scale-105'
                        : 'text-black hover:bg-black hover:text-white hover:scale-105'
                    }`}
                    style={{ letterSpacing: '-0.42px' }}
                  >
                    <item.icon className="h-4 w-4 mr-2" />
                    {item.name}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* 모바일 메뉴 버튼 */}
          <div className="md:hidden">
            <button
              type="button"
              className="inline-flex items-center justify-center p-2 rounded-lg text-black hover:bg-black hover:text-white focus:outline-none"
            >
              <span className="sr-only">메뉴 열기</span>
              <svg
                className="h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation; 