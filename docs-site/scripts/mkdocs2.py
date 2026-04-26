from __future__ import annotations

import os
import pathlib
import sys


def _patch_windows_posixpath() -> None:
    if os.name != "nt":
        return
    try:
        pathlib.PosixPath(".")
        return
    except Exception:
        pass

    class CompatPosixPath(pathlib.PurePosixPath):
        pass

    pathlib.PosixPath = CompatPosixPath  # type: ignore[assignment]


def main() -> int:
    _patch_windows_posixpath()
    site_root = pathlib.Path(__file__).resolve().parents[1]
    os.chdir(site_root)
    from mkdocs.cli import cli

    return int(cli() or 0)


if __name__ == "__main__":
    raise SystemExit(main())
