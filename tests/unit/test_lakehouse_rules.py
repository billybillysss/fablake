from __future__ import annotations

import pytest

from fablake.exceptions import TableIdentifierError
from fablake.lakehouse.rules import (
    normalize_schema,
    normalize_table_name,
    require_schema_mode,
    validate_table_reference,
)


def test_normalize_schema_handles_empty_values():
    assert normalize_schema(None) is None
    assert normalize_schema("") is None
    assert normalize_schema("  ") is None


def test_normalize_schema_rejects_invalid_segments():
    with pytest.raises(TableIdentifierError):
        normalize_schema("brz.raw")
    with pytest.raises(TableIdentifierError):
        normalize_schema("brz/orders")


def test_normalize_table_name_rejects_invalid_values():
    with pytest.raises(TableIdentifierError):
        normalize_table_name("")
    with pytest.raises(TableIdentifierError):
        normalize_table_name("orders/raw")


def test_require_schema_mode_defaults_none_to_true():
    assert require_schema_mode(None) is True


def test_validate_table_reference_accepts_schema_enabled_values():
    assert validate_table_reference(schema_enabled=True, schema="brz", name="orders") == ("brz", "orders")


def test_validate_table_reference_rejects_schema_on_non_schema_lakehouse():
    with pytest.raises(TableIdentifierError, match="Schema must be omitted"):
        validate_table_reference(schema_enabled=False, schema="brz", name="orders")
