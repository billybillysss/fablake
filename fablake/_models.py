from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from typing import Literal


@dataclass(frozen=True)
class LakehouseBinding:
    workspace: str
    lakehouse: str
    identifier_mode: Literal["name", "id"]


@dataclass(frozen=True)
class LakehousePathInfo:
    name: str
    type: str
    size: int | None
    metadata: dict[str, str] | None = None
    creation_time: datetime | None = None
    deleted: bool | None = None
    deleted_time: datetime | None = None
    last_modified: datetime | None = None
    content_settings: dict[str, Any] | None = None
    remaining_retention_days: int | None = None
    archive_status: str | None = None
    last_accessed_on: datetime | None = None
    etag: str | None = None
    tags: dict[str, str] | None = None
    tag_count: int | None = None
    raw: dict[str, Any] | None = None
