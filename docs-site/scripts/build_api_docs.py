from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "docs" / "api"


OBJECTS: list[tuple[str, str, str, str]] = [
    (
        "lakehouse.md",
        "fablake.lakehouse.core",
        "Lakehouse",
        "Lakehouse is the main entry point for fablake file and table path workflows.",
    ),
    (
        "lakehouse-path.md",
        "fablake.path",
        "LakehousePath",
        "LakehousePath provides pathlib-like ergonomics over fablake logical paths.",
    ),
    (
        "lakehouse-table.md",
        "fablake.lakehouse.table_path",
        "LakehouseTable",
        "LakehouseTable is a lightweight path-like locator for the Tables root.",
    ),
    (
        "lakehouse-tables.md",
        "fablake.lakehouse.tables",
        "LakehouseTables",
        "LakehouseTables provides table discovery helpers under the Tables root.",
    ),
    (
        "path-info.md",
        "fablake._models",
        "LakehousePathInfo",
        "LakehousePathInfo represents normalized metadata returned by path.info().",
    ),
]


MODULE_PAGES: list[tuple[str, str, str]] = [
    (
        "exceptions.md",
        "fablake.exceptions",
        "Package exceptions raised by public fablake operations.",
    ),
]


MANUAL_EXAMPLES: dict[str, str] = {
    "Lakehouse": """```python
from fablake import Lakehouse

lh = Lakehouse(workspace=\"Finance\", lakehouse=\"Ops\", schema_enabled=True)
orders_file = lh.files / \"raw\" / \"orders.parquet\"
orders_table = lh.table(\"orders\", schema=\"brz\")
```""",
    "LakehousePath": """```python
path = lh.files / \"config\" / \"settings.json\"

if path.exists():
    print(path.read_text())
```""",
    "LakehouseTable": """```python
table_root = lh.table(\"orders\", schema=\"dbo\")
print(table_root)
```""",
    "LakehouseTables": """```python
matches = lh.tables.list("db*.*der")

for table in matches:
    print(table)
```""",
}


MANUAL_SIGNATURES: dict[str, str] = {
    "LakehousePath": (
        "LakehousePath(fs: FabLakeFileSystem, *, root: str = 'Files', path: str = '')"
    ),
    "LakehouseTable": (
        "LakehouseTable(filesystem: FabLakeFileSystem, schema: str | None, "
        "name: str, schema_enabled: bool = True)"
    ),
}


MANUAL_PARAMETERS: dict[str, list[str]] = {
    "LakehousePath": [
        "- `fs`: `FabLakeFileSystem`",
        "- `root`: `str` (default: `Files`)",
        "- `path`: `str` (default: ``)",
    ],
    "LakehouseTable": [
        "- `filesystem`: `FabLakeFileSystem`",
        "- `schema`: `str | None`",
        "- `name`: `str`",
        "- `schema_enabled`: `bool` (default: `True`)",
    ],
}


MANUAL_PROPERTIES: dict[str, list[str]] = {
    "LakehouseTable": [
        "- `schema: str | None`",
        "- `name: str`",
        "- `schema_enabled: bool`",
        "- `relative_path: str`",
        "- `identifier: str`",
        "- `uri: str`",
    ],
}


def _signature_for(callable_obj: Any) -> str:
    try:
        return str(inspect.signature(callable_obj))
    except (TypeError, ValueError):
        return "(...)"


def _format_parameters(callable_obj: Any) -> list[str]:
    try:
        params = list(inspect.signature(callable_obj).parameters.values())
    except (TypeError, ValueError):
        return ["- Not available"]

    rendered: list[str] = []
    for param in params:
        name = param.name
        annotation = ""
        if param.annotation is not inspect._empty:
            annotation = f": `{param.annotation}`"
        default = ""
        if param.default is not inspect._empty:
            default = f" (default: `{param.default}`)"
        rendered.append(f"- `{name}`{annotation}{default}")
    return rendered or ["- None"]


def _return_annotation(callable_obj: Any) -> str:
    try:
        sig = inspect.signature(callable_obj)
    except (TypeError, ValueError):
        return "Not available"
    if sig.return_annotation is inspect._empty:
        return "Not declared"
    return f"`{sig.return_annotation}`"


def _doc_text(obj: Any) -> str:
    text = inspect.getdoc(obj) or "No description provided."
    return text


def _render_class_page(module_name: str, class_name: str, intro: str) -> str:
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    constructor = getattr(cls, "__init__", None)

    lines: list[str] = []
    lines.append(f"# {class_name}")
    lines.append("")
    lines.append(intro)
    lines.append("")
    lines.append("## Signature")
    lines.append("")
    lines.append("```python")
    manual_signature = MANUAL_SIGNATURES.get(class_name)
    if manual_signature is not None:
        lines.append(manual_signature)
    else:
        lines.append(f"{class_name}{_signature_for(constructor)}")
    lines.append("```")
    lines.append("")
    lines.append("## Parameters")
    lines.append("")
    manual_parameters = MANUAL_PARAMETERS.get(class_name)
    if manual_parameters is not None:
        lines.extend(manual_parameters)
    else:
        lines.extend(_format_parameters(constructor))
    lines.append("")
    lines.append("## Description")
    lines.append("")
    lines.append(_doc_text(cls))
    lines.append("")
    example = MANUAL_EXAMPLES.get(class_name)
    if example:
        lines.append("## Example")
        lines.append("")
        lines.append(example)
        lines.append("")
    manual_properties = MANUAL_PROPERTIES.get(class_name)
    if manual_properties:
        lines.append("## Properties")
        lines.append("")
        lines.extend(manual_properties)
        lines.append("")
    lines.append("## Methods")
    lines.append("")

    members: list[tuple[str, Any]] = []
    for name, member in inspect.getmembers(cls):
        if name.startswith("_"):
            continue
        if inspect.isfunction(member) or inspect.ismethod(member):
            members.append((name, member))

    if not members:
        lines.append("No public methods.")
        lines.append("")
        return "\n".join(lines)

    for name, member in members:
        lines.append(f"### {class_name}.{name}")
        lines.append("")
        lines.append('<div class="api-signature">')
        lines.append("")
        lines.append("```python")
        lines.append(f"{name}{_signature_for(member)}")
        lines.append("```")
        lines.append("")
        lines.append("</div>")
        lines.append("")
        lines.append("Parameters:")
        lines.append("")
        lines.extend(_format_parameters(member))
        lines.append("")
        lines.append(f"Returns: {_return_annotation(member)}")
        lines.append("")
        lines.append(_doc_text(member))
        lines.append("")

    return "\n".join(lines)


def _render_module_page(module_name: str, intro: str) -> str:
    module = importlib.import_module(module_name)
    title = module_name.split(".")[-1]

    lines: list[str] = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(intro)
    lines.append("")
    lines.append("## Public Objects")
    lines.append("")

    public_members: list[tuple[str, Any]] = []
    for name, member in inspect.getmembers(module):
        if name.startswith("_"):
            continue
        if inspect.isclass(member) or inspect.isfunction(member):
            if getattr(member, "__module__", None) == module.__name__:
                public_members.append((name, member))

    if not public_members:
        lines.append("No public functions or classes.")
        lines.append("")
        return "\n".join(lines)

    for name, member in public_members:
        lines.append(f"### {name}")
        lines.append("")
        if inspect.isfunction(member):
            lines.append('<div class="api-signature">')
            lines.append("")
            lines.append("```python")
            lines.append(f"{name}{_signature_for(member)}")
            lines.append("```")
            lines.append("")
            lines.append("</div>")
            lines.append("")
            lines.append("Parameters:")
            lines.append("")
            lines.extend(_format_parameters(member))
            lines.append("")
            lines.append(f"Returns: {_return_annotation(member)}")
            lines.append("")
            lines.append(_doc_text(member))
            lines.append("")
        else:
            lines.append(_doc_text(member))
            lines.append("")

    return "\n".join(lines)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content + "\n", encoding="utf-8")


def main() -> None:
    _write(
        API_DIR / "index.md",
        "\n".join(
            [
                "# Python API",
                "",
                "This section combines generated signatures with handwritten guidance.",
                "",
                "- [Lakehouse](lakehouse/)",
                "- [LakehousePath](lakehouse-path/)",
                "- [LakehouseTable](lakehouse-table/)",
                "- [LakehouseTables](lakehouse-tables/)",
                "- [LakehousePathInfo](path-info/)",
                "- [exceptions](exceptions/)",
            ]
        ),
    )

    for file_name, module_name, class_name, intro in OBJECTS:
        content = _render_class_page(module_name, class_name, intro)
        _write(API_DIR / file_name, content)

    for file_name, module_name, intro in MODULE_PAGES:
        content = _render_module_page(module_name, intro)
        _write(API_DIR / file_name, content)


if __name__ == "__main__":
    main()
