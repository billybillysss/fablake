from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _run(*args: str) -> None:
    subprocess.run([sys.executable, *args], check=True, cwd=ROOT)


def generate_api() -> None:
    _run("docs-site/scripts/build_api_docs.py")


def sync_changelog() -> None:
    _run("docs-site/scripts/sync_changelog.py")


def build_docs() -> None:
    generate_api()
    sync_changelog()
    _run("docs-site/scripts/mkdocs2.py", "build")


def serve_docs() -> None:
    generate_api()
    sync_changelog()
    _run("docs-site/scripts/mkdocs2.py", "serve")


def main() -> int:
    action = sys.argv[1] if len(sys.argv) > 1 else "serve"

    if action == "api":
        generate_api()
        return 0
    if action == "sync":
        sync_changelog()
        return 0
    if action == "build":
        build_docs()
        return 0
    if action == "serve":
        serve_docs()
        return 0

    print("Usage: python scripts/docs.py [serve|build|api|sync]")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
