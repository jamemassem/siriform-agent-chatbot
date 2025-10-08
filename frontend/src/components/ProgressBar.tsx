/**
 * ProgressBar component with gradient fill and smooth animations.
 */
import React from 'react';
import './ProgressBar.css';

interface ProgressBarProps {
  percentage: number;
  label?: string;
  showPercentage?: boolean;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  percentage,
  label = 'ความคืบหน้า',
  showPercentage = true,
}) => {
  // Clamp percentage between 0 and 100
  const clampedPercentage = Math.min(Math.max(percentage, 0), 100);
  
  // Determine color based on percentage
  const getColorClass = () => {
    if (clampedPercentage < 33) return 'low';
    if (clampedPercentage < 66) return 'medium';
    return 'high';
  };
  
  return (
    <div className="progress-bar-container">
      <div className="progress-bar-header">
        <span className="progress-bar-label">{label}</span>
        {showPercentage && (
          <span className="progress-bar-percentage">
            {Math.round(clampedPercentage)}%
          </span>
        )}
      </div>
      <div className="progress-bar-track">
        <div
          className={`progress-bar-fill ${getColorClass()}`}
          style={{ width: `${clampedPercentage}%` }}
          role="progressbar"
          aria-valuenow={clampedPercentage}
          aria-valuemin={0}
          aria-valuemax={100}
        >
          <div className="progress-bar-shine" />
        </div>
      </div>
    </div>
  );
};

export default ProgressBar;
