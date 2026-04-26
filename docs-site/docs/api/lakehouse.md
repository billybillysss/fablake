# Lakehouse

Lakehouse is the main entry point for fablake file and table path workflows.

## Signature

```python
Lakehouse(self, *, workspace: 'str | None' = None, workspace_id: 'str | None' = None, lakehouse: 'str | None' = None, lakehouse_id: 'str | None' = None, schema_enabled: 'bool' = True, **filesystem_kwargs) -> 'None'
```

## Parameters

- `self`
- `workspace`: `str | None` (default: `None`)
- `workspace_id`: `str | None` (default: `None`)
- `lakehouse`: `str | None` (default: `None`)
- `lakehouse_id`: `str | None` (default: `None`)
- `schema_enabled`: `bool` (default: `True`)
- `filesystem_kwargs`

## Description

Bound fablake Lakehouse context.

The class provides a filesystem-first entry point for working with paths
under the `Files` root and table locators under the `Tables` root.

A `Lakehouse` instance must be created with either:

- name binding: `workspace` + `lakehouse`
- id binding: `workspace_id` + `lakehouse_id`

## Example

```python
from fablake import Lakehouse

lh = Lakehouse(workspace="Finance", lakehouse="Ops", schema_enabled=True)
orders_file = lh.files / "raw" / "orders.parquet"
orders_table = lh.table("orders", schema="brz")
```

## Methods

### Lakehouse.path

<div class="api-signature">

```python
path(self, path: 'str' = '', *, root: 'str' = 'Files') -> 'LakehousePath'
```

</div>

Parameters:

- `self`
- `path`: `str` (default: ``)
- `root`: `str` (default: `Files`)

Returns: `LakehousePath`

Create a path object under the selected lakehouse root.

Parameters
----------
path:
    Logical path inside the selected root.
root:
    Lakehouse root to use. Supported values are `Files` and `Tables`.

### Lakehouse.table

<div class="api-signature">

```python
table(self, name: 'str', schema: 'str | None' = None) -> 'LakehouseTable'
```

</div>

Parameters:

- `self`
- `name`: `str`
- `schema`: `str | None` (default: `None`)

Returns: `LakehouseTable`

Create a table-root locator.

Parameters
----------
name:
    Table name as a single path segment.
schema:
    Schema name for schema-enabled lakehouses. Use `None` to target the
    default schema (`dbo`). Must be `None` when `schema_enabled=False`.

Returns
-------
LakehouseTable
    Table root locator under the `Tables` root.

