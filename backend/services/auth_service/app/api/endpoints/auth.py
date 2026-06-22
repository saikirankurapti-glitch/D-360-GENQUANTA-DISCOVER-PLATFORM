from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_db
from ...core.security import verify_password, create_access_token, create_refresh_token, decode_token
from ...repositories.user_repo import UserRepository
from ...schemas.user import UserCreate, UserResponse, Token, LoginRequest, TokenRefreshRequest
from ...models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject identifier",
        )
    user = UserRepository.get_by_id(db, int(user_id_str))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(obj_in: UserCreate, db: Session = Depends(get_db)):
    user = UserRepository.get_by_email(db, email=obj_in.email)
    if user:
        from ...core.audit_client import log_audit_event
        log_audit_event(
            action="USER_REGISTRATION",
            service_name="auth_service",
            username=obj_in.email,
            endpoint="/api/v1/auth/register",
            status="FAILURE",
            details={"reason": "Email already exists"}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )
    
    new_user = UserRepository.create(db, obj_in=obj_in)
    from ...core.audit_client import log_audit_event
    log_audit_event(
        action="USER_REGISTRATION",
        service_name="auth_service",
        user_id=new_user.id,
        username=new_user.email,
        endpoint="/api/v1/auth/register",
        status="SUCCESS"
    )
    return new_user

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = UserRepository.get_by_email(db, email=login_data.email)
    if not user or not verify_password(login_data.password, user.hashed_password):
        from ...core.audit_client import log_audit_event
        log_audit_event(
            action="USER_LOGIN",
            service_name="auth_service",
            username=login_data.email,
            endpoint="/api/v1/auth/login",
            status="FAILURE",
            details={"reason": "Incorrect email or password"}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    from ...core.audit_client import log_audit_event
    log_audit_event(
        action="USER_LOGIN",
        service_name="auth_service",
        user_id=user.id,
        username=user.email,
        endpoint="/api/v1/auth/login",
        status="SUCCESS"
    )
    
    access_token = create_access_token(subject=user.id, role=user.role)
    refresh_token = create_refresh_token(subject=user.id)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user.role
    )

@router.post("/refresh", response_model=Token)
def refresh(refresh_data: TokenRefreshRequest, db: Session = Depends(get_db)):
    payload = decode_token(refresh_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
        
    user = UserRepository.get_by_id(db, int(user_id_str))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
        
    access_token = create_access_token(subject=user.id, role=user.role)
    new_refresh_token = create_refresh_token(subject=user.id)
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        role=user.role
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
