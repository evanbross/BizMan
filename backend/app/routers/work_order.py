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

from app.core.dependencies import get_work_order_service
from app.schemas.work_order import (
    WorkOrderCreate,
    WorkOrderPartCreate,
    WorkOrderPartRead,
    WorkOrderRead,
    WorkOrderUpdate,
)
from app.services.exceptions import ServiceConflictError
from app.services.work_order import WorkOrderService

router = APIRouter(prefix="/work-orders", tags=["work-orders"])


# ai: claude-sonnet-5 | 2026-09-13
@router.post("", response_model=WorkOrderRead, status_code=status.HTTP_201_CREATED)
async def create_work_order(
    data: WorkOrderCreate, service: WorkOrderService = Depends(get_work_order_service)
) -> WorkOrderRead:
    work_order = await service.create(data)
    return WorkOrderRead.model_validate(work_order)


# ai: claude-sonnet-5 | 2026-09-13
@router.get("", response_model=list[WorkOrderRead])
async def list_work_orders(
    limit: int = 100,
    offset: int = 0,
    service: WorkOrderService = Depends(get_work_order_service),
) -> list[WorkOrderRead]:
    work_orders = await service.list(limit=limit, offset=offset)
    return [WorkOrderRead.model_validate(work_order) for work_order in work_orders]


# ai: claude-sonnet-5 | 2026-09-13
@router.get("/{work_order_id}", response_model=WorkOrderRead)
async def get_work_order(
    work_order_id: uuid.UUID, service: WorkOrderService = Depends(get_work_order_service)
) -> WorkOrderRead:
    work_order = await service.get(work_order_id)
    if work_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work order not found")
    return WorkOrderRead.model_validate(work_order)


# ai: claude-sonnet-5 | 2026-09-13
@router.patch("/{work_order_id}", response_model=WorkOrderRead)
async def update_work_order(
    work_order_id: uuid.UUID,
    data: WorkOrderUpdate,
    service: WorkOrderService = Depends(get_work_order_service),
) -> WorkOrderRead:
    work_order = await service.update(work_order_id, data)
    if work_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work order not found")
    return WorkOrderRead.model_validate(work_order)


# ai: claude-sonnet-5 | 2026-09-13
@router.get("/{work_order_id}/parts", response_model=list[WorkOrderPartRead])
async def list_work_order_parts(
    work_order_id: uuid.UUID, service: WorkOrderService = Depends(get_work_order_service)
) -> list[WorkOrderPartRead]:
    parts_used = await service.list_parts_used(work_order_id)
    if parts_used is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work order not found")
    return [WorkOrderPartRead.model_validate(part_used) for part_used in parts_used]


# ai: claude-sonnet-5 | 2026-09-13
@router.post(
    "/{work_order_id}/parts",
    response_model=WorkOrderPartRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_work_order_part(
    work_order_id: uuid.UUID,
    data: WorkOrderPartCreate,
    service: WorkOrderService = Depends(get_work_order_service),
) -> WorkOrderPartRead:
    """404 if the work order doesn't exist; 409 if the referenced Part doesn't have enough stock
    (see WorkOrderService.add_part_used).
    """
    try:
        part_used = await service.add_part_used(work_order_id, data)
    except ServiceConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if part_used is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Work order not found")
    return WorkOrderPartRead.model_validate(part_used)
