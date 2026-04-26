from __future__ import annotations

import pytest

from fablake import LakehousePath, LakehousePathInfo


pytestmark = pytest.mark.live_fablake


def test_live_path_metadata_and_properties_contract(live_test_root):
    folder = live_test_root / "meta"
    file_path = folder / "payload.txt"

    folder.mkdir(parents=True, exist_ok=True)
    file_path.write_text("hello-metadata", encoding="utf-8")

    duplicate = live_test_root.joinpath("meta", "payload.txt")

    assert isinstance(file_path, LakehousePath)
    assert file_path.fs is live_test_root.fs
    assert file_path.root == "Files"
    assert file_path.path.endswith("meta/payload.txt")
    assert file_path.parts[-2:] == ("meta", "payload.txt")
    assert file_path.name == "payload.txt"
    assert file_path.stem == "payload"
    assert file_path.suffix == ".txt"
    assert file_path.parent == folder
    assert duplicate == file_path
    assert hash(duplicate) == hash(file_path)
    assert repr(file_path) == f"LakehousePath('{file_path.as_posix()}')"
    assert file_path.uri == str(file_path)

    file_info = file_path.info()
    folder_info = folder.info()

    assert isinstance(file_info, LakehousePathInfo)
    assert file_info.name == file_path.as_posix()
    assert file_info.type == "file"
    assert file_info.size == len("hello-metadata")
    assert file_info.creation_time is not None
    assert file_info.last_modified is not None
    assert file_info.etag
    assert file_info.tag_count is None or isinstance(file_info.tag_count, int)
    assert file_info.content_settings is not None
    assert file_info.metadata is None or isinstance(file_info.metadata, dict)
    assert file_info.tags is None or isinstance(file_info.tags, dict)
    assert isinstance(file_info.raw, dict)
    assert file_info.raw["name"] == file_path.as_posix()

    if isinstance(file_info.content_settings, dict):
        assert "content_type" in file_info.content_settings
    else:
        assert getattr(file_info.content_settings, "content_type", None) is not None

    assert isinstance(folder_info, LakehousePathInfo)
    assert folder_info.name == folder.as_posix()
    assert folder_info.type in {"directory", "dir"}
    assert folder_info.raw is not None

    assert file_path.resolve() == file_path
    assert file_path.resolve(strict=True) == file_path


def test_live_path_missing_ok_and_read_write_roundtrip(live_test_root):
    text_path = live_test_root / "writes" / "sample.txt"
    bytes_path = live_test_root / "writes" / "sample.bin"
    missing = live_test_root / "writes" / "missing.txt"

    text_path.parent.mkdir(parents=True, exist_ok=True)

    assert text_path.write_text("hello-write-text", encoding="utf-8") == len("hello-write-text")
    assert bytes_path.write_bytes(b"\x01\x02\x03") == 3
    assert text_path.read_text(encoding="utf-8") == "hello-write-text"
    assert bytes_path.read_bytes() == b"\x01\x02\x03"

    missing.unlink(missing_ok=True)
    assert not missing.exists()

    bytes_path.unlink()
    text_path.unlink()
    assert not bytes_path.exists()
    assert not text_path.exists()
