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

from app.models.customer import Customer
from app.models.location import Location


async def _create_invoice(client: AsyncClient, location: Location, customer: Customer) -> dict:
    response = await client.post(
        "/invoices", json={"location_id": str(location.id), "customer_id": str(customer.id)}
    )
    assert response.status_code == 201
    return response.json()


async def _create_unit(client: AsyncClient, location: Location, serial_no: str) -> dict:
    response = await client.post(
        "/units",
        json={
            "location_id": str(location.id),
            "category": "mower",
            "manufacturer": "Toro",
            "model": "TimeCutter",
            "serial_no": serial_no,
            "cost": "1000.00",
            "price": "1500.00",
        },
    )
    assert response.status_code == 201
    return response.json()


async def _create_part(
    client: AsyncClient, location: Location, sku: str, qty_on_hand: int
) -> dict:
    response = await client.post(
        "/parts",
        json={
            "location_id": str(location.id),
            "sku": sku,
            "description": "Spark plug",
            "manufacturer": "Toro",
            "qty_on_hand": qty_on_hand,
            "cost": "5.00",
            "price": "10.00",
        },
    )
    assert response.status_code == 201
    return response.json()


async def test_sell_a_unit_flips_it_to_sold(
    client: AsyncClient, location: Location, customer: Customer
) -> None:
    invoice = await _create_invoice(client, location, customer)
    unit = await _create_unit(client, location, "SN-INV-1")

    response = await client.post(
        f"/invoices/{invoice['id']}/lines",
        json={"unit_id": unit["id"], "description": "TimeCutter mower", "unit_price": "1500.00"},
    )

    assert response.status_code == 201
    assert response.json()["unit_id"] == unit["id"]

    sold_unit = (await client.get(f"/units/{unit['id']}")).json()
    assert sold_unit["status"] == "sold"


async def test_selling_an_already_sold_unit_conflicts(
    client: AsyncClient, location: Location, customer: Customer
) -> None:
    invoice = await _create_invoice(client, location, customer)
    unit = await _create_unit(client, location, "SN-INV-2")
    await client.post(f"/units/{unit['id']}/mark-sold")

    response = await client.post(
        f"/invoices/{invoice['id']}/lines",
        json={"unit_id": unit["id"], "description": "TimeCutter mower", "unit_price": "1500.00"},
    )

    assert response.status_code == 409


async def test_sell_parts_decrements_stock(
    client: AsyncClient, location: Location, customer: Customer
) -> None:
    invoice = await _create_invoice(client, location, customer)
    part = await _create_part(client, location, "SKU-INV-1", qty_on_hand=5)

    response = await client.post(
        f"/invoices/{invoice['id']}/lines",
        json={
            "part_id": part["id"],
            "description": "Spark plug",
            "quantity": 2,
            "unit_price": "10.00",
        },
    )

    assert response.status_code == 201
    part_after = (await client.get(f"/parts/{part['id']}")).json()
    assert part_after["qty_on_hand"] == 3


async def test_add_line_to_missing_invoice_is_404(client: AsyncClient, location: Location) -> None:
    part = await _create_part(client, location, "SKU-INV-2", qty_on_hand=5)

    response = await client.post(
        f"/invoices/{uuid.uuid4()}/lines",
        json={"part_id": part["id"], "description": "Spark plug", "unit_price": "10.00"},
    )

    assert response.status_code == 404


async def test_list_invoice_lines(
    client: AsyncClient, location: Location, customer: Customer
) -> None:
    invoice = await _create_invoice(client, location, customer)
    part = await _create_part(client, location, "SKU-INV-3", qty_on_hand=5)
    await client.post(
        f"/invoices/{invoice['id']}/lines",
        json={"part_id": part["id"], "description": "Spark plug", "unit_price": "10.00"},
    )

    response = await client.get(f"/invoices/{invoice['id']}/lines")

    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_work_order_consumes_part_stock(
    client: AsyncClient, location: Location, customer: Customer
) -> None:
    work_order = (
        await client.post(
            "/work-orders",
            json={"location_id": str(location.id), "customer_id": str(customer.id)},
        )
    ).json()
    part = await _create_part(client, location, "SKU-WO-1", qty_on_hand=4)

    response = await client.post(
        f"/work-orders/{work_order['id']}/parts", json={"part_id": part["id"], "quantity": 3}
    )

    assert response.status_code == 201
    part_after = (await client.get(f"/parts/{part['id']}")).json()
    assert part_after["qty_on_hand"] == 1


async def test_work_order_insufficient_stock_conflicts(
    client: AsyncClient, location: Location, customer: Customer
) -> None:
    work_order = (
        await client.post(
            "/work-orders",
            json={"location_id": str(location.id), "customer_id": str(customer.id)},
        )
    ).json()
    part = await _create_part(client, location, "SKU-WO-2", qty_on_hand=1)

    response = await client.post(
        f"/work-orders/{work_order['id']}/parts", json={"part_id": part["id"], "quantity": 5}
    )

    assert response.status_code == 409


async def test_add_part_to_missing_work_order_is_404(
    client: AsyncClient, location: Location
) -> None:
    part = await _create_part(client, location, "SKU-WO-3", qty_on_hand=5)

    response = await client.post(
        f"/work-orders/{uuid.uuid4()}/parts", json={"part_id": part["id"], "quantity": 1}
    )

    assert response.status_code == 404
