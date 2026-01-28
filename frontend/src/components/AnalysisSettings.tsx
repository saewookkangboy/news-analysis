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
      {/* 헤더 - Flat Design */}
      <div className="mb-6 pb-4 border-b border-gray-200">
        <h2 className="flat-heading-3 mb-1">
          분석 설정
        </h2>
        <p className="flat-caption">
          카테고리와 옵션을 선택하세요
        </p>
      </div>

      {/* 카테고리 선택 - Flat Design */}
      <div className="mb-6">
        <label className="flat-caption block mb-3 font-medium uppercase tracking-wide text-gray-700">
          카테고리 선택
        </label>
        <div className="space-y-2">
          {categories.map((category, index) => (
            <button
              key={category.value}
              onClick={() => onCategoryChange(category.value as CategoryType)}
              className={`w-full text-left p-3 rounded border transition-colors duration-200 ${
                selectedCategory === category.value
                  ? 'border-blue-600 bg-blue-600 text-white'
                  : 'border-gray-200 bg-white text-gray-900 hover:bg-gray-50 hover:border-blue-500'
              }`}
              style={{ 
                animationDelay: `${index * 50}ms`
              }}
            >
              <div className="font-medium text-sm mb-0.5">{category.label}</div>
              <div className="text-xs opacity-75">
                {category.description}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* 현재 선택된 카테고리 정보 - Flat Design */}
      <div className="mb-6 p-3 flat-card">
        <div className="flat-caption mb-1">현재 선택</div>
        <div className="text-sm font-medium text-gray-900">
          {getCategoryTitle(selectedCategory)}
        </div>
      </div>

      {/* 관리자 패널 토글 - Flat Design */}
      <div className="mt-auto pt-4 border-t border-gray-200">
        <button
          onClick={onToggleAdminPanel}
          className="flat-btn flat-btn-secondary w-full"
        >
          {showAdminPanel ? '관리자 패널 숨기기' : '관리자 패널 보기'}
        </button>
      </div>
    </div>
  );
};

export default AnalysisSettings;
