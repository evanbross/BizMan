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

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.core.dependencies import get_unit_service
from app.schemas.unit import UnitCreate, UnitRead, UnitUpdate
from app.services.unit import UnitService

router = APIRouter(prefix="/units", tags=["units"])


# ai: claude-sonnet-5 | 2026-09-13
@router.post("", response_model=UnitRead, status_code=status.HTTP_201_CREATED)
async def create_unit(
    data: UnitCreate, service: UnitService = Depends(get_unit_service)
) -> UnitRead:
    try:
        unit = await service.create(data)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A unit with this serial number already exists",
        ) from exc
    return UnitRead.model_validate(unit)


# ai: claude-sonnet-5 | 2026-09-13
@router.get("", response_model=list[UnitRead])
async def list_units(
    limit: int = 100,
    offset: int = 0,
    service: UnitService = Depends(get_unit_service),
) -> list[UnitRead]:
    units = await service.list(limit=limit, offset=offset)
    return [UnitRead.model_validate(unit) for unit in units]


# ai: claude-sonnet-5 | 2026-09-13
@router.get("/{unit_id}", response_model=UnitRead)
async def get_unit(
    unit_id: uuid.UUID, service: UnitService = Depends(get_unit_service)
) -> UnitRead:
    unit = await service.get(unit_id)
    if unit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
    return UnitRead.model_validate(unit)


# ai: claude-sonnet-5 | 2026-09-13
@router.patch("/{unit_id}", response_model=UnitRead)
async def update_unit(
    unit_id: uuid.UUID,
    data: UnitUpdate,
    service: UnitService = Depends(get_unit_service),
) -> UnitRead:
    unit = await service.update(unit_id, data)
    if unit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
    return UnitRead.model_validate(unit)


# ai: claude-sonnet-5 | 2026-09-13
@router.post("/{unit_id}/mark-sold", response_model=UnitRead)
async def mark_unit_sold(
    unit_id: uuid.UUID, service: UnitService = Depends(get_unit_service)
) -> UnitRead:
    """409, not 404, on failure - a unit that doesn't exist and a unit that was already sold by
    someone else look the same to the caller here (see UnitService.mark_sold).
    """
    unit = await service.mark_sold(unit_id)
    if unit is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Unit not available for sale"
        )
    return UnitRead.model_validate(unit)
