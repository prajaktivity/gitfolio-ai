from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.models import PlanType


# ── Auth ──────────────────────────────────────────────────────────────────────

class GitHubCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserPublic"


# ── User ──────────────────────────────────────────────────────────────────────

class UserPublic(BaseModel):
    id: int
    github_username: str
    name: Optional[str]
    email: Optional[str]
    avatar_url: Optional[str]
    plan: PlanType
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


# ── GitHub Profile ─────────────────────────────────────────────────────────────

class LanguageStat(BaseModel):
    name: str
    percentage: float
    bytes: int
    color: Optional[str] = None


class RepoSummary(BaseModel):
    name: str
    description: Optional[str]
    url: str
    stars: int
    forks: int
    language: Optional[str]
    topics: List[str] = []
    updated_at: Optional[str]


class GitHubProfileResponse(BaseModel):
    id: int
    github_username: str
    public_repos: int
    followers: int
    following: int
    total_stars: int
    total_forks: int
    total_commits: int
    account_age_days: int
    top_languages: List[Dict[str, Any]]
    top_repos: List[Dict[str, Any]]
    skill_tags: List[str]
    last_synced_at: datetime

    class Config:
        from_attributes = True


# ── Analysis ──────────────────────────────────────────────────────────────────

class ScoreBreakdown(BaseModel):
    overall: float
    activity: float
    quality: float
    diversity: float
    impact: float


class ProfileAnalysisResponse(BaseModel):
    id: int
    slug: str
    is_public: bool
    headline: Optional[str]
    summary: Optional[str]
    strengths: List[str]
    improvement_areas: List[str]
    career_level: Optional[str]
    recommended_roles: List[str]
    scores: ScoreBreakdown
    job_match_score: Optional[float]
    job_match_feedback: Optional[str]
    pdf_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class PublicProfileResponse(BaseModel):
    user: UserPublic
    github_profile: GitHubProfileResponse
    analysis: ProfileAnalysisResponse


class JobMatchRequest(BaseModel):
    job_description: str
    analysis_id: int


class JobMatchResponse(BaseModel):
    match_score: float
    feedback: str
    matching_skills: List[str]
    missing_skills: List[str]
    recommendation: str


# ── Payments ──────────────────────────────────────────────────────────────────

class CheckoutSessionRequest(BaseModel):
    plan_type: PlanType  # one_time or pro


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str
