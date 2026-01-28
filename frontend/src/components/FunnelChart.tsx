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
      <div className="py-8 text-center text-sm text-black/60 ibm-plex-sans-kr-regular">
        퍼널 데이터가 없습니다.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {data.map((step, i) => (
        <div key={step.step}>
          <div className="flex justify-between text-xs mb-1 ibm-plex-sans-kr-medium">
            <span>{step.step}</span>
            <span>
              {step.count.toLocaleString()} ({step.percentage}%)
            </span>
          </div>
          <div className="h-6 bg-black/5 rounded overflow-hidden">
            <div
              className="h-full bg-black rounded transition-all duration-300"
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
