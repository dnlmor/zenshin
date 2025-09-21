import { AlertTriangle, TrendingUp, ArrowRight } from 'lucide-react';
import { ImprovementsListProps } from '@/types';

const ImprovementsList: React.FC<ImprovementsListProps> = ({ improvements }) => {
  if (!improvements || improvements.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <TrendingUp className="w-12 h-12 mx-auto mb-3 text-gray-300" />
        <p>No specific improvements suggested in this analysis.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-2 mb-6">
        <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
          <TrendingUp className="w-5 h-5 text-blue-600" />
        </div>
        <h3 className="text-xl font-semibold text-gray-900">
          Areas for Improvement
        </h3>
      </div>

      <div className="grid gap-6">
        {improvements.map((improvement, index) => (
          <div
            key={index}
            className="improvement-card group"
          >
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                  {index + 1}
                </div>
              </div>
              
              <div className="flex-1 space-y-3">
                {/* Header with title and score */}
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold text-gray-900 text-lg">
                    {improvement.title}
                  </h4>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-500">Score:</span>
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                      {improvement.score}
                    </span>
                  </div>
                </div>

                {/* Issue description */}
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                  <div className="flex items-start space-x-2">
                    <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-sm font-medium text-amber-800 mb-1">Issue:</p>
                      <p className="text-sm text-amber-700">{improvement.issue}</p>
                    </div>
                  </div>
                </div>

                {/* Action recommendation */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                  <div className="flex items-start space-x-2">
                    <ArrowRight className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-sm font-medium text-green-800 mb-1">Action:</p>
                      <p className="text-sm text-green-700">{improvement.action}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ImprovementsList;