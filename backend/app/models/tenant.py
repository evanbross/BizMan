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

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


# ai: claude-sonnet-5 | 2026-09-13
class Tenant(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A single dealer. The root of multi-tenancy - every other table's `tenant_id` FKs here."""

    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(nullable=False)


# ai: claude-sonnet-5 | 2026-09-13
class Membership(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Links a Supabase Auth user to the tenant they work for. Phase 1 has no roles/permissions
    (see docs/dealer-ops-blueprint.md "Explicitly out of scope") - this table exists purely to
    resolve which tenant a logged-in user's requests are scoped to.
    """

    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("tenant_id", "user_id", name="uq_memberships_tenant_user"),)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # References Supabase's own auth.users table, not one of ours - it's provisioned by the
    # Supabase stack itself, not by our Alembic migrations. See AGENTS.md.
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False, index=True
    )
