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
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import InvoiceStatus


# ai: claude-sonnet-5 | 2026-09-13
class InvoiceCreate(BaseModel):
    """Status isn't here - every invoice starts at `quote` (Invoice.status's model default)."""

    location_id: uuid.UUID
    customer_id: uuid.UUID


# ai: claude-sonnet-5 | 2026-09-13
class InvoiceUpdate(BaseModel):
    status: InvoiceStatus | None = None
    payment_note: str | None = None


# ai: claude-sonnet-5 | 2026-09-13
class InvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    location_id: uuid.UUID
    customer_id: uuid.UUID
    status: InvoiceStatus
    payment_note: str | None
    created_at: datetime
    updated_at: datetime


# ai: claude-sonnet-5 | 2026-09-13
class InvoiceLineCreate(BaseModel):
    unit_id: uuid.UUID | None = None
    part_id: uuid.UUID | None = None
    description: str
    quantity: int = Field(default=1, gt=0)
    unit_price: Decimal

    # ai: claude-sonnet-5 | 2026-09-13
    @model_validator(mode="after")
    def _exactly_one_of_unit_or_part(self) -> "InvoiceLineCreate":
        if (self.unit_id is None) == (self.part_id is None):
            raise ValueError("exactly one of unit_id or part_id must be set")
        return self


# ai: claude-sonnet-5 | 2026-09-13
class InvoiceLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    invoice_id: uuid.UUID
    unit_id: uuid.UUID | None
    part_id: uuid.UUID | None
    description: str
    quantity: int
    unit_price: Decimal
    created_at: datetime
