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


async def test_create_and_get_location(client: AsyncClient) -> None:
    create_response = await client.post("/locations", json={"name": "Main Shop"})
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["name"] == "Main Shop"

    get_response = await client.get(f"/locations/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == created["id"]


async def test_list_locations(client: AsyncClient) -> None:
    await client.post("/locations", json={"name": "Shop A"})
    await client.post("/locations", json={"name": "Shop B"})

    response = await client.get("/locations")

    assert response.status_code == 200
    names = {location["name"] for location in response.json()}
    assert {"Shop A", "Shop B"} <= names


async def test_update_location(client: AsyncClient) -> None:
    created = (await client.post("/locations", json={"name": "Old Name"})).json()

    response = await client.patch(f"/locations/{created['id']}", json={"name": "New Name"})

    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


async def test_get_location_not_found(client: AsyncClient) -> None:
    response = await client.get(f"/locations/{uuid.uuid4()}")

    assert response.status_code == 404


async def test_update_location_not_found(client: AsyncClient) -> None:
    response = await client.patch(f"/locations/{uuid.uuid4()}", json={"name": "Nope"})

    assert response.status_code == 404
