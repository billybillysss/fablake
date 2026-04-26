# Tables

`lh.table(name, schema=...)` returns a `LakehouseTable` locator for the `Tables`
root.

It is a path-like table root reference, not a dataframe object.

## Schema-enabled lakehouses

When `schema_enabled=True`:

```python
orders = lh.table("orders", schema="brz")
print(orders)
# abfss://.../Tables/brz/orders
```

`schema=None` defaults to `dbo`:

```python
default_orders = lh.table("orders", schema=None)
print(default_orders)
# abfss://.../Tables/dbo/orders
```

## Non-schema lakehouses

When `schema_enabled=False`, schema must be omitted:

```python
lh = Lakehouse(workspace="Finance", lakehouse="Ops", schema_enabled=False)
orders = lh.table("orders", schema=None)
print(orders)
# abfss://.../Tables/orders
```

Passing a non-empty schema in non-schema mode raises `TableIdentifierError`.

## List matching tables

Use `lh.tables.list(pattern)` to discover table roots.

```python
matches = lh.tables.list("db*.*der")

for table in matches:
    print(table)
```

Pattern semantics:

- schema-enabled + no schema filter: match against `<schema>.<table>`
- schema-enabled + `schema=...`: match against `<table>` within that schema
- non-schema mode: match against `<table>`

## Identifier validation rules

- Table name is required and must be a single path segment.
- Schema, when provided, must be a single path segment.
- Slash and backslash separators are rejected.
