# Installation

## Requirements

- Python `>=3.10`
- A Microsoft Fabric OneLake Lakehouse to access

## Install with uv

```bash
uv add fablake
```

For local and CI authentication with Azure credentials:

```bash
uv add azure-identity
```

Or install via package extra:

```bash
pip install "fablake[auth]"
```

## Install with pip

```bash
pip install fablake azure-identity
```

## Dependency model

`fablake` uses:

- `fsspec` for filesystem interfaces
- `adlfs` for Azure Data Lake / ABFS transport

You can install and use additional data libraries as needed, such as `pandas`,
`pyarrow`, `polars`, `dask`, or `duckdb`.
