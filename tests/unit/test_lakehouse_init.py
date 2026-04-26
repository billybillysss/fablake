from __future__ import annotations

import pytest

from fablake import Lakehouse
from fablake.exceptions import ResolutionError


def test_lakehouse_constructs_from_names():
    lh = Lakehouse(
        workspace="Finance",
        lakehouse="Ops",
        schema_enabled=True,
        credential="explicit-credential",
    )

    assert lh.workspace == "Finance"
    assert lh.lakehouse == "Ops"
    assert lh.workspace_id == "Finance"
    assert lh.lakehouse_id == "Ops"
    assert lh.binding.identifier_mode == "name"


def test_lakehouse_constructs_from_ids():
    lh = Lakehouse(
        workspace_id="ws-guid",
        lakehouse_id="lh-guid",
        schema_enabled=True,
        credential="explicit-credential",
    )

    assert lh.workspace is None
    assert lh.lakehouse is None
    assert lh.workspace_id == "ws-guid"
    assert lh.lakehouse_id == "lh-guid"
    assert lh.binding.identifier_mode == "id"


def test_lakehouse_mixed_name_and_id_raises():
    with pytest.raises(ResolutionError, match="not mixed"):
        Lakehouse(
            workspace="Finance",
            lakehouse_id="lh-guid",
            schema_enabled=True,
            credential="explicit-credential",
        )


def test_lakehouse_missing_workspace_raises():
    with pytest.raises(ResolutionError, match="Provide both workspace and lakehouse"):
        Lakehouse(lakehouse="Ops", schema_enabled=True, credential="explicit-credential")


def test_lakehouse_missing_lakehouse_raises():
    with pytest.raises(ResolutionError, match="Provide both workspace and lakehouse"):
        Lakehouse(workspace="Finance", schema_enabled=True, credential="explicit-credential")


def test_lakehouse_fs_is_single_public_filesystem_handle(lakehouse_schema_enabled):
    assert lakehouse_schema_enabled.fs.protocol == "abfs"
    assert hasattr(lakehouse_schema_enabled.fs, "open")
    assert hasattr(lakehouse_schema_enabled.fs, "exists")
    assert not hasattr(lakehouse_schema_enabled, "filesystem")
    assert not hasattr(lakehouse_schema_enabled, "raw_fs")


def test_lakehouse_storage_options_returns_copy(lakehouse_schema_enabled):
    first = lakehouse_schema_enabled.storage_options
    first["account_name"] = "changed"
    second = lakehouse_schema_enabled.storage_options

    assert second["account_name"] == "onelake"
    assert second["account_host"] == "onelake.blob.fabric.microsoft.com"
    assert second["anon"] is False
    assert second["asynchronous"] is False
