from __future__ import annotations

import importlib
import sys
import types
from typing import Any, cast


def test_pandas_read_parquet_uses_lakehouse_fs_and_uri(monkeypatch, lakehouse_schema_enabled):
    calls = {}
    module = types.ModuleType("pandas")

    def read_parquet(path, **kwargs):
        calls["path"] = path
        calls["kwargs"] = kwargs
        return "ok"

    setattr(module, "read_parquet", read_parquet)
    monkeypatch.setitem(sys.modules, "pandas", module)

    pd = cast(Any, importlib.import_module("pandas"))

    result = pd.read_parquet(
        str(lakehouse_schema_enabled.files / "raw" / "orders.parquet"),
        engine="pyarrow",
        filesystem=lakehouse_schema_enabled.fs,
    )

    assert result == "ok"
    assert calls["path"] == "abfss://Finance@onelake.dfs.fabric.microsoft.com/Ops.lakehouse/Files/raw/orders.parquet"
    assert calls["kwargs"]["filesystem"] is lakehouse_schema_enabled.fs
    assert calls["kwargs"]["engine"] == "pyarrow"


def test_pyarrow_read_table_uses_lakehouse_fs_and_uri(monkeypatch, lakehouse_schema_enabled):
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

    result = pq.read_table(
        lakehouse_schema_enabled.files / "raw" / "orders.parquet",
        filesystem=lakehouse_schema_enabled.fs,
    )

    assert result == "table"
    assert calls["kwargs"]["filesystem"] is lakehouse_schema_enabled.fs


def test_dask_read_parquet_uses_table_uri_and_storage_options(monkeypatch, lakehouse_schema_enabled):
    calls = {}
    package = types.ModuleType("dask")
    dataframe = types.ModuleType("dask.dataframe")

    def read_parquet(path, **kwargs):
        calls["path"] = path
        calls["kwargs"] = kwargs
        return "ddf"

    setattr(dataframe, "read_parquet", read_parquet)
    setattr(package, "dataframe", dataframe)
    monkeypatch.setitem(sys.modules, "dask", package)
    monkeypatch.setitem(sys.modules, "dask.dataframe", dataframe)

    dd = cast(Any, importlib.import_module("dask.dataframe"))

    result = dd.read_parquet(
        lakehouse_schema_enabled.table(schema="brz", name="orders"),
        storage_options=lakehouse_schema_enabled.storage_options,
        engine="pyarrow",
    )

    assert result == "ddf"
    assert str(calls["path"]) == "abfss://Finance@onelake.dfs.fabric.microsoft.com/Ops.lakehouse/Tables/brz/orders"
    assert calls["kwargs"]["storage_options"] == lakehouse_schema_enabled.storage_options
    assert calls["kwargs"]["engine"] == "pyarrow"


def test_dask_read_parquet_uses_non_schema_table_path(monkeypatch, lakehouse_non_schema):
    calls = {}
    package = types.ModuleType("dask")
    dataframe = types.ModuleType("dask.dataframe")

    def read_parquet(path, **kwargs):
        calls["path"] = path
        calls["kwargs"] = kwargs
        return "ddf"

    setattr(dataframe, "read_parquet", read_parquet)
    setattr(package, "dataframe", dataframe)
    monkeypatch.setitem(sys.modules, "dask", package)
    monkeypatch.setitem(sys.modules, "dask.dataframe", dataframe)

    dd = cast(Any, importlib.import_module("dask.dataframe"))

    dd.read_parquet(
        lakehouse_non_schema.table(schema=None, name="orders"),
        storage_options=lakehouse_non_schema.storage_options,
        engine="pyarrow",
    )

    assert str(calls["path"]) == "abfss://Finance@onelake.dfs.fabric.microsoft.com/Ops.lakehouse/Tables/orders"


def test_polars_read_parquet_uses_file_like_object_from_lakehouse_fs(monkeypatch, lakehouse_schema_enabled):
    calls = {}
    module = types.ModuleType("polars")

    def read_parquet(stream):
        calls["stream"] = stream
        return "polars-df"

    setattr(module, "read_parquet", read_parquet)
    monkeypatch.setitem(sys.modules, "polars", module)

    pl = cast(Any, importlib.import_module("polars"))

    with lakehouse_schema_enabled.fs.open(str(lakehouse_schema_enabled.files / "raw" / "orders.parquet"), "rb") as stream:
        result = pl.read_parquet(stream)

    assert result == "polars-df"
    assert calls["stream"] is not None
    assert lakehouse_schema_enabled.fs.open_calls[-1][0] == "abfss://Finance@onelake.dfs.fabric.microsoft.com/Ops.lakehouse/Files/raw/orders.parquet"
    assert lakehouse_schema_enabled.fs.open_calls[-1][1] == "rb"


def test_duckdb_register_filesystem_and_query_use_lakehouse_contract(monkeypatch, lakehouse_schema_enabled):
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

    duckdb.register_filesystem(lakehouse_schema_enabled.fs)
    result = duckdb.sql(
        f"SELECT * FROM read_parquet('{lakehouse_schema_enabled.table(schema='brz', name='orders')}')",
    )

    assert calls["fs"] is lakehouse_schema_enabled.fs
    assert "abfss://Finance@onelake.dfs.fabric.microsoft.com/Ops.lakehouse/Tables/brz/orders" in calls["query"]
    assert result == "duckdb-result"
