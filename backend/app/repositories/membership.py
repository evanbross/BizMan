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

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Membership


# ai: claude-sonnet-5 | 2026-09-13
class MembershipRepository:
    """Deliberately not a TenantScopedRepository: this is how tenant_id gets resolved in the
    first place (see core/dependencies.py get_current_tenant_id), so it has no tenant to scope
    by yet - it scopes by user_id instead.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ai: claude-sonnet-5 | 2026-09-13
    async def get_tenant_id_for_user(self, user_id: uuid.UUID) -> uuid.UUID | None:
        """Phase 1 has no multi-tenant switcher (docs/dealer-ops-blueprint.md) - a user with more
        than one membership just gets the first one found.
        """
        stmt = select(Membership.tenant_id).where(Membership.user_id == user_id).limit(1)
        return (await self._session.execute(stmt)).scalar_one_or_none()
