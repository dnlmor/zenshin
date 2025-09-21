import { LoadingSpinnerProps } from '@/types';

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  message = 'Loading...' 
}) => {
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-10 h-10',
    lg: 'w-16 h-16'
  };

  return (
    <div className="flex flex-col items-center justify-center p-8 space-y-4">
      {/* Animated spinner with multiple rings */}
      <div className="relative">
        {/* Outer ring */}
        <div className={`${sizeClasses[size]} border-4 border-blue-200 rounded-full animate-spin`}>
          <div className="absolute inset-0 border-4 border-transparent border-t-blue-600 rounded-full animate-spin"></div>
        </div>
        
        {/* Inner ring - spins opposite direction */}
        <div className={`absolute inset-2 border-2 border-purple-200 rounded-full animate-spin`} style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}>
          <div className="absolute inset-0 border-2 border-transparent border-b-purple-500 rounded-full animate-spin" style={{ animationDirection: 'reverse' }}></div>
        </div>
        
        {/* Center dot */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-2 h-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full pulse-slow"></div>
        </div>
      </div>

      {/* Loading message */}
      {message && (
        <div className="text-center">
          <p className="text-gray-600 font-medium animate-pulse">
            {message}
          </p>
          <div className="flex space-x-1 justify-center mt-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LoadingSpinner;