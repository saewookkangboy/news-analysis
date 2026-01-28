import React from 'react';

interface AdminPanelProps {
  onDataUpdate?: () => void;
}

const AdminPanel: React.FC<AdminPanelProps> = ({ onDataUpdate }) => {
  return (
    <div className="flat-card p-4">
      <h3 className="flat-heading-3 text-sm mb-2">관리자 패널</h3>
      <p className="flat-caption mb-3 text-gray-600">
        데이터 새로고침 및 관리 기능 (추후 연동)
      </p>
      {onDataUpdate && (
        <button
          type="button"
          onClick={onDataUpdate}
          className="flat-btn flat-btn-secondary text-sm"
        >
          데이터 새로고침
        </button>
      )}
    </div>
  );
};

export default AdminPanel;
