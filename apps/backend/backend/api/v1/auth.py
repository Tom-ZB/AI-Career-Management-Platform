"""
Authentication and user authorization routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.dependencies import get_db
from backend.crud import user as crud_user
from backend.schemas.user import UserCreate, User, Token
from backend.core import security
from backend.api import deps

auth_router = APIRouter()


@auth_router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate, db: Session = Depends(get_db)
):
    """
    Register a new user.
    """
    # Check for existing user by email or username
    existing_email = crud_user.get_by_email(db, email=user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    existing_username = crud_user.get_by_username(db, username=user_in.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    new_user = crud_user.create(db, obj_in=user_in)
    return new_user


@auth_router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    OAuth2 compatible token login, get an access token for further requests.
    """
    user = crud_user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive",
        )

    # Create access and refresh tokens
    access_token = security.create_access_token(subject=str(user.id))
    refresh_token = security.create_refresh_token(subject=str(user.id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@auth_router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_token_body: Token,
    db: Session = Depends(get_db),
):
    """
    Refresh expired access tokens with a valid refresh token.
    """
    payload = security.verify_token(refresh_token_body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user_id = payload.get("sub")
    user = crud_user.get(db, id=int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    access_token = security.create_access_token(subject=str(user.id))
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
    current_user: User = Depends(deps.get_current_user),
):
    """
    Logout user (client-side token deletion).
    """
    return {"detail": "Logout successful - delete the token on client side"}