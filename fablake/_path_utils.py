from __future__ import annotations


def normalize_logical_path(path: str | None, *, collapse_parent_segments: bool) -> str:
    value = str(path or "").strip().replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    value = value.strip("/")
    if value in {"", "."}:
        return ""

    if not collapse_parent_segments:
        return value

    parts: list[str] = []
    for part in value.split("/"):
        item = part.strip()
        if item in {"", "."}:
            continue
        if item == "..":
            if parts:
                parts.pop()
            continue
        parts.append(item)
    return "/".join(parts)
