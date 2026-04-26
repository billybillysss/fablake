from __future__ import annotations

import os
import tempfile
import uuid
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path

import pytest

from fablake import Lakehouse


pytestmark = pytest.mark.live_fablake


def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def _env(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def _require_env(name: str) -> str:
    value = _env(name)
    if value is None:
        pytest.skip(f"Set {name} to run live fablake integration tests.")
        raise AssertionError("pytest.skip should have stopped execution")
    return value


@dataclass(frozen=True)
class LiveConfig:
    workspace_id: str
    lakehouse_id: str
    test_root: str
    table_name: str
    max_concurrency: int
    upload_count: int
    upload_size_bytes: int
    max_upload_seconds: float | None


@pytest.fixture(scope="session")
def live_config() -> LiveConfig:
    _load_dotenv()
    max_upload_seconds = _env("FABLAKE_TEST_MAX_UPLOAD_SECONDS")
    return LiveConfig(
        workspace_id=_require_env("FABLAKE_TEST_WORKSPACE_ID"),
        lakehouse_id=_require_env("FABLAKE_TEST_LAKEHOUSE_ID"),
        test_root=_env("FABLAKE_TEST_ROOT") or "regression",
        table_name=_env("FABLAKE_TEST_TABLE") or "dbo.test",
        max_concurrency=max(1, int(_env("FABLAKE_TEST_MAX_CONCURRENCY") or "8")),
        upload_count=int(_env("FABLAKE_TEST_UPLOAD_COUNT") or "1000"),
        upload_size_bytes=max(1, int(_env("FABLAKE_TEST_UPLOAD_SIZE_BYTES") or "1024")),
        max_upload_seconds=float(max_upload_seconds) if max_upload_seconds else None,
    )


@pytest.fixture(scope="session")
def default_azure_credential():
    try:
        module = import_module("azure.identity")
    except ImportError as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"azure-identity is required for live tests: {exc}")
        raise AssertionError("pytest.skip should have stopped execution")

    credential_cls = getattr(module, "DefaultAzureCredential")
    return credential_cls()


@pytest.fixture(scope="session")
def live_lakehouse(default_azure_credential, live_config: LiveConfig) -> Lakehouse:
    try:
        return Lakehouse(
            workspace_id=live_config.workspace_id,
            lakehouse_id=live_config.lakehouse_id,
            schema_enabled=True,
            credential=default_azure_credential,
            max_concurrency=live_config.max_concurrency,
        )
    except RuntimeError as exc:
        if "missing the runtime dependencies" in str(exc):
            pytest.skip(str(exc))
        raise


@pytest.fixture
def live_test_root(live_lakehouse: Lakehouse, live_config: LiveConfig):
    root = live_lakehouse.files / live_config.test_root / f"pytest-{uuid.uuid4().hex}"
    root.mkdir(parents=True, exist_ok=True)
    yield root
    if root.exists():
        root.fs.rm(root.as_posix(), recursive=True)


@pytest.fixture
def temp_dir_path() -> Path:
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)
