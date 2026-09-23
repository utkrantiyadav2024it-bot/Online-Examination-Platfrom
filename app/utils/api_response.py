"""
Shared response helpers.

Every endpoint in the Reporting & Analytics and Audit Logging modules returns
the same JSON envelope already used by the Authentication module:

    {
        "success": <bool>,
        "message": <str>,
        "data":    <object|null>,
        "errors":  <object|null>
    }
"""

from decimal import Decimal
from datetime import datetime, date

from flask import jsonify


def success_response(data=None, message="OK", status_code=200):
    return jsonify({
        "success": True,
        "message": message,
        "data": data,
        "errors": None
    }), status_code


def error_response(message="Request failed", status_code=400, errors=None):
    return jsonify({
        "success": False,
        "message": message,
        "data": None,
        "errors": errors
    }), status_code


def to_float(value, default=0.0):
    """DECIMAL columns come back as Decimal; JSON cannot serialise those."""
    if value is None:
        return default
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def to_int(value, default=0):
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def iso(value):
    """Serialise DATETIME/DATE columns as ISO-8601 strings."""
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


def row_to_dict(row):
    """SQLAlchemy Row -> plain dict (works for both Core and text() results)."""
    if row is None:
        return None
    return dict(row._mapping)
