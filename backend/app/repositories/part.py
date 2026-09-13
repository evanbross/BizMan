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

from sqlalchemy import update

from app.models.part import Part
from app.repositories.base import TenantScopedRepository


# ai: claude-sonnet-5 | 2026-09-13
class PartRepository(TenantScopedRepository[Part]):
    model = Part

    # ai: claude-sonnet-5 | 2026-09-13
    async def decrement_stock(self, part_id: uuid.UUID, quantity: int) -> Part | None:
        """Single-statement conditional UPDATE guarding on current `qty_on_hand`, not a
        SELECT-then-write: a parts-counter sale and a work order consuming the same part at once
        can't both succeed past zero. Returns None if the part doesn't exist, isn't this tenant's,
        or doesn't have `quantity` on hand - callers should surface that as "insufficient stock,"
        not silently go negative. See AGENTS.md "Key patterns to preserve."
        """
        stmt = (
            update(Part)
            .where(
                Part.id == part_id,
                Part.tenant_id == self._tenant_id,
                Part.qty_on_hand >= quantity,
            )
            .values(qty_on_hand=Part.qty_on_hand - quantity)
            .returning(Part)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ai: claude-sonnet-5 | 2026-09-13
    async def increment_stock(self, part_id: uuid.UUID, quantity: int) -> Part | None:
        """Restock / return path - no lower-bound race to guard against, but still a single
        UPDATE rather than SELECT-then-write for consistency with decrement_stock.
        """
        stmt = (
            update(Part)
            .where(Part.id == part_id, Part.tenant_id == self._tenant_id)
            .values(qty_on_hand=Part.qty_on_hand + quantity)
            .returning(Part)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
