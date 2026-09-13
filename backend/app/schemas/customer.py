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

from pydantic import BaseModel, ConfigDict


# ai: claude-sonnet-5 | 2026-09-13
class CustomerCreate(BaseModel):
    name: str
    phone: str | None = None
    email: str | None = None
    address: str | None = None


# ai: claude-sonnet-5 | 2026-09-13
class CustomerUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None


# ai: claude-sonnet-5 | 2026-09-13
class CustomerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    phone: str | None
    email: str | None
    address: str | None
    created_at: datetime
    updated_at: datetime
