from __future__ import annotations

from pathlib import Path


DOCS_SITE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = DOCS_SITE_ROOT.parents[0]


def main() -> None:
    source = REPO_ROOT / "CHANGELOG.md"
    target = DOCS_SITE_ROOT / "docs" / "changelog.md"
    text = source.read_text(encoding="utf-8")
    target.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
