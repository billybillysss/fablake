# API reference

This page documents the public API surface exposed by `fablake`.

For signatures and per-function parameter details, see
[Python API](api/).

## Top-level exports

From `fablake`:

- `Lakehouse`
- `LakehousePath`
- `LakehousePathInfo`

From `fablake.lakehouse`:

- `Lakehouse`
- `LakehouseTable`
- `LakehouseTables`

## Lakehouse

Main object for binding workspace/lakehouse context and creating file/table
locators.

### Constructor

```python
Lakehouse(
    *,
    workspace: str | None = None,
    workspace_id: str | None = None,
    lakehouse: str | None = None,
    lakehouse_id: str | None = None,
    schema_enabled: bool = True,
    **filesystem_kwargs,
)
```

### Properties

- `workspace: str | None`
- `workspace_id: str`
- `lakehouse: str | None`
- `lakehouse_id: str`
- `binding: LakehouseBinding`
- `schema_enabled: bool | None`
- `fs`
- `storage_options: dict[str, Any]`
- `files: LakehousePath`
- `tables: LakehouseTables`

### Methods

- `path(path: str = "", *, root: str = "Files") -> LakehousePath`
- `table(name: str, schema: str | None = None) -> LakehouseTable`

## LakehousePath

Path-like wrapper around fablake file paths under a selected root.

### Selected properties

- `fs`
- `root`
- `path`
- `parts`
- `name`
- `stem`
- `suffix`
- `parent`
- `uri`

### Selected methods

- path construction: `joinpath(...)`, `/`
- conversion: `as_posix()`, `__fspath__()`
- metadata: `exists()`, `is_dir()`, `is_file()`, `info()`
- traversal: `iterdir()`, `glob()`, `rglob()`, `find(...)`
- file ops: `open(...)`, `read_text(...)`, `read_bytes(...)`,
  `write_text(...)`, `write_bytes(...)`
- dir ops: `mkdir(...)`
- mutation: `unlink(...)`, `rename(...)`
- resolution: `resolve(...)`

## LakehouseTable

Table root locator for the `Tables` area.

### Fields

- `schema: str | None`
- `name: str`
- `schema_enabled: bool`

### Properties

- `relative_path: str`
- `uri: str`

### Behavior

- `str(table)` returns the ABFSS URI
- `os.fspath(table)` returns the ABFSS URI

## LakehouseTables

Table discovery helper attached to `Lakehouse.tables`.

### Methods

- `list(pattern: str = "*", *, schema: str | None = None) -> list[LakehouseTable]`

Pattern behavior:

- schema-enabled + no schema filter: match `<schema>.<table>`
- schema-enabled + `schema=...`: match `<table>` names in that schema
- non-schema mode: match `<table>`

## LakehousePathInfo

Dataclass returned by `LakehousePath.info()`.

Fields include:

- `name`, `type`, `size`
- `metadata`, `creation_time`, `deleted`, `deleted_time`, `last_modified`
- `content_settings`, `remaining_retention_days`, `archive_status`
- `last_accessed_on`, `etag`, `tags`, `tag_count`
- `raw`

## Exceptions

- `FabLakeError`: base package exception
- `ResolutionError`: raised for workspace/lakehouse resolution failures
- `TableIdentifierError`: raised for malformed table identifiers
- `SparkRequiredError`: raised when Spark is required but unavailable
