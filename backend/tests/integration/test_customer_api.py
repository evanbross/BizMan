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

from httpx import AsyncClient


async def test_create_and_get_customer(client: AsyncClient) -> None:
    create_response = await client.post(
        "/customers", json={"name": "Jane Dealer", "phone": "555-0100"}
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["name"] == "Jane Dealer"
    assert created["phone"] == "555-0100"
    assert created["email"] is None

    get_response = await client.get(f"/customers/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == created["id"]


async def test_update_customer_partial_fields(client: AsyncClient) -> None:
    created = (
        await client.post("/customers", json={"name": "Jane Dealer", "phone": "555-0100"})
    ).json()

    response = await client.patch(f"/customers/{created['id']}", json={"email": "jane@example.com"})

    assert response.status_code == 200
    updated = response.json()
    assert updated["email"] == "jane@example.com"
    assert updated["phone"] == "555-0100"  # untouched fields survive a partial PATCH


async def test_get_customer_not_found(client: AsyncClient) -> None:
    response = await client.get(f"/customers/{uuid.uuid4()}")

    assert response.status_code == 404
