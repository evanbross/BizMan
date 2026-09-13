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


# ai: claude-sonnet-5 | 2026-09-13
class PartCreate(BaseModel):
    location_id: uuid.UUID
    sku: str
    description: str
    manufacturer: str
    qty_on_hand: int = 0
    reorder_threshold: int = 0
    cost: Decimal
    price: Decimal


# ai: claude-sonnet-5 | 2026-09-13
class PartUpdate(BaseModel):
    """`qty_on_hand` isn't here - it only moves through PartRepository.decrement_stock /
    increment_stock's race-safe conditional UPDATEs, never a generic field patch.
    """

    description: str | None = None
    manufacturer: str | None = None
    reorder_threshold: int | None = None
    cost: Decimal | None = None
    price: Decimal | None = None


# ai: claude-sonnet-5 | 2026-09-13
class PartRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    location_id: uuid.UUID
    sku: str
    description: str
    manufacturer: str
    qty_on_hand: int
    reorder_threshold: int
    cost: Decimal
    price: Decimal
    created_at: datetime
    updated_at: datetime


# ai: claude-sonnet-5 | 2026-09-13
class StockAdjustment(BaseModel):
    """Body for the increment/decrement-stock endpoints."""

    quantity: int
