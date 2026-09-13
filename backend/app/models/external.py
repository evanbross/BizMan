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

from sqlalchemy import Column, Table
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base

# Stub registration of Supabase's own `auth.users` table - just enough (schema + table name +
# the one column FK'd against) for SQLAlchemy to resolve Membership.user_id's ForeignKey.
# `alembic/env.py`'s `include_object` filter excludes anything in the `auth` schema from
# autogenerate, so this never gets a create/drop migration of its own - Supabase owns that table.
auth_users = Table(
    "users",
    Base.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    schema="auth",
)
