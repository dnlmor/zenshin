// API Response Types
export interface Repository {
  name: string;
  url: string;
  languages: string[];
  total_files_analyzed: number;
}

export interface Strength {
  title: string;
  description: string;
}

export interface Improvement {
  title: string;
  score: string;
  issue: string;
  action: string;
}

export interface CodeExample {
  before: string;
  after: string;
}

export interface Analysis {
  overall_score: number;
  summary: string;
  strengths: Strength[];
  improvements: Improvement[];
  code_examples: CodeExample;
  final_thoughts: string;
}

export interface AnalysisResponse {
  repository: Repository;
  analysis: Analysis;
  raw_review: string;
  timestamp: string;
}

// Request Types
export interface AnalysisRequest {
  github_url: string;
  project_description?: string;
  project_goals?: string[];
  focus_areas?: string[];
  experience_level?: string;
}

// UI State Types
export interface AnalysisState {
  isLoading: boolean;
  data: AnalysisResponse | null;
  error: string | null;
}

// Form Types
export interface RepositoryForm {
  url: string;
  description: string;
  goals: string[];
  focusAreas: string[];
  experienceLevel: ExperienceLevel;
}

export type ExperienceLevel = 'beginner' | 'intermediate' | 'advanced' | '';

// Component Props Types
export interface ScoreDisplayProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
}

export interface StrengthsListProps {
  strengths: Strength[];
}

export interface ImprovementsListProps {
  improvements: Improvement[];
}

export interface CodeExampleProps {
  codeExample: CodeExample;
  language?: string;
}

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
}

// Constants Types
export type FocusArea = 'security' | 'performance' | 'maintainability' | 'style' | 'testing';

export interface FormValidation {
  isValid: boolean;
  errors: Record<string, string>;
}