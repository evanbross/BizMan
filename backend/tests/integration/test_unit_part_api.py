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

from httpx import AsyncClient

from app.models.location import Location


async def test_create_unit_duplicate_serial_conflicts(
    client: AsyncClient, location: Location
) -> None:
    payload = {
        "location_id": str(location.id),
        "category": "mower",
        "manufacturer": "Toro",
        "model": "TimeCutter",
        "serial_no": "SN-100",
        "cost": "1000.00",
        "price": "1500.00",
    }

    first = await client.post("/units", json=payload)
    assert first.status_code == 201

    second = await client.post("/units", json=payload)
    assert second.status_code == 409


async def test_mark_unit_sold_then_conflict_on_second_attempt(
    client: AsyncClient, location: Location
) -> None:
    created = (
        await client.post(
            "/units",
            json={
                "location_id": str(location.id),
                "category": "mower",
                "manufacturer": "Ariens",
                "model": "Gravely",
                "serial_no": "SN-200",
                "cost": "1000.00",
                "price": "1500.00",
            },
        )
    ).json()

    first_sale = await client.post(f"/units/{created['id']}/mark-sold")
    assert first_sale.status_code == 200
    assert first_sale.json()["status"] == "sold"

    second_sale = await client.post(f"/units/{created['id']}/mark-sold")
    assert second_sale.status_code == 409


async def test_create_part_duplicate_sku_conflicts(
    client: AsyncClient, location: Location
) -> None:
    payload = {
        "location_id": str(location.id),
        "sku": "SKU-1",
        "description": "Air filter",
        "manufacturer": "Toro",
        "qty_on_hand": 5,
        "cost": "10.00",
        "price": "20.00",
    }

    first = await client.post("/parts", json=payload)
    assert first.status_code == 201

    second = await client.post("/parts", json=payload)
    assert second.status_code == 409


async def test_decrement_part_stock_success_and_insufficient_stock(
    client: AsyncClient, location: Location
) -> None:
    created = (
        await client.post(
            "/parts",
            json={
                "location_id": str(location.id),
                "sku": "SKU-2",
                "description": "Spark plug",
                "manufacturer": "Toro",
                "qty_on_hand": 3,
                "cost": "5.00",
                "price": "10.00",
            },
        )
    ).json()

    decrement_ok = await client.post(
        f"/parts/{created['id']}/decrement-stock", json={"quantity": 2}
    )
    assert decrement_ok.status_code == 200
    assert decrement_ok.json()["qty_on_hand"] == 1

    decrement_too_much = await client.post(
        f"/parts/{created['id']}/decrement-stock", json={"quantity": 2}
    )
    assert decrement_too_much.status_code == 409


async def test_increment_part_stock(client: AsyncClient, location: Location) -> None:
    created = (
        await client.post(
            "/parts",
            json={
                "location_id": str(location.id),
                "sku": "SKU-3",
                "description": "Oil filter",
                "manufacturer": "Toro",
                "qty_on_hand": 0,
                "cost": "5.00",
                "price": "10.00",
            },
        )
    ).json()

    response = await client.post(f"/parts/{created['id']}/increment-stock", json={"quantity": 4})

    assert response.status_code == 200
    assert response.json()["qty_on_hand"] == 4
