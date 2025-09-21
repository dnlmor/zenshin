import { CheckCircle, Star } from 'lucide-react';
import { StrengthsListProps } from '@/types';

const StrengthsList: React.FC<StrengthsListProps> = ({ strengths }) => {
  if (!strengths || strengths.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <Star className="w-12 h-12 mx-auto mb-3 text-gray-300" />
        <p>No specific strengths identified in this analysis.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-2 mb-6">
        <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
          <CheckCircle className="w-5 h-5 text-green-600" />
        </div>
        <h3 className="text-xl font-semibold text-gray-900">
          What's Working Well
        </h3>
      </div>

      <div className="grid gap-4">
        {strengths.map((strength, index) => (
          <div
            key={index}
            className="strength-card group"
          >
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center mt-0.5">
                <CheckCircle className="w-4 h-4 text-white" />
              </div>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900 mb-2">
                  {strength.title}
                </h4>
                <p className="text-gray-600 leading-relaxed">
                  {strength.description}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StrengthsList;