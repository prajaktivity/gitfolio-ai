from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import uuid

from app.models.models import GitHubProfile, ProfileAnalysis, User
from app.services.github_service import GitHubService
from app.services.ai_service import generate_profile_analysis, generate_profile_slug


async def get_profile_by_user_id(db: AsyncSession, user_id: int) -> Optional[GitHubProfile]:
    result = await db.execute(
        select(GitHubProfile).where(GitHubProfile.user_id == user_id)
        .order_by(GitHubProfile.last_synced_at.desc())
    )
    return result.scalar_one_or_none()


async def get_analysis_by_slug(db: AsyncSession, slug: str) -> Optional[ProfileAnalysis]:
    result = await db.execute(
        select(ProfileAnalysis).where(
            ProfileAnalysis.slug == slug,
            ProfileAnalysis.is_public == True,
        )
    )
    return result.scalar_one_or_none()


async def get_analysis_by_user_id(db: AsyncSession, user_id: int) -> Optional[ProfileAnalysis]:
    result = await db.execute(
        select(ProfileAnalysis).where(ProfileAnalysis.user_id == user_id)
        .order_by(ProfileAnalysis.updated_at.desc())
    )
    return result.scalar_one_or_none()


async def sync_github_profile(db: AsyncSession, user: User) -> GitHubProfile:
    """Fetch latest GitHub data and update/create profile record."""
    github_service = GitHubService(user.github_access_token)
    raw_data = await github_service.analyze_profile(user.github_username)

    profile = await get_profile_by_user_id(db, user.id)
    
    if not profile:
        profile = GitHubProfile(user_id=user.id, github_username=user.github_username)
        db.add(profile)

    profile.public_repos = raw_data["public_repos"]
    profile.followers = raw_data["followers"]
    profile.following = raw_data["following"]
    profile.total_stars = raw_data["total_stars"]
    profile.total_forks = raw_data["total_forks"]
    profile.total_commits = raw_data["total_commits"]
    profile.account_age_days = raw_data["account_age_days"]
    profile.top_languages = raw_data["top_languages"]
    profile.top_repos = raw_data["top_repos"]
    profile.contribution_data = raw_data["contribution_data"]
    profile.skill_tags = raw_data["skill_tags"]

    await db.flush()
    return profile


async def create_or_update_analysis(
    db: AsyncSession, user: User, profile: GitHubProfile
) -> ProfileAnalysis:
    """Generate AI analysis and save it."""
    profile_data = {
        "github_username": profile.github_username,
        "public_repos": profile.public_repos,
        "followers": profile.followers,
        "total_stars": profile.total_stars,
        "total_forks": profile.total_forks,
        "total_commits": profile.total_commits,
        "account_age_days": profile.account_age_days,
        "top_languages": profile.top_languages,
        "top_repos": profile.top_repos,
        "contribution_data": profile.contribution_data or {},
        "skill_tags": profile.skill_tags,
    }

    ai_result = await generate_profile_analysis(profile_data)
    scores = ai_result.get("scores", {})

    analysis = await get_analysis_by_user_id(db, user.id)
    
    if not analysis:
        slug = await generate_profile_slug(
            user.github_username, ai_result.get("headline", "")
        )
        # Ensure unique slug
        existing = await get_analysis_by_slug(db, slug)
        if existing:
            slug = f"{slug}-{str(uuid.uuid4())[:6]}"

        analysis = ProfileAnalysis(
            user_id=user.id,
            profile_id=profile.id,
            slug=slug,
        )
        db.add(analysis)

    analysis.headline = ai_result.get("headline")
    analysis.summary = ai_result.get("summary")
    analysis.strengths = ai_result.get("strengths", [])
    analysis.improvement_areas = ai_result.get("improvement_areas", [])
    analysis.career_level = ai_result.get("career_level")
    analysis.recommended_roles = ai_result.get("recommended_roles", [])
    analysis.overall_score = scores.get("overall", 0)
    analysis.activity_score = scores.get("activity", 0)
    analysis.quality_score = scores.get("quality", 0)
    analysis.diversity_score = scores.get("diversity", 0)
    analysis.impact_score = scores.get("impact", 0)

    await db.flush()
    return analysis
