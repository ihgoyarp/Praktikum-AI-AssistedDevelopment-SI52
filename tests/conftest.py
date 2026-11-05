import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    database_path = tmp_path / "lab_equipment.db"
    application = create_app(
        {
            "TESTING": True,
            "DATABASE": str(database_path),
            "PROPAGATE_EXCEPTIONS": True,
        }
    )
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def create_item(client):
    def _create_item(name="Multimeter", total_stock=10):
        response = client.post(
            "/items",
            json={"name": name, "total_stock": total_stock},
        )
        assert response.status_code == 201, response.get_json()
        return response.get_json()

    return _create_item
