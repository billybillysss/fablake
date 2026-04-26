from __future__ import annotations

from fablake.path import LakehousePath


def _configure_tables_listing(lakehouse, mapping: dict[str, list[str]], directories: set[str]) -> None:
    def fake_ls(path: str, *, root: str = "Files", **kwargs):
        assert root == "Tables"
        return [
            LakehousePath(lakehouse.fs, root="Tables", path=entry)
            for entry in mapping.get(path, [])
        ]

    def fake_isdir(path: str, *, root: str = "Files", **kwargs):
        assert root == "Tables"
        return path in directories

    lakehouse.fs.ls = fake_ls
    lakehouse.fs.isdir = fake_isdir


def test_tables_list_matches_schema_dot_table_pattern_when_schema_not_provided(lakehouse_schema_enabled):
    _configure_tables_listing(
        lakehouse_schema_enabled,
        mapping={
            "": ["dbo", "brz", "_delta_log"],
            "dbo": ["dbo/order", "dbo/customers", "dbo/readme.txt"],
            "brz": ["brz/orders"],
        },
        directories={"dbo", "brz", "dbo/order", "dbo/customers", "brz/orders"},
    )

    result = lakehouse_schema_enabled.tables.list("db*.*der")

    assert [item.relative_path for item in result] == ["dbo/order"]


def test_tables_list_matches_table_name_within_explicit_schema(lakehouse_schema_enabled):
    _configure_tables_listing(
        lakehouse_schema_enabled,
        mapping={
            "dbo": ["dbo/orders", "dbo/order_lines", "dbo/customers"],
        },
        directories={"dbo/orders", "dbo/order_lines", "dbo/customers"},
    )

    result = lakehouse_schema_enabled.tables.list("ord*", schema="dbo")

    assert [item.relative_path for item in result] == ["dbo/order_lines", "dbo/orders"]


def test_tables_list_matches_flat_table_names_for_non_schema_lakehouse(lakehouse_non_schema):
    _configure_tables_listing(
        lakehouse_non_schema,
        mapping={
            "": ["orders", "order_items", "customers", "README.md"],
        },
        directories={"orders", "order_items", "customers"},
    )

    result = lakehouse_non_schema.tables.list("ord*")

    assert [item.relative_path for item in result] == ["order_items", "orders"]
