import React, { memo } from 'react';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  text?: string;
}

const sizeClasses = {
  small: 'w-6 h-6 border-2',
  medium: 'w-10 h-10 border-2',
  large: 'w-12 h-12 border-2',
};

const LoadingSpinner: React.FC<LoadingSpinnerProps> = memo(({ size = 'medium', text }) => {
  return (
    <div className="flex flex-col items-center justify-center gap-3" role="status" aria-live="polite">
      <div
        className={`animate-spin rounded-full border-blue-600 border-t-transparent ${sizeClasses[size]}`}
        aria-label="로딩 중"
      />
      {text && (
        <p className="flat-caption text-gray-600">
          {text}
        </p>
      )}
      <span className="sr-only">로딩 중입니다. 잠시만 기다려주세요.</span>
    </div>
  );
});

LoadingSpinner.displayName = 'LoadingSpinner';

export default LoadingSpinner;
