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

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import WorkOrderStatus


# ai: claude-sonnet-5 | 2026-09-13
class WorkOrderCreate(BaseModel):
    """Status isn't here - every work order starts at `dropped_off` (WorkOrder.status's model
    default).
    """

    location_id: uuid.UUID
    customer_id: uuid.UUID
    unit_id: uuid.UUID | None = None
    intake_notes: str | None = None


# ai: claude-sonnet-5 | 2026-09-13
class WorkOrderUpdate(BaseModel):
    status: WorkOrderStatus | None = None
    intake_notes: str | None = None


# ai: claude-sonnet-5 | 2026-09-13
class WorkOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    location_id: uuid.UUID
    customer_id: uuid.UUID
    unit_id: uuid.UUID | None
    status: WorkOrderStatus
    intake_notes: str | None
    created_at: datetime
    updated_at: datetime


# ai: claude-sonnet-5 | 2026-09-13
class WorkOrderPartCreate(BaseModel):
    part_id: uuid.UUID
    quantity: int = Field(default=1, gt=0)


# ai: claude-sonnet-5 | 2026-09-13
class WorkOrderPartRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    work_order_id: uuid.UUID
    part_id: uuid.UUID
    quantity: int
    created_at: datetime
