"""
Security Utilities

Password hashing and JWT token management.

Interview Insight:
- NEVER store passwords in plaintext
- bcrypt is the industry standard for password hashing
- JWT (JSON Web Tokens) are used for stateless authentication

Best Practice:
- Separate access tokens (short-lived) and refresh tokens (long-lived)
- Include minimal claims in JWT (just user_id, not sensitive data)
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

settings = get_settings()

# Password hashing context
# bcrypt is recommended for password hashing:
# - Automatically handles salt generation
# - Deliberately slow (prevents brute force)
# - Work factor can be increased over time
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Interview Insight:
    Q: "Why not use SHA-256 for passwords?"
    A: SHA-256 is fast (bad for passwords - enables brute force).
       bcrypt is deliberately slow and includes a salt.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Best Practice:
    This uses constant-time comparison to prevent timing attacks.
    (An attacker can't learn about the hash by measuring response time)
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
    additional_claims: dict[str, Any] | None = None,
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: Usually the user_id (as string)
        expires_delta: How long until token expires
        additional_claims: Extra data to include in token
    
    Interview Insight:
    JWT Structure: header.payload.signature
    - Header: Algorithm and token type
    - Payload: Claims (sub, exp, iat, custom data)
    - Signature: Ensures token wasn't tampered with
    
    Common Mistake:
    Don't put sensitive data (email, roles) in JWT - it's base64 encoded,
    not encrypted. Anyone can decode it. Only put data you'd be okay
    showing publicly.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode: dict[str, Any] = {
        "sub": subject,  # Subject claim (who the token is for)
        "exp": expire,   # Expiration claim
        "iat": datetime.now(timezone.utc),  # Issued at claim
        "type": "access",
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def create_refresh_token(subject: str) -> str:
    """
    Create a JWT refresh token.
    
    Refresh tokens are long-lived and used to obtain new access tokens
    without requiring the user to log in again.
    
    Trade-off:
    - Long expiry = better UX (less frequent logins)
    - Long expiry = worse security (stolen token valid longer)
    - Mitigation: Token rotation (new refresh token on each use)
    """
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }
    
    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def decode_token(token: str) -> dict[str, Any] | None:
    """
    Decode and validate a JWT token.
    
    Returns None if token is invalid or expired.
    
    Interview Insight:
    This is where token validation happens:
    1. Signature verification (was this signed by us?)
    2. Expiration check (is it still valid?)
    3. Claims extraction (what's in the token?)
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        return payload
    except JWTError:
        return None
