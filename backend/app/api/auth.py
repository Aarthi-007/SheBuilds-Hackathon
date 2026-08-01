from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserDTO, StandardResponse, UpdateProfileRequest
from app.services.auth_service import AuthService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Module 1 - Authentication & Users"])

@router.post("/register", response_model=StandardResponse)
async def register(req: RegisterRequest):
    user, org, access_token, refresh_token = await AuthService.register(req)
    user_dto = UserDTO(
        id=str(user.id),
        organization_id=str(org.id),
        full_name=user.full_name,
        email=user.email,
        role=user.role
    )
    token_resp = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_dto
    )
    return StandardResponse(
        success=True,
        message="User registered successfully",
        data=token_resp
    )

@router.post("/login", response_model=StandardResponse)
async def login(req: LoginRequest):
    user, org, access_token, refresh_token = await AuthService.login(req)
    user_dto = UserDTO(
        id=str(user.id),
        organization_id=str(org.id),
        full_name=user.full_name,
        email=user.email,
        role=user.role
    )
    token_resp = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_dto
    )
    return StandardResponse(
        success=True,
        message="Login successful",
        data=token_resp
    )

@router.get("/me", response_model=StandardResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    user_dto = UserDTO(
        id=str(current_user.id),
        organization_id=current_user.organization_id,
        full_name=current_user.full_name,
        email=current_user.email,
        role=current_user.role
    )
    return StandardResponse(success=True, data=user_dto)

@router.put("/profile", response_model=StandardResponse)
async def update_profile(req: UpdateProfileRequest, current_user: User = Depends(get_current_user)):
    if req.full_name: current_user.full_name = req.full_name
    if req.email: current_user.email = req.email
    await current_user.save()
    user_dto = UserDTO(
        id=str(current_user.id),
        organization_id=current_user.organization_id,
        full_name=current_user.full_name,
        email=current_user.email,
        role=current_user.role
    )
    return StandardResponse(success=True, message="Profile updated", data=user_dto)
