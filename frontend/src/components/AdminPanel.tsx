import React from 'react';

interface AdminPanelProps {
  onDataUpdate?: () => void;
}

const AdminPanel: React.FC<AdminPanelProps> = ({ onDataUpdate }) => {
  return (
    <div className="p-4 bg-black/5 border border-black rounded-lg">
      <h3 className="text-sm font-semibold text-black mb-2 ibm-plex-sans-kr-semibold">관리자 패널</h3>
      <p className="text-xs text-black/70 mb-3 ibm-plex-sans-kr-regular">
        데이터 새로고침 및 관리 기능 (추후 연동)
      </p>
      {onDataUpdate && (
        <button
          type="button"
          onClick={onDataUpdate}
          className="px-3 py-1.5 text-xs font-medium text-black bg-white border border-black rounded hover:bg-black hover:text-white ibm-plex-sans-kr-medium transition-colors"
        >
          데이터 새로고침
        </button>
      )}
    </div>
  );
};

export default AdminPanel;
