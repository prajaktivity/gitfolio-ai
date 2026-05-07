export type PlanType = "free" | "one_time" | "pro";

export interface User {
  id: number;
  github_username: string;
  name?: string;
  email?: string;
  avatar_url?: string;
  plan: PlanType;
  created_at: string;
}

export interface Language {
  name: string;
  percentage: number;
  bytes: number;
  color: string;
}

export interface Repo {
  name: string;
  description?: string;
  url: string;
  stars: number;
  forks: number;
  language?: string;
  topics: string[];
  updated_at?: string;
}

export interface GitHubProfile {
  id: number;
  github_username: string;
  public_repos: number;
  followers: number;
  following: number;
  total_stars: number;
  total_forks: number;
  total_commits: number;
  account_age_days: number;
  top_languages: Language[];
  top_repos: Repo[];
  skill_tags: string[];
  last_synced_at: string;
}

export interface ScoreBreakdown {
  overall: number;
  activity: number;
  quality: number;
  diversity: number;
  impact: number;
}

export interface ProfileAnalysis {
  id: number;
  slug: string;
  is_public: boolean;
  headline?: string;
  summary?: string;
  strengths: string[];
  improvement_areas: string[];
  career_level?: string;
  recommended_roles: string[];
  scores: ScoreBreakdown;
  job_match_score?: number;
  job_match_feedback?: string;
  pdf_url?: string;
  created_at: string;
  updated_at?: string;
}

export interface PublicProfile {
  user: User;
  github_profile: GitHubProfile;
  analysis: ProfileAnalysis;
}

export interface Plan {
  id: string;
  name: string;
  price: number;
  billing: string;
  features: string[];
  cta: string;
  highlighted?: boolean;
}
