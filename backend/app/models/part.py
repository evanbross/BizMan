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
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantScopedMixin


# ai: claude-sonnet-5 | 2026-09-13
class Part(TenantScopedMixin, Base):
    """Non-serialized, quantity-tracked inventory (docs/dealer-ops-blueprint.md). `qty_on_hand`
    is only ever changed through PartRepository.adjust_stock's single-statement conditional
    UPDATE - never read-modify-write - so concurrent sales/work-order consumption can't race
    past zero. See AGENTS.md "Key patterns to preserve."
    """

    __tablename__ = "parts"
    __table_args__ = (
        UniqueConstraint("tenant_id", "sku", name="uq_parts_tenant_sku"),
        CheckConstraint("qty_on_hand >= 0", name="ck_parts_qty_on_hand_non_negative"),
    )

    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    sku: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    manufacturer: Mapped[str] = mapped_column(nullable=False)
    qty_on_hand: Mapped[int] = mapped_column(nullable=False, default=0)
    reorder_threshold: Mapped[int] = mapped_column(nullable=False, default=0)
    cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
