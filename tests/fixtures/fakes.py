from __future__ import annotations

import io


class FakeFile(io.BytesIO):
    def __init__(self, payload: bytes = b"stub") -> None:
        super().__init__(payload)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return None


class FakeFsspecFilesystem:
    def __init__(self, protocol: str, **kwargs) -> None:
        self.protocol = protocol
        self.kwargs = dict(kwargs)
        self.open_calls: list[tuple[str, str, dict]] = []
        self.last_exists_path: str | None = None
        self.last_ls_path: str | None = None

    def exists(self, path: str, **kwargs) -> bool:
        self.last_exists_path = path
        return True

    def isdir(self, path: str) -> bool:
        return path.endswith("/") or path.endswith("Files") or path.endswith("Tables")

    def isfile(self, path: str) -> bool:
        return not self.isdir(path)

    def info(self, path: str, **kwargs):
        return {"name": path, "type": "file", "size": 4}

    def ls(self, path: str, detail: bool = True, **kwargs):
        self.last_ls_path = path
        entries = [f"{path.rstrip('/')}/folder1", f"{path.rstrip('/')}/a.yaml"]
        if detail:
            return [{"name": entry, "type": "file", "size": 4} for entry in entries]
        return entries

    def find(self, path: str, maxdepth=None, withdirs: bool = False, detail: bool = False, **kwargs):
        entries = [f"{path.rstrip('/')}/folder1/a.yaml", f"{path.rstrip('/')}/folder1/b.yaml"]
        if detail:
            return {entry: {"name": entry, "type": "file", "size": 4} for entry in entries}
        return entries

    def glob(self, path: str, **kwargs):
        return [path]

    def open(self, path: str, mode: str = "rb", **kwargs):
        self.open_calls.append((path, mode, dict(kwargs)))
        return FakeFile()

    def mkdir(self, path: str, **kwargs):
        return None

    def makedirs(self, path: str, exist_ok: bool = False):
        return None

    def rm(self, path, recursive: bool = False, **kwargs):
        return None

    def copy(self, path1, path2, recursive: bool = False, on_error: str | None = None, maxdepth=None, **kwargs):
        return None

    def mv(self, path1, path2, recursive: bool = False, maxdepth=None, **kwargs):
        return None
