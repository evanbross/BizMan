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

from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceLineCreate,
    InvoiceLineRead,
    InvoiceRead,
    InvoiceUpdate,
)
from app.schemas.location import LocationCreate, LocationRead, LocationUpdate
from app.schemas.part import PartCreate, PartRead, PartUpdate, StockAdjustment
from app.schemas.unit import UnitCreate, UnitRead, UnitUpdate
from app.schemas.work_order import (
    WorkOrderCreate,
    WorkOrderPartCreate,
    WorkOrderPartRead,
    WorkOrderRead,
    WorkOrderUpdate,
)

__all__ = [
    "CustomerCreate",
    "CustomerRead",
    "CustomerUpdate",
    "InvoiceCreate",
    "InvoiceLineCreate",
    "InvoiceLineRead",
    "InvoiceRead",
    "InvoiceUpdate",
    "LocationCreate",
    "LocationRead",
    "LocationUpdate",
    "PartCreate",
    "PartRead",
    "PartUpdate",
    "StockAdjustment",
    "UnitCreate",
    "UnitRead",
    "UnitUpdate",
    "WorkOrderCreate",
    "WorkOrderPartCreate",
    "WorkOrderPartRead",
    "WorkOrderRead",
    "WorkOrderUpdate",
]
