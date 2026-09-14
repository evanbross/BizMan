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

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.unit import Unit
from app.repositories.unit import UnitRepository
from app.schemas.unit import UnitCreate, UnitUpdate

logger = logging.getLogger(__name__)


# ai: claude-sonnet-5 | 2026-09-13
class UnitService:
    """Owns the commit boundary for unit writes - the repository only flushes (see
    DATABASE_STANDARDS.md "Repository Transaction Discipline"), so this class is where the
    request-scoped session is actually committed once a write succeeds.
    """

    def __init__(self, repo: UnitRepository, session: AsyncSession) -> None:
        self._repo = repo
        self._session = session

    async def create(self, data: UnitCreate) -> Unit:
        """Raises IntegrityError on a duplicate (tenant_id, serial_no) - the router turns that
        into a 409 rather than a raw 500, per PYTHON_STANDARDS.md "Service Layer Exception
        Handling."
        """
        unit = Unit(
            location_id=data.location_id,
            category=data.category,
            manufacturer=data.manufacturer,
            model=data.model,
            serial_no=data.serial_no,
            cost=data.cost,
            price=data.price,
        )
        try:
            unit = await self._repo.add(unit)
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            logger.warning("Failed to create unit (serial_no=%s): %s", data.serial_no, exc)
            raise
        return unit

    async def get(self, unit_id: uuid.UUID) -> Unit | None:
        return await self._repo.get(unit_id)

    async def list(self, *, limit: int = 100, offset: int = 0) -> Sequence[Unit]:
        return await self._repo.list(limit=limit, offset=offset)

    async def update(self, unit_id: uuid.UUID, data: UnitUpdate) -> Unit | None:
        values = data.model_dump(exclude_unset=True)
        unit = await self._repo.update(unit_id, values)
        await self._session.commit()
        return unit

    async def mark_sold(self, unit_id: uuid.UUID) -> Unit | None:
        """None means the unit doesn't exist, isn't this tenant's, or was already sold - the
        router treats all three as a 409, matching UnitRepository.mark_sold's documented
        semantics ("someone beat you to it").
        """
        unit = await self._repo.mark_sold(unit_id)
        await self._session.commit()
        return unit
