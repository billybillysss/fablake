from __future__ import annotations

import json
import re
import sys
from pathlib import Path


SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def _sort_key(version: str) -> tuple[int, int, int]:
    major, minor, patch = version.split(".")
    return int(major), int(minor), int(patch)


def build_manifest(site_root: Path, default: str = "latest") -> dict:
    keys: list[str] = []
    for entry in site_root.iterdir():
        if not entry.is_dir():
            continue
        name = entry.name
        if name in {"latest", "dev"} or SEMVER.match(name):
            keys.append(name)

    semver_versions = sorted([k for k in keys if SEMVER.match(k)], key=_sort_key, reverse=True)
    ordered: list[str] = []
    if default in keys:
        ordered.append(default)
    elif default == "latest":
        ordered.append("latest")

    for value in semver_versions:
        if value not in ordered:
            ordered.append(value)

    for value in keys:
        if value not in ordered:
            ordered.append(value)

    versions = [{"key": key, "label": key} for key in ordered]
    return {"default": default, "versions": versions}


def main() -> None:
    site_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("site")
    default = sys.argv[2] if len(sys.argv) > 2 else "latest"
    manifest = build_manifest(site_root, default=default)
    out_path = site_root / "versions.json"
    out_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
