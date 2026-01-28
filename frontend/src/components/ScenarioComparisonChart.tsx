import React, { memo, useMemo } from 'react';
import type { ScenarioPerformance } from '../services/dashboardService';

interface ScenarioComparisonChartProps {
  data: ScenarioPerformance[];
}

const ScenarioComparisonChart: React.FC<ScenarioComparisonChartProps> = memo(({ data }) => {
  const maxRate = useMemo(() => {
    if (!data || data.length === 0) return 0.01;
    return Math.max(...data.map((d) => d.conversion_rate), 0.01);
  }, [data]);

  if (!data || data.length === 0) {
    return (
      <div className="py-8 text-center text-sm text-black/60 ibm-plex-sans-kr-regular">
        시나리오 성과 데이터가 없습니다.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {data.map((s) => (
        <div key={s.scenario_id}>
          <div className="flex justify-between text-xs mb-1 ibm-plex-sans-kr-medium">
            <span>{s.name}</span>
            <span>{s.conversion_rate}% · {s.total_events.toLocaleString()} 이벤트</span>
          </div>
          <div className="h-5 bg-black/5 rounded overflow-hidden">
            <div
              className="h-full bg-black rounded transition-all duration-300"
              style={{ width: `${(s.conversion_rate / maxRate) * 100}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
});

ScenarioComparisonChart.displayName = 'ScenarioComparisonChart';

export default ScenarioComparisonChart;
