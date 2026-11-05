from .errors import ValidationError


def require_json_object(payload):
    """Ensure the request body is a JSON object."""
    if not isinstance(payload, dict):
        raise ValidationError("Request body must be a JSON object")
    return payload


def require_non_empty_string(payload, field):
    """Return a trimmed, non-empty string field from the payload."""
    value = _require_present(payload, field)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"'{field}' must be a non-empty string")
    return value.strip()


def require_int(payload, field, minimum=None):
    """Return an integer field, rejecting booleans and invalid values."""
    value = _require_present(payload, field)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"'{field}' must be an integer")
    if minimum is not None and value < minimum:
        raise ValidationError(f"'{field}' must be greater than or equal to {minimum}")
    return value


def _require_present(payload, field):
    if field not in payload:
        raise ValidationError(f"'{field}' is required")
    return payload[field]
