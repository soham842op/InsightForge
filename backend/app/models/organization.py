"""
Organization Model

Represents a tenant (company/team) in the multi-tenant system.

Interview Insight:
- This is the core of multi-tenant architecture
- All tenant-specific data will have an organization_id foreign key
- The slug provides human-readable URLs (e.g., /org/acme-corp)
"""

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import String, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.membership import Membership


class Organization(Base, TimestampMixin, SoftDeleteMixin):
    """
    Organization (tenant) model.
    
    Design Decisions:
    1. Slug for URL-friendly identification
       - "acme-corp" instead of "550e8400-e29b-41d4-a716-446655440000"
       - Unique constraint ensures no collisions
    
    2. JSON settings field
       - Flexible key-value storage for org-specific settings
       - Avoids frequent schema migrations for new settings
       - Trade-off: Harder to query/index individual settings
    
    3. Usage limits
       - Essential for SaaS pricing tiers
       - Tracks datasets, storage, API calls per billing period
    """
    
    __tablename__ = "organizations"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Organization identity
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    
    # Optional description
    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    
    # Flexible settings storage
    # Example: {"timezone": "America/New_York", "dateFormat": "MM/DD/YYYY"}
    settings: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )
    
    # Usage limits (for SaaS tiers)
    # These would be updated based on subscription plan
    max_datasets: Mapped[int] = mapped_column(
        Integer,
        default=10,  # Free tier default
        nullable=False,
    )
    max_storage_mb: Mapped[int] = mapped_column(
        Integer,
        default=100,  # 100 MB for free tier
        nullable=False,
    )
    max_queries_per_month: Mapped[int] = mapped_column(
        Integer,
        default=1000,  # Free tier default
        nullable=False,
    )
    
    # Current usage tracking
    current_dataset_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    current_storage_mb: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    
    # Relationships
    memberships: Mapped[list["Membership"]] = relationship(
        "Membership",
        back_populates="organization",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<Organization {self.slug}>"
    
    @property
    def members(self) -> list:
        """Get all active members of this organization."""
        return [m.user for m in self.memberships if m.is_active]
    
    @property
    def is_at_dataset_limit(self) -> bool:
        """Check if organization has reached dataset limit."""
        return self.current_dataset_count >= self.max_datasets
    
    @property
    def is_at_storage_limit(self) -> bool:
        """Check if organization has reached storage limit."""
        return self.current_storage_mb >= self.max_storage_mb
