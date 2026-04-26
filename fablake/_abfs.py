from __future__ import annotations

import importlib
from typing import Any

try:
    from fsspec.spec import AbstractFileSystem
except Exception:  # pragma: no cover - import guard for test doubles
    class AbstractFileSystem:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs) -> None:
            pass

from ._path_utils import normalize_logical_path
from .exceptions import ResolutionError


class FabLakeFileSystem(AbstractFileSystem):
    protocol = "abfs"
    cachable = False
    _ACCOUNT_NAME = "onelake"
    _ACCOUNT_HOST = "onelake.blob.fabric.microsoft.com"
    _DFS_HOST = "onelake.dfs.fabric.microsoft.com"
    _SUPPORTED_ROOTS = {"files": "Files", "tables": "Tables"}
    _DELETE_STATUS_OK_MESSAGE = "Operation returned an invalid status 'OK'"
    _RESOLUTION_ERROR_MARKERS = (
        "ArtifactNotFound",
        "WorkspaceNotFound",
        "is not found in workspace",
    )

    def __init__(
        self,
        *,
        workspace: str | None = None,
        lakehouse: str | None = None,
        identifier_mode: str | None = None,
        workspace_id: str | None = None,
        lakehouse_id: str | None = None,
        max_concurrency: int = 8,
        **kwargs,
    ) -> None:
        try:
            super().__init__(asynchronous=False)
        except Exception:
            super().__init__()

        try:
            fsspec = importlib.import_module("fsspec")
        except Exception as exc:  # pragma: no cover - import guard
            raise RuntimeError(
                "The active Python interpreter is missing the runtime dependencies for "
                "fablake. Install this package into that interpreter with `uv add fablake` "
                "or, from this repo, `uv sync`. If you prefer pip, use `pip "
                "install fablake` or `pip install -e .`. This installs fsspec and adlfs "
                "for direct `import fablake` usage.",
            ) from exc

        if identifier_mode is None:
            if workspace is not None or lakehouse is not None:
                identifier_mode = "name"
            else:
                identifier_mode = "id"

        mode = str(identifier_mode).strip().lower()
        if mode not in {"name", "id"}:
            raise ValueError("identifier_mode must be either 'name' or 'id'.")
        self.identifier_mode = mode

        workspace_value = workspace if workspace is not None else workspace_id
        lakehouse_value = lakehouse if lakehouse is not None else lakehouse_id
        if workspace_value is None or lakehouse_value is None:
            raise ValueError("Both workspace and lakehouse values are required.")

        self.workspace = str(workspace_value).strip()
        self.lakehouse = str(lakehouse_value).strip()
        if not self.workspace or not self.lakehouse:
            raise ValueError("workspace and lakehouse values must be non-empty.")

        self.workspace_id = self.workspace
        self.lakehouse_id = self.lakehouse
        self.max_concurrency = int(max_concurrency)

        fs_kwargs = dict(kwargs)
        if fs_kwargs.get("credential") is None:
            fs_kwargs.pop("credential", None)
        fs_kwargs.setdefault("anon", False)
        fs_kwargs.setdefault("account_name", self._ACCOUNT_NAME)
        fs_kwargs.setdefault("account_host", self._ACCOUNT_HOST)
        fs_kwargs.setdefault("asynchronous", False)
        fs_kwargs.setdefault("max_concurrency", self.max_concurrency)

        self._storage_options = dict(fs_kwargs)
        self._fs = fsspec.filesystem("abfs", **fs_kwargs)

    @property
    def storage_options(self) -> dict[str, Any]:
        return dict(self._storage_options)

    @storage_options.setter
    def storage_options(self, value: Any) -> None:
        incoming = dict(value or {})
        current = dict(getattr(self, "_storage_options", {}))
        current.update(incoming)
        self._storage_options = current
        self._fsspec_storage_options = incoming

    @property
    def fs(self):
        return self._fs

    def __getattr__(self, name: str):
        return getattr(self._fs, name)

    @classmethod
    def normalize_root(cls, value: str) -> str:
        key = str(value or "").strip().strip("/").lower()
        root = cls._SUPPORTED_ROOTS.get(key)
        if root is None:
            allowed = ", ".join(sorted(cls._SUPPORTED_ROOTS.values()))
            raise ValueError(f"Unsupported root '{value}'. Allowed values: {allowed}")
        return root

    @staticmethod
    def _normalize_logical(path: str | None) -> str:
        return normalize_logical_path(path, collapse_parent_segments=False)

    @staticmethod
    def _is_abfs_path(path: str | None) -> bool:
        value = str(path or "").strip().lower()
        return value.startswith("abfss://") or value.startswith("abfs://")

    @classmethod
    def _strip_protocol(cls, path: str | None) -> str:
        value = str(path or "").strip().replace("\\", "/")
        if value.startswith("fablake://"):
            value = value[len("fablake://") :]
        elif value.startswith("onelake://"):
            value = value[len("onelake://") :]
        return value

    def base_url_for(self, root: str = "Files") -> str:
        normalized_root = self.normalize_root(root)
        item_token = self._item_token
        return (
            f"abfss://{self.workspace}@{self._DFS_HOST}/"
            f"{item_token}/{normalized_root}"
        )

    @property
    def _item_token(self) -> str:
        if self.identifier_mode == "id":
            return self.lakehouse
        return f"{self.lakehouse}.lakehouse"

    def _to_logical_path(self, path: str | None, *, root: str) -> str:
        value = self._strip_protocol(path)
        value = value.strip("/")

        if self._is_abfs_path(value):
            prefix = (
                f"abfss://{self.workspace}@{self._DFS_HOST}/"
            )
            if value.startswith(prefix):
                value = value[len(prefix) :]

        if value.startswith(f"{self.workspace}/"):
            value = value[len(self.workspace) + 1 :]
        if self.identifier_mode == "id":
            item_token = self._item_token
            if value.startswith(f"{item_token}/"):
                value = value[len(item_token) + 1 :]
        else:
            lower_value = value.lower()
            item_token = f"{self.lakehouse}.lakehouse"
            item_prefix = f"{item_token}/"
            if lower_value.startswith(item_prefix.lower()):
                value = value[len(item_prefix) :]
            elif lower_value.startswith(f"{self.lakehouse.lower()}/"):
                value = value[len(self.lakehouse) + 1 :]

        root_norm = self.normalize_root(root)
        root_key = value.split("/", 1)[0].lower() if value else ""
        if root_key in self._SUPPORTED_ROOTS:
            value = value.split("/", 1)[1] if "/" in value else ""

        if value == root_norm:
            return ""
        if value.startswith(f"{root_norm}/"):
            value = value[len(root_norm) + 1 :]

        return self._normalize_logical(value)

    def to_url(self, path: str | None, *, root: str = "Files") -> str:
        value = str(path or "").strip()
        if self._is_abfs_path(value):
            return value

        logical = self._to_logical_path(value, root=root)
        base = self.base_url_for(root)
        if not logical:
            return base
        return f"{base}/{logical}"

    def _to_url_path_arg(self, path: str | list[str], *, root: str = "Files"):
        if isinstance(path, list):
            return [self.to_url(item, root=root) for item in path]
        return self.to_url(path, root=root)

    def exists(self, path: str, *, root: str = "Files", **kwargs) -> bool:
        return bool(self._fs.exists(self.to_url(path, root=root), **kwargs))

    @classmethod
    def _iter_exception_chain(cls, error: BaseException):
        current: BaseException | None = error
        seen: set[int] = set()
        while current is not None and id(current) not in seen:
            yield current
            seen.add(id(current))
            current = current.__cause__ or current.__context__

    def _resolution_error_from_not_found(
        self,
        error: FileNotFoundError,
        *,
        path: str,
        root: str,
    ) -> ResolutionError | None:
        for chained in self._iter_exception_chain(error):
            detail = str(chained).strip()
            if not detail:
                continue
            if any(marker in detail for marker in self._RESOLUTION_ERROR_MARKERS):
                target = self._to_logical_path(path, root=root) or "."
                binding = (
                    f"workspace '{self.workspace}' and lakehouse '{self.lakehouse}'"
                    if self.identifier_mode == "name"
                    else f"workspace_id '{self.workspace}' and lakehouse_id '{self.lakehouse}'"
                )
                return ResolutionError(
                    f"Could not resolve {binding} while accessing '{target}' under {root}: {detail}",
                )
        return None

    def _call_with_resolution_handling(self, operation, *, path: str, root: str):
        try:
            return operation()
        except FileNotFoundError as error:
            resolution_error = self._resolution_error_from_not_found(error, path=path, root=root)
            if resolution_error is not None:
                raise resolution_error from error
            raise

    def isdir(self, path: str, *, root: str = "Files") -> bool:
        fn = getattr(self._fs, "isdir", None)
        if callable(fn):
            return bool(fn(self.to_url(path, root=root)))
        info = self.info(path, root=root)
        return str(info.get("type") or "").lower() in {"directory", "dir"}

    def isfile(self, path: str, *, root: str = "Files") -> bool:
        fn = getattr(self._fs, "isfile", None)
        if callable(fn):
            return bool(fn(self.to_url(path, root=root)))
        info = self.info(path, root=root)
        return str(info.get("type") or "").lower() == "file"

    def info(self, path: str, *, root: str = "Files", **kwargs) -> dict[str, Any]:
        info = self._call_with_resolution_handling(
            lambda: self._fs.info(self.to_url(path, root=root), **kwargs),
            path=path,
            root=root,
        )
        if isinstance(info, dict):
            return dict(info)
        return {"name": str(path), "type": "file", "size": None}

    def _logical_name_from_listing(self, value: str, *, root: str) -> str:
        return self._to_logical_path(value, root=root)

    def _make_path(self, logical_path: str, *, root: str):
        from .path import LakehousePath

        return LakehousePath(self, root=root, path=logical_path)

    def ls(self, path: str, *, root: str = "Files", **kwargs):
        entries = self._call_with_resolution_handling(
            lambda: self._fs.ls(self.to_url(path, root=root), detail=False, **kwargs),
            path=path,
            root=root,
        )
        return [self._make_path(self._logical_name_from_listing(str(entry), root=root), root=root) for entry in (entries or [])]

    def find(
        self,
        path: str,
        *,
        root: str = "Files",
        maxdepth: int | None = None,
        withdirs: bool = False,
        **kwargs,
    ):
        entries = self._call_with_resolution_handling(
            lambda: self._fs.find(
                self.to_url(path, root=root),
                maxdepth=maxdepth,
                withdirs=withdirs,
                detail=False,
                **kwargs,
            ),
            path=path,
            root=root,
        )
        return [self._make_path(self._logical_name_from_listing(str(entry), root=root), root=root) for entry in (entries or [])]

    def glob(self, path: str, *, root: str = "Files", **kwargs):
        entries = self._call_with_resolution_handling(
            lambda: self._fs.glob(self.to_url(path, root=root), **kwargs),
            path=path,
            root=root,
        )
        return [self._make_path(self._logical_name_from_listing(str(entry), root=root), root=root) for entry in (entries or [])]

    def open(self, path: str, mode: str = "rb", *, root: str = "Files", **kwargs):
        return self._call_with_resolution_handling(
            lambda: self._fs.open(self.to_url(path, root=root), mode=mode, **kwargs),
            path=path,
            root=root,
        )

    def mkdir(self, path: str, *, root: str = "Files", create_parents: bool = True, **kwargs):
        if create_parents:
            return self.makedirs(path, root=root, exist_ok=kwargs.get("exist_ok", False))
        return self._call_with_resolution_handling(
            lambda: self._fs.mkdir(self.to_url(path, root=root), **kwargs),
            path=path,
            root=root,
        )

    def makedirs(self, path: str, *, root: str = "Files", exist_ok: bool = False):
        return self._call_with_resolution_handling(
            lambda: self._fs.makedirs(self.to_url(path, root=root), exist_ok=exist_ok),
            path=path,
            root=root,
        )

    def put(self, lpath: str | list[str], rpath: str | list[str], *, root: str = "Files", **kwargs):
        return self._fs.put(lpath, self._to_url_path_arg(rpath, root=root), **kwargs)

    def rm(self, path: str | list[str], *, root: str = "Files", recursive: bool = False, **kwargs):
        try:
            return self._fs.rm(
                self._to_url_path_arg(path, root=root),
                recursive=recursive,
                **kwargs,
            )
        except RuntimeError as exc:
            if self._DELETE_STATUS_OK_MESSAGE in str(exc):
                return None
            raise

    def copy(
        self,
        path1: str | list[str],
        path2: str | list[str],
        *,
        root: str = "Files",
        recursive: bool = False,
        on_error: str | None = None,
        maxdepth: int | None = None,
        **kwargs,
    ):
        if on_error is None:
            on_error = "ignore" if recursive else "raise"
        if recursive and not isinstance(path1, list) and not isinstance(path2, list):
            source = str(path1)
            destination = str(path2)
            if self._to_logical_path(source, root=root) == self._to_logical_path(destination, root=root):
                return None
            if self.isdir(source, root=root):
                return self._copy_tree(
                    source,
                    destination,
                    root=root,
                    on_error=on_error,
                    **kwargs,
                )
        return self._fs.copy(
            self._to_url_path_arg(path1, root=root),
            self._to_url_path_arg(path2, root=root),
            recursive=recursive,
            on_error=on_error,
            maxdepth=maxdepth,
            **kwargs,
        )

    def mv(
        self,
        path1: str | list[str],
        path2: str | list[str],
        *,
        root: str = "Files",
        recursive: bool = False,
        maxdepth: int | None = None,
        **kwargs,
    ):
        if recursive and not isinstance(path1, list) and not isinstance(path2, list):
            source = str(path1)
            destination = str(path2)
            if self._to_logical_path(source, root=root) == self._to_logical_path(destination, root=root):
                return None
            if self.isdir(source, root=root):
                return self._move_tree(
                    source,
                    destination,
                    root=root,
                    **kwargs,
                )
        return self._fs.mv(
            self._to_url_path_arg(path1, root=root),
            self._to_url_path_arg(path2, root=root),
            recursive=recursive,
            maxdepth=maxdepth,
            **kwargs,
        )

    @staticmethod
    def _relative_to(base: str, value: str) -> str:
        if value == base:
            return ""
        prefix = f"{base}/"
        if value.startswith(prefix):
            return value[len(prefix) :]
        return value

    @staticmethod
    def _join_logical(base: str, suffix: str) -> str:
        left = str(base or "").strip("/")
        right = str(suffix or "").strip("/")
        if left and right:
            return f"{left}/{right}"
        return left or right

    def _collect_tree_entries(self, source: str, *, root: str):
        raw_entries = self._call_with_resolution_handling(
            lambda: self._fs.find(
                self.to_url(source, root=root),
                withdirs=True,
                detail=True,
            ),
            path=source,
            root=root,
        )

        if isinstance(raw_entries, dict):
            pairs = [(str(name), dict(metadata or {})) for name, metadata in raw_entries.items()]
        else:
            pairs = [(str(name), {}) for name in (raw_entries or [])]

        source_logical = self._to_logical_path(source, root=root)
        files: list[str] = []
        dirs: list[str] = []

        for name, metadata in pairs:
            logical_name = self._logical_name_from_listing(name, root=root)
            if not logical_name or logical_name == source_logical:
                continue
            entry_type = str(metadata.get("type") or "").lower()
            if entry_type in {"directory", "dir"}:
                dirs.append(logical_name)
            elif entry_type == "file":
                files.append(logical_name)
            elif logical_name.endswith("/"):
                dirs.append(logical_name.rstrip("/"))
            else:
                files.append(logical_name)

        return source_logical, sorted(set(files)), sorted(set(dirs), key=lambda item: item.count("/"))

    def _copy_tree(
        self,
        source: str,
        destination: str,
        *,
        root: str,
        on_error: str,
        **kwargs,
    ):
        source_logical, files, dirs = self._collect_tree_entries(source, root=root)
        destination_logical = self._to_logical_path(destination, root=root)

        self.makedirs(destination_logical, root=root, exist_ok=True)
        for directory in dirs:
            relative = self._relative_to(source_logical, directory)
            if not relative:
                continue
            self.makedirs(self._join_logical(destination_logical, relative), root=root, exist_ok=True)

        for file_path in files:
            relative = self._relative_to(source_logical, file_path)
            target_file = self._join_logical(destination_logical, relative)
            parent = target_file.rsplit("/", 1)[0] if "/" in target_file else ""
            if parent:
                self.makedirs(parent, root=root, exist_ok=True)
            try:
                self._fs.copy(
                    self.to_url(file_path, root=root),
                    self.to_url(target_file, root=root),
                    recursive=False,
                    on_error="raise",
                    maxdepth=None,
                    **kwargs,
                )
            except Exception:
                if on_error == "ignore":
                    continue
                raise
        return None

    def _move_tree(
        self,
        source: str,
        destination: str,
        *,
        root: str,
        **kwargs,
    ):
        source_logical, files, dirs = self._collect_tree_entries(source, root=root)
        destination_logical = self._to_logical_path(destination, root=root)

        self.makedirs(destination_logical, root=root, exist_ok=True)
        for directory in dirs:
            relative = self._relative_to(source_logical, directory)
            if not relative:
                continue
            self.makedirs(self._join_logical(destination_logical, relative), root=root, exist_ok=True)

        for file_path in files:
            relative = self._relative_to(source_logical, file_path)
            target_file = self._join_logical(destination_logical, relative)
            parent = target_file.rsplit("/", 1)[0] if "/" in target_file else ""
            if parent:
                self.makedirs(parent, root=root, exist_ok=True)
            self._fs.mv(
                self.to_url(file_path, root=root),
                self.to_url(target_file, root=root),
                recursive=False,
                maxdepth=None,
                **kwargs,
            )

        for directory in sorted(dirs, key=lambda item: item.count("/"), reverse=True):
            if self.exists(directory, root=root):
                self.rm(directory, root=root, recursive=False)
        if self.exists(source_logical, root=root):
            self.rm(source_logical, root=root, recursive=False)
        return None
