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

from app.models.enums import UnitStatus
from app.models.unit import Unit
from app.repositories.base import TenantScopedRepository


# ai: claude-sonnet-5 | 2026-09-13
class UnitRepository(TenantScopedRepository[Unit]):
    model = Unit

    # ai: claude-sonnet-5 | 2026-09-13
    async def mark_sold(self, unit_id: uuid.UUID) -> Unit | None:
        """Single-statement conditional UPDATE, not SELECT-then-write: two counter staff invoicing
        the same unit at once can't both succeed. Returns None if the unit doesn't exist, isn't
        this tenant's, or was already sold - callers should treat that as "someone beat you to it."
        See AGENTS.md "Key patterns to preserve."
        """
        stmt = (
            update(Unit)
            .where(
                Unit.id == unit_id,
                Unit.tenant_id == self._tenant_id,
                Unit.status == UnitStatus.IN_STOCK,
            )
            .values(status=UnitStatus.SOLD)
            .returning(Unit)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
