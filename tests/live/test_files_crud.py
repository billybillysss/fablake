from __future__ import annotations

import tempfile
from pathlib import Path

import pytest


pytestmark = pytest.mark.live_fablake


def test_live_filesystem_crud_and_regression_contract(live_test_root, record_property):
    source = live_test_root / "source.txt"
    copied = live_test_root / "copied.txt"
    moved = live_test_root / "moved.txt"
    nested = live_test_root / "nested"
    nested_child = nested / "child.txt"

    with tempfile.TemporaryDirectory() as temp_dir:
        local_source = Path(temp_dir) / "source.txt"
        local_source.write_text("hello-fablake", encoding="utf-8")
        live_test_root.fs.put(str(local_source), source.as_posix())

    nested.mkdir(parents=True, exist_ok=True)
    nested_child.write_text("nested-content")

    assert source.exists()
    assert source.is_file()
    assert source.read_text() == "hello-fablake"
    assert nested_child.exists()
    assert nested_child.read_text() == "nested-content"

    live_test_root.fs.copy(source.as_posix(), copied.as_posix())
    assert copied.exists()
    assert copied.read_text() == "hello-fablake"

    live_test_root.fs.mv(copied.as_posix(), moved.as_posix())
    assert not copied.exists()
    assert moved.exists()
    assert moved.read_text() == "hello-fablake"

    listed_names = {item.name for item in live_test_root.iterdir()}
    assert {"source.txt", "moved.txt", "nested"}.issubset(listed_names)

    nested_listing = {item.name for item in nested.iterdir()}
    assert "child.txt" in nested_listing

    moved.unlink()
    source.unlink()
    nested_child.unlink()

    assert not moved.exists()
    assert not source.exists()
    assert not nested_child.exists()

    record_property("live_root", str(live_test_root))
    record_property("listed_names", sorted(listed_names))
