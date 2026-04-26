# LakehousePath

LakehousePath provides pathlib-like ergonomics over fablake logical paths.

## Signature

```python
LakehousePath(fs: FabLakeFileSystem, *, root: str = 'Files', path: str = '')
```

## Parameters

- `fs`: `FabLakeFileSystem`
- `root`: `str` (default: `Files`)
- `path`: `str` (default: ``)

## Description

Path-like wrapper for fablake logical paths.

A `LakehousePath` represents a logical path under a lakehouse root (for
example `Files`) and stringifies to a fully-qualified ABFSS URI.

## Example

```python
path = lh.files / "config" / "settings.json"

if path.exists():
    print(path.read_text())
```

## Methods

### LakehousePath.as_posix

<div class="api-signature">

```python
as_posix(self) -> 'str'
```

</div>

Parameters:

- `self`

Returns: `str`

No description provided.

### LakehousePath.exists

<div class="api-signature">

```python
exists(self) -> 'bool'
```

</div>

Parameters:

- `self`

Returns: `bool`

Return `True` when the path exists.

### LakehousePath.find

<div class="api-signature">

```python
find(self, *, maxdepth: 'int | None' = None, withdirs: 'bool' = False)
```

</div>

Parameters:

- `self`
- `maxdepth`: `int | None` (default: `None`)
- `withdirs`: `bool` (default: `False`)

Returns: Not declared

Return descendants discovered by the backend `find` operation.

Parameters
----------
maxdepth:
    Optional recursion limit.
withdirs:
    Include directory entries when `True`.

### LakehousePath.glob

<div class="api-signature">

```python
glob(self, pattern: 'str')
```

</div>

Parameters:

- `self`
- `pattern`: `str`

Returns: Not declared

Yield paths matching a glob pattern.

Parameters
----------
pattern:
    Glob expression relative to this path.

### LakehousePath.info

<div class="api-signature">

```python
info(self) -> 'LakehousePathInfo'
```

</div>

Parameters:

- `self`

Returns: `LakehousePathInfo`

Return normalized metadata for the path.

Returns
-------
LakehousePathInfo
    Dataclass containing common path metadata and raw backend payload.

### LakehousePath.is_dir

<div class="api-signature">

```python
is_dir(self) -> 'bool'
```

</div>

Parameters:

- `self`

Returns: `bool`

Return `True` when the path points to a directory.

### LakehousePath.is_file

<div class="api-signature">

```python
is_file(self) -> 'bool'
```

</div>

Parameters:

- `self`

Returns: `bool`

Return `True` when the path points to a file.

### LakehousePath.iterdir

<div class="api-signature">

```python
iterdir(self) -> 'Iterable[LakehousePath]'
```

</div>

Parameters:

- `self`

Returns: `Iterable[LakehousePath]`

Yield immediate child paths for a directory.

### LakehousePath.joinpath

<div class="api-signature">

```python
joinpath(self, *other: 'str') -> 'LakehousePath'
```

</div>

Parameters:

- `self`
- `other`: `str`

Returns: `LakehousePath`

Return a new path with `other` segments appended.

Parameters
----------
*other:
    One or more path segments.

### LakehousePath.mkdir

<div class="api-signature">

```python
mkdir(self, *, parents: 'bool' = True, exist_ok: 'bool' = False) -> 'None'
```

</div>

Parameters:

- `self`
- `parents`: `bool` (default: `True`)
- `exist_ok`: `bool` (default: `False`)

Returns: `None`

Create this directory path.

Parameters
----------
parents:
    Create missing parents when `True`.
exist_ok:
    Ignore existing directory errors when `True`.

### LakehousePath.open

<div class="api-signature">

```python
open(self, mode: 'str' = 'r', **kwargs)
```

</div>

Parameters:

- `self`
- `mode`: `str` (default: `r`)
- `kwargs`

Returns: Not declared

Open the path using the backing filesystem.

Parameters
----------
mode:
    Standard file mode such as `r`, `rb`, `w`, or `wb`.
**kwargs:
    Additional backend-specific open options.

### LakehousePath.read_bytes

<div class="api-signature">

```python
read_bytes(self) -> 'bytes'
```

</div>

Parameters:

- `self`

Returns: `bytes`

Read and return binary content.

### LakehousePath.read_text

<div class="api-signature">

```python
read_text(self, **kwargs) -> 'str'
```

</div>

Parameters:

- `self`
- `kwargs`

Returns: `str`

Read and return text content.

Parameters
----------
**kwargs:
    Text mode options passed to `open`, such as `encoding`.

### LakehousePath.rename

<div class="api-signature">

```python
rename(self, target: 'str') -> 'LakehousePath'
```

</div>

Parameters:

- `self`
- `target`: `str`

Returns: `LakehousePath`

Rename this path to a sibling file name.

Parameters
----------
target:
    New file name. Must be a single segment, not a path.

Returns
-------
LakehousePath
    New path object pointing to the renamed target.

### LakehousePath.resolve

<div class="api-signature">

```python
resolve(self, strict: 'bool' = False) -> 'LakehousePath'
```

</div>

Parameters:

- `self`
- `strict`: `bool` (default: `False`)

Returns: `LakehousePath`

Return a normalized path object.

Parameters
----------
strict:
    If `True`, raise `FileNotFoundError` when the path does not exist.

### LakehousePath.rglob

<div class="api-signature">

```python
rglob(self, pattern: 'str')
```

</div>

Parameters:

- `self`
- `pattern`: `str`

Returns: Not declared

Yield paths recursively matching a glob pattern.

Parameters
----------
pattern:
    Glob expression evaluated recursively below this path.

### LakehousePath.unlink

<div class="api-signature">

```python
unlink(self, *, missing_ok: 'bool' = False) -> 'None'
```

</div>

Parameters:

- `self`
- `missing_ok`: `bool` (default: `False`)

Returns: `None`

Delete a file path.

Parameters
----------
missing_ok:
    If `True`, do not raise when the path is missing.

### LakehousePath.write_bytes

<div class="api-signature">

```python
write_bytes(self, data: 'bytes') -> 'int'
```

</div>

Parameters:

- `self`
- `data`: `bytes`

Returns: `int`

Write binary content.

Parameters
----------
data:
    Byte payload to write.

### LakehousePath.write_text

<div class="api-signature">

```python
write_text(self, data: 'str', **kwargs) -> 'int'
```

</div>

Parameters:

- `self`
- `data`: `str`
- `kwargs`

Returns: `int`

Write text content.

Parameters
----------
data:
    Text payload to write.
**kwargs:
    Text mode options passed to `open`, such as `encoding`.

