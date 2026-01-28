import React, { memo, useMemo } from 'react';
import type { KPITrend } from '../services/dashboardService';

interface KPITrendChartProps {
  data: KPITrend[];
}

const KPITrendChart: React.FC<KPITrendChartProps> = memo(({ data }) => {
  const { minVal, maxVal, range } = useMemo(() => {
    if (!data || data.length === 0) {
      return { minVal: 0, maxVal: 0, range: 1 };
    }
    const values = data.map((d) => d.value);
    const min = Math.min(...values);
    const max = Math.max(...values);
    return {
      minVal: min,
      maxVal: max,
      range: max - min || 1
    };
  }, [data]);

  if (!data || data.length === 0) {
    return (
      <div className="py-8 text-center text-sm text-black/60 ibm-plex-sans-kr-regular">
        KPI 트렌드 데이터가 없습니다.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {data.map((d) => (
        <div key={d.date} className="flex items-center gap-3">
          <span className="text-xs text-black/70 w-24 ibm-plex-sans-kr-regular">{d.date}</span>
          <div className="flex-1 h-5 bg-black/5 rounded overflow-hidden">
            <div
              className="h-full bg-black rounded transition-all duration-300"
              style={{ width: `${((d.value - minVal) / range) * 100}%` }}
            />
          </div>
          <span className="text-xs font-medium w-12 text-right ibm-plex-sans-kr-medium">{d.value}%</span>
        </div>
      ))}
    </div>
  );
});

KPITrendChart.displayName = 'KPITrendChart';

export default KPITrendChart;
