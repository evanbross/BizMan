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

from app.models.part import Part
from app.repositories.part import PartRepository
from app.schemas.part import PartCreate, PartUpdate

logger = logging.getLogger(__name__)


# ai: claude-sonnet-5 | 2026-09-13
class PartService:
    """Owns the commit boundary for part writes - the repository only flushes (see
    DATABASE_STANDARDS.md "Repository Transaction Discipline"), so this class is where the
    request-scoped session is actually committed once a write succeeds.
    """

    def __init__(self, repo: PartRepository, session: AsyncSession) -> None:
        self._repo = repo
        self._session = session

    async def create(self, data: PartCreate) -> Part:
        """Raises IntegrityError on a duplicate (tenant_id, sku) - the router turns that into a
        409 rather than a raw 500, per PYTHON_STANDARDS.md "Service Layer Exception Handling."
        """
        part = Part(
            location_id=data.location_id,
            sku=data.sku,
            description=data.description,
            manufacturer=data.manufacturer,
            qty_on_hand=data.qty_on_hand,
            reorder_threshold=data.reorder_threshold,
            cost=data.cost,
            price=data.price,
        )
        try:
            part = await self._repo.add(part)
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            logger.warning("Failed to create part (sku=%s): %s", data.sku, exc)
            raise
        return part

    async def get(self, part_id: uuid.UUID) -> Part | None:
        return await self._repo.get(part_id)

    async def list(self, *, limit: int = 100, offset: int = 0) -> Sequence[Part]:
        return await self._repo.list(limit=limit, offset=offset)

    async def update(self, part_id: uuid.UUID, data: PartUpdate) -> Part | None:
        values = data.model_dump(exclude_unset=True)
        part = await self._repo.update(part_id, values)
        await self._session.commit()
        return part

    async def increment_stock(self, part_id: uuid.UUID, quantity: int) -> Part | None:
        part = await self._repo.increment_stock(part_id, quantity)
        await self._session.commit()
        return part

    async def decrement_stock(self, part_id: uuid.UUID, quantity: int) -> Part | None:
        """None means the part doesn't exist, isn't this tenant's, or doesn't have `quantity` on
        hand - the router treats all three as a 409, matching PartRepository.decrement_stock's
        documented semantics ("insufficient stock").
        """
        part = await self._repo.decrement_stock(part_id, quantity)
        await self._session.commit()
        return part
