# LakehouseTable

LakehouseTable is a lightweight path-like locator for the Tables root.

## Signature

```python
LakehouseTable(filesystem: FabLakeFileSystem, schema: str | None, name: str, schema_enabled: bool = True)
```

## Parameters

- `filesystem`: `FabLakeFileSystem`
- `schema`: `str | None`
- `name`: `str`
- `schema_enabled`: `bool` (default: `True`)

## Description

Table-root locator under the fablake `Tables` area.

The object is path-like and stringifies to an ABFSS URI.

## Example

```python
table_root = lh.table("orders", schema="dbo")
print(table_root)
```

## Properties

- `schema: str | None`
- `name: str`
- `schema_enabled: bool`
- `relative_path: str`
- `identifier: str`
- `uri: str`

## Methods

No public methods.

