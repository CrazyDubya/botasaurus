"""Authentication Service"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from uuid import UUID

from ..core.config import settings
from ..core.database.models import User, Session as UserSession
from .schemas import UserCreate, UserLogin, Token


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication business logic"""

    def __init__(self, db: Session):
        self.db = db

    def register(self, user_data: UserCreate) -> Token:
        """
        Register a new user.

        Args:
            user_data: User registration data

        Returns:
            Token with access and refresh tokens

        Raises:
            HTTPException: If email already exists
        """
        # Check if user exists
        existing = self.db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash password
        password_hash = pwd_context.hash(user_data.password)

        # Create user
        user = User(
            email=user_data.email,
            password_hash=password_hash,
            name=user_data.name,
            plan="free",
            is_active=True,
            is_verified=False
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # Generate tokens
        return self._create_tokens(user)

    def login(self, credentials: UserLogin) -> Token:
        """
        Login user and return tokens.

        Args:
            credentials: Login credentials

        Returns:
            Token with access and refresh tokens

        Raises:
            HTTPException: If credentials are invalid
        """
        # Find user
        user = self.db.query(User).filter(User.email == credentials.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        if not pwd_context.verify(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )

        # Generate tokens
        return self._create_tokens(user)

    def _create_tokens(self, user: User) -> Token:
        """Create access and refresh tokens"""

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self._create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )

        # Create refresh token
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = self._create_access_token(
            data={"sub": str(user.id), "email": user.email, "type": "refresh"},
            expires_delta=refresh_token_expires
        )

        # Store session
        session = UserSession(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.utcnow() + refresh_token_expires
        )
        self.db.add(session)
        self.db.commit()

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=int(access_token_expires.total_seconds())
        )

    def _create_access_token(self, data: dict, expires_delta: timedelta) -> str:
        """Create JWT token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    def verify_token(self, token: str) -> dict:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

    def refresh_token(self, refresh_token: str) -> Token:
        """Refresh access token using refresh token"""
        payload = self.verify_token(refresh_token)

        # Check if it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Check if session exists
        session = self.db.query(UserSession).filter(
            UserSession.token == refresh_token
        ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Get user
        user = self.db.query(User).filter(User.id == session.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        # Create new tokens
        return self._create_tokens(user)

    def logout(self, token: str):
        """Logout user by deleting session"""
        session = self.db.query(UserSession).filter(
            UserSession.token == token
        ).first()

        if session:
            self.db.delete(session)
            self.db.commit()

    def get_user_by_id(self, user_id: UUID) -> User:
        """Get user by ID"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
