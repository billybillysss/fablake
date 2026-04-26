from __future__ import annotations

import os

import pytest


def test_files_join_and_stringify_to_canonical_uri(lakehouse_schema_enabled):
    path = lakehouse_schema_enabled.files / "folder1" / "a.yaml"

    assert path.as_posix() == "folder1/a.yaml"
    assert str(path) == "abfss://Finance@onelake.dfs.fabric.microsoft.com/Ops.lakehouse/Files/folder1/a.yaml"
    assert os.fspath(path) == str(path)


def test_files_repr_stays_logical(lakehouse_schema_enabled):
    path = lakehouse_schema_enabled.files / "folder1" / "a.yaml"

    assert repr(path) == "LakehousePath('folder1/a.yaml')"


def test_files_root_repr_is_dot(lakehouse_schema_enabled):
    assert repr(lakehouse_schema_enabled.files) == "LakehousePath('.')"


def test_files_root_stringifies_to_files_root_uri(lakehouse_schema_enabled):
    assert str(lakehouse_schema_enabled.files) == "abfss://Finance@onelake.dfs.fabric.microsoft.com/Ops.lakehouse/Files"


def test_lh_fs_open_accepts_stringified_path(lakehouse_schema_enabled):
    path = lakehouse_schema_enabled.files / "folder1" / "a.yaml"

    with lakehouse_schema_enabled.fs.open(str(path), "rb") as stream:
        payload = stream.read()

    assert payload == b"stub"
    assert lakehouse_schema_enabled.fs.open_calls[-1][0] == str(path)
    assert lakehouse_schema_enabled.fs.open_calls[-1][1] == "rb"


def test_path_open_uses_underlying_uri(lakehouse_schema_enabled):
    path = lakehouse_schema_enabled.files / "folder1" / "a.yaml"

    with path.open("rb") as stream:
        payload = stream.read()

    assert payload == b"stub"
    assert lakehouse_schema_enabled.fs.open_calls[-1][0] == str(path)


def test_resolve_returns_normalized_path_object(lakehouse_schema_enabled):
    path = lakehouse_schema_enabled.files / "folder1" / "a.yaml"

    resolved = path.resolve()

    assert resolved.as_posix() == "folder1/a.yaml"
    assert str(resolved) == "abfss://Finance@onelake.dfs.fabric.microsoft.com/Ops.lakehouse/Files/folder1/a.yaml"


def test_resolve_strict_true_returns_path_when_exists(lakehouse_schema_enabled):
    path = lakehouse_schema_enabled.files / "folder1" / "a.yaml"

    resolved = path.resolve(strict=True)

    assert resolved.as_posix() == "folder1/a.yaml"


def test_resolve_strict_true_raises_when_missing(lakehouse_schema_enabled):
    path = lakehouse_schema_enabled.files / "folder1" / "missing.txt"
    path.fs._fs.exists = lambda *_args, **_kwargs: False

    with pytest.raises(FileNotFoundError, match="folder1/missing.txt"):
        path.resolve(strict=True)


def test_files_and_tables_use_distinct_roots(lakehouse_schema_enabled):
    file_uri = str(lakehouse_schema_enabled.files / "folder1" / "a.yaml")
    table_uri = str(lakehouse_schema_enabled.table(schema="brz", name="orders"))

    assert "/Files/" in file_uri
    assert "/Tables/brz/orders" in table_uri


def test_fs_ls_returns_child_names_for_workspace_prefixed_entries(lakehouse_schema_enabled):
    regression = lakehouse_schema_enabled.files / "regression"
    child_name = "put-script-87433e8ca439487b96d5648a311c1820"
    backend_name = f"Finance/Ops.lakehouse/Files/regression/{child_name}"

    def fake_ls(path: str, detail: bool = False, **kwargs):
        return [backend_name]

    lakehouse_schema_enabled.fs._fs.ls = fake_ls

    result = lakehouse_schema_enabled.fs.ls(regression)

    assert [item.as_posix() for item in result] == [f"regression/{child_name}"]


def test_path_info_normalizes_workspace_prefixed_name_field(lakehouse_schema_enabled):
    regression = lakehouse_schema_enabled.files / "regression"
    child_name = "put-script-8faf4e8e5b444662a4c2014358afe355"
    backend_name = f"Finance/Ops.lakehouse/Files/regression/{child_name}"

    def fake_info(path: str, **kwargs):
        return {"name": backend_name, "type": "directory", "size": None}

    lakehouse_schema_enabled.fs._fs.info = fake_info

    result = (regression / child_name).info()

    assert result.name == f"regression/{child_name}"
    assert result.type == "directory"


def test_find_returns_path_objects_rooted_at_files(lakehouse_schema_enabled):
    base = lakehouse_schema_enabled.files / "regression" / "put-script-87433"
    backend_prefix = "Finance/Ops.lakehouse/Files/regression/put-script-87433"

    def fake_find(path: str, detail: bool = False, **kwargs):
        return [
            f"{backend_prefix}/bulk/dummy-0000.bin",
            f"{backend_prefix}/bulk/dummy-0001.bin",
        ]

    base.fs._fs.find = fake_find

    assert [item.as_posix() for item in base.find()] == [
        "regression/put-script-87433/bulk/dummy-0000.bin",
        "regression/put-script-87433/bulk/dummy-0001.bin",
    ]


def test_glob_does_not_duplicate_current_path_prefix(lakehouse_schema_enabled):
    base = lakehouse_schema_enabled.files / "regression" / "put-script-87433"
    backend_name = "Finance/Ops.lakehouse/Files/regression/put-script-87433/bulk/dummy-0000.bin"

    def fake_find(path: str, detail: bool = False, **kwargs):
        return [backend_name]

    base.fs._fs.find = fake_find

    matches = list(base.glob("**/*.bin"))

    assert [item.as_posix() for item in matches] == [
        "regression/put-script-87433/bulk/dummy-0000.bin",
    ]


def test_rename_accepts_new_file_name_only(lakehouse_schema_enabled):
    source = lakehouse_schema_enabled.files / "folder" / "a.txt"
    calls: list[tuple[str, str, str]] = []

    def fake_mv(path1: str, path2: str, *, root: str = "Files", **kwargs):
        calls.append((path1, path2, root))

    source.fs.mv = fake_mv

    renamed = source.rename("b.txt")

    assert renamed.as_posix() == "folder/b.txt"
    assert calls == [("folder/a.txt", "folder/b.txt", "Files")]


@pytest.mark.parametrize("target", ["../b.txt", "archive/b.txt", "folder\\b.txt", ".", "..", ""])
def test_rename_rejects_path_like_targets(lakehouse_schema_enabled, target):
    source = lakehouse_schema_enabled.files / "folder" / "a.txt"

    with pytest.raises(ValueError, match="file name|path segment|path separators|non-empty"):
        source.rename(target)


def test_rename_rejects_fablakepath_target(lakehouse_schema_enabled):
    source = lakehouse_schema_enabled.files / "folder" / "a.txt"
    target = lakehouse_schema_enabled.files / "folder" / "b.txt"

    with pytest.raises(TypeError, match="file name string"):
        source.rename(target)


def test_rename_rejects_root_path(lakehouse_schema_enabled):
    with pytest.raises(ValueError, match="root path"):
        lakehouse_schema_enabled.files.rename("b.txt")
