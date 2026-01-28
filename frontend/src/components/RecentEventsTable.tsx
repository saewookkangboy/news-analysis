import React, { memo } from 'react';
import type { RecentEvent } from '../services/dashboardService';

interface RecentEventsTableProps {
  events: RecentEvent[];
}

const RecentEventsTable: React.FC<RecentEventsTableProps> = memo(({ events }) => {
  if (!events || events.length === 0) {
    return (
      <div className="py-8 text-center text-sm text-black/60 ibm-plex-sans-kr-regular">
        최근 이벤트가 없습니다.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm ibm-plex-sans-kr-regular">
        <thead>
          <tr className="border-b border-black">
            <th className="pb-2 pr-4 font-medium">시간</th>
            <th className="pb-2 pr-4 font-medium">이벤트</th>
            <th className="pb-2 font-medium">사용자</th>
          </tr>
        </thead>
        <tbody>
          {events.map((e) => (
            <tr key={e.id} className="border-b border-black/20">
              <td className="py-2 pr-4 text-black/70">
                {e.timestamp ? new Date(e.timestamp).toLocaleString('ko-KR') : '-'}
              </td>
              <td className="py-2 pr-4">{e.event_type}</td>
              <td className="py-2">{e.user_id}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
});

RecentEventsTable.displayName = 'RecentEventsTable';

export default RecentEventsTable;
