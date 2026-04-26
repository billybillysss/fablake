from __future__ import annotations

import os

import pytest

from fablake import Lakehouse
from fablake._abfs import FabLakeFileSystem
from fablake.exceptions import TableIdentifierError
from fablake.lakehouse import LakehouseTable


def test_schema_enabled_table_uses_schema_folder(lakehouse_schema_enabled):
    table = lakehouse_schema_enabled.table(schema="brz", name="orders")

    assert table.schema == "brz"
    assert table.name == "orders"
    assert table.relative_path == "brz/orders"
    assert table.identifier == "brz.orders"
    assert isinstance(table, str)
    assert str(table) == "abfss://Finance@onelake.dfs.fabric.microsoft.com/Ops.lakehouse/Tables/brz/orders"
    assert os.fspath(table) == str(table)
    assert repr(table) == "LakehouseTable('brz.orders')"


def test_schema_enabled_table_accepts_name_first_signature(lakehouse_schema_enabled):
    table = lakehouse_schema_enabled.table(schema="brz", name="orders")

    assert table.schema == "brz"
    assert table.name == "orders"
    assert table.relative_path == "brz/orders"


def test_schema_enabled_table_defaults_to_dbo(lakehouse_schema_enabled):
    table = lakehouse_schema_enabled.table(schema=None, name="orders")

    assert table.schema is None
    assert table.relative_path == "dbo/orders"
    assert str(table) == "abfss://Finance@onelake.dfs.fabric.microsoft.com/Ops.lakehouse/Tables/dbo/orders"


def test_schema_enabled_table_accepts_explicit_dbo(lakehouse_schema_enabled):
    table = lakehouse_schema_enabled.table(schema="dbo", name="orders")

    assert table.relative_path == "dbo/orders"
    assert str(table) == "abfss://Finance@onelake.dfs.fabric.microsoft.com/Ops.lakehouse/Tables/dbo/orders"


def test_non_schema_table_uses_flat_tables_root(lakehouse_non_schema):
    table = lakehouse_non_schema.table(schema=None, name="orders")

    assert table.relative_path == "orders"
    assert str(table) == "abfss://Finance@onelake.dfs.fabric.microsoft.com/Ops.lakehouse/Tables/orders"
    assert repr(table) == "LakehouseTable('orders')"


def test_non_schema_table_rejects_explicit_schema(lakehouse_non_schema):
    with pytest.raises(TableIdentifierError, match="Schema must be omitted"):
        lakehouse_non_schema.table(schema="brz", name="orders")


def test_table_defaults_to_schema_enabled_when_unspecified():
    lh = Lakehouse(
        workspace_id="ws-guid",
        lakehouse_id="lh-guid",
        credential="explicit-credential",
    )

    table = lh.table(schema="brz", name="orders")

    assert table.relative_path == "brz/orders"
    assert str(table) == "abfss://ws-guid@onelake.dfs.fabric.microsoft.com/lh-guid/Tables/brz/orders"


def test_table_defaults_none_schema_to_dbo_when_unspecified():
    lh = Lakehouse(
        workspace_id="ws-guid",
        lakehouse_id="lh-guid",
        credential="explicit-credential",
    )

    table = lh.table(schema=None, name="orders")

    assert table.relative_path == "dbo/orders"
    assert str(table) == "abfss://ws-guid@onelake.dfs.fabric.microsoft.com/lh-guid/Tables/dbo/orders"


def test_name_first_signature_defaults_to_dbo_when_schema_omitted(lakehouse_schema_enabled):
    table = lakehouse_schema_enabled.table(name="orders")

    assert table.relative_path == "dbo/orders"


def test_standalone_table_defaults_to_schema_enabled():
    filesystem = FabLakeFileSystem(
        workspace="Finance",
        lakehouse="Ops",
        identifier_mode="name",
        credential="explicit-credential",
    )

    table = LakehouseTable(filesystem, schema="dbo", name="orders")

    assert table.relative_path == "dbo/orders"
    assert str(table) == "abfss://Finance@onelake.dfs.fabric.microsoft.com/Ops.lakehouse/Tables/dbo/orders"


@pytest.mark.parametrize(
    ("schema", "name", "message"),
    [
        ("brz.raw", "orders", "Schema name must be a single path segment"),
        ("a/b", "orders", "Schema name must be a single path segment"),
        (None, "", "Table name is required"),
        (None, "bad/name", "Table name must be a single path segment"),
    ],
)
def test_invalid_table_inputs_raise(lakehouse_schema_enabled, schema, name, message):
    with pytest.raises(TableIdentifierError, match=message):
        lakehouse_schema_enabled.table(schema=schema, name=name)


def test_table_accepts_second_positional_schema_argument(lakehouse_schema_enabled):
    table = lakehouse_schema_enabled.table("orders", "dbo")

    assert table.relative_path == "dbo/orders"
