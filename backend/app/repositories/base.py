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
from typing import Any, Generic, TypeVar

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import TenantScopedMixin

ModelT = TypeVar("ModelT", bound=TenantScopedMixin)


# ai: claude-sonnet-5 | 2026-09-13
class TenantScopedRepository(Generic[ModelT]):
    """Every query a subclass issues must go through `_select()`/this class's methods, never a
    bare `select(self.model)` - that's the one place tenant filtering is applied, and it's what
    makes cross-tenant data leakage structurally impossible rather than a convention to remember.
    See AGENTS.md "Key patterns to preserve."
    """

    model: type[ModelT]

    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id

    def _select(self):
        return select(self.model).where(self.model.tenant_id == self._tenant_id)

    async def get(self, entity_id: uuid.UUID) -> ModelT | None:
        stmt = self._select().where(self.model.id == entity_id)
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def list(self, *, limit: int = 100, offset: int = 0) -> Sequence[ModelT]:
        stmt = self._select().order_by(self.model.created_at.desc()).limit(limit).offset(offset)
        return (await self._session.execute(stmt)).scalars().all()

    async def add(self, obj: ModelT) -> ModelT:
        obj.tenant_id = self._tenant_id
        self._session.add(obj)
        await self._session.flush()
        return obj

    # ai: claude-sonnet-5 | 2026-09-13
    async def update(self, entity_id: uuid.UUID, values: dict[str, Any]) -> ModelT | None:
        """Single-statement conditional UPDATE, not SELECT-then-write - consistent with the
        counter/status-flip repositories (see PartRepository.decrement_stock, UnitRepository.
        mark_sold) even though a plain field update has no lower-bound race to guard against.
        Returns None if the row doesn't exist or isn't this tenant's.
        """
        if not values:
            return await self.get(entity_id)
        stmt = (
            update(self.model)
            .where(self.model.id == entity_id, self.model.tenant_id == self._tenant_id)
            .values(**values)
            .returning(self.model)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
