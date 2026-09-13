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

from sqlalchemy import ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantScopedMixin
from app.models.enums import UnitStatus


# ai: claude-sonnet-5 | 2026-09-13
class Unit(TenantScopedMixin, Base):
    """A whole-goods item (mower, tractor, etc). Serialized and tracked individually - unlike
    Part, quantity doesn't apply. Serial number is tracked from day one even though warranty/
    registration automation is Phase 2+, since retrofitting serial tracking onto sold history
    later is painful (docs/dealer-ops-blueprint.md).
    """

    __tablename__ = "units"
    __table_args__ = (UniqueConstraint("tenant_id", "serial_no", name="uq_units_tenant_serial_no"),)

    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(nullable=False)
    manufacturer: Mapped[str] = mapped_column(nullable=False)
    model: Mapped[str] = mapped_column(nullable=False)
    serial_no: Mapped[str] = mapped_column(nullable=False)
    cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[UnitStatus] = mapped_column(nullable=False, default=UnitStatus.IN_STOCK)
