from flask import Blueprint, jsonify, request

from ..services import item_service

bp = Blueprint("items", __name__, url_prefix="/items")


@bp.get("")
def get_items():
    return jsonify(item_service.list_items()), 200


@bp.post("")
def post_item():
    payload = request.get_json(silent=True)
    item = item_service.create_item(payload)
    return jsonify(item), 201
