# Usage examples

This guide collects the main usage patterns for `fablake`, centered on the
filesystem-first `Lakehouse` API.

## Create a lakehouse context

You can bind a lakehouse by name or by id.

Use one style per instance:

- names: `workspace=...` and `lakehouse=...`
- ids: `workspace_id=...` and `lakehouse_id=...`

Mixed values are rejected.

Use whichever style is easier for your application inputs.

```python
from fablake import Lakehouse

lh = Lakehouse(
    workspace="Finance",
    lakehouse="Ops",
    schema_enabled=True,
)

lh_by_id = Lakehouse(
    workspace_id="<workspace-id>",
    lakehouse_id="<lakehouse-id>",
    schema_enabled=True,
)
```

## Filesystem and pathlib-like paths

`lh.files` is the root of the `Files` area.

```python
from fablake import Lakehouse

lh = Lakehouse(workspace="Finance", lakehouse="Ops", schema_enabled=True)

path = lh.files / "raw" / "orders" / "2026-01-01.json"

print(path.as_posix())
# raw/orders/2026-01-01.json

print(str(path))
# abfss://.../Files/raw/orders/2026-01-01.json
```

You can also build paths explicitly:

```python
logs = lh.path("logs/2026/04", root="Files")
archive = lh.path("archive/2026", root="Files")
```

Use `lh.files / ...` for most file paths. Use `lh.path(...)` when you already
have a path string.

## Read and write files

```python
from fablake import Lakehouse

lh = Lakehouse(workspace="Finance", lakehouse="Ops", schema_enabled=True)

config = lh.files / "config" / "settings.json"

if config.exists():
    text = config.read_text()

output = lh.files / "tmp" / "result.txt"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text("done")

renamed = output.rename("result-final.txt")
```

`rename(...)` only accepts a new file name (single segment). Targets such as
`../result.txt` or `archive/result.txt` are rejected.

## Use the filesystem handle

`lh.fs` is the main filesystem handle.

```python
from fablake import Lakehouse

lh = Lakehouse(workspace="Finance", lakehouse="Ops", schema_enabled=True)

with lh.fs.open(lh.files / "folder1" / "a.yaml", "rb") as stream:
    payload = stream.read()
```

## Inspect storage options

`lh.storage_options` exposes the storage/backend configuration used to create
`lh.fs`.

```python
from fablake import Lakehouse

lh = Lakehouse(workspace="Finance", lakehouse="Ops", schema_enabled=True)

print(lh.storage_options)
```

## Table root locators

`lh.table(name, schema=...)` returns the physical table root path in fablake.
Pass that path to the library that should read the table.

### Schema-enabled lakehouses

```python
from fablake import Lakehouse

lh = Lakehouse(workspace="Finance", lakehouse="Ops", schema_enabled=True)

orders = lh.table("orders", schema="brz")
default_orders = lh.table("orders", schema=None)

print(str(orders))
# abfss://.../Tables/brz/orders

print(str(default_orders))
# abfss://.../Tables/dbo/orders
```

### Non-schema lakehouses

```python
from fablake import Lakehouse

lh = Lakehouse(workspace="Finance", lakehouse="Ops", schema_enabled=False)

orders = lh.table("orders", schema=None)

print(str(orders))
# abfss://.../Tables/orders
```

For non-schema lakehouses, omit the schema.

## Dask example

Install Dask separately if you want to use this workflow.

```python
import dask.dataframe as dd
from fablake import Lakehouse

lh = Lakehouse(workspace="Finance", lakehouse="Ops", schema_enabled=True)

ddf = dd.read_parquet(
    lh.table("orders", schema="brz"),
    storage_options=lh.storage_options,
    engine="pyarrow",
)
```

## pandas example

Install `pandas` and `pyarrow` separately if you want to use this workflow.

```python
import pandas as pd
from fablake import Lakehouse

lh = Lakehouse(workspace="Finance", lakehouse="Ops", schema_enabled=True)

df = pd.read_parquet(
    lh.files / "raw" / "orders.parquet",
    engine="pyarrow",
    filesystem=lh.fs,
)
```

## PyArrow example

Install `pyarrow` separately if you want to use this workflow.

```python
import pyarrow.parquet as pq
from fablake import Lakehouse

lh = Lakehouse(workspace="Finance", lakehouse="Ops", schema_enabled=True)

table = pq.read_table(
    lh.files / "raw" / "orders.parquet",
    filesystem=lh.fs,
)
```

## Polars example

Install `polars` separately if you want to use this workflow.

```python
import polars as pl
from fablake import Lakehouse

lh = Lakehouse(workspace="Finance", lakehouse="Ops", schema_enabled=True)

with lh.fs.open(lh.files / "raw" / "orders.parquet", "rb") as stream:
    df = pl.read_parquet(stream)
```

## DuckDB example

Install `duckdb` separately if you want to use this workflow.

```python
import duckdb
from fablake import Lakehouse

lh = Lakehouse(workspace="Finance", lakehouse="Ops", schema_enabled=True)

duckdb.register_filesystem(lh.fs)

df = duckdb.sql(
    f"SELECT * FROM read_parquet('{lh.table('orders', schema='brz')}') LIMIT 10",
).df()
```

## Table roots are locators, not dataframes

`lh.table(...)` gives you the physical fablake table root. Pass it into the
library that should read it.

```python
from fablake import Lakehouse

lh = Lakehouse(workspace="Finance", lakehouse="Ops", schema_enabled=True)

table_root = lh.table("orders", schema="brz")

print(table_root)
# abfss://.../Tables/brz/orders
```

Use that locator with tools like Dask, DuckDB, or any other consumer that can
work with the table root plus the matching filesystem or storage options.

## Discover tables by pattern

```python
from fablake import Lakehouse

lh = Lakehouse(workspace="Finance", lakehouse="Ops", schema_enabled=True)

for table in lh.tables.list("db*.*der"):
    print(table)
```
