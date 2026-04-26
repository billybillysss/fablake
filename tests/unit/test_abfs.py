from __future__ import annotations

import importlib

import pytest

from fablake._abfs import FabLakeFileSystem
from fablake.exceptions import ResolutionError


@pytest.fixture
def filesystem():
    return FabLakeFileSystem(
        workspace_id="ws-123",
        lakehouse_id="lh-456",
        credential="explicit-credential",
    )


def test_rm_tolerates_fablake_delete_status_ok_response(filesystem):
    def fail_rm(*args, **kwargs):
        raise RuntimeError("Operation returned an invalid status 'OK'")

    filesystem._fs.rm = fail_rm

    filesystem.rm("folder1/a.yaml")


def test_rm_re_raises_unrelated_runtime_errors(filesystem):
    def fail_rm(*args, **kwargs):
        raise RuntimeError("different failure")

    filesystem._fs.rm = fail_rm

    with pytest.raises(RuntimeError, match="different failure"):
        filesystem.rm("folder1/a.yaml")


def test_mv_delegates_to_underlying_abfs_mv(filesystem):
    calls: list[tuple[object, object, dict]] = []

    def fake_mv(path1, path2, **kwargs):
        calls.append((path1, path2, kwargs))

    filesystem._fs.mv = fake_mv

    filesystem.mv("from.txt", "to.txt")

    assert calls == [
        (
            "abfss://ws-123@onelake.dfs.fabric.microsoft.com/lh-456/Files/from.txt",
            "abfss://ws-123@onelake.dfs.fabric.microsoft.com/lh-456/Files/to.txt",
            {"recursive": False, "maxdepth": None},
        ),
    ]


def test_put_delegates_to_underlying_abfs(filesystem):
    calls: list[tuple[object, object, dict]] = []

    def fake_put(lpath, rpath, **kwargs):
        calls.append((lpath, rpath, kwargs))

    filesystem._fs.put = fake_put

    filesystem.put("local.bin", "remote.bin")

    assert calls == [
        (
            "local.bin",
            "abfss://ws-123@onelake.dfs.fabric.microsoft.com/lh-456/Files/remote.bin",
            {},
        ),
    ]


def test_put_uses_name_based_fablake_abfss_form():
    filesystem = FabLakeFileSystem(
        workspace="Finance",
        lakehouse="Ops",
        identifier_mode="name",
        credential="explicit-credential",
    )
    calls: list[tuple[object, object, dict]] = []

    def fake_put(lpath, rpath, **kwargs):
        calls.append((lpath, rpath, kwargs))

    filesystem._fs.put = fake_put

    filesystem.put("local.bin", "remote.bin")

    assert calls == [
        (
            "local.bin",
            "abfss://Finance@onelake.dfs.fabric.microsoft.com/Ops.lakehouse/Files/remote.bin",
            {},
        ),
    ]


def test_missing_fsspec_error_guides_package_install(monkeypatch):
    original_import_module = importlib.import_module

    def fake_import_module(name: str, package: str | None = None):
        if name == "fsspec":
            raise ModuleNotFoundError("No module named 'fsspec'")
        return original_import_module(name, package)

    monkeypatch.setattr(importlib, "import_module", fake_import_module)

    with pytest.raises(RuntimeError, match=r"install fablake|install -e \\."):
        FabLakeFileSystem(workspace_id="ws-123", lakehouse_id="lh-456")


def test_ls_raises_resolution_error_for_missing_name_bound_lakehouse():
    filesystem = FabLakeFileSystem(
        workspace="WS_EDA_BENNY",
        lakehouse="LH_GEN_CTA",
        identifier_mode="name",
        credential="explicit-credential",
    )

    def fail_ls(*args, **kwargs):
        error = FileNotFoundError(
            "[Errno 2] No such file or directory: 'WS_EDA_BENNY/LH_GEN_CTA.lakehouse/Files'",
        )
        error.__cause__ = Exception(
            "Request Failed with Artifact 'LH_GEN_CTA.lakehouse' is not found in workspace 'WS_EDA_BENNY'. "
            "ErrorCode:ArtifactNotFound",
        )
        raise error

    filesystem._fs.ls = fail_ls

    with pytest.raises(ResolutionError, match="ArtifactNotFound") as exc_info:
        filesystem.ls(".")

    assert "workspace 'WS_EDA_BENNY'" in str(exc_info.value)
    assert "lakehouse 'LH_GEN_CTA'" in str(exc_info.value)


def test_ls_preserves_plain_missing_path_file_not_found(filesystem):
    def fail_ls(*args, **kwargs):
        raise FileNotFoundError(
            "[Errno 2] No such file or directory: 'ws-123/lh-456/Files/t12'",
        )

    filesystem._fs.ls = fail_ls

    with pytest.raises(FileNotFoundError, match=r"Files/t12"):
        filesystem.ls("t12")


def test_storage_options_setter_updates_public_storage_options(filesystem):
    filesystem.storage_options = {"account_name": "custom", "anon": True}

    current = filesystem.storage_options
    assert current["account_name"] == "custom"
    assert current["anon"] is True
    assert current["account_host"] == "onelake.blob.fabric.microsoft.com"

    current["account_name"] = "changed"
    assert filesystem.storage_options["account_name"] == "custom"


def test_copy_recursive_directory_uses_file_level_fallback(filesystem):
    copied: list[tuple[str, str, dict]] = []

    def fake_find(path: str, withdirs: bool = False, detail: bool = False, **kwargs):
        assert withdirs is True
        assert detail is True
        return {
            "ws-123/lh-456/Files/source/nested": {"type": "directory"},
            "ws-123/lh-456/Files/source/a.txt": {"type": "file"},
            "ws-123/lh-456/Files/source/nested/b.txt": {"type": "file"},
        }

    def fake_copy(path1, path2, **kwargs):
        copied.append((path1, path2, kwargs))

    filesystem._fs.find = fake_find
    filesystem._fs.copy = fake_copy
    filesystem._fs.isdir = lambda path: path.endswith("/Files/source")

    filesystem.copy("source", "target", recursive=True)

    assert copied == [
        (
            "abfss://ws-123@onelake.dfs.fabric.microsoft.com/lh-456/Files/source/a.txt",
            "abfss://ws-123@onelake.dfs.fabric.microsoft.com/lh-456/Files/target/a.txt",
            {"recursive": False, "on_error": "raise", "maxdepth": None},
        ),
        (
            "abfss://ws-123@onelake.dfs.fabric.microsoft.com/lh-456/Files/source/nested/b.txt",
            "abfss://ws-123@onelake.dfs.fabric.microsoft.com/lh-456/Files/target/nested/b.txt",
            {"recursive": False, "on_error": "raise", "maxdepth": None},
        ),
    ]


def test_mv_recursive_directory_uses_file_level_fallback(filesystem):
    moved: list[tuple[str, str, dict]] = []
    removed: list[tuple[str, bool]] = []
    existing = {
        "abfss://ws-123@onelake.dfs.fabric.microsoft.com/lh-456/Files/source",
        "abfss://ws-123@onelake.dfs.fabric.microsoft.com/lh-456/Files/source/nested",
    }

    def fake_find(path: str, withdirs: bool = False, detail: bool = False, **kwargs):
        assert withdirs is True
        assert detail is True
        return {
            "ws-123/lh-456/Files/source/nested": {"type": "directory"},
            "ws-123/lh-456/Files/source/a.txt": {"type": "file"},
            "ws-123/lh-456/Files/source/nested/b.txt": {"type": "file"},
        }

    def fake_mv(path1, path2, **kwargs):
        moved.append((path1, path2, kwargs))

    def fake_exists(path: str, **kwargs):
        return path in existing

    def fake_rm(path: str, recursive: bool = False, **kwargs):
        removed.append((path, recursive))
        existing.discard(path)

    filesystem._fs.find = fake_find
    filesystem._fs.mv = fake_mv
    filesystem._fs.exists = fake_exists
    filesystem._fs.rm = fake_rm
    filesystem._fs.isdir = lambda path: path.endswith("/Files/source")

    filesystem.mv("source", "target", recursive=True)

    assert moved == [
        (
            "abfss://ws-123@onelake.dfs.fabric.microsoft.com/lh-456/Files/source/a.txt",
            "abfss://ws-123@onelake.dfs.fabric.microsoft.com/lh-456/Files/target/a.txt",
            {"recursive": False, "maxdepth": None},
        ),
        (
            "abfss://ws-123@onelake.dfs.fabric.microsoft.com/lh-456/Files/source/nested/b.txt",
            "abfss://ws-123@onelake.dfs.fabric.microsoft.com/lh-456/Files/target/nested/b.txt",
            {"recursive": False, "maxdepth": None},
        ),
    ]
    assert removed == [
        ("abfss://ws-123@onelake.dfs.fabric.microsoft.com/lh-456/Files/source/nested", False),
        ("abfss://ws-123@onelake.dfs.fabric.microsoft.com/lh-456/Files/source", False),
    ]
