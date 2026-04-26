# fablake

`fablake` is a production-oriented Python library for Microsoft Fabric OneLake
Lakehouse access.

It provides:

- a filesystem-first `Lakehouse` API
- a pathlib-like `LakehousePath` for `Files` paths
- table root locators and discovery helpers for `Tables` interop
- filesystem interop for `pandas`, `PyArrow`, `Polars`, and `DuckDB`
- runtime support for both Microsoft Fabric notebooks and local development

## Install

Install with `uv`:

```bash
uv add fablake
```

For local authentication via Azure credentials, also install:

```bash
uv add azure-identity
```

`pip install fablake azure-identity` also works.

You can also install the auth extra with `pip install "fablake[auth]"`.

## Quick start

```python
from fablake import Lakehouse

lh = Lakehouse(workspace="Finance", lakehouse="Ops", schema_enabled=True)

path = lh.files / "raw" / "orders" / "2026-01-01.json"

if path.exists():
    print(path.read_text())

table_root = lh.table("orders", schema="brz")
print(table_root)

for table in lh.tables.list("db*.*der"):
    print(table)
```

## Core concepts

- `lh.files` targets the Lakehouse `Files` root.
- `lh.table(name, schema=...)` returns a `Tables` locator, not a dataframe.
- `lh.tables.list(pattern)` returns matching `LakehouseTable` locators.
- `lh.fs` exposes the underlying filesystem handle for library interop.

## Interop and runtime

- Use `lh.fs` as the filesystem layer for `pandas`, `PyArrow`, `Polars`, and
  `DuckDB` workflows.
- Inside Microsoft Fabric notebooks, omitted credentials use notebook/runtime
  auth resolution.
- In local development, install `azure-identity` and use your local Azure
  credential flow.

Filesystem interop example:

```python
from fablake import Lakehouse
import duckdb
import pandas as pd
import polars as pl
import pyarrow.parquet as pq

lh = Lakehouse(workspace="Finance", lakehouse="Ops", schema_enabled=True)
path = lh.files / "raw" / "orders.parquet"

# pandas + PyArrow engine
df_pd = pd.read_parquet(path, engine="pyarrow", filesystem=lh.fs)

# PyArrow
table = pq.read_table(path, filesystem=lh.fs)

# Polars (via file-like stream)
with lh.fs.open(path, "rb") as stream:
    df_pl = pl.read_parquet(stream)

# DuckDB
duckdb.register_filesystem(lh.fs)
df_duck = duckdb.sql(f"SELECT * FROM read_parquet('{path}')").df()
```

## Documentation

- User guide: [docs-site/docs/index.md](docs-site/docs/index.md)
- Python API docs: [docs-site/docs/api/index.md](docs-site/docs/api/index.md)
- Usage examples: [docs-site/docs/usage-examples.md](docs-site/docs/usage-examples.md)
- Changelog: [CHANGELOG.md](CHANGELOG.md)
- Version selector source: [docs-site/docs/versions.json](docs-site/docs/versions.json)

Build docs locally:

```bash
uv sync --group docs
uv run python scripts/docs.py serve
```

Other helper commands:

```bash
uv run python scripts/docs.py build
uv run python scripts/docs.py api
uv run python scripts/docs.py sync
```
