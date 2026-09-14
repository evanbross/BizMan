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

from app.core.dependencies import get_invoice_service
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceLineCreate,
    InvoiceLineRead,
    InvoiceRead,
    InvoiceUpdate,
)
from app.services.exceptions import ServiceConflictError
from app.services.invoice import InvoiceService

router = APIRouter(prefix="/invoices", tags=["invoices"])


# ai: claude-sonnet-5 | 2026-09-13
@router.post("", response_model=InvoiceRead, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    data: InvoiceCreate, service: InvoiceService = Depends(get_invoice_service)
) -> InvoiceRead:
    invoice = await service.create(data)
    return InvoiceRead.model_validate(invoice)


# ai: claude-sonnet-5 | 2026-09-13
@router.get("", response_model=list[InvoiceRead])
async def list_invoices(
    limit: int = 100,
    offset: int = 0,
    service: InvoiceService = Depends(get_invoice_service),
) -> list[InvoiceRead]:
    invoices = await service.list(limit=limit, offset=offset)
    return [InvoiceRead.model_validate(invoice) for invoice in invoices]


# ai: claude-sonnet-5 | 2026-09-13
@router.get("/{invoice_id}", response_model=InvoiceRead)
async def get_invoice(
    invoice_id: uuid.UUID, service: InvoiceService = Depends(get_invoice_service)
) -> InvoiceRead:
    invoice = await service.get(invoice_id)
    if invoice is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return InvoiceRead.model_validate(invoice)


# ai: claude-sonnet-5 | 2026-09-13
@router.patch("/{invoice_id}", response_model=InvoiceRead)
async def update_invoice(
    invoice_id: uuid.UUID,
    data: InvoiceUpdate,
    service: InvoiceService = Depends(get_invoice_service),
) -> InvoiceRead:
    invoice = await service.update(invoice_id, data)
    if invoice is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return InvoiceRead.model_validate(invoice)


# ai: claude-sonnet-5 | 2026-09-13
@router.get("/{invoice_id}/lines", response_model=list[InvoiceLineRead])
async def list_invoice_lines(
    invoice_id: uuid.UUID, service: InvoiceService = Depends(get_invoice_service)
) -> list[InvoiceLineRead]:
    lines = await service.list_lines(invoice_id)
    if lines is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return [InvoiceLineRead.model_validate(line) for line in lines]


# ai: claude-sonnet-5 | 2026-09-13
@router.post(
    "/{invoice_id}/lines", response_model=InvoiceLineRead, status_code=status.HTTP_201_CREATED
)
async def add_invoice_line(
    invoice_id: uuid.UUID,
    data: InvoiceLineCreate,
    service: InvoiceService = Depends(get_invoice_service),
) -> InvoiceLineRead:
    """404 if the invoice doesn't exist; 409 if the referenced Unit was already sold or the
    referenced Part doesn't have enough stock (see InvoiceService.add_line).
    """
    try:
        line = await service.add_line(invoice_id, data)
    except ServiceConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if line is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return InvoiceLineRead.model_validate(line)
