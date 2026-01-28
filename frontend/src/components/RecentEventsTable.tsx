import React, { memo } from 'react';
import type { RecentEvent } from '../services/dashboardService';

interface RecentEventsTableProps {
  events: RecentEvent[];
}

const RecentEventsTable: React.FC<RecentEventsTableProps> = memo(({ events }) => {
  if (!events || events.length === 0) {
    return (
      <div className="py-8 text-center flat-caption text-gray-500">
        최근 이벤트가 없습니다.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="flat-table w-full text-left text-sm">
        <thead>
          <tr>
            <th>시간</th>
            <th>이벤트</th>
            <th>사용자</th>
          </tr>
        </thead>
        <tbody>
          {events.map((e) => (
            <tr key={e.id}>
              <td className="text-gray-600">
                {e.timestamp ? new Date(e.timestamp).toLocaleString('ko-KR') : '-'}
              </td>
              <td className="text-gray-900">{e.event_type}</td>
              <td className="text-gray-900">{e.user_id}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
});

RecentEventsTable.displayName = 'RecentEventsTable';

export default RecentEventsTable;
