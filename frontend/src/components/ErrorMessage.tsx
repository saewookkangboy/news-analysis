import React, { memo } from 'react';

interface ErrorMessageProps {
  error: string;
  onRetry?: () => void;
  showRetry?: boolean;
}

const ErrorMessage: React.FC<ErrorMessageProps> = memo(({ error, onRetry, showRetry = false }) => {
  return (
    <div className="flex flex-col items-center justify-center gap-4 p-8 bg-white border border-black rounded-lg max-w-md mx-auto">
      <div className="flex items-center justify-center w-12 h-12 mb-2 rounded-full bg-red-50">
        <svg
          className="w-6 h-6 text-red-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>
      <h3 className="text-base font-semibold text-black ibm-plex-sans-kr-semibold">
        오류가 발생했습니다
      </h3>
      <p className="text-sm text-black/70 text-center ibm-plex-sans-kr-regular" style={{ letterSpacing: '-0.42px' }}>
        {error}
      </p>
      {showRetry && onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="px-6 py-2 text-sm font-medium text-white bg-black border border-black rounded-lg hover:bg-gray-800 ibm-plex-sans-kr-medium transition-colors focus:outline-none focus:ring-2 focus:ring-black focus:ring-offset-2"
          aria-label="다시 시도"
        >
          다시 시도
        </button>
      )}
    </div>
  );
});

ErrorMessage.displayName = 'ErrorMessage';

export default ErrorMessage;
