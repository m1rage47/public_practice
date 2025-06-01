import pytest


def test_client_create(client):
    rv = client.post(
        "/clients",
        json={
            "name": "Test",
            "surname": "User",
            "email": "test@example.com",
            "credit_card": "9876543210987654",
            "car_number": "BB4321AA",
        },
    )
    assert rv.status_code == 201
    data = rv.get_json()
    assert data["name"] == "Test"
    assert data["surname"] == "User"
    assert "id" in data


def test_parking_create(client):
    rv = client.post(
        "/parkings",
        json={
            "address": "Moscow, Tverskaya Street",
            "opened": True,
            "count_places": 80,
            "count_available_places": 80,
        },
    )
    assert rv.status_code == 201, rv.data  # Покажет ошибку, если не 201
    data = rv.get_json()
    # data = rv.get_json()
    assert data is not None, rv.data
    assert data["opened"] is True
    assert data["count_places"] == 80


@pytest.mark.parametrize("route", ["/clients", "/clients/1"])
def test_route_status(client, route):
    rv = client.get(route)
    assert rv.status_code == 200


@pytest.mark.parking
def test_parking_enter(client):
    rv = client.post("/client_parkings", json={"client_id": 1, "parking_id": 1})
    assert rv.status_code == 201

    # Повторный заезд — ошибка
    rv = client.post("/client_parkings", json={"client_id": 1, "parking_id": 1})
    assert rv.status_code == 400


@pytest.mark.parking
def test_parking_leave(client):
    # Убедимся, что клиент заехал
    client.post("/client_parkings", json={"client_id": 1, "parking_id": 1})

    rv = client.delete("/client_parkings", json={"client_id": 1, "parking_id": 1})
    assert rv.status_code == 204

    # Повторный выезд — ошибка
    rv = client.delete("/client_parkings", json={"client_id": 1, "parking_id": 1})
    assert rv.status_code == 400
