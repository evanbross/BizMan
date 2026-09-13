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

from sqlalchemy import select

from app.models.invoice import Invoice, InvoiceLine
from app.repositories.base import TenantScopedRepository


# ai: claude-sonnet-5 | 2026-09-13
class InvoiceRepository(TenantScopedRepository[Invoice]):
    model = Invoice

    # ai: claude-sonnet-5 | 2026-09-13
    async def list_lines(self, invoice_id: uuid.UUID) -> Sequence[InvoiceLine]:
        """Tenant filtering here goes through `invoice_id` (itself only reachable via `get()`,
        which is tenant-scoped) rather than a second `tenant_id` check, since InvoiceLine has no
        independent lookup path of its own.
        """
        stmt = select(InvoiceLine).where(InvoiceLine.invoice_id == invoice_id)
        return (await self._session.execute(stmt)).scalars().all()

    # ai: claude-sonnet-5 | 2026-09-13
    async def add_line(self, line: InvoiceLine) -> InvoiceLine:
        line.tenant_id = self._tenant_id
        self._session.add(line)
        await self._session.flush()
        return line
