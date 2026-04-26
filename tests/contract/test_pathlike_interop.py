from __future__ import annotations

import importlib
import os
import sys
import types
from typing import Any, cast

def test_fablake_path_is_os_pathlike(lakehouse_schema_enabled):
    path = lakehouse_schema_enabled.files / "raw" / "orders.parquet"

    assert os.fspath(path) == "abfss://Finance@onelake.dfs.fabric.microsoft.com/Ops.lakehouse/Files/raw/orders.parquet"


def test_lakehouse_fs_open_accepts_fablakepath_directly(lakehouse_schema_enabled):
    path = lakehouse_schema_enabled.files / "raw" / "orders.parquet"

    with lakehouse_schema_enabled.fs.open(path, "rb") as stream:
        payload = stream.read()

    assert payload == b"stub"
    assert lakehouse_schema_enabled.fs.open_calls[-1][0] == os.fspath(path)
    assert lakehouse_schema_enabled.fs.open_calls[-1][1] == "rb"


def test_lakehouse_fs_ls_accepts_fablakepath_directly(lakehouse_schema_enabled):
    path = lakehouse_schema_enabled.files / "raw"

    listing = lakehouse_schema_enabled.fs.ls(path)

    assert [item.as_posix() for item in listing] == [
        "raw/folder1",
        "raw/a.yaml",
    ]
    assert lakehouse_schema_enabled.fs.last_ls_path == os.fspath(path)


def test_lakehouse_fs_open_normalizes_fablakepath_to_uri(lakehouse_schema_enabled):
    path = lakehouse_schema_enabled.files / "raw" / "orders.parquet"

    with lakehouse_schema_enabled.fs.open(path, "rb") as stream:
        payload = stream.read()

    assert payload == b"stub"
    assert lakehouse_schema_enabled.fs.open_calls[-1][0] == os.fspath(path)


def test_pandas_read_parquet_accepts_fablakepath_directly(monkeypatch, lakehouse_schema_enabled):
    calls = {}
    module = types.ModuleType("pandas")

    def read_parquet(path, **kwargs):
        calls["path"] = path
        calls["kwargs"] = kwargs
        return "ok"

    setattr(module, "read_parquet", read_parquet)
    monkeypatch.setitem(sys.modules, "pandas", module)

    pd = cast(Any, importlib.import_module("pandas"))
    path = lakehouse_schema_enabled.files / "raw" / "orders.parquet"

    result = pd.read_parquet(
        path,
        engine="pyarrow",
        filesystem=lakehouse_schema_enabled.fs,
    )

    assert result == "ok"
    assert os.fspath(calls["path"]) == os.fspath(path)
    assert calls["kwargs"]["filesystem"] is lakehouse_schema_enabled.fs


def test_pyarrow_read_table_receives_fablakepath_directly(monkeypatch, lakehouse_schema_enabled):
    calls = {}
    package = types.ModuleType("pyarrow")
    parquet = types.ModuleType("pyarrow.parquet")

    def read_table(path, **kwargs):
        calls["path"] = path
        calls["kwargs"] = kwargs
        return "table"

    setattr(parquet, "read_table", read_table)
    setattr(package, "parquet", parquet)
    monkeypatch.setitem(sys.modules, "pyarrow", package)
    monkeypatch.setitem(sys.modules, "pyarrow.parquet", parquet)

    pq = cast(Any, importlib.import_module("pyarrow.parquet"))
    path = lakehouse_schema_enabled.files / "raw" / "orders.parquet"

    result = pq.read_table(path, filesystem=lakehouse_schema_enabled.fs)

    assert result == "table"
    assert os.fspath(calls["path"]) == os.fspath(path)
    assert calls["kwargs"]["filesystem"] is lakehouse_schema_enabled.fs


def test_polars_read_parquet_accepts_fablakepath_directly(monkeypatch, lakehouse_schema_enabled):
    calls = {}
    module = types.ModuleType("polars")

    def read_parquet(path):
        calls["path"] = path
        return "polars-df"

    setattr(module, "read_parquet", read_parquet)
    monkeypatch.setitem(sys.modules, "polars", module)

    pl = cast(Any, importlib.import_module("polars"))
    path = lakehouse_schema_enabled.files / "raw" / "orders.parquet"

    result = pl.read_parquet(path)

    assert result == "polars-df"
    assert os.fspath(calls["path"]) == os.fspath(path)


def test_duckdb_read_parquet_query_accepts_fablakepath_directly(monkeypatch, lakehouse_schema_enabled):
    calls = {}
    module = types.ModuleType("duckdb")

    def register_filesystem(fs):
        calls["fs"] = fs

    def sql(query: str):
        calls["query"] = query
        return "duckdb-result"

    setattr(module, "register_filesystem", register_filesystem)
    setattr(module, "sql", sql)
    monkeypatch.setitem(sys.modules, "duckdb", module)

    duckdb = cast(Any, importlib.import_module("duckdb"))
    table_root = lakehouse_schema_enabled.table(schema="brz", name="orders")

    duckdb.register_filesystem(lakehouse_schema_enabled.fs)
    result = duckdb.sql(f"SELECT * FROM read_parquet('{table_root}')")

    assert result == "duckdb-result"
    assert calls["fs"] is lakehouse_schema_enabled.fs
    assert os.fspath(table_root) in calls["query"]
