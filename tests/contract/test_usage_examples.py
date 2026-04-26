from __future__ import annotations

import os


def test_create_lakehouse_context_examples_work():
    from fablake import Lakehouse

    lh = Lakehouse(
        workspace="Finance",
        lakehouse="Ops",
        schema_enabled=True,
        credential="explicit-credential",
    )
    lh_by_id = Lakehouse(
        workspace_id="ws-guid",
        lakehouse_id="lh-guid",
        schema_enabled=True,
        credential="explicit-credential",
    )

    assert lh.binding.identifier_mode == "name"
    assert lh.workspace == "Finance"
    assert lh.lakehouse == "Ops"
    assert lh_by_id.binding.identifier_mode == "id"
    assert lh_by_id.workspace is None
    assert lh_by_id.lakehouse is None


def test_filesystem_and_explicit_path_examples_work(lakehouse_schema_enabled):
    path = lakehouse_schema_enabled.files / "raw" / "orders" / "2026-01-01.json"
    logs = lakehouse_schema_enabled.path("logs/2026/04", root="Files")
    archive = lakehouse_schema_enabled.path("archive/2026", root="Files")

    assert path.as_posix() == "raw/orders/2026-01-01.json"
    assert str(path) == "abfss://Finance@onelake.dfs.fabric.microsoft.com/Ops.lakehouse/Files/raw/orders/2026-01-01.json"
    assert logs.as_posix() == "logs/2026/04"
    assert str(logs) == "abfss://Finance@onelake.dfs.fabric.microsoft.com/Ops.lakehouse/Files/logs/2026/04"
    assert archive.as_posix() == "archive/2026"
    assert str(archive) == "abfss://Finance@onelake.dfs.fabric.microsoft.com/Ops.lakehouse/Files/archive/2026"


def test_raw_filesystem_and_storage_options_examples_work(lakehouse_schema_enabled):
    path = lakehouse_schema_enabled.files / "folder1" / "a.yaml"

    with lakehouse_schema_enabled.fs.open(path, "rb") as stream:
        payload = stream.read()

    storage_options = lakehouse_schema_enabled.storage_options

    assert payload == b"stub"
    assert storage_options["account_name"] == "onelake"
    assert storage_options["account_host"] == "onelake.blob.fabric.microsoft.com"
    assert storage_options["credential"] == "explicit-credential"


def test_table_root_locator_examples_work(lakehouse_schema_enabled, lakehouse_non_schema):
    orders = lakehouse_schema_enabled.table(schema="brz", name="orders")
    default_orders = lakehouse_schema_enabled.table(schema=None, name="orders")
    non_schema_orders = lakehouse_non_schema.table(schema=None, name="orders")

    assert str(orders) == "abfss://Finance@onelake.dfs.fabric.microsoft.com/Ops.lakehouse/Tables/brz/orders"
    assert str(default_orders) == "abfss://Finance@onelake.dfs.fabric.microsoft.com/Ops.lakehouse/Tables/dbo/orders"
    assert str(non_schema_orders) == "abfss://Finance@onelake.dfs.fabric.microsoft.com/Ops.lakehouse/Tables/orders"
    assert os.fspath(orders) == str(orders)


def test_table_root_is_a_locator_not_a_dataframe(lakehouse_schema_enabled):
    table_root = lakehouse_schema_enabled.table(schema="brz", name="orders")

    assert table_root.relative_path == "brz/orders"
    assert str(table_root) == "abfss://Finance@onelake.dfs.fabric.microsoft.com/Ops.lakehouse/Tables/brz/orders"
