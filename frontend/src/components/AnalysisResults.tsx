import { Github, Clock, Eye, MessageSquare, RotateCcw } from 'lucide-react';
import { AnalysisResponse } from '@/types';
import { formatTimestamp } from '@/utils/constants';
import ScoreDisplay from './ScoreDisplay';
import StrengthsList from './StrengthsList';
import ImprovementsList from './ImprovementsList';
import CodeExample from './CodeExample';

interface AnalysisResultsProps {
  data: AnalysisResponse;
  onReset: () => void;
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({ data, onReset }) => {
  const { repository, analysis } = data;

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header Section */}
      <div className="card">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
                <Github className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {repository.name}
                </h1>
                <a
                  href={repository.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 transition-colors duration-200 text-sm"
                >
                  {repository.url}
                </a>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
              <div className="flex items-center space-x-1">
                <Eye className="w-4 h-4" />
                <span>{repository.total_files_analyzed} files analyzed</span>
              </div>
              <div className="flex items-center space-x-1">
                <Clock className="w-4 h-4" />
                <span>{formatTimestamp(data.timestamp)}</span>
              </div>
            </div>

            {/* Languages */}
            <div className="mt-4">
              <div className="flex flex-wrap gap-2">
                {repository.languages.map(language => (
                  <span
                    key={language}
                    className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-medium"
                  >
                    {language}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Score Display */}
          <div className="flex flex-col items-center lg:items-end space-y-4">
            <ScoreDisplay score={analysis.overall_score} size="lg" />
            <button
              onClick={onReset}
              className="btn-secondary flex items-center space-x-2"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Analyze Another</span>
            </button>
          </div>
        </div>

        {/* Summary */}
        {analysis.summary && (
          <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-100">
            <h3 className="font-semibold text-gray-900 mb-2">Analysis Summary</h3>
            <p className="text-gray-700 leading-relaxed">{analysis.summary}</p>
          </div>
        )}
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-2 gap-8">
        {/* Strengths */}
        <div className="card">
          <StrengthsList strengths={analysis.strengths} />
        </div>

        {/* Improvements */}
        <div className="card">
          <ImprovementsList improvements={analysis.improvements} />
        </div>
      </div>

      {/* Code Examples */}
      {analysis.code_examples && (analysis.code_examples.before || analysis.code_examples.after) && (
        <div className="card">
          <CodeExample codeExample={analysis.code_examples} />
        </div>
      )}

      {/* Final Thoughts */}
      {analysis.final_thoughts && (
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <div className="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center">
              <MessageSquare className="w-5 h-5 text-indigo-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900">
              Final Thoughts
            </h3>
          </div>
          <div className="p-6 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl border border-indigo-100">
            <p className="text-gray-700 leading-relaxed text-lg">
              {analysis.final_thoughts}
            </p>
          </div>
        </div>
      )}

      {/* Raw Review (Collapsible) */}
      <details className="card">
        <summary className="cursor-pointer font-medium text-gray-700 hover:text-gray-900 transition-colors duration-200">
          View Raw AI Review
        </summary>
        <div className="mt-4 p-4 bg-gray-50 rounded-xl">
          <pre className="whitespace-pre-wrap text-sm text-gray-600 font-mono scrollbar-thin max-h-96 overflow-y-auto">
            {data.raw_review}
          </pre>
        </div>
      </details>
    </div>
  );
};

export default AnalysisResults;