# Changelog

All notable changes to this project are documented in this file.

## Unreleased

## 0.1.0 - 2026-04-26

### Added

- Initial public release of `fablake` as a production-oriented OneLake Lakehouse
  path and filesystem library.
- `Lakehouse` as the main entry point with explicit name-based and ID-based
  binding modes.
- `LakehousePath` for pathlib-like `Files` operations.
- `LakehouseTable` table-root locator for `Tables` paths.
- Authentication resolution across explicit credentials and Azure identity
  defaults.
- Interop-oriented filesystem APIs and storage options for pandas, PyArrow,
  Polars, Dask, and DuckDB workflows.
