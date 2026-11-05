from ..database import get_db
from ..errors import NotFoundError, ValidationError
from ..repositories import item_repository, loan_repository
from ..utils import utc_now_iso
from ..validators import require_int, require_json_object, require_non_empty_string


def _serialize(row):
    return dict(row)


def create_loan(payload):
    payload = require_json_object(payload)
    student_id = require_non_empty_string(payload, "student_id")
    item_id = require_int(payload, "item_id", minimum=1)
    quantity = require_int(payload, "quantity", minimum=1)

    db = get_db()

    # Item existence is checked first so a missing item always yields 404,
    # as required by the PRD, instead of a generic insufficient-stock error.
    if item_repository.get_by_id(db, item_id) is None:
        raise NotFoundError("Item not found")

    try:
        updated = item_repository.decrease_available_stock(db, item_id, quantity)
        if updated == 0:
            db.rollback()
            raise ValidationError("Insufficient stock")

        loan_id = loan_repository.create(
            db,
            student_id=student_id,
            item_id=item_id,
            quantity=quantity,
            status="BORROWED",
            created_at=utc_now_iso(),
        )
        db.commit()
    except ValidationError:
        raise
    except Exception:
        db.rollback()
        raise

    return _serialize(loan_repository.get_by_id(db, loan_id))


def return_loan(loan_id):
    db = get_db()
    loan = loan_repository.get_by_id(db, loan_id)

    if loan is None:
        raise NotFoundError("Loan not found")
    if loan["status"] == "RETURNED":
        raise ValidationError("Loan has already been returned")
    if loan["status"] != "BORROWED":
        raise ValidationError("Loan cannot be returned in its current status")

    try:
        updated = loan_repository.mark_returned(db, loan_id)
        if updated == 0:
            db.rollback()
            raise ValidationError("Loan has already been returned")

        item_repository.increase_available_stock(db, loan["item_id"], loan["quantity"])
        db.commit()
    except ValidationError:
        raise
    except Exception:
        db.rollback()
        raise

    return _serialize(loan_repository.get_by_id(db, loan_id))


def list_student_loans(student_id):
    if not isinstance(student_id, str) or not student_id.strip():
        raise ValidationError("'student_id' must be a non-empty string")

    db = get_db()
    return [
        _serialize(row)
        for row in loan_repository.list_by_student(db, student_id.strip())
    ]
