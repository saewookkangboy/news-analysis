import React, { useState, useEffect } from 'react';

const NetworkStatus: React.FC = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (isOnline) {
    return null;
  }

  return (
    <div 
      className="bg-yellow-500 text-black text-center py-2 px-4 text-sm ibm-plex-sans-kr-medium"
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <span className="sr-only">경고: </span>
      인터넷 연결이 끊어졌습니다. 오프라인 모드로 작동 중입니다.
    </div>
  );
};

export default NetworkStatus;
