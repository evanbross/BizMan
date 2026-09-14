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

from app.core.dependencies import get_location_service
from app.schemas.location import LocationCreate, LocationRead, LocationUpdate
from app.services.location import LocationService

router = APIRouter(prefix="/locations", tags=["locations"])


# ai: claude-sonnet-5 | 2026-09-13
@router.post("", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
async def create_location(
    data: LocationCreate, service: LocationService = Depends(get_location_service)
) -> LocationRead:
    location = await service.create(data)
    return LocationRead.model_validate(location)


# ai: claude-sonnet-5 | 2026-09-13
@router.get("", response_model=list[LocationRead])
async def list_locations(
    limit: int = 100,
    offset: int = 0,
    service: LocationService = Depends(get_location_service),
) -> list[LocationRead]:
    locations = await service.list(limit=limit, offset=offset)
    return [LocationRead.model_validate(location) for location in locations]


# ai: claude-sonnet-5 | 2026-09-13
@router.get("/{location_id}", response_model=LocationRead)
async def get_location(
    location_id: uuid.UUID, service: LocationService = Depends(get_location_service)
) -> LocationRead:
    location = await service.get(location_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return LocationRead.model_validate(location)


# ai: claude-sonnet-5 | 2026-09-13
@router.patch("/{location_id}", response_model=LocationRead)
async def update_location(
    location_id: uuid.UUID,
    data: LocationUpdate,
    service: LocationService = Depends(get_location_service),
) -> LocationRead:
    location = await service.update(location_id, data)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return LocationRead.model_validate(location)
