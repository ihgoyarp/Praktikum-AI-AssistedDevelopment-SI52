def test_get_items_returns_empty_list_when_database_is_empty(client):
    response = client.get("/items")

    assert response.status_code == 200
    assert response.get_json() == []


def test_create_item_initializes_available_stock(client):
    response = client.post(
        "/items",
        json={"name": "Oscilloscope", "total_stock": 5},
    )

    assert response.status_code == 201
    item = response.get_json()
    assert isinstance(item["id"], int)
    assert item["name"] == "Oscilloscope"
    assert item["total_stock"] == 5
    assert item["available_stock"] == 5


def test_get_items_returns_created_items_with_current_stock(client, create_item):
    first = create_item(name="Multimeter", total_stock=4)
    second = create_item(name="Power Supply", total_stock=2)

    response = client.get("/items")

    assert response.status_code == 200
    assert response.get_json() == [first, second]


def test_create_item_requires_name(client):
    response = client.post("/items", json={"total_stock": 5})

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_item_rejects_blank_name(client):
    response = client.post("/items", json={"name": "   ", "total_stock": 5})

    assert response.status_code == 400


def test_create_item_rejects_negative_total_stock(client):
    response = client.post("/items", json={"name": "Multimeter", "total_stock": -1})

    assert response.status_code == 400


def test_create_item_rejects_non_integer_total_stock(client):
    response = client.post("/items", json={"name": "Multimeter", "total_stock": "5"})

    assert response.status_code == 400


def test_create_item_rejects_non_object_body(client):
    response = client.post("/items", data="[]", content_type="application/json")

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_item_rejects_malformed_json(client):
    response = client.post(
        "/items",
        data="{not valid json",
        content_type="application/json",
    )

    assert response.status_code == 400
