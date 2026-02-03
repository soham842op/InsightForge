"""
User Model

Represents an individual user account in the system.

Interview Insight:
- Users are separate from Organizations (multi-tenant design)
- A user can belong to multiple organizations via Memberships
- Password is stored as a hash, NEVER plaintext
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, SoftDeleteMixin

# TYPE_CHECKING prevents circular imports at runtime
# This is a common pattern in Python for type hints
if TYPE_CHECKING:
    from app.models.membership import Membership


class User(Base, TimestampMixin, SoftDeleteMixin):
    """
    User account model.
    
    Design Decisions:
    1. UUID primary key instead of auto-increment integer
       - Prevents ID enumeration attacks (can't guess /users/2, /users/3)
       - Works in distributed systems (no central ID generator needed)
       - URLs don't reveal business metrics (user count)
    
    2. Email as unique identifier
       - Standard for SaaS applications
       - Case-insensitive (we'll lowercase on save)
    
    3. Separate full_name, not first_name/last_name
       - More inclusive of cultures with different naming conventions
       - Simpler to implement
    """
    
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Authentication fields
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,  # Index for fast login lookups
    )
    hashed_password: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,  # Nullable for OAuth-only users
    )
    
    # Profile fields
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    
    # Account status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,  # Requires email verification
        nullable=False,
    )
    
    # OAuth fields (for social login)
    oauth_provider: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    oauth_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    
    # Last login tracking (useful for security and analytics)
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Relationships
    # back_populates creates bidirectional relationship
    memberships: Mapped[list["Membership"]] = relationship(
        "Membership",
        back_populates="user",
        lazy="selectin",  # Eager load memberships when loading user
    )
    
    def __repr__(self) -> str:
        return f"<User {self.email}>"
    
    @property
    def organizations(self) -> list:
        """
        Convenience property to get all organizations this user belongs to.
        
        Best Practice: Properties provide a clean interface while
        hiding the underlying join table complexity.
        """
        return [m.organization for m in self.memberships if m.is_active]
