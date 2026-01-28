import React, { memo } from 'react';

interface MetricCardProps {
  title: string;
  value: string;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon?: string;
}

const MetricCard: React.FC<MetricCardProps> = memo(({ title, value, change, changeType = 'neutral', icon }) => {
  const changeColor =
    changeType === 'positive'
      ? 'text-green-600'
      : changeType === 'negative'
        ? 'text-red-600'
        : 'text-black';

  return (
    <div 
      className="p-4 bg-white border border-black rounded-lg ibm-plex-sans-kr-regular transition-all duration-200 hover:shadow-md focus-within:ring-2 focus-within:ring-black focus-within:ring-offset-2"
      role="article"
      aria-label={`${title}: ${value}${change ? `, ${change}` : ''}`}
      tabIndex={0}
    >
      {icon && (
        <span className="inline-block w-8 h-8 mb-2 rounded bg-black/5" aria-hidden="true" />
      )}
      <div className="text-xs text-black/70 mb-1 ibm-plex-sans-kr-medium" style={{ letterSpacing: '-0.36px' }}>
        {title}
      </div>
      <div className="text-lg font-semibold text-black ibm-plex-sans-kr-semibold" style={{ letterSpacing: '-0.72px' }}>
        {value}
      </div>
      {change != null && (
        <div 
          className={`text-xs mt-1 ${changeColor}`} 
          style={{ letterSpacing: '-0.36px' }}
          aria-label={`변화율: ${change}`}
        >
          {change}
        </div>
      )}
    </div>
  );
});

MetricCard.displayName = 'MetricCard';

export default MetricCard;
