import React, { memo, useMemo } from 'react';
import type { FunnelData } from '../services/dashboardService';

interface FunnelChartProps {
  data: FunnelData[];
}

const FunnelChart: React.FC<FunnelChartProps> = memo(({ data }) => {
  const maxCount = useMemo(() => {
    if (!data || data.length === 0) return 1;
    return Math.max(...data.map((d) => d.count), 1);
  }, [data]);

  if (!data || data.length === 0) {
    return (
      <div className="py-8 text-center flat-caption text-gray-500">
        퍼널 데이터가 없습니다.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {data.map((step, i) => (
        <div key={step.step}>
          <div className="flex justify-between text-xs mb-1 font-medium text-gray-700">
            <span>{step.step}</span>
            <span>
              {step.count.toLocaleString()} ({step.percentage}%)
            </span>
          </div>
          <div className="flat-progress h-6">
            <div
              className="flat-progress-bar h-full bg-blue-600 transition-all duration-300"
              style={{ width: `${(step.count / maxCount) * 100}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
});

FunnelChart.displayName = 'FunnelChart';

export default FunnelChart;
