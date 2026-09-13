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

from pydantic import BaseModel, ConfigDict

from app.models.enums import UnitStatus


# ai: claude-sonnet-5 | 2026-09-13
class UnitCreate(BaseModel):
    location_id: uuid.UUID
    category: str
    manufacturer: str
    model: str
    serial_no: str
    cost: Decimal
    price: Decimal


# ai: claude-sonnet-5 | 2026-09-13
class UnitUpdate(BaseModel):
    """`status` isn't here - it only changes via the dedicated mark-sold endpoint's race-safe
    conditional UPDATE (UnitRepository.mark_sold), never a generic field patch.
    """

    category: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    cost: Decimal | None = None
    price: Decimal | None = None


# ai: claude-sonnet-5 | 2026-09-13
class UnitRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    location_id: uuid.UUID
    category: str
    manufacturer: str
    model: str
    serial_no: str
    cost: Decimal
    price: Decimal
    status: UnitStatus
    created_at: datetime
    updated_at: datetime
