# Filesystem interop

Use `lh.fs` and `lh.storage_options` to integrate with data tools.

## pandas + PyArrow

```python
import pandas as pd

df = pd.read_parquet(
    lh.files / "raw" / "orders.parquet",
    engine="pyarrow",
    filesystem=lh.fs,
)
```

## PyArrow

```python
import pyarrow.parquet as pq

table = pq.read_table(
    lh.files / "raw" / "orders.parquet",
    filesystem=lh.fs,
)
```

## Polars

```python
import polars as pl

with lh.fs.open(lh.files / "raw" / "orders.parquet", "rb") as stream:
    df = pl.read_parquet(stream)
```

## Dask

```python
import dask.dataframe as dd

ddf = dd.read_parquet(
    lh.table("orders", schema="brz"),
    storage_options=lh.storage_options,
    engine="pyarrow",
)
```

## DuckDB

```python
import duckdb

duckdb.register_filesystem(lh.fs)

df = duckdb.sql(
    f"SELECT * FROM read_parquet('{lh.table('orders', schema='brz')}') LIMIT 10",
).df()
```

## Interop guidance

- Use `lh.files / ...` for file-level reads and writes.
- Use `lh.table(...)` for table-root readers.
- Use `lh.fs` when the target library accepts a filesystem object.
- Use `lh.storage_options` when the target library expects fsspec storage options.
