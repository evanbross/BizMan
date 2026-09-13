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

from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TenantScopedMixin


# ai: claude-sonnet-5 | 2026-09-13
class Location(TenantScopedMixin, Base):
    """Single row in Phase 1 (docs/dealer-ops-blueprint.md), but every other operational table
    carries a `location_id` FK so multi-location isn't a schema rewrite later.
    """

    __tablename__ = "locations"

    name: Mapped[str] = mapped_column(nullable=False)
