# LakehouseTables

LakehouseTables provides table discovery helpers under the Tables root.

## Signature

```python
LakehouseTables(self, lakehouse: 'Lakehouse') -> 'None'
```

## Parameters

- `self`
- `lakehouse`: `Lakehouse`

## Description

Table discovery helpers under the `Tables` root.

## Example

```python
matches = lh.tables.list("db*.*der")

for table in matches:
    print(table)
```

## Methods

### LakehouseTables.list

<div class="api-signature">

```python
list(self, pattern: 'str' = '*', *, schema: 'str | None' = None) -> 'list[LakehouseTable]'
```

</div>

Parameters:

- `self`
- `pattern`: `str` (default: `*`)
- `schema`: `str | None` (default: `None`)

Returns: `list[LakehouseTable]`

Return table locators matching `pattern`.

Pattern matching rules:

- schema-enabled + no schema filter: match against `<schema>.<table>`
- schema-enabled + schema filter: match against `<table>` in that schema
- non-schema mode: match against `<table>`

