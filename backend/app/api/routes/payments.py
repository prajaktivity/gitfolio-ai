from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
import stripe
import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.models import User, PlanType, Payment
from app.services.user_service import upgrade_user_plan
from app.schemas.schemas import CheckoutSessionRequest, CheckoutSessionResponse

stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/create-checkout", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if request.plan_type == PlanType.FREE:
        raise HTTPException(status_code=400, detail="Cannot checkout for free plan")

    if request.plan_type == PlanType.ONE_TIME:
        price_id = settings.STRIPE_ONE_TIME_PRICE_ID
        mode = "payment"
    else:
        price_id = settings.STRIPE_SUBSCRIPTION_PRICE_ID
        mode = "subscription"

    session = stripe.checkout.Session.create(
        customer_email=current_user.email,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode=mode,
        success_url=f"{settings.FRONTEND_URL}/dashboard?upgrade=success",
        cancel_url=f"{settings.FRONTEND_URL}/pricing?upgrade=cancelled",
        metadata={
            "user_id": str(current_user.id),
            "plan_type": request.plan_type.value,
        },
    )

    return CheckoutSessionResponse(
        checkout_url=session.url,
        session_id=session.id,
    )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = int(session["metadata"]["user_id"])
        plan_type = session["metadata"]["plan_type"]

        plan = PlanType(plan_type)
        stripe_data = {
            "customer_id": session.get("customer"),
            "subscription_id": session.get("subscription"),
        }
        await upgrade_user_plan(db, user_id, plan, stripe_data)

        # Record payment
        payment = Payment(
            user_id=user_id,
            stripe_payment_intent_id=session.get("payment_intent"),
            stripe_session_id=session["id"],
            amount=session.get("amount_total", 0),
            currency=session.get("currency", "usd"),
            plan_type=plan,
            status="succeeded",
        )
        db.add(payment)
        await db.flush()

    elif event["type"] == "customer.subscription.deleted":
        # Downgrade to free on subscription cancellation
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]
        
        from sqlalchemy import select
        from app.models.models import User as UserModel
        result = await db.execute(
            select(UserModel).where(UserModel.stripe_customer_id == customer_id)
        )
        user = result.scalar_one_or_none()
        if user:
            user.plan = PlanType.FREE
            user.stripe_subscription_id = None
            await db.flush()

    return {"status": "ok"}


@router.get("/plans")
async def get_plans():
    return {
        "plans": [
            {
                "id": "free",
                "name": "Free",
                "price": 0,
                "billing": "forever",
                "features": [
                    "GitHub profile analysis",
                    "AI-generated summary",
                    "Shareable public URL",
                    "Skill breakdown",
                    "Basic score metrics",
                ],
                "cta": "Get Started",
            },
            {
                "id": "one_time",
                "name": "Full Profile",
                "price": 9,
                "billing": "one-time",
                "features": [
                    "Everything in Free",
                    "Remove GitFolio watermark",
                    "PDF export (recruiter-ready)",
                    "Detailed improvement tips",
                    "Priority re-analysis",
                    "Multiple GitHub profiles",
                ],
                "cta": "Buy Once",
                "highlighted": True,
            },
            {
                "id": "pro",
                "name": "Job Hunter",
                "price": 5,
                "billing": "per month",
                "features": [
                    "Everything in Full Profile",
                    "Job description matcher",
                    "Skill gap analysis per role",
                    "Unlimited re-analyses",
                    "Interview prep tips",
                ],
                "cta": "Go Pro",
            },
        ]
    }
