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
        : 'text-gray-600';

  return (
    <div 
      className="flat-metric-card transition-colors duration-200 hover:bg-gray-50 focus-within:ring-2 focus-within:ring-blue-500 focus-within:ring-offset-2"
      role="article"
      aria-label={`${title}: ${value}${change ? `, ${change}` : ''}`}
      tabIndex={0}
    >
      {icon && (
        <span className="inline-block w-8 h-8 mb-2 rounded bg-gray-100" aria-hidden="true" />
      )}
      <div className="flat-caption mb-1">
        {title}
      </div>
      <div className="flat-metric-value">
        {value}
      </div>
      {change != null && (
        <div 
          className={`text-xs mt-1 font-medium ${changeColor}`}
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
