import React from 'react';
import { CategoryType } from '../services/dashboardService';

interface AnalysisSettingsProps {
  selectedCategory: CategoryType;
  onCategoryChange: (category: CategoryType) => void;
  showAdminPanel: boolean;
  onToggleAdminPanel: () => void;
}

const AnalysisSettings: React.FC<AnalysisSettingsProps> = ({
  selectedCategory,
  onCategoryChange,
  showAdminPanel,
  onToggleAdminPanel
}) => {
  const categories = [
    { value: 'all', label: '전체', description: '모든 카테고리 지표' },
    { value: 'ecommerce', label: 'E-commerce', description: '온라인 쇼핑몰 지표' },
    { value: 'lead_generation', label: '잠재고객 확보', description: '리드 생성 및 관리 지표' },
    { value: 'general_website', label: '일반 웹사이트', description: '일반 웹사이트 트래픽 지표' }
  ] as const;

  const getCategoryTitle = (category: CategoryType) => {
    switch (category) {
      case 'ecommerce': return 'E-commerce';
      case 'lead_generation': return '잠재고객 확보';
      case 'general_website': return '일반 웹사이트';
      default: return '전체';
    }
  };

  return (
    <div className="h-full flex flex-col animate-fade-in">
      {/* 헤더 */}
      <div className="mb-6 pb-4 border-b border-black">
        <h2 className="text-lg font-semibold text-black mb-1 tracking-tight" style={{ letterSpacing: '-0.72px' }}>
          분석 설정
        </h2>
        <p className="text-xs text-black" style={{ letterSpacing: '-0.36px' }}>
          카테고리와 옵션을 선택하세요
        </p>
      </div>

      {/* 카테고리 선택 */}
      <div className="mb-6">
        <label className="block text-xs font-medium text-black mb-3 uppercase tracking-wide">
          카테고리 선택
        </label>
        <div className="space-y-2">
          {categories.map((category, index) => (
            <button
              key={category.value}
              onClick={() => onCategoryChange(category.value as CategoryType)}
              className={`w-full text-left p-3 rounded-lg border transition-all duration-200 ${
                selectedCategory === category.value
                  ? 'border-black bg-black text-white scale-105'
                  : 'border-black bg-white text-black hover:bg-black hover:text-white hover:scale-105'
              }`}
              style={{ 
                animationDelay: `${index * 50}ms`,
                letterSpacing: '-0.42px'
              }}
            >
              <div className="font-medium text-sm mb-0.5">{category.label}</div>
              <div className="text-xs opacity-75" style={{ letterSpacing: '-0.36px' }}>
                {category.description}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* 현재 선택된 카테고리 정보 */}
      <div className="mb-6 p-3 bg-white rounded-lg border border-black">
        <div className="text-xs text-black mb-1">현재 선택</div>
        <div className="text-sm font-medium text-black">
          {getCategoryTitle(selectedCategory)}
        </div>
      </div>

      {/* 관리자 패널 토글 */}
      <div className="mt-auto pt-4 border-t border-black">
        <button
          onClick={onToggleAdminPanel}
          className="w-full px-3 py-2 text-xs font-medium text-black bg-white border border-black rounded-lg hover:bg-black hover:text-white transition-colors duration-200"
        >
          {showAdminPanel ? '관리자 패널 숨기기' : '관리자 패널 보기'}
        </button>
      </div>
    </div>
  );
};

export default AnalysisSettings;
