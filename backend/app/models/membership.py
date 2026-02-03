"""
Membership Model

The join table between Users and Organizations.

Interview Insight:
- This is a classic "association table" pattern
- But it's more than a simple join - it has its own attributes (role, dates)
- This is sometimes called an "association object" pattern in SQLAlchemy
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User


class MemberRole(str, Enum):
    """
    Roles a member can have within an organization.
    
    Interview Insight: RBAC Implementation
    - Using Enum ensures type safety and prevents invalid roles
    - String inheritance allows direct JSON serialization
    - Roles are hierarchical: Owner > Admin > Analyst > Viewer
    
    Best Practice:
    Start with fewer roles and add more as needed.
    Too many roles early on leads to confusion and maintenance burden.
    """
    OWNER = "owner"      # Full control, billing, can delete org
    ADMIN = "admin"      # Manage members, datasets, settings
    ANALYST = "analyst"  # Create/edit analyses, upload data
    VIEWER = "viewer"    # Read-only access
    
    @classmethod
    def get_permission_level(cls, role: "MemberRole") -> int:
        """
        Returns numeric permission level for comparison.
        Higher number = more permissions.
        
        Example use:
            if user_role.permission_level >= MemberRole.ADMIN.permission_level:
                allow_action()
        """
        levels = {
            cls.OWNER: 100,
            cls.ADMIN: 75,
            cls.ANALYST: 50,
            cls.VIEWER: 25,
        }
        return levels.get(role, 0)
    
    @property
    def permission_level(self) -> int:
        return MemberRole.get_permission_level(self)
    
    def can_manage_members(self) -> bool:
        """Check if this role can invite/remove members."""
        return self in (MemberRole.OWNER, MemberRole.ADMIN)
    
    def can_upload_data(self) -> bool:
        """Check if this role can upload datasets."""
        return self in (MemberRole.OWNER, MemberRole.ADMIN, MemberRole.ANALYST)
    
    def can_delete_organization(self) -> bool:
        """Check if this role can delete the organization."""
        return self == MemberRole.OWNER


class Membership(Base, TimestampMixin):
    """
    Organization membership model.
    
    Design Decisions:
    1. Composite unique constraint on (user_id, organization_id)
       - Prevents duplicate memberships
       - Done at database level for data integrity
    
    2. is_active flag instead of deletion
       - Preserves history of who was in the org
       - Enables "rejoin" without losing context
    
    3. invited_by tracking
       - Audit trail for security
       - Useful for analytics (referral tracking)
    """
    
    __tablename__ = "memberships"
    
    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "organization_id",
            name="uq_user_organization",
        ),
    )
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Foreign keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Role within the organization
    role: Mapped[MemberRole] = mapped_column(
        String(50),
        default=MemberRole.VIEWER,
        nullable=False,
    )
    
    # Membership status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    
    # Tracking when they joined
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Who invited this member (null if org creator)
    invited_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="memberships",
        foreign_keys=[user_id],
    )
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="memberships",
    )
    invited_by: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[invited_by_id],
    )
    
    def __repr__(self) -> str:
        return f"<Membership user={self.user_id} org={self.organization_id} role={self.role}>"
