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

import logging
import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.work_order import WorkOrder, WorkOrderPart
from app.repositories.part import PartRepository
from app.repositories.work_order import WorkOrderRepository
from app.schemas.work_order import WorkOrderCreate, WorkOrderPartCreate, WorkOrderUpdate
from app.services.exceptions import ServiceConflictError

logger = logging.getLogger(__name__)


# ai: claude-sonnet-5 | 2026-09-13
class WorkOrderService:
    """Owns the commit boundary for work order writes, including the cross-entity side effect of
    `add_part_used` (decrementing a Part's stock) - the repository layer only flushes (see
    DATABASE_STANDARDS.md "Repository Transaction Discipline"). Coordinating PartRepository from
    here, rather than from the router, keeps the "work the ticket" business rule
    (docs/dealer-ops-blueprint.md) out of the router entirely.
    """

    def __init__(
        self, repo: WorkOrderRepository, part_repo: PartRepository, session: AsyncSession
    ) -> None:
        self._repo = repo
        self._part_repo = part_repo
        self._session = session

    async def create(self, data: WorkOrderCreate) -> WorkOrder:
        work_order = await self._repo.add(
            WorkOrder(
                location_id=data.location_id,
                customer_id=data.customer_id,
                unit_id=data.unit_id,
                intake_notes=data.intake_notes,
            )
        )
        await self._session.commit()
        return work_order

    async def get(self, work_order_id: uuid.UUID) -> WorkOrder | None:
        return await self._repo.get(work_order_id)

    async def list(self, *, limit: int = 100, offset: int = 0) -> Sequence[WorkOrder]:
        return await self._repo.list(limit=limit, offset=offset)

    async def update(self, work_order_id: uuid.UUID, data: WorkOrderUpdate) -> WorkOrder | None:
        values = data.model_dump(exclude_unset=True)
        work_order = await self._repo.update(work_order_id, values)
        await self._session.commit()
        return work_order

    async def list_parts_used(self, work_order_id: uuid.UUID) -> Sequence[WorkOrderPart] | None:
        """None means the work order doesn't exist or isn't this tenant's - distinct from an
        empty list of parts on a real work order. WorkOrderRepository.list_parts_used has no
        tenant filter of its own (see its docstring), so this `get()` is what makes the lookup
        tenant-scoped.
        """
        work_order = await self._repo.get(work_order_id)
        if work_order is None:
            return None
        return await self._repo.list_parts_used(work_order_id)

    async def add_part_used(
        self, work_order_id: uuid.UUID, data: WorkOrderPartCreate
    ) -> WorkOrderPart | None:
        """None means the work order doesn't exist. Raises ServiceConflictError if the Part
        doesn't have `quantity` on hand - the router turns that into a 409.
        """
        work_order = await self._repo.get(work_order_id)
        if work_order is None:
            return None

        part = await self._part_repo.decrement_stock(data.part_id, data.quantity)
        if part is None:
            raise ServiceConflictError("Insufficient stock or part not found")

        part_used = await self._repo.add_part_used(
            WorkOrderPart(work_order_id=work_order_id, part_id=data.part_id, quantity=data.quantity)
        )
        await self._session.commit()
        return part_used
