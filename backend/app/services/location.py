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

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.location import Location
from app.repositories.location import LocationRepository
from app.schemas.location import LocationCreate, LocationUpdate


# ai: claude-sonnet-5 | 2026-09-13
class LocationService:
    """Owns the commit boundary for location writes - the repository only flushes (see
    DATABASE_STANDARDS.md "Repository Transaction Discipline"), so this class is where the
    request-scoped session is actually committed once a write succeeds.
    """

    def __init__(self, repo: LocationRepository, session: AsyncSession) -> None:
        self._repo = repo
        self._session = session

    async def create(self, data: LocationCreate) -> Location:
        location = await self._repo.add(Location(name=data.name))
        await self._session.commit()
        return location

    async def get(self, location_id: uuid.UUID) -> Location | None:
        return await self._repo.get(location_id)

    async def list(self, *, limit: int = 100, offset: int = 0) -> Sequence[Location]:
        return await self._repo.list(limit=limit, offset=offset)

    async def update(self, location_id: uuid.UUID, data: LocationUpdate) -> Location | None:
        values = data.model_dump(exclude_unset=True)
        location = await self._repo.update(location_id, values)
        await self._session.commit()
        return location
