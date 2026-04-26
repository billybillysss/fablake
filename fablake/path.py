from __future__ import annotations

from collections.abc import Iterable
from fnmatch import fnmatch

from ._abfs import FabLakeFileSystem
from ._models import LakehousePathInfo
from ._path_utils import normalize_logical_path


class LakehousePath(str):
    """Path-like wrapper for fablake logical paths.

    A `LakehousePath` represents a logical path under a lakehouse root (for
    example `Files`) and stringifies to a fully-qualified ABFSS URI.
    """

    __slots__ = ("_fs", "_root", "_path")

    def __new__(
        cls,
        fs: FabLakeFileSystem,
        *,
        root: str = "Files",
        path: str = "",
    ) -> LakehousePath:
        """Create a path wrapper.

        Parameters
        ----------
        fs:
            Backing fablake filesystem instance.
        root:
            Root segment (`Files` or `Tables`).
        path:
            Logical path below the selected root.
        """
        normalized_root = FabLakeFileSystem.normalize_root(root)
        normalized_path = cls._normalize_subpath(path)
        uri = fs.to_url(normalized_path, root=normalized_root)
        instance = str.__new__(cls, uri)
        object.__setattr__(instance, "_fs", fs)
        object.__setattr__(instance, "_root", normalized_root)
        object.__setattr__(instance, "_path", normalized_path)
        return instance

    @property
    def fs(self) -> FabLakeFileSystem:
        return self._fs

    @property
    def root(self) -> str:
        return self._root

    @staticmethod
    def _normalize_subpath(path: str | None) -> str:
        return normalize_logical_path(path, collapse_parent_segments=True)

    @property
    def path(self) -> str:
        return self._path or "."

    @property
    def parts(self) -> tuple[str, ...]:
        if not self._path:
            return tuple()
        return tuple(self._path.split("/"))

    @property
    def name(self) -> str:
        if not self._path:
            return ""
        return self._path.rsplit("/", 1)[-1]

    @property
    def stem(self) -> str:
        if "." not in self.name:
            return self.name
        return self.name.rsplit(".", 1)[0]

    @property
    def suffix(self) -> str:
        if "." not in self.name:
            return ""
        return f".{self.name.rsplit('.', 1)[-1]}"

    @property
    def parent(self) -> LakehousePath:
        if not self._path or "/" not in self._path:
            return LakehousePath(self._fs, root=self._root, path="")
        return LakehousePath(self._fs, root=self._root, path=self._path.rsplit("/", 1)[0])

    def as_posix(self) -> str:
        return self.path

    @property
    def uri(self) -> str:
        return str(self)

    def joinpath(self, *other: str) -> LakehousePath:
        """Return a new path with `other` segments appended.

        Parameters
        ----------
        *other:
            One or more path segments.
        """
        joined = self._path
        for part in other:
            normalized = self._normalize_subpath(part)
            if not normalized:
                continue
            if joined:
                joined = f"{joined}/{normalized}"
            else:
                joined = normalized
        return LakehousePath(self._fs, root=self._root, path=joined)

    def __truediv__(self, key: str) -> LakehousePath:
        return self.joinpath(key)

    def __repr__(self) -> str:
        return f"LakehousePath('{self.as_posix()}')"

    def __fspath__(self) -> str:
        return str(self)

    def _normalized_entry_name(self, entry_name: str) -> str:
        value = str(entry_name or "").strip().replace("\\", "/")
        return self._fs._to_logical_path(value, root=self._root)

    def exists(self) -> bool:
        """Return `True` when the path exists."""
        return self._fs.exists(self._path, root=self._root)

    def is_dir(self) -> bool:
        """Return `True` when the path points to a directory."""
        return self._fs.isdir(self._path, root=self._root)

    def is_file(self) -> bool:
        """Return `True` when the path points to a file."""
        return self._fs.isfile(self._path, root=self._root)

    def info(self) -> LakehousePathInfo:
        """Return normalized metadata for the path.

        Returns
        -------
        LakehousePathInfo
            Dataclass containing common path metadata and raw backend payload.
        """
        info = dict(self._fs.info(self._path, root=self._root) or {})
        normalized_name = self._normalized_entry_name(str(info.get("name") or self._path))
        info["name"] = normalized_name
        content_settings = info.get("content_settings")
        tags = info.get("tags")
        metadata = info.get("metadata")
        return LakehousePathInfo(
            name=normalized_name,
            type=str(info.get("type") or "unknown"),
            size=info.get("size"),
            metadata=dict(metadata) if isinstance(metadata, dict) else metadata,
            creation_time=info.get("creation_time"),
            deleted=info.get("deleted"),
            deleted_time=info.get("deleted_time"),
            last_modified=info.get("last_modified"),
            content_settings=(
                dict(content_settings) if isinstance(content_settings, dict) else content_settings
            ),
            remaining_retention_days=info.get("remaining_retention_days"),
            archive_status=info.get("archive_status"),
            last_accessed_on=info.get("last_accessed_on"),
            etag=info.get("etag"),
            tags=dict(tags) if isinstance(tags, dict) else tags,
            tag_count=info.get("tag_count"),
            raw=info,
        )

    def iterdir(self) -> Iterable[LakehousePath]:
        """Yield immediate child paths for a directory."""
        for item in self._fs.ls(self._path, root=self._root):
            if item.parent.as_posix() != self.as_posix():
                continue
            yield item

    def glob(self, pattern: str):
        """Yield paths matching a glob pattern.

        Parameters
        ----------
        pattern:
            Glob expression relative to this path.
        """
        normalized_pattern = self._normalize_subpath(pattern)
        if not normalized_pattern:
            return iter(())

        if "/" not in normalized_pattern and "**" not in normalized_pattern:
            matches: list[LakehousePath] = []
            for item in self._fs.ls(self._path, root=self._root):
                if item.parent.as_posix() != self.as_posix():
                    continue
                if fnmatch(item.name, normalized_pattern):
                    matches.append(item)
            return iter(matches)

        matches: list[LakehousePath] = []
        for item in self.find(withdirs=True):
            if item == self:
                continue
            relative_name = item.as_posix()
            if self._path:
                relative_name = relative_name[len(self._path) + 1 :]
            if fnmatch(relative_name, normalized_pattern):
                matches.append(item)
        return iter(matches)

    def rglob(self, pattern: str):
        """Yield paths recursively matching a glob pattern.

        Parameters
        ----------
        pattern:
            Glob expression evaluated recursively below this path.
        """
        normalized_pattern = self._normalize_subpath(pattern)
        if not normalized_pattern:
            return iter(())
        matches: list[LakehousePath] = []
        for item in self.find(withdirs=True):
            if item == self:
                continue
            relative_name = item.as_posix()
            if self._path:
                relative_name = relative_name[len(self._path) + 1 :]
            if fnmatch(relative_name, normalized_pattern) or fnmatch(
                relative_name,
                f"**/{normalized_pattern}",
            ):
                matches.append(item)
        return iter(matches)

    def find(
        self,
        *,
        maxdepth: int | None = None,
        withdirs: bool = False,
    ):
        """Return descendants discovered by the backend `find` operation.

        Parameters
        ----------
        maxdepth:
            Optional recursion limit.
        withdirs:
            Include directory entries when `True`.
        """
        return self._fs.find(
            self._path,
            root=self._root,
            maxdepth=maxdepth,
            withdirs=withdirs,
        )

    def open(self, mode: str = "r", **kwargs):
        """Open the path using the backing filesystem.

        Parameters
        ----------
        mode:
            Standard file mode such as `r`, `rb`, `w`, or `wb`.
        **kwargs:
            Additional backend-specific open options.
        """
        return self._fs.open(self._path, mode=mode, root=self._root, **kwargs)

    def resolve(self, strict: bool = False) -> LakehousePath:
        """Return a normalized path object.

        Parameters
        ----------
        strict:
            If `True`, raise `FileNotFoundError` when the path does not exist.
        """
        resolved = LakehousePath(self._fs, root=self._root, path=self._path)
        if strict and not resolved.exists():
            raise FileNotFoundError(f"No such file or directory: '{resolved.as_posix()}'")
        return resolved

    def read_text(self, **kwargs) -> str:
        """Read and return text content.

        Parameters
        ----------
        **kwargs:
            Text mode options passed to `open`, such as `encoding`.
        """
        with self.open("r", **kwargs) as stream:
            return stream.read()

    def read_bytes(self) -> bytes:
        """Read and return binary content."""
        with self.open("rb") as stream:
            return stream.read()

    def write_text(self, data: str, **kwargs) -> int:
        """Write text content.

        Parameters
        ----------
        data:
            Text payload to write.
        **kwargs:
            Text mode options passed to `open`, such as `encoding`.
        """
        with self.open("w", **kwargs) as stream:
            return stream.write(data)

    def write_bytes(self, data: bytes) -> int:
        """Write binary content.

        Parameters
        ----------
        data:
            Byte payload to write.
        """
        with self.open("wb") as stream:
            return stream.write(data)

    def mkdir(self, *, parents: bool = True, exist_ok: bool = False) -> None:
        """Create this directory path.

        Parameters
        ----------
        parents:
            Create missing parents when `True`.
        exist_ok:
            Ignore existing directory errors when `True`.
        """
        self._fs.mkdir(
            self._path,
            root=self._root,
            create_parents=parents,
            exist_ok=exist_ok,
        )

    def unlink(self, *, missing_ok: bool = False) -> None:
        """Delete a file path.

        Parameters
        ----------
        missing_ok:
            If `True`, do not raise when the path is missing.
        """
        if missing_ok and not self.exists():
            return
        self._fs.rm(self._path, root=self._root, recursive=False)

    @staticmethod
    def _normalize_rename_name(target: str) -> str:
        value = str(target or "").strip()
        if not value:
            raise ValueError("Rename target must be a non-empty file name.")
        if value in {".", ".."}:
            raise ValueError("Rename target must be a file name, not a path segment.")
        if "/" in value or "\\" in value:
            raise ValueError("Rename target must be a single file name without path separators.")
        return value

    def rename(self, target: str) -> LakehousePath:
        """Rename this path to a sibling file name.

        Parameters
        ----------
        target:
            New file name. Must be a single segment, not a path.

        Returns
        -------
        LakehousePath
            New path object pointing to the renamed target.
        """
        if isinstance(target, LakehousePath):
            raise TypeError("Rename target must be a file name string.")
        if not self._path:
            raise ValueError("Cannot rename the root path.")

        target_name = self._normalize_rename_name(target)
        target_path = self.parent / target_name
        self._fs.mv(self._path, target_path._path, root=self._root)
        return target_path
