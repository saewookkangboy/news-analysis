import React from 'react';
import type { CategoryType, CategoryMetrics } from '../services/dashboardService';

interface CategoryMetricsProps {
  category: CategoryType;
  metrics: CategoryMetrics | Partial<CategoryMetrics>;
}

const CategoryMetricsComponent: React.FC<CategoryMetricsProps> = ({ category, metrics }) => {
  if (!metrics || Object.keys(metrics).length === 0) {
    return null;
  }

  const ecommerce = metrics.ecommerce;
  const leadGen = metrics.lead_generation;
  const general = metrics.general_website;

  return (
    <div className="p-4 bg-white border border-black rounded-lg mb-6">
      <h3 className="text-sm font-semibold text-black mb-3 ibm-plex-sans-kr-semibold">카테고리별 메트릭</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-sm ibm-plex-sans-kr-regular">
        {ecommerce && (
          <div>
            <div className="font-medium mb-1">E-commerce</div>
            <div className="text-black/70">
              매출 ₩{ecommerce.revenue?.toLocaleString() ?? 0} · 주문 {ecommerce.orders ?? 0} · AOV ₩
              {ecommerce.average_order_value?.toLocaleString() ?? 0}
            </div>
          </div>
        )}
        {leadGen && (
          <div>
            <div className="font-medium mb-1">잠재고객 확보</div>
            <div className="text-black/70">
              리드 {leadGen.leads ?? 0} · 전환율 {leadGen.conversion_rate ?? 0}%
            </div>
          </div>
        )}
        {general && (
          <div>
            <div className="font-medium mb-1">일반 웹사이트</div>
            <div className="text-black/70">
              PV {general.page_views?.toLocaleString() ?? 0} · 순방문자 {general.unique_visitors?.toLocaleString() ?? 0}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CategoryMetricsComponent;
