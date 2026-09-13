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

from sqlalchemy import CheckConstraint, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantScopedMixin
from app.models.enums import InvoiceStatus


# ai: claude-sonnet-5 | 2026-09-13
class Invoice(TenantScopedMixin, Base):
    """Quote-to-invoice flow (docs/dealer-ops-blueprint.md). Status starts at `quote`; a quote
    becomes real once staff invoice it, and `paid` is recorded as a note-field payment method in
    Phase 1 - no payment processing integration yet.
    """

    __tablename__ = "invoices"

    location_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("locations.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    status: Mapped[InvoiceStatus] = mapped_column(nullable=False, default=InvoiceStatus.QUOTE)
    payment_note: Mapped[str | None] = mapped_column(default=None)


# ai: claude-sonnet-5 | 2026-09-13
class InvoiceLine(TenantScopedMixin, Base):
    """A line references either a Unit or a Part, never both or neither - one sales flow for both
    (docs/dealer-ops-blueprint.md). `unit_price`/`description` are captured at sale time rather
    than joined live from Unit/Part, so a later price or description change doesn't rewrite
    invoice history.
    """

    __tablename__ = "invoice_lines"
    __table_args__ = (
        CheckConstraint(
            "(unit_id IS NOT NULL) != (part_id IS NOT NULL)",
            name="ck_invoice_lines_exactly_one_of_unit_or_part",
        ),
    )

    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True
    )
    unit_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("units.id", ondelete="RESTRICT"), default=None
    )
    part_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("parts.id", ondelete="RESTRICT"), default=None
    )
    description: Mapped[str] = mapped_column(nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False, default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
