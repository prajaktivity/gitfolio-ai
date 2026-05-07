from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.models.models import User, PlanType


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_github_id(db: AsyncSession, github_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.github_id == github_id))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(
        select(User).where(User.github_username == username)
    )
    return result.scalar_one_or_none()


async def create_or_update_user(db: AsyncSession, github_data: dict, access_token: str) -> User:
    user = await get_user_by_github_id(db, github_data["github_id"])
    
    if user:
        user.name = github_data.get("name", user.name)
        user.email = github_data.get("email", user.email)
        user.avatar_url = github_data.get("avatar_url", user.avatar_url)
        user.github_access_token = access_token
        await db.flush()
        return user
    
    user = User(
        github_id=github_data["github_id"],
        github_username=github_data["github_username"],
        name=github_data.get("name"),
        email=github_data.get("email"),
        avatar_url=github_data.get("avatar_url"),
        github_access_token=access_token,
        plan=PlanType.FREE,
    )
    db.add(user)
    await db.flush()
    return user


async def upgrade_user_plan(db: AsyncSession, user_id: int, plan: PlanType, stripe_data: dict = None) -> User:
    user = await get_user_by_id(db, user_id)
    if not user:
        raise ValueError("User not found")
    
    user.plan = plan
    if stripe_data:
        user.stripe_customer_id = stripe_data.get("customer_id", user.stripe_customer_id)
        user.stripe_subscription_id = stripe_data.get("subscription_id", user.stripe_subscription_id)
    
    await db.flush()
    return user
