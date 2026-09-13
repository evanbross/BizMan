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

# Every model must be imported here, even if unused directly, so `Base.metadata` (wired into
# alembic/env.py) sees every table when autogenerating migrations.
from app.models.base import Base
from app.models.customer import Customer
from app.models.external import auth_users  # noqa: F401 - registers the table for FK resolution
from app.models.invoice import Invoice, InvoiceLine
from app.models.location import Location
from app.models.part import Part
from app.models.tenant import Membership, Tenant
from app.models.unit import Unit
from app.models.work_order import WorkOrder, WorkOrderPart

__all__ = [
    "Base",
    "Customer",
    "Invoice",
    "InvoiceLine",
    "Location",
    "Membership",
    "Part",
    "Tenant",
    "Unit",
    "WorkOrder",
    "WorkOrderPart",
]
