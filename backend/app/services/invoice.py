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

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invoice import Invoice, InvoiceLine
from app.repositories.invoice import InvoiceRepository
from app.repositories.part import PartRepository
from app.repositories.unit import UnitRepository
from app.schemas.invoice import InvoiceCreate, InvoiceLineCreate, InvoiceUpdate
from app.services.exceptions import ServiceConflictError

logger = logging.getLogger(__name__)


# ai: claude-sonnet-5 | 2026-09-13
class InvoiceService:
    """Owns the commit boundary for invoice writes, including the cross-entity side effects of
    `add_line` (flipping a Unit to sold, decrementing a Part's stock) - the repository layer only
    flushes (see DATABASE_STANDARDS.md "Repository Transaction Discipline"). Coordinating
    UnitRepository/PartRepository from here, rather than from the router, keeps the "sell a unit"/
    "sell parts" business rule (docs/dealer-ops-blueprint.md) out of the router entirely.
    """

    def __init__(
        self,
        repo: InvoiceRepository,
        unit_repo: UnitRepository,
        part_repo: PartRepository,
        session: AsyncSession,
    ) -> None:
        self._repo = repo
        self._unit_repo = unit_repo
        self._part_repo = part_repo
        self._session = session

    async def create(self, data: InvoiceCreate) -> Invoice:
        invoice = await self._repo.add(
            Invoice(location_id=data.location_id, customer_id=data.customer_id)
        )
        await self._session.commit()
        return invoice

    async def get(self, invoice_id: uuid.UUID) -> Invoice | None:
        return await self._repo.get(invoice_id)

    async def list(self, *, limit: int = 100, offset: int = 0) -> Sequence[Invoice]:
        return await self._repo.list(limit=limit, offset=offset)

    async def update(self, invoice_id: uuid.UUID, data: InvoiceUpdate) -> Invoice | None:
        values = data.model_dump(exclude_unset=True)
        invoice = await self._repo.update(invoice_id, values)
        await self._session.commit()
        return invoice

    async def list_lines(self, invoice_id: uuid.UUID) -> Sequence[InvoiceLine] | None:
        """None means the invoice doesn't exist or isn't this tenant's - distinct from an empty
        list of lines on a real invoice.
        """
        invoice = await self._repo.get(invoice_id)
        if invoice is None:
            return None
        return await self._repo.list_lines(invoice_id)

    async def add_line(
        self, invoice_id: uuid.UUID, data: InvoiceLineCreate
    ) -> InvoiceLine | None:
        """None means the invoice doesn't exist. Raises ServiceConflictError if the referenced
        Unit was already sold or the referenced Part doesn't have `quantity` on hand - the router
        turns that into a 409. Exactly one of unit_id/part_id is set (enforced by
        InvoiceLineCreate's validator), so exactly one branch below ever runs.
        """
        invoice = await self._repo.get(invoice_id)
        if invoice is None:
            return None

        if data.unit_id is not None:
            unit = await self._unit_repo.mark_sold(data.unit_id)
            if unit is None:
                raise ServiceConflictError("Unit not available for sale")
        elif data.part_id is not None:
            part = await self._part_repo.decrement_stock(data.part_id, data.quantity)
            if part is None:
                raise ServiceConflictError("Insufficient stock or part not found")
        else:
            raise ValueError("InvoiceLineCreate must set exactly one of unit_id or part_id")

        line = await self._repo.add_line(
            InvoiceLine(
                invoice_id=invoice_id,
                unit_id=data.unit_id,
                part_id=data.part_id,
                description=data.description,
                quantity=data.quantity,
                unit_price=data.unit_price,
            )
        )
        await self._session.commit()
        return line
