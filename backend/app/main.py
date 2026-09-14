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

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.caddy import deregister_from_caddy, register_with_caddy
from app.core.logging_config import configure_logging
from app.routers import (
    customer_router,
    invoice_router,
    location_router,
    part_router,
    unit_router,
    work_order_router,
)

configure_logging()


# ai: claude-sonnet-5 | 2026-09-12
@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    register_with_caddy()
    yield
    deregister_from_caddy()


# ai: claude-sonnet-5 | 2026-09-12
app = FastAPI(title="BizMan API", version="0.1.0", lifespan=lifespan)

# Never import shared infra (db session factory, config, tenant-context deps) back from this
# module inside a router — see PYTHON_STANDARDS.md "Circular Imports."
app.include_router(location_router)
app.include_router(customer_router)
app.include_router(unit_router)
app.include_router(part_router)
app.include_router(invoice_router)
app.include_router(work_order_router)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
