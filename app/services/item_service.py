from ..database import get_db
from ..repositories import item_repository
from ..validators import require_int, require_json_object, require_non_empty_string


def _serialize(row):
    return dict(row)


def list_items():
    db = get_db()
    return [_serialize(row) for row in item_repository.list_all(db)]


def create_item(payload):
    payload = require_json_object(payload)
    name = require_non_empty_string(payload, "name")
    total_stock = require_int(payload, "total_stock", minimum=0)

    db = get_db()
    try:
        item_id = item_repository.create(db, name, total_stock)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return _serialize(item_repository.get_by_id(db, item_id))
