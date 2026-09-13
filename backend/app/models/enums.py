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

from enum import StrEnum


# ai: claude-sonnet-5 | 2026-09-13
class UnitStatus(StrEnum):
    IN_STOCK = "in_stock"
    SOLD = "sold"


# ai: claude-sonnet-5 | 2026-09-13
class InvoiceStatus(StrEnum):
    QUOTE = "quote"
    INVOICED = "invoiced"
    PAID = "paid"


# ai: claude-sonnet-5 | 2026-09-13
class WorkOrderStatus(StrEnum):
    """Phase 1 has no recovery-rate/tech-efficiency math (docs/dealer-ops-blueprint.md) - this is
    the whole lifecycle.
    """

    DROPPED_OFF = "dropped_off"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    PICKED_UP = "picked_up"
