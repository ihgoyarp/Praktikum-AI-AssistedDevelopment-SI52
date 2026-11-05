from flask import Blueprint, jsonify, request

from ..services import loan_service

bp = Blueprint("loans", __name__, url_prefix="/loans")


@bp.post("")
def post_loan():
    payload = request.get_json(silent=True)
    loan = loan_service.create_loan(payload)
    return jsonify(loan), 201


@bp.put("/<int:loan_id>/return")
def put_loan_return(loan_id):
    loan = loan_service.return_loan(loan_id)
    return jsonify(loan), 200


@bp.get("/student/<student_id>")
def get_student_loans(student_id):
    return jsonify(loan_service.list_student_loans(student_id)), 200
