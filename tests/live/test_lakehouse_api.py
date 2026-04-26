from __future__ import annotations

import os

import pytest

from fablake import LakehousePath, LakehousePathInfo
from fablake.lakehouse import LakehouseTable


pytestmark = pytest.mark.live_fablake


def test_live_lakehouse_exposes_binding_and_storage_contract(live_lakehouse, live_config):
    assert live_lakehouse.workspace is None
    assert live_lakehouse.lakehouse is None
    assert live_lakehouse.workspace_id == live_config.workspace_id
    assert live_lakehouse.lakehouse_id == live_config.lakehouse_id
    assert live_lakehouse.binding.workspace == live_config.workspace_id
    assert live_lakehouse.binding.lakehouse == live_config.lakehouse_id
    assert live_lakehouse.binding.identifier_mode == "id"
    assert live_lakehouse.schema_enabled is True

    storage_options = live_lakehouse.storage_options
    assert storage_options["account_name"] == "onelake"
    assert storage_options["account_host"] == "onelake.blob.fabric.microsoft.com"
    assert storage_options["anon"] is False
    assert storage_options["asynchronous"] is False
    assert storage_options["max_concurrency"] == live_config.max_concurrency
    assert storage_options["credential"] is not None


def test_live_path_and_table_locators_expose_expected_public_contract(live_lakehouse, live_config):
    files_root = live_lakehouse.files
    explicit = live_lakehouse.path("alpha/beta.txt")
    table = live_lakehouse.table(schema="dbo", name=live_config.table_name.split(".", 1)[-1])

    assert isinstance(files_root, LakehousePath)
    assert files_root.root == "Files"
    assert files_root.path == "."
    assert files_root.as_posix() == "."
    assert files_root.uri.endswith("/Files")

    assert isinstance(explicit, LakehousePath)
    assert explicit.as_posix() == "alpha/beta.txt"
    assert explicit.root == "Files"
    assert explicit.uri.endswith("/Files/alpha/beta.txt")
    assert os.fspath(explicit) == str(explicit)

    assert isinstance(table, LakehouseTable)
    assert table.schema == "dbo"
    assert table.name == live_config.table_name.split(".", 1)[-1]
    assert table.relative_path == live_config.table_name.replace(".", "/")
    assert table.uri.endswith(f"/Tables/{table.relative_path}")
    assert str(table) == table.uri
    assert os.fspath(table) == table.uri
    assert repr(table) == f"LakehouseTable('{table.identifier}')"
