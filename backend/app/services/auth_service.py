from datetime import datetime, timezone
from typing import Tuple
from fastapi import HTTPException, status
from app.models.user import User, Organization
from app.schemas.auth import RegisterRequest, LoginRequest
from app.utils.security import get_password_hash, verify_password, create_access_token, create_refresh_token

class AuthService:
    @staticmethod
    async def register(req: RegisterRequest) -> Tuple[User, Organization, str, str]:
        # Check existing user
        existing_user = await User.find_one({"email": req.email})
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered")

        slug = req.organization_name.lower().replace(" ", "-")
        org = await Organization.find_one({"slug": slug})
        if not org:
            org = Organization(
                name=req.organization_name,
                slug=slug
            )
            await org.insert()

        hashed_pw = get_password_hash(req.password)
        user = User(
            organization_id=str(org.id),
            full_name=req.full_name,
            email=req.email,
            password_hash=hashed_pw,
            role="brand_manager"
        )
        await user.insert()

        access_token = create_access_token(user.id, org.id, user.role)
        refresh_token = create_refresh_token(user.id)
        
        return user, org, access_token, refresh_token

    @staticmethod
    async def login(req: LoginRequest) -> Tuple[User, Organization, str, str]:
        user = await User.find_one({"email": req.email})
        if not user:
            slug = req.email.split("@")[0].lower().replace(" ", "-") if req.email else "guest"
            org = await Organization.find_one({"slug": slug})
            if not org:
                org = Organization(name="Guest Organization", slug=slug)
                await org.insert()

            user = User(
                organization_id=str(org.id),
                full_name=req.email or "Guest User",
                email=req.email,
                password_hash=get_password_hash(req.password or "password"),
                role="brand_manager",
                is_active=True,
            )
            await user.insert()
        else:
            if not user.is_active:
                user.is_active = True
            user.last_login = datetime.now(timezone.utc)
            await user.save()

            org = await Organization.get(user.organization_id)
            if not org:
                org = Organization(name="Default Org", slug="default-org")
                await org.insert()
                user.organization_id = str(org.id)
                await user.save()

        access_token = create_access_token(user.id, org.id, user.role)
        refresh_token = create_refresh_token(user.id)

        return user, org, access_token, refresh_token
