from __future__ import annotations

from fnmatch import fnmatch
from typing import TYPE_CHECKING

from .rules import normalize_schema, require_schema_mode
from .table_path import LakehouseTable

if TYPE_CHECKING:
    from .core import Lakehouse


class LakehouseTables:
    """Table discovery helpers under the `Tables` root."""

    def __init__(self, lakehouse: Lakehouse) -> None:
        self._lakehouse = lakehouse

    def list(self, pattern: str = "*", *, schema: str | None = None) -> list[LakehouseTable]:
        """Return table locators matching `pattern`.

        Pattern matching rules:

        - schema-enabled + no schema filter: match against `<schema>.<table>`
        - schema-enabled + schema filter: match against `<table>` in that schema
        - non-schema mode: match against `<table>`
        """
        schema_enabled = require_schema_mode(self._lakehouse.schema_enabled)
        normalized_pattern = str(pattern or "").strip() or "*"
        normalized_schema = normalize_schema(schema)

        if schema_enabled:
            if normalized_schema is not None:
                return self._list_for_schema(
                    schema=normalized_schema,
                    pattern=normalized_pattern,
                )
            return self._list_schema_enabled(pattern=normalized_pattern)

        return self._list_non_schema(pattern=normalized_pattern)

    def _list_schema_enabled(self, *, pattern: str) -> list[LakehouseTable]:
        result: list[LakehouseTable] = []
        for schema_entry in self._lakehouse.fs.ls("", root="Tables"):
            if not schema_entry.is_dir():
                continue
            schema_name = schema_entry.name
            for table_entry in self._lakehouse.fs.ls(schema_name, root="Tables"):
                if not table_entry.is_dir():
                    continue
                identifier = f"{schema_name}.{table_entry.name}"
                if not fnmatch(identifier, pattern):
                    continue
                result.append(self._lakehouse.table(schema=schema_name, name=table_entry.name))
        return sorted(result, key=lambda item: item.relative_path)

    def _list_for_schema(self, *, schema: str, pattern: str) -> list[LakehouseTable]:
        result: list[LakehouseTable] = []
        for table_entry in self._lakehouse.fs.ls(schema, root="Tables"):
            if not table_entry.is_dir():
                continue
            if not fnmatch(table_entry.name, pattern):
                continue
            result.append(self._lakehouse.table(schema=schema, name=table_entry.name))
        return sorted(result, key=lambda item: item.relative_path)

    def _list_non_schema(self, *, pattern: str) -> list[LakehouseTable]:
        result: list[LakehouseTable] = []
        for table_entry in self._lakehouse.fs.ls("", root="Tables"):
            if not table_entry.is_dir():
                continue
            if not fnmatch(table_entry.name, pattern):
                continue
            result.append(self._lakehouse.table(schema=None, name=table_entry.name))
        return sorted(result, key=lambda item: item.relative_path)
