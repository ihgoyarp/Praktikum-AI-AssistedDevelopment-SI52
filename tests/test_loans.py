import pytest


def _borrow(client, item_id, student_id="20240001", quantity=2):
    return client.post(
        "/loans",
        json={
            "student_id": student_id,
            "item_id": item_id,
            "quantity": quantity,
        },
    )


def test_create_loan_reduces_available_stock(client, create_item):
    item = create_item(total_stock=5)

    response = _borrow(client, item["id"], quantity=2)

    assert response.status_code == 201
    loan = response.get_json()
    assert isinstance(loan["id"], int)
    assert loan["student_id"] == "20240001"
    assert loan["item_id"] == item["id"]
    assert loan["quantity"] == 2
    assert loan["status"] == "BORROWED"
    assert loan["created_at"].endswith("Z")

    items = client.get("/items").get_json()
    assert items[0]["available_stock"] == 3


def test_create_loan_returns_400_when_stock_is_insufficient(client, create_item):
    item = create_item(total_stock=3)

    response = _borrow(client, item["id"], quantity=4)

    assert response.status_code == 400
    assert "error" in response.get_json()

    items = client.get("/items").get_json()
    assert items[0]["available_stock"] == 3

    history = client.get("/loans/student/20240001").get_json()
    assert history == []


def test_create_loan_returns_404_when_item_does_not_exist(client):
    response = _borrow(client, item_id=999, quantity=1)

    assert response.status_code == 404
    assert "error" in response.get_json()


@pytest.mark.parametrize("quantity", [0, -1, 1.5, "2", True])
def test_create_loan_rejects_invalid_quantity(client, create_item, quantity):
    item = create_item(total_stock=5)

    response = _borrow(client, item["id"], quantity=quantity)

    assert response.status_code == 400
    assert client.get("/items").get_json()[0]["available_stock"] == 5


@pytest.mark.parametrize("field", ["student_id", "item_id", "quantity"])
def test_create_loan_requires_all_fields(client, create_item, field):
    item = create_item(total_stock=5)
    payload = {"student_id": "20240001", "item_id": item["id"], "quantity": 1}
    payload.pop(field)

    response = client.post("/loans", json=payload)

    assert response.status_code == 400


def test_return_loan_restores_stock_and_updates_status(client, create_item):
    item = create_item(total_stock=5)
    loan = _borrow(client, item["id"], quantity=2).get_json()

    response = client.put(f"/loans/{loan['id']}/return")

    assert response.status_code == 200
    returned = response.get_json()
    assert returned["status"] == "RETURNED"
    assert returned["id"] == loan["id"]

    items = client.get("/items").get_json()
    assert items[0]["available_stock"] == 5


def test_return_loan_returns_404_when_loan_does_not_exist(client):
    response = client.put("/loans/999/return")

    assert response.status_code == 404
    assert "error" in response.get_json()


def test_return_loan_twice_returns_400_and_does_not_restore_stock_twice(
    client, create_item
):
    item = create_item(total_stock=5)
    loan = _borrow(client, item["id"], quantity=2).get_json()

    first = client.put(f"/loans/{loan['id']}/return")
    second = client.put(f"/loans/{loan['id']}/return")

    assert first.status_code == 200
    assert second.status_code == 400
    assert client.get("/items").get_json()[0]["available_stock"] == 5


def test_student_history_only_contains_that_students_loans(client, create_item):
    item = create_item(total_stock=10)
    first = _borrow(client, item["id"], student_id="20240001", quantity=1).get_json()
    _borrow(client, item["id"], student_id="20240002", quantity=2)
    latest = _borrow(client, item["id"], student_id="20240001", quantity=3).get_json()

    response = client.get("/loans/student/20240001")

    assert response.status_code == 200
    history = response.get_json()
    assert [loan["id"] for loan in history] == [latest["id"], first["id"]]
    assert all(loan["student_id"] == "20240001" for loan in history)


def test_student_history_returns_empty_list_when_no_loans(client):
    response = client.get("/loans/student/unknown-student")

    assert response.status_code == 200
    assert response.get_json() == []


def test_returned_loan_still_appears_in_history(client, create_item):
    item = create_item(total_stock=5)
    loan = _borrow(client, item["id"], quantity=2).get_json()
    client.put(f"/loans/{loan['id']}/return")

    history = client.get("/loans/student/20240001").get_json()

    assert len(history) == 1
    assert history[0]["status"] == "RETURNED"
