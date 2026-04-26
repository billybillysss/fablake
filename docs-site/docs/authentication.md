# Authentication

By default, you usually do not need to pass `credential=...` explicitly.

`Lakehouse(...)` and `FabLakeFileSystem(...)` pass credential handling to the
underlying fsspec/adlfs backend unless you provide an explicit credential.

Effective behavior:

1. If `credential` is provided and not `None`, it is forwarded to the backend.
2. If `credential` is omitted (or `None`), backend/runtime default auth
   resolution is used.

## Explicit credential

Pass any compatible Azure credential object:

```python
from azure.identity import DefaultAzureCredential
from fablake import Lakehouse

lh = Lakehouse(
    workspace_id="<workspace-id>",
    lakehouse_id="<lakehouse-id>",
    schema_enabled=True,
    credential=DefaultAzureCredential(),
)
```

## Notebook runtimes

In Microsoft Fabric notebook environments, authentication may be resolved by
the runtime/backend stack without passing `credential` explicitly.

## Local development

Install `azure-identity` and configure one of the Azure credential sources used
by `DefaultAzureCredential` so the backend can resolve credentials locally.

```bash
uv add azure-identity
```

## Failure behavior

When credentials cannot be resolved by the backend/runtime environment,
operations fail with backend authentication errors. In that case:

- install and configure `azure-identity` for local environments
- or pass `credential=...` explicitly
