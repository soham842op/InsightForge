"""
Base Model with Common Fields

This base class provides fields that every table should have.

Best Practice:
- All tables should have created_at and updated_at for debugging and auditing
- UUID primary keys prevent ID enumeration attacks and work well in distributed systems
- Soft deletes (is_deleted) preserve data integrity and enable recovery
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    
    Interview Insight:
    Using a custom base class with shared columns is called the
    "Template Method" pattern. It ensures consistency across all
    models and reduces code duplication (DRY principle).
    """
    pass


class TimestampMixin:
    """
    Mixin for created_at and updated_at timestamps.
    
    Best Practice:
    - server_default uses database's NOW() function, not Python's datetime
    - This ensures consistency even with multiple app servers
    - onupdate automatically updates the timestamp on any change
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """
    Mixin for soft delete functionality.
    
    Trade-off:
    Soft deletes add complexity (every query needs is_deleted=False filter)
    but provide safety and auditability.
    
    Alternative: Use a separate "archive" table for deleted records.
    We chose inline soft delete for simplicity.
    """
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,  # Index for faster filtering
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
