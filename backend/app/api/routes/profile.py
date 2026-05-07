from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io

from app.core.database import get_db
from app.core.security import get_current_user, get_optional_user
from app.models.models import User, PlanType
from app.services.profile_service import (
    sync_github_profile,
    create_or_update_analysis,
    get_analysis_by_slug,
    get_analysis_by_user_id,
    get_profile_by_user_id,
)
from app.services.ai_service import generate_job_match
from app.services.pdf_service import generate_pdf
from app.schemas.schemas import (
    GitHubProfileResponse,
    ProfileAnalysisResponse,
    PublicProfileResponse,
    JobMatchRequest,
    JobMatchResponse,
    ScoreBreakdown,
    UserPublic,
)

router = APIRouter(prefix="/profile", tags=["profile"])


@router.post("/sync", response_model=ProfileAnalysisResponse)
async def sync_and_analyze(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Sync GitHub data and regenerate AI analysis."""
    profile = await sync_github_profile(db, current_user)
    analysis = await create_or_update_analysis(db, current_user, profile)

    return ProfileAnalysisResponse(
        id=analysis.id,
        slug=analysis.slug,
        is_public=analysis.is_public,
        headline=analysis.headline,
        summary=analysis.summary,
        strengths=analysis.strengths or [],
        improvement_areas=analysis.improvement_areas or [],
        career_level=analysis.career_level,
        recommended_roles=analysis.recommended_roles or [],
        scores=ScoreBreakdown(
            overall=analysis.overall_score or 0,
            activity=analysis.activity_score or 0,
            quality=analysis.quality_score or 0,
            diversity=analysis.diversity_score or 0,
            impact=analysis.impact_score or 0,
        ),
        job_match_score=analysis.job_match_score,
        job_match_feedback=analysis.job_match_feedback,
        pdf_url=analysis.pdf_url,
        created_at=analysis.created_at,
        updated_at=analysis.updated_at,
    )


@router.get("/me", response_model=ProfileAnalysisResponse)
async def get_my_analysis(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    analysis = await get_analysis_by_user_id(db, current_user.id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Profile not yet analyzed. Run /profile/sync first.")

    return ProfileAnalysisResponse(
        id=analysis.id,
        slug=analysis.slug,
        is_public=analysis.is_public,
        headline=analysis.headline,
        summary=analysis.summary,
        strengths=analysis.strengths or [],
        improvement_areas=analysis.improvement_areas or [],
        career_level=analysis.career_level,
        recommended_roles=analysis.recommended_roles or [],
        scores=ScoreBreakdown(
            overall=analysis.overall_score or 0,
            activity=analysis.activity_score or 0,
            quality=analysis.quality_score or 0,
            diversity=analysis.diversity_score or 0,
            impact=analysis.impact_score or 0,
        ),
        job_match_score=analysis.job_match_score,
        job_match_feedback=analysis.job_match_feedback,
        pdf_url=analysis.pdf_url,
        created_at=analysis.created_at,
        updated_at=analysis.updated_at,
    )


@router.get("/public/{slug}", response_model=PublicProfileResponse)
async def get_public_profile(
    slug: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_optional_user),
):
    analysis = await get_analysis_by_slug(db, slug)
    if not analysis:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile = await get_profile_by_user_id(db, analysis.user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="GitHub data not found")

    # Mask PDF URL for free users viewing others' profiles
    pdf_url = analysis.pdf_url
    if not current_user or (current_user.id != analysis.user_id and current_user.plan == PlanType.FREE):
        pdf_url = None

    return {
        "user": analysis.user,
        "github_profile": profile,
        "analysis": ProfileAnalysisResponse(
            id=analysis.id,
            slug=analysis.slug,
            is_public=analysis.is_public,
            headline=analysis.headline,
            summary=analysis.summary,
            strengths=analysis.strengths or [],
            improvement_areas=analysis.improvement_areas or [],
            career_level=analysis.career_level,
            recommended_roles=analysis.recommended_roles or [],
            scores=ScoreBreakdown(
                overall=analysis.overall_score or 0,
                activity=analysis.activity_score or 0,
                quality=analysis.quality_score or 0,
                diversity=analysis.diversity_score or 0,
                impact=analysis.impact_score or 0,
            ),
            job_match_score=analysis.job_match_score,
            job_match_feedback=analysis.job_match_feedback,
            pdf_url=pdf_url,
            created_at=analysis.created_at,
            updated_at=analysis.updated_at,
        ),
    }


@router.post("/job-match", response_model=JobMatchResponse)
async def match_job(
    request: JobMatchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Pro feature: match profile against a job description."""
    if current_user.plan == PlanType.FREE:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Job matching is a Pro feature. Upgrade to use it.",
        )

    analysis = await get_analysis_by_user_id(db, current_user.id)
    profile = await get_profile_by_user_id(db, current_user.id)

    if not analysis or not profile:
        raise HTTPException(status_code=404, detail="Please sync your profile first.")

    profile_data = {
        "github_username": profile.github_username,
        "top_languages": profile.top_languages,
        "skill_tags": profile.skill_tags,
        "total_commits": profile.total_commits,
        "total_stars": profile.total_stars,
        "public_repos": profile.public_repos,
        "contribution_data": profile.contribution_data or {},
    }
    analysis_data = {
        "summary": analysis.summary,
        "career_level": analysis.career_level,
        "strengths": analysis.strengths,
    }

    result = await generate_job_match(profile_data, analysis_data, request.job_description)

    # Save to analysis
    analysis.job_description = request.job_description
    analysis.job_match_score = result.get("match_score")
    analysis.job_match_feedback = result.get("feedback")
    await db.flush()

    return JobMatchResponse(
        match_score=result["match_score"],
        feedback=result["feedback"],
        matching_skills=result.get("matching_skills", []),
        missing_skills=result.get("missing_skills", []),
        recommendation=result.get("recommendation", ""),
    )


@router.get("/export-pdf")
async def export_pdf(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export profile as PDF. Requires one_time or pro plan."""
    if current_user.plan == PlanType.FREE:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="PDF export requires the Full Profile plan ($9). Upgrade to download.",
        )

    analysis = await get_analysis_by_user_id(db, current_user.id)
    profile = await get_profile_by_user_id(db, current_user.id)

    if not analysis or not profile:
        raise HTTPException(status_code=404, detail="Please sync your profile first.")

    pdf_data = {
        "github_username": current_user.github_username,
        "name": current_user.name,
        "avatar_url": current_user.avatar_url,
        "headline": analysis.headline,
        "summary": analysis.summary,
        "career_level": analysis.career_level,
        "public_repos": profile.public_repos,
        "total_stars": profile.total_stars,
        "total_commits": profile.total_commits,
        "followers": profile.followers,
        "overall_score": analysis.overall_score,
        "activity_score": analysis.activity_score,
        "quality_score": analysis.quality_score,
        "diversity_score": analysis.diversity_score,
        "impact_score": analysis.impact_score,
        "top_languages": profile.top_languages,
        "skill_tags": profile.skill_tags,
        "top_repos": profile.top_repos,
        "strengths": analysis.strengths,
        "recommended_roles": analysis.recommended_roles,
    }

    pdf_bytes = await generate_pdf(pdf_data)
    filename = f"gitfolio-{current_user.github_username}.pdf"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
