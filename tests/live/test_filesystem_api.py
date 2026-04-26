from __future__ import annotations

from pathlib import Path

import pytest

from fablake import LakehousePath


pytestmark = pytest.mark.live_fablake


def test_live_filesystem_listing_directory_and_metadata_contract(live_test_root):
    base = live_test_root / "fs-api"
    nested = base / "nested"
    child = nested / "item.txt"

    live_test_root.fs.makedirs(base.as_posix(), exist_ok=True)
    live_test_root.fs.mkdir(nested.as_posix(), create_parents=False)
    child.write_text("filesystem-contract", encoding="utf-8")

    assert live_test_root.fs.exists(base.as_posix())
    assert live_test_root.fs.isdir(base.as_posix())
    assert live_test_root.fs.isfile(child.as_posix())

    info = live_test_root.fs.info(child.as_posix())
    assert info["name"].endswith("fs-api/nested/item.txt")
    assert info["type"] == "file"
    assert info["size"] == len("filesystem-contract")

    listed = live_test_root.fs.ls(base.as_posix())
    found = live_test_root.fs.find(base.as_posix(), withdirs=True)
    globbed = live_test_root.fs.glob(f"{base.as_posix()}/**/*.txt")

    assert all(isinstance(item, LakehousePath) for item in listed)
    assert all(isinstance(item, LakehousePath) for item in found)
    assert all(isinstance(item, LakehousePath) for item in globbed)
    assert [item.as_posix() for item in listed] == [nested.as_posix()]
    assert nested in found
    assert child in found
    assert [item.as_posix() for item in globbed] == [child.as_posix()]


def test_live_filesystem_recursive_copy_mv_rm_and_tables_root_contract(
    live_lakehouse,
    live_test_root,
    live_config,
    temp_dir_path,
):
    local_tree = temp_dir_path / "payload"
    local_nested = local_tree / "nested"
    remote_source = live_test_root / "recursive-source"
    remote_copy = live_test_root / "recursive-copy"
    remote_moved = live_test_root / "recursive-moved"

    local_nested.mkdir(parents=True, exist_ok=True)
    (local_tree / "root.txt").write_text("root-file", encoding="utf-8")
    (local_nested / "child.txt").write_text("nested-file", encoding="utf-8")

    live_test_root.fs.put(str(local_tree), remote_source.as_posix(), recursive=True)
    live_test_root.fs.copy(remote_source.as_posix(), remote_copy.as_posix(), recursive=True)
    live_test_root.fs.mv(remote_copy.as_posix(), remote_moved.as_posix(), recursive=True)

    source_listing = sorted(item.as_posix() for item in live_test_root.fs.find(remote_source.as_posix(), withdirs=True))
    moved_listing = sorted(item.as_posix() for item in live_test_root.fs.find(remote_moved.as_posix(), withdirs=True))
    assert f"{remote_source.as_posix()}/nested" in source_listing
    assert f"{remote_source.as_posix()}/root.txt" in source_listing
    assert f"{remote_source.as_posix()}/nested/child.txt" in source_listing
    assert f"{remote_moved.as_posix()}/nested" in moved_listing
    assert f"{remote_moved.as_posix()}/root.txt" in moved_listing
    assert f"{remote_moved.as_posix()}/nested/child.txt" in moved_listing
    assert not remote_copy.exists()

    live_test_root.fs.rm(remote_source.as_posix(), recursive=True)
    live_test_root.fs.rm(remote_moved.as_posix(), recursive=True)
    assert not remote_source.exists()
    assert not remote_moved.exists()

    table = live_lakehouse.table(schema="dbo", name=live_config.table_name.split(".", 1)[-1])
    table_root = live_lakehouse.path(table.relative_path, root="Tables")
    table_info = live_lakehouse.fs.info(table.relative_path, root="Tables")

    assert table_root.root == "Tables"
    assert str(table_root) == str(table)
    assert live_lakehouse.fs.exists(table.relative_path, root="Tables")
    assert live_lakehouse.fs.isdir(table.relative_path, root="Tables")
    assert table_info["name"].endswith(table.relative_path)
    assert table_info["type"] in {"directory", "dir"}

    table_listing = live_lakehouse.fs.ls("dbo", root="Tables")
    assert any(item == table_root for item in table_listing)
