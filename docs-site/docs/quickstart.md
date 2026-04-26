# Quickstart

## Create a lakehouse context

```python
from fablake import Lakehouse

lh = Lakehouse(
    workspace="Finance",
    lakehouse="Ops",
    schema_enabled=True,
)
```

You can also bind by IDs:

```python
lh = Lakehouse(
    workspace_id="<workspace-id>",
    lakehouse_id="<lakehouse-id>",
    schema_enabled=True,
)
```

## Work with files

```python
path = lh.files / "raw" / "orders" / "2026-01-01.json"

if path.exists():
    print(path.read_text())

output = lh.files / "tmp" / "result.txt"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text("done")
```

## Build table locators

```python
orders = lh.table("orders", schema="brz")
print(orders)
# abfss://.../Tables/brz/orders
```

In schema-enabled lakehouses, `schema=None` maps to `dbo`:

```python
default_orders = lh.table("orders", schema=None)
print(default_orders)
# abfss://.../Tables/dbo/orders
```

For non-schema lakehouses:

```python
lh = Lakehouse(workspace="Finance", lakehouse="Ops", schema_enabled=False)
orders = lh.table("orders", schema=None)
```

List matching table locators:

```python
for table in lh.tables.list("db*.*der"):
    print(table)
```
