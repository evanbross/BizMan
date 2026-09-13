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
from collections.abc import Sequence

from sqlalchemy import select

from app.models.work_order import WorkOrder, WorkOrderPart
from app.repositories.base import TenantScopedRepository


# ai: claude-sonnet-5 | 2026-09-13
class WorkOrderRepository(TenantScopedRepository[WorkOrder]):
    model = WorkOrder

    # ai: claude-sonnet-5 | 2026-09-13
    async def list_parts_used(self, work_order_id: uuid.UUID) -> Sequence[WorkOrderPart]:
        stmt = select(WorkOrderPart).where(WorkOrderPart.work_order_id == work_order_id)
        return (await self._session.execute(stmt)).scalars().all()

    # ai: claude-sonnet-5 | 2026-09-13
    async def add_part_used(self, part_used: WorkOrderPart) -> WorkOrderPart:
        """Records consumption only - callers must separately call
        `PartRepository.decrement_stock()` to actually move inventory; this repository doesn't
        reach across into Part's table itself. See AGENTS.md "Key patterns to preserve."
        """
        part_used.tenant_id = self._tenant_id
        self._session.add(part_used)
        await self._session.flush()
        return part_used
