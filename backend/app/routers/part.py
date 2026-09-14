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

from app.core.dependencies import get_part_service
from app.schemas.part import PartCreate, PartRead, PartUpdate, StockAdjustment
from app.services.part import PartService

router = APIRouter(prefix="/parts", tags=["parts"])


# ai: claude-sonnet-5 | 2026-09-13
@router.post("", response_model=PartRead, status_code=status.HTTP_201_CREATED)
async def create_part(
    data: PartCreate, service: PartService = Depends(get_part_service)
) -> PartRead:
    try:
        part = await service.create(data)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="A part with this SKU already exists"
        ) from exc
    return PartRead.model_validate(part)


# ai: claude-sonnet-5 | 2026-09-13
@router.get("", response_model=list[PartRead])
async def list_parts(
    limit: int = 100,
    offset: int = 0,
    service: PartService = Depends(get_part_service),
) -> list[PartRead]:
    parts = await service.list(limit=limit, offset=offset)
    return [PartRead.model_validate(part) for part in parts]


# ai: claude-sonnet-5 | 2026-09-13
@router.get("/{part_id}", response_model=PartRead)
async def get_part(
    part_id: uuid.UUID, service: PartService = Depends(get_part_service)
) -> PartRead:
    part = await service.get(part_id)
    if part is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Part not found")
    return PartRead.model_validate(part)


# ai: claude-sonnet-5 | 2026-09-13
@router.patch("/{part_id}", response_model=PartRead)
async def update_part(
    part_id: uuid.UUID,
    data: PartUpdate,
    service: PartService = Depends(get_part_service),
) -> PartRead:
    part = await service.update(part_id, data)
    if part is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Part not found")
    return PartRead.model_validate(part)


# ai: claude-sonnet-5 | 2026-09-13
@router.post("/{part_id}/increment-stock", response_model=PartRead)
async def increment_part_stock(
    part_id: uuid.UUID,
    data: StockAdjustment,
    service: PartService = Depends(get_part_service),
) -> PartRead:
    part = await service.increment_stock(part_id, data.quantity)
    if part is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Part not found")
    return PartRead.model_validate(part)


# ai: claude-sonnet-5 | 2026-09-13
@router.post("/{part_id}/decrement-stock", response_model=PartRead)
async def decrement_part_stock(
    part_id: uuid.UUID,
    data: StockAdjustment,
    service: PartService = Depends(get_part_service),
) -> PartRead:
    """409, not 404, on failure - a part that doesn't exist and a part without enough stock look
    the same to the caller here (see PartService.decrement_stock).
    """
    part = await service.decrement_stock(part_id, data.quantity)
    if part is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Insufficient stock or part not found"
        )
    return PartRead.model_validate(part)
