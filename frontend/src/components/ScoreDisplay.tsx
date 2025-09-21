import { ScoreDisplayProps } from '@/types';
import { getScoreColor, getScoreLabel } from '@/utils/constants';

const ScoreDisplay: React.FC<ScoreDisplayProps> = ({ score, size = 'md' }) => {
  const colorClass = getScoreColor(score);
  const label = getScoreLabel(score);
  
  const sizeConfig = {
    sm: {
      container: 'w-16 h-16',
      text: 'text-sm',
      label: 'text-xs'
    },
    md: {
      container: 'w-24 h-24',
      text: 'text-lg',
      label: 'text-sm'
    },
    lg: {
      container: 'w-32 h-32',
      text: 'text-2xl',
      label: 'text-base'
    }
  };

  const config = sizeConfig[size];

  // Calculate stroke-dasharray for the progress circle
  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const strokeDasharray = `${(score / 100) * circumference} ${circumference}`;

  return (
    <div className="flex flex-col items-center space-y-2">
      {/* Circular progress indicator */}
      <div className={`relative ${config.container} flex items-center justify-center`}>
        {/* Background circle */}
        <svg className="transform -rotate-90 w-full h-full" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r={radius}
            strokeWidth="8"
            fill="transparent"
            className="stroke-gray-200"
          />
          {/* Progress circle */}
          <circle
            cx="50"
            cy="50"
            r={radius}
            strokeWidth="8"
            fill="transparent"
            strokeDasharray={strokeDasharray}
            strokeLinecap="round"
            className={`transition-all duration-1000 ease-out ${
              score >= 90 ? 'stroke-emerald-500' :
              score >= 80 ? 'stroke-blue-500' :
              score >= 70 ? 'stroke-amber-500' : 'stroke-red-500'
            }`}
          />
        </svg>
        
        {/* Score text */}
        <div className={`absolute inset-0 flex flex-col items-center justify-center ${config.text} font-bold`}>
          <span className="text-gray-900">{score}</span>
          <span className="text-gray-500 text-xs">/100</span>
        </div>
      </div>

      {/* Score label */}
      <div className={`px-3 py-1 rounded-full border ${colorClass} ${config.label} font-medium`}>
        {label}
      </div>
    </div>
  );
};

export default ScoreDisplay;