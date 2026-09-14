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

from app.routers.customer import router as customer_router
from app.routers.invoice import router as invoice_router
from app.routers.location import router as location_router
from app.routers.part import router as part_router
from app.routers.unit import router as unit_router
from app.routers.work_order import router as work_order_router

__all__ = [
    "customer_router",
    "invoice_router",
    "location_router",
    "part_router",
    "unit_router",
    "work_order_router",
]
