import { useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { useAnalysis } from '@/hooks/useAnalysis';
import RepositoryInput from '@/components/RepositoryInput';
import AnalysisResults from '@/components/AnalysisResults';
import LoadingSpinner from '@/components/LoadingSpinner';

function App() {
  const {
    isLoading,
    data,
    error,
    loadingMessage,
    progress,
    analyzeRepository,
    clearError,
    reset,
  } = useAnalysis();

  const [showResults, setShowResults] = useState(false);

  const handleAnalysis = async (request: any) => {
    setShowResults(false);
    await analyzeRepository(request);
    if (!error) {
      setShowResults(true);
    }
  };

  const handleReset = () => {
    reset();
    setShowResults(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      <div className="container mx-auto px-4 py-8">
        {/* Error Display */}
        {error && (
          <div className="max-w-2xl mx-auto mb-8">
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <h3 className="font-medium text-red-800 mb-1">Analysis Failed</h3>
                <p className="text-red-700 text-sm">{error}</p>
                <button
                  onClick={clearError}
                  className="mt-2 text-red-600 hover:text-red-800 text-sm font-medium"
                >
                  Try Again
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="max-w-2xl mx-auto">
            <div className="card text-center">
              <LoadingSpinner size="lg" message={loadingMessage} />
              
              {/* Progress Bar */}
              <div className="mt-6">
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-500 mt-2">
                  {Math.round(progress)}% Complete
                </p>
              </div>

              <div className="mt-4 text-sm text-gray-600">
                <p>This usually takes 10-30 seconds...</p>
              </div>
            </div>
          </div>
        )}

        {/* Main Content */}
        {!isLoading && !showResults && (
          <RepositoryInput 
            onSubmit={handleAnalysis}
            isLoading={isLoading}
          />
        )}

        {/* Results */}
        {!isLoading && showResults && data && (
          <AnalysisResults 
            data={data}
            onReset={handleReset}
          />
        )}
      </div>

      {/* Footer */}
      <footer className="mt-16 py-8 text-center text-gray-500 text-sm">
        <p>
          Built with ❤️ by dnlmor
        </p>
      </footer>
    </div>
  );
}

export default App;