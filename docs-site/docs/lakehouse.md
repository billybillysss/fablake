# Lakehouse API

`Lakehouse` is the main entry point for filesystem and path operations.

## Constructor

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

## Binding modes

Use exactly one binding style per instance:

- Name binding: `workspace` and `lakehouse`
- ID binding: `workspace_id` and `lakehouse_id`

Mixed name and ID values are rejected.

## Key properties

- `workspace`: name when name-bound, otherwise `None`
- `workspace_id`: bound workspace identifier
- `lakehouse`: name when name-bound, otherwise `None`
- `lakehouse_id`: bound lakehouse identifier
- `binding`: normalized binding object
- `schema_enabled`: schema mode configuration
- `fs`: filesystem handle
- `storage_options`: filesystem storage configuration
- `files`: `LakehousePath` rooted at `Files`
- `tables`: table discovery helper

## Key methods

- `path(path="", root="Files")` to create a `LakehousePath`
- `table(name, schema=...)` to create a `LakehouseTable` locator

## Examples

Name-bound lakehouse:

```python
from fablake import Lakehouse

lh = Lakehouse(workspace="Finance", lakehouse="Ops", schema_enabled=True)
```

ID-bound lakehouse:

```python
lh = Lakehouse(
    workspace_id="<workspace-id>",
    lakehouse_id="<lakehouse-id>",
    schema_enabled=True,
)
```
