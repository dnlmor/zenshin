import { useState } from 'react';
import { Github, Sparkles, ChevronDown, X } from 'lucide-react';
import { RepositoryForm, AnalysisRequest } from '@/types';
import { 
  validateGitHubUrl, 
  EXPERIENCE_LEVELS, 
  FOCUS_AREAS, 
  DEFAULT_FORM_VALUES 
} from '@/utils/constants';

interface RepositoryInputProps {
  onSubmit: (request: AnalysisRequest) => void;
  isLoading: boolean;
}

const RepositoryInput: React.FC<RepositoryInputProps> = ({ onSubmit, isLoading }) => {
  const [form, setForm] = useState<RepositoryForm>(DEFAULT_FORM_VALUES);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    const newErrors: Record<string, string> = {};
    
    if (!form.url.trim()) {
      newErrors.url = 'GitHub URL is required';
    } else if (!validateGitHubUrl(form.url)) {
      newErrors.url = 'Please enter a valid GitHub repository URL';
    }

    setErrors(newErrors);

    if (Object.keys(newErrors).length === 0) {
      // Convert form to API request
      const request: AnalysisRequest = {
        github_url: form.url.trim(),
        ...(form.description && { project_description: form.description }),
        ...(form.goals.length > 0 && { project_goals: form.goals }),
        ...(form.focusAreas.length > 0 && { focus_areas: form.focusAreas }),
        ...(form.experienceLevel && { experience_level: form.experienceLevel }),
      };

      onSubmit(request);
    }
  };

  const addGoal = (goal: string) => {
    if (goal.trim() && !form.goals.includes(goal.trim())) {
      setForm(prev => ({
        ...prev,
        goals: [...prev.goals, goal.trim()]
      }));
    }
  };

  const removeGoal = (goalToRemove: string) => {
    setForm(prev => ({
      ...prev,
      goals: prev.goals.filter(goal => goal !== goalToRemove)
    }));
  };

  const toggleFocusArea = (area: string) => {
    setForm(prev => ({
      ...prev,
      focusAreas: prev.focusAreas.includes(area)
        ? prev.focusAreas.filter(a => a !== area)
        : [...prev.focusAreas, area]
    }));
  };

  return (
    <div className="card max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl mb-4 floating">
          <Github className="w-8 h-8 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-gradient mb-2">
          Zenshin - Your AI Code Review Assistant
        </h1>
        <p className="text-gray-600">
          Get intelligent insights and suggestions for your GitHub repository
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* GitHub URL Input */}
        <div>
          <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
            GitHub Repository URL
          </label>
          <div className="relative">
            <Github className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              id="url"
              type="url"
              value={form.url}
              onChange={(e) => setForm(prev => ({ ...prev, url: e.target.value }))}
              placeholder="https://github.com/username/repository"
              className={`input-modern pl-12 ${errors.url ? 'border-red-300 focus:ring-red-500' : ''}`}
              disabled={isLoading}
            />
          </div>
          {errors.url && (
            <p className="mt-1 text-sm text-red-600">{errors.url}</p>
          )}
          <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Note:</strong> Use the regular GitHub repository URL (without .git extension)
            </p>
            <p className="text-xs text-blue-600 mt-1">
              Example: https://github.com/microsoft/vscode
            </p>
          </div>
        </div>

        {/* Advanced Options Toggle */}
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 font-medium transition-colors duration-200"
        >
          <Sparkles className="w-4 h-4" />
          <span>Advanced Options</span>
          <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${showAdvanced ? 'rotate-180' : ''}`} />
        </button>

        {/* Advanced Options */}
        {showAdvanced && (
          <div className="space-y-6 p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-100">
            {/* Project Description */}
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                Project Description
              </label>
              <textarea
                id="description"
                value={form.description}
                onChange={(e) => setForm(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Briefly describe what your project does..."
                rows={3}
                className="input-modern resize-none"
                disabled={isLoading}
              />
            </div>

            {/* Experience Level */}
            <div>
              <label htmlFor="experience" className="block text-sm font-medium text-gray-700 mb-2">
                Your Experience Level
              </label>
              <select
                id="experience"
                value={form.experienceLevel}
                onChange={(e) => setForm(prev => ({ ...prev, experienceLevel: e.target.value as any }))}
                className="input-modern"
                disabled={isLoading}
              >
                {EXPERIENCE_LEVELS.map(level => (
                  <option key={level.value} value={level.value}>
                    {level.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Focus Areas */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Focus Areas
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {FOCUS_AREAS.map(area => (
                  <button
                    key={area.value}
                    type="button"
                    onClick={() => toggleFocusArea(area.value)}
                    disabled={isLoading}
                    className={`p-3 rounded-xl border-2 text-left transition-all duration-200 ${
                      form.focusAreas.includes(area.value)
                        ? 'border-blue-500 bg-blue-50 text-blue-900'
                        : 'border-gray-200 bg-white hover:border-gray-300'
                    }`}
                  >
                    <div className="font-medium text-sm">{area.label}</div>
                    <div className="text-xs text-gray-500 mt-1">{area.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Project Goals */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Project Goals (Optional)
              </label>
              <div className="flex flex-wrap gap-2 mb-3">
                {form.goals.map(goal => (
                  <span
                    key={goal}
                    className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                  >
                    {goal}
                    <button
                      type="button"
                      onClick={() => removeGoal(goal)}
                      className="ml-2 text-blue-600 hover:text-blue-800"
                      disabled={isLoading}
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
              <input
                type="text"
                placeholder="Add a goal and press Enter..."
                className="input-modern"
                disabled={isLoading}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addGoal(e.currentTarget.value);
                    e.currentTarget.value = '';
                  }
                }}
              />
            </div>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading || !form.url.trim()}
          className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
        >
          {isLoading ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
              <span>Analyzing Repository...</span>
            </div>
          ) : (
            <div className="flex items-center justify-center space-x-2">
              <Sparkles className="w-5 h-5" />
              <span>Start AI Analysis</span>
            </div>
          )}
        </button>
      </form>

      {/* Example URLs */}
      <div className="mt-6 p-4 bg-gray-50 rounded-xl">
        <p className="text-sm text-gray-600 mb-2">Try these example repositories:</p>
        <div className="flex flex-wrap gap-2">
          {[
            'https://github.com/microsoft/vscode',
            'https://github.com/facebook/react',
            'https://github.com/vercel/next.js'
          ].map(url => (
            <button
              key={url}
              type="button"
              onClick={() => setForm(prev => ({ ...prev, url }))}
              disabled={isLoading}
              className="text-xs text-blue-600 hover:text-blue-800 bg-white px-2 py-1 rounded-md border border-gray-200 hover:border-blue-300 transition-colors duration-200"
            >
              {url.split('/').slice(-1)[0]}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RepositoryInput;