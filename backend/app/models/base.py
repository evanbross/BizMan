# =============================================================================
# Copyright (c) 2026 ZombieTech LLC. All rights reserved.
#
# LICENSE: Proprietary
# This source code is the confidential and proprietary property of
# ZombieTech LLC. It is provided for authorized development and operation of
# ZombieTech LLC products and services only.
# You may NOT:
#   - Use this code, in whole or in part, outside a ZombieTech LLC product or
#     service without express prior written permission
#   - Sell, sublicense, or otherwise monetize this code or derivatives of it
#     independent of a ZombieTech LLC product or service
#   - Redistribute this code without explicit written permission from
#     ZombieTech LLC
#
# No warranty is provided, express or implied. Use at your own risk.
#
# Licensing inquiries: license@zombietech.biz
# =============================================================================

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# ai: claude-sonnet-5 | 2026-09-13
class Base(DeclarativeBase):
    """Shared declarative base - `alembic/env.py` wires `target_metadata` to this."""


# ai: claude-sonnet-5 | 2026-09-13
class UUIDPrimaryKeyMixin:
    """Postgres-generated UUID primary key (`pgcrypto`'s `gen_random_uuid()`, enabled by default
    on Supabase) so rows can be inserted outside the ORM (raw SQL, Supabase dashboard) without
    losing a valid, collision-free id.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )


# ai: claude-sonnet-5 | 2026-09-13
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


# ai: claude-sonnet-5 | 2026-09-13
class TenantScopedMixin(UUIDPrimaryKeyMixin, TimestampMixin):
    """Base for every tenant-owned table. `tenant_id` is indexed on its own (not just as the lead
    column of a composite index) because `TenantScopedRepository` filters every query by it alone.

    RLS policies added in the Alembic migration are a defense-in-depth backstop only - the backend
    connects with the Supabase service-role key (which bypasses RLS), so this FK plus
    `TenantScopedRepository` filtering is the actual enforcement path. See AGENTS.md.
    """

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
