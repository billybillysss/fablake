from __future__ import annotations

from ..exceptions import ResolutionError, TableIdentifierError


def normalize_schema(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    if not normalized:
        return None
    if "/" in normalized or "\\" in normalized or "." in normalized:
        raise TableIdentifierError("Schema name must be a single path segment.")
    return normalized


def normalize_table_name(value: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise TableIdentifierError("Table name is required.")
    if "/" in normalized or "\\" in normalized:
        raise TableIdentifierError("Table name must be a single path segment.")
    return normalized


def require_schema_mode(schema_enabled: bool | None) -> bool:
    if schema_enabled is None:
        return True
    return schema_enabled


def validate_table_reference(
    *,
    schema_enabled: bool,
    schema: str | None,
    name: str,
) -> tuple[str | None, str]:
    normalized_schema = normalize_schema(schema)
    normalized_name = normalize_table_name(name)

    if not schema_enabled and normalized_schema is not None:
        raise TableIdentifierError(
            "Schema must be omitted for non-schema lakehouses.",
        )

    return normalized_schema, normalized_name
