import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  ChartBarIcon, 
  MapIcon, 
  PresentationChartLineIcon,
  CogIcon,
  UserGroupIcon,
  XMarkIcon,
  Bars3Icon
} from '@heroicons/react/24/outline';

const Navigation: React.FC = () => {
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  const navigation = [
    { name: '대시보드', href: '/', icon: ChartBarIcon },
    { name: '시나리오 관리', href: '/scenarios', icon: MapIcon },
    { name: '고객 여정 맵', href: '/journey-map', icon: UserGroupIcon },
    { name: 'KPI 분석', href: '/kpi', icon: PresentationChartLineIcon },
    { name: '설정', href: '/settings', icon: CogIcon },
  ];

  // 모바일 메뉴 외부 클릭 시 닫기
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target as Node) &&
        buttonRef.current &&
        !buttonRef.current.contains(event.target as Node)
      ) {
        setIsMobileMenuOpen(false);
      }
    };

    if (isMobileMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      // ESC 키로 메뉴 닫기
      const handleEscape = (event: KeyboardEvent) => {
        if (event.key === 'Escape') {
          setIsMobileMenuOpen(false);
        }
      };
      document.addEventListener('keydown', handleEscape);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
        document.removeEventListener('keydown', handleEscape);
      };
    }
  }, [isMobileMenuOpen]);

  // 라우트 변경 시 모바일 메뉴 닫기
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location.pathname]);

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
                    className={`inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ibm-plex-sans-kr-medium focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2 ${
                      isActive
                        ? 'bg-black text-white scale-105'
                        : 'text-black hover:bg-black hover:text-white hover:scale-105'
                    }`}
                    style={{ letterSpacing: '-0.42px' }}
                    aria-current={isActive ? 'page' : undefined}
                  >
                    <item.icon className="h-4 w-4 mr-2" aria-hidden="true" />
                    {item.name}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* 모바일 메뉴 버튼 */}
          <div className="md:hidden">
            <button
              ref={buttonRef}
              type="button"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-lg text-black hover:bg-black hover:text-white focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2"
              aria-expanded={isMobileMenuOpen}
              aria-controls="mobile-menu"
              aria-label={isMobileMenuOpen ? '메뉴 닫기' : '메뉴 열기'}
            >
              {isMobileMenuOpen ? (
                <XMarkIcon className="h-5 w-5" aria-hidden="true" />
              ) : (
                <Bars3Icon className="h-5 w-5" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>

        {/* 모바일 메뉴 */}
        {isMobileMenuOpen && (
          <div
            ref={menuRef}
            id="mobile-menu"
            className="md:hidden border-t border-black bg-white"
            role="menu"
            aria-label="모바일 네비게이션 메뉴"
          >
            <div className="px-2 pt-2 pb-3 space-y-1">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`flex items-center px-4 py-3 rounded-lg text-base font-medium transition-all duration-200 ibm-plex-sans-kr-medium ${
                      isActive
                        ? 'bg-black text-white'
                        : 'text-black hover:bg-black hover:text-white'
                    }`}
                    style={{ letterSpacing: '-0.42px' }}
                    role="menuitem"
                    aria-current={isActive ? 'page' : undefined}
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <item.icon className="h-5 w-5 mr-3" aria-hidden="true" />
                    {item.name}
                  </Link>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navigation; 