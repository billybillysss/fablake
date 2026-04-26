# Files and paths

`lh.files` is the root `LakehousePath` for the Lakehouse `Files` area.

## Build paths

```python
path = lh.files / "raw" / "orders" / "2026-01-01.json"

print(path.as_posix())
# raw/orders/2026-01-01.json

print(str(path))
# abfss://.../Files/raw/orders/2026-01-01.json
```

You can also build a path from a string:

```python
logs = lh.path("logs/2026/04", root="Files")
```

## Path semantics

- `as_posix()` returns the logical path under the selected root
- `str(path)` returns the fully qualified ABFSS URI
- `path.parent`, `path.name`, `path.stem`, `path.suffix`, and `path.parts`
  follow pathlib-style behavior

## Common operations

```python
path.exists()
path.is_file()
path.is_dir()
path.info()

path.read_text()
path.write_text("hello")

path.read_bytes()
path.write_bytes(b"hello")
```

Directory and discovery operations:

```python
path.parent.mkdir(parents=True, exist_ok=True)

for child in (lh.files / "raw").iterdir():
    print(child)

for item in (lh.files / "raw").find(withdirs=True):
    print(item)
```

## Rename behavior

`LakehousePath.rename(target)` only accepts a single file name segment.

Accepted:

- `result-final.txt`

Rejected:

- `../result.txt`
- `archive/result.txt`
- `path-like` `LakehousePath` objects

The root path itself cannot be renamed.
