export interface StandupItem {
  developer: string;
  yesterday: string[];
  today: string[];
  blockers: string[];
  mood?: string;
}

export interface TeamStandup {
  date: string;
  team_items: StandupItem[];
  summary?: string;
  key_highlights: string[];
  team_blockers: string[];
  total_developers: number;
  developers_with_blockers: number;
}

export interface ReviewFinding {
  file_path: string;
  line_number?: number;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  category: string;
  message: string;
  suggestion?: string;
  code_snippet?: string;
}

export interface CodeReview {
  pr_number: number;
  pr_title: string;
  reviewer: string;
  timestamp: string;
  summary: string;
  overall_score: number;
  findings: ReviewFinding[];
  suggestions: string[];
  approved: boolean;
  critical_issues: number;
  high_issues: number;
}

export interface DeveloperActivity {
  developer: string;
  date: string;
  total_commits: number;
  total_prs: number;
  total_issues: number;
  commits: GitHubCommit[];
  pull_requests: GitHubPullRequest[];
  issues: GitHubIssue[];
}

export interface GitHubCommit {
  sha: string;
  message: string;
  author: string;
  timestamp: string;
  url: string;
  files_changed: string[];
}

export interface GitHubPullRequest {
  number: number;
  title: string;
  body?: string;
  author: string;
  state: string;
  created_at: string;
  updated_at: string;
  url: string;
  diff_url: string;
  files_changed: string[];
  additions: number;
  deletions: number;
}

export interface GitHubIssue {
  number: number;
  title: string;
  body?: string;
  author: string;
  state: string;
  created_at: string;
  updated_at: string;
  url: string;
  labels: string[];
}

export interface DocstringGeneration {
  file_path: string;
  function_name: string;
  original_code: string;
  generated_docstring: string;
  style: string;
}

export interface TestGeneration {
  file_path: string;
  function_name: string;
  original_code: string;
  generated_test: string;
  test_framework: string;
  coverage_estimate?: number;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface GenerateRequest {
  type: 'standup' | 'review' | 'docstring' | 'test';
  data: Record<string, any>;
}