# Design notes

This document describes the main design choices behind `fablake`.

## Filesystem-first API

`fablake` centers on filesystem and path workflows instead of introducing a new
table abstraction layer. This keeps interop with the broader Python data stack
simple and explicit.

## Explicit roots

The API intentionally separates:

- `Files` for general file operations
- `Tables` for physical table root locations

This matches fablake structure and prevents accidental mixing of concerns.

## Binding model

`Lakehouse` supports two binding modes:

- name-bound (`workspace` + `lakehouse`)
- ID-bound (`workspace_id` + `lakehouse_id`)

Mixing modes in one instance is rejected to avoid ambiguous addressing.

## Path normalization

Logical paths are normalized before transport-level URI conversion.

`LakehousePath` operations are designed to be predictable and close to
`pathlib`, while preserving fablake-specific URI behavior.

## Table locators, not dataframes

`LakehouseTable` values are transport locators. They are intentionally simple,
path-like values you pass to engines such as Dask, DuckDB, pandas, PyArrow, and
Polars.

## Authentication resolution

Credential handling favors explicit configuration first. When no credential is
provided, authentication resolution is delegated to the underlying
fsspec/adlfs backend and runtime environment.
