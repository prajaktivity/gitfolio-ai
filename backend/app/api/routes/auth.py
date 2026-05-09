from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import secrets

from app.core.database import get_db
from app.core.security import create_access_token, get_current_user
from app.core.config import settings
from app.services.github_service import GitHubService, exchange_code_for_token
from app.services.user_service import create_or_update_user
from app.schemas.schemas import TokenResponse, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/github/login")
async def github_login():
    """Redirect to GitHub OAuth authorization page."""
    state = secrets.token_urlsafe(16)
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
        "scope": "read:user user:email repo",
        "state": state,
    }
    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(f"https://github.com/login/oauth/authorize?{query_string}")


@router.get("/github/callback")
async def github_callback(
    code: str,
    state: str = None,
    db: AsyncSession = Depends(get_db),
):
    """Handle GitHub OAuth callback and return JWT token."""
    access_token = await exchange_code_for_token(code)
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange code for GitHub token",
        )

    github_service = GitHubService(access_token)
    github_user = await github_service.get_user()

    user_data = {
        "github_id": github_user["id"],
        "github_username": github_user["login"],
        "name": github_user.get("name"),
        "email": github_user.get("email"),
        "avatar_url": github_user.get("avatar_url"),
    }

    user = await create_or_update_user(db, user_data, access_token)
    jwt_token = create_access_token({"sub": str(user.id)})

    # Redirect to frontend with token
    return RedirectResponse(
        f"{settings.FRONTEND_URL}/auth/callback?token={jwt_token}"
    )


@router.get("/me", response_model=UserPublic)
async def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}
