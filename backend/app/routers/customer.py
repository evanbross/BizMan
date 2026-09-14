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

from app.core.dependencies import get_customer_service
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from app.services.customer import CustomerService

router = APIRouter(prefix="/customers", tags=["customers"])


# ai: claude-sonnet-5 | 2026-09-13
@router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
async def create_customer(
    data: CustomerCreate, service: CustomerService = Depends(get_customer_service)
) -> CustomerRead:
    customer = await service.create(data)
    return CustomerRead.model_validate(customer)


# ai: claude-sonnet-5 | 2026-09-13
@router.get("", response_model=list[CustomerRead])
async def list_customers(
    limit: int = 100,
    offset: int = 0,
    service: CustomerService = Depends(get_customer_service),
) -> list[CustomerRead]:
    customers = await service.list(limit=limit, offset=offset)
    return [CustomerRead.model_validate(customer) for customer in customers]


# ai: claude-sonnet-5 | 2026-09-13
@router.get("/{customer_id}", response_model=CustomerRead)
async def get_customer(
    customer_id: uuid.UUID, service: CustomerService = Depends(get_customer_service)
) -> CustomerRead:
    customer = await service.get(customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return CustomerRead.model_validate(customer)


# ai: claude-sonnet-5 | 2026-09-13
@router.patch("/{customer_id}", response_model=CustomerRead)
async def update_customer(
    customer_id: uuid.UUID,
    data: CustomerUpdate,
    service: CustomerService = Depends(get_customer_service),
) -> CustomerRead:
    customer = await service.update(customer_id, data)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return CustomerRead.model_validate(customer)
