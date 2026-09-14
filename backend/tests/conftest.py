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

import asyncio
import os
import subprocess
import sys
import uuid
from collections.abc import AsyncGenerator

import asyncpg
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.db import get_session
from app.core.dependencies import get_current_tenant_id
from app.main import app
from app.models.customer import Customer
from app.models.location import Location
from app.models.tenant import Tenant
from app.repositories.customer import CustomerRepository
from app.repositories.invoice import InvoiceRepository
from app.repositories.location import LocationRepository
from app.repositories.part import PartRepository
from app.repositories.unit import UnitRepository
from app.repositories.work_order import WorkOrderRepository

# The repo root (containing alembic.ini) - two levels up from this file (tests/ -> backend/ ->
# repo root). alembic.ini's `script_location`/`prepend_sys_path` are relative to that directory
# (see AGENTS.md "Local dev" - `alembic` is always invoked from the repo root).
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _test_database_url() -> str:
    """Derives a sibling `<db>_test` database from the app's real DATABASE_URL - never a
    separately configured URL, so it can't silently drift from the dev connection (see
    COMMON_CODING_STANDARDS.md "Single Source of Truth"). Keeps the suite off the dev database
    per TESTING_STANDARDS.md "Tests Must Work Against a Fresh Schema".
    """
    admin_url = make_url(settings.database_url)
    test_url = admin_url.set(database=f"{admin_url.database}_test")
    return test_url.render_as_string(hide_password=False)


TEST_DATABASE_URL = _test_database_url()


def _prepare_test_database() -> None:
    """Creates the `_test` database if missing, and stubs just enough of Supabase's `auth`
    schema (a bare `auth.users` table and a no-op `auth.uid()`) for the initial migration's
    Membership FK and RLS policies to apply - a plain `CREATE DATABASE` clones template1, which
    has no `auth` schema of its own (that's provisioned by the Supabase CLI stack only in its
    own `postgres` database). Mirrors the same minimal stub app/models/external.py already uses
    at the ORM level, just in raw SQL. Idempotent - safe to call every test session.
    """
    admin_url = make_url(settings.database_url)
    test_db_name = make_url(TEST_DATABASE_URL).database

    async def _run() -> None:
        conn = await asyncpg.connect(
            host=admin_url.host,
            port=admin_url.port,
            user=admin_url.username,
            password=admin_url.password,
            database=admin_url.database,
        )
        try:
            exists = await conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1", test_db_name
            )
            if not exists:
                await conn.execute(f'CREATE DATABASE "{test_db_name}"')
        finally:
            await conn.close()

        test_conn = await asyncpg.connect(
            host=admin_url.host,
            port=admin_url.port,
            user=admin_url.username,
            password=admin_url.password,
            database=test_db_name,
        )
        try:
            await test_conn.execute("CREATE SCHEMA IF NOT EXISTS auth")
            await test_conn.execute("CREATE TABLE IF NOT EXISTS auth.users (id uuid PRIMARY KEY)")
            await test_conn.execute(
                "CREATE OR REPLACE FUNCTION auth.uid() RETURNS uuid "
                "LANGUAGE sql STABLE AS $$ SELECT NULL::uuid $$"
            )
        finally:
            await test_conn.close()

    asyncio.run(_run())


def _run_migrations() -> None:
    """Shells out to the real `alembic upgrade head` (same command AGENTS.md documents for dev)
    against the test database, rather than reimplementing schema creation - the migration is the
    single source of truth for the schema either way. Overriding DATABASE_URL only for this
    subprocess's environment leaves the already-imported `settings` singleton in this test
    process untouched.
    """
    env = {**os.environ, "DATABASE_URL": TEST_DATABASE_URL}
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=_REPO_ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.fixture(scope="session", autouse=True)
def _migrated_test_database() -> None:
    """Session-scoped and autouse: every test in the suite runs against a freshly migrated
    `_test` database on the same local Supabase Postgres instance used for dev - never mocked
    (see DATABASE_STANDARDS.md "No Mocked Databases in Integration Tests"). Plain `def`, not
    `async def`: both steps use their own throwaway `asyncio.run`/subprocess, so this runs before
    pytest-asyncio's session event loop exists and can't conflict with it.
    """
    try:
        _prepare_test_database()
        _run_migrations()
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"alembic upgrade head against the test database failed:\n{exc.stdout}\n{exc.stderr}"
        ) from exc


@pytest.fixture(scope="session")
async def engine(_migrated_test_database: None) -> AsyncGenerator[AsyncEngine]:
    test_engine = create_async_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    yield test_engine
    await test_engine.dispose()


@pytest.fixture
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession]:
    """Wraps each test in one real transaction that's rolled back at teardown, no matter how many
    times application code calls `session.commit()` (every service in app/services/ does) - the
    standard SQLAlchemy "join a Session into an external transaction" test pattern.
    `join_transaction_mode="create_savepoint"` makes an inner `commit()` release/reopen a SAVEPOINT
    instead of the real transaction, so the final `rollback()` here always undoes everything.
    """
    async with engine.connect() as connection:
        await connection.begin()
        session_factory = async_sessionmaker(
            bind=connection, expire_on_commit=False, join_transaction_mode="create_savepoint"
        )
        session = session_factory()
        try:
            yield session
        finally:
            await session.close()
            await connection.rollback()


@pytest.fixture
async def tenant_id(db_session: AsyncSession) -> uuid.UUID:
    """A fresh Tenant row for each test, scoped to that test's own rolled-back transaction."""
    tenant = Tenant(name="Test Dealer")
    db_session.add(tenant)
    await db_session.flush()
    return tenant.id


@pytest.fixture
def location_repo(db_session: AsyncSession, tenant_id: uuid.UUID) -> LocationRepository:
    return LocationRepository(db_session, tenant_id)


@pytest.fixture
def customer_repo(db_session: AsyncSession, tenant_id: uuid.UUID) -> CustomerRepository:
    return CustomerRepository(db_session, tenant_id)


@pytest.fixture
def unit_repo(db_session: AsyncSession, tenant_id: uuid.UUID) -> UnitRepository:
    return UnitRepository(db_session, tenant_id)


@pytest.fixture
def part_repo(db_session: AsyncSession, tenant_id: uuid.UUID) -> PartRepository:
    return PartRepository(db_session, tenant_id)


@pytest.fixture
def invoice_repo(db_session: AsyncSession, tenant_id: uuid.UUID) -> InvoiceRepository:
    return InvoiceRepository(db_session, tenant_id)


@pytest.fixture
def work_order_repo(db_session: AsyncSession, tenant_id: uuid.UUID) -> WorkOrderRepository:
    return WorkOrderRepository(db_session, tenant_id)


@pytest.fixture
async def location(location_repo: LocationRepository) -> Location:
    return await location_repo.add(Location(name="Main Shop"))


@pytest.fixture
async def customer(customer_repo: CustomerRepository) -> Customer:
    return await customer_repo.add(Customer(name="Jane Dealer"))


@pytest.fixture
async def client(
    db_session: AsyncSession, tenant_id: uuid.UUID
) -> AsyncGenerator[AsyncClient]:
    """An HTTP client against the real FastAPI app with the DB session and tenant resolution
    overridden - `get_session` yields this test's own rolled-back-at-teardown session, and
    `get_current_tenant_id` returns the fixture tenant directly, skipping real Supabase JWT
    verification entirely (that's Supabase's concern, not this suite's - see
    `get_current_user_id` in core/dependencies.py). Both overridden dependencies are the exact
    callables every router's dependency chain resolves through, so this covers every route.
    """

    async def _override_get_session() -> AsyncGenerator[AsyncSession]:
        yield db_session

    async def _override_get_current_tenant_id() -> uuid.UUID:
        return tenant_id

    app.dependency_overrides[get_session] = _override_get_session
    app.dependency_overrides[get_current_tenant_id] = _override_get_current_tenant_id
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as async_client:
            yield async_client
    finally:
        app.dependency_overrides.clear()
