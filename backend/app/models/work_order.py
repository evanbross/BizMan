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

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantScopedMixin
from app.models.enums import WorkOrderStatus


# ai: claude-sonnet-5 | 2026-09-13
class WorkOrder(TenantScopedMixin, Base):
    """dropped off -> in progress -> ready -> picked up (docs/dealer-ops-blueprint.md). `unit_id`
    is nullable: the customer's unit may not have been bought there or have its serial on file.
    """

    __tablename__ = "work_orders"

    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    unit_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("units.id", ondelete="SET NULL"), default=None
    )
    status: Mapped[WorkOrderStatus] = mapped_column(nullable=False, default=WorkOrderStatus.DROPPED_OFF)
    intake_notes: Mapped[str | None] = mapped_column(default=None)


# ai: claude-sonnet-5 | 2026-09-13
class WorkOrderPart(TenantScopedMixin, Base):
    """A Part consumed against a WorkOrder ("attach Parts consumed against inventory as they're
    used" - docs/dealer-ops-blueprint.md). Recording consumption here, separate from decrementing
    Part.qty_on_hand, keeps the audit trail (which ticket used what) independent of the current
    stock level.
    """

    __tablename__ = "work_order_parts"

    work_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    part_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("parts.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    quantity: Mapped[int] = mapped_column(nullable=False, default=1)
