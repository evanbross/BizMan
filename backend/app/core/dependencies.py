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

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_session
from app.repositories.customer import CustomerRepository
from app.repositories.invoice import InvoiceRepository
from app.repositories.location import LocationRepository
from app.repositories.membership import MembershipRepository
from app.repositories.part import PartRepository
from app.repositories.unit import UnitRepository
from app.repositories.work_order import WorkOrderRepository
from app.services.customer import CustomerService
from app.services.invoice import InvoiceService
from app.services.location import LocationService
from app.services.part import PartService
from app.services.unit import UnitService
from app.services.work_order import WorkOrderService

_bearer_scheme = HTTPBearer()


# ai: claude-sonnet-5 | 2026-09-13
async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> uuid.UUID:
    """Verifies the Supabase Auth JWT's signature and expiry - Supabase already authenticated the
    user at sign-in, so this only needs to prove the token wasn't tampered with or replayed after
    expiring, not re-run auth itself.
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        ) from exc
    return uuid.UUID(payload["sub"])


# ai: claude-sonnet-5 | 2026-09-13
async def get_current_tenant_id(
    user_id: uuid.UUID = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> uuid.UUID:
    """The single place a request's tenant is resolved - every `get_<entity>_repo` dependency
    below chains through this, which is what makes tenant scoping structural rather than
    something each router has to remember to apply. See AGENTS.md "Key patterns to preserve."
    """
    tenant_id = await MembershipRepository(session).get_tenant_id_for_user(user_id)
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User has no tenant membership"
        )
    return tenant_id


# ai: claude-sonnet-5 | 2026-09-13
def get_location_repo(
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> LocationRepository:
    return LocationRepository(session, tenant_id)


# ai: claude-sonnet-5 | 2026-09-13
def get_customer_repo(
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> CustomerRepository:
    return CustomerRepository(session, tenant_id)


# ai: claude-sonnet-5 | 2026-09-13
def get_unit_repo(
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> UnitRepository:
    return UnitRepository(session, tenant_id)


# ai: claude-sonnet-5 | 2026-09-13
def get_part_repo(
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> PartRepository:
    return PartRepository(session, tenant_id)


# ai: claude-sonnet-5 | 2026-09-13
def get_invoice_repo(
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> InvoiceRepository:
    return InvoiceRepository(session, tenant_id)


# ai: claude-sonnet-5 | 2026-09-13
def get_work_order_repo(
    session: AsyncSession = Depends(get_session),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
) -> WorkOrderRepository:
    return WorkOrderRepository(session, tenant_id)


# ai: claude-sonnet-5 | 2026-09-13
def get_location_service(
    repo: LocationRepository = Depends(get_location_repo),
    session: AsyncSession = Depends(get_session),
) -> LocationService:
    return LocationService(repo, session)


# ai: claude-sonnet-5 | 2026-09-13
def get_customer_service(
    repo: CustomerRepository = Depends(get_customer_repo),
    session: AsyncSession = Depends(get_session),
) -> CustomerService:
    return CustomerService(repo, session)


# ai: claude-sonnet-5 | 2026-09-13
def get_unit_service(
    repo: UnitRepository = Depends(get_unit_repo),
    session: AsyncSession = Depends(get_session),
) -> UnitService:
    return UnitService(repo, session)


# ai: claude-sonnet-5 | 2026-09-13
def get_part_service(
    repo: PartRepository = Depends(get_part_repo),
    session: AsyncSession = Depends(get_session),
) -> PartService:
    return PartService(repo, session)


# ai: claude-sonnet-5 | 2026-09-13
def get_invoice_service(
    repo: InvoiceRepository = Depends(get_invoice_repo),
    unit_repo: UnitRepository = Depends(get_unit_repo),
    part_repo: PartRepository = Depends(get_part_repo),
    session: AsyncSession = Depends(get_session),
) -> InvoiceService:
    return InvoiceService(repo, unit_repo, part_repo, session)


# ai: claude-sonnet-5 | 2026-09-13
def get_work_order_service(
    repo: WorkOrderRepository = Depends(get_work_order_repo),
    part_repo: PartRepository = Depends(get_part_repo),
    session: AsyncSession = Depends(get_session),
) -> WorkOrderService:
    return WorkOrderService(repo, part_repo, session)
