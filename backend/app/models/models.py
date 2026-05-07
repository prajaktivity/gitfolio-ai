from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, 
    ForeignKey, JSON, Enum as SAEnum, Float
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class PlanType(str, enum.Enum):
    FREE = "free"
    ONE_TIME = "one_time"
    PRO = "pro"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, index=True, nullable=False)
    github_username = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200))
    email = Column(String(300), index=True)
    avatar_url = Column(String(500))
    github_access_token = Column(Text)  # encrypted in prod
    plan = Column(SAEnum(PlanType), default=PlanType.FREE, nullable=False)
    stripe_customer_id = Column(String(200))
    stripe_subscription_id = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    profiles = relationship("GitHubProfile", back_populates="user", cascade="all, delete-orphan")
    analyses = relationship("ProfileAnalysis", back_populates="user", cascade="all, delete-orphan")


class GitHubProfile(Base):
    __tablename__ = "github_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    github_username = Column(String(100), index=True, nullable=False)
    
    # Raw GitHub data
    public_repos = Column(Integer, default=0)
    followers = Column(Integer, default=0)
    following = Column(Integer, default=0)
    total_stars = Column(Integer, default=0)
    total_forks = Column(Integer, default=0)
    total_commits = Column(Integer, default=0)
    account_age_days = Column(Integer, default=0)
    
    # Computed data
    top_languages = Column(JSON, default=list)      # [{"name": "Python", "percentage": 45.2, "bytes": 12345}]
    top_repos = Column(JSON, default=list)          # top 6 repos with metadata
    contribution_data = Column(JSON, default=dict)  # last 12 months activity
    skill_tags = Column(JSON, default=list)         # auto-detected ["FastAPI", "Docker", "React"]
    
    last_synced_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="profiles")
    analyses = relationship("ProfileAnalysis", back_populates="profile", cascade="all, delete-orphan")


class ProfileAnalysis(Base):
    __tablename__ = "profile_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    profile_id = Column(Integer, ForeignKey("github_profiles.id"), nullable=False)
    
    # Public profile settings
    slug = Column(String(150), unique=True, index=True)  # gitfolio.app/u/slug
    is_public = Column(Boolean, default=True)
    
    # AI-generated content
    headline = Column(String(300))                   # "Full-stack dev specializing in Python & React"
    summary = Column(Text)                           # 3-4 sentence AI narrative
    strengths = Column(JSON, default=list)           # ["Consistent contributor", "Strong Python skills"]
    improvement_areas = Column(JSON, default=list)   # ["Add more README docs", "Diversify languages"]
    career_level = Column(String(50))                # "Junior", "Mid-level", "Senior"
    recommended_roles = Column(JSON, default=list)   # ["Backend Developer", "Python Engineer"]
    
    # Scores (0-100)
    overall_score = Column(Float, default=0)
    activity_score = Column(Float, default=0)
    quality_score = Column(Float, default=0)
    diversity_score = Column(Float, default=0)
    impact_score = Column(Float, default=0)
    
    # Job matching (pro feature)
    job_description = Column(Text)
    job_match_score = Column(Float)
    job_match_feedback = Column(Text)
    
    # PDF
    pdf_url = Column(String(500))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="analyses")
    profile = relationship("GitHubProfile", back_populates="analyses")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stripe_payment_intent_id = Column(String(200), unique=True)
    stripe_session_id = Column(String(200), unique=True)
    amount = Column(Integer)  # in cents
    currency = Column(String(10), default="usd")
    plan_type = Column(SAEnum(PlanType))
    status = Column(String(50))  # succeeded, pending, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
