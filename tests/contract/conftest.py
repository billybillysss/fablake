from __future__ import annotations

import sys
import types
from typing import cast

import pytest

from tests.fixtures.fakes import FakeFsspecFilesystem


@pytest.fixture(autouse=True)
def stub_fsspec(monkeypatch):
    module = types.ModuleType("fsspec")
    created: list[FakeFsspecFilesystem] = []

    def filesystem(protocol: str, **kwargs):
        fs = FakeFsspecFilesystem(protocol, **kwargs)
        created.append(fs)
        return fs

    setattr(module, "filesystem", filesystem)
    monkeypatch.setitem(sys.modules, "fsspec", module)
    return cast(list[FakeFsspecFilesystem], created)


@pytest.fixture
def lakehouse_schema_enabled():
    from fablake import Lakehouse

    return Lakehouse(
        workspace="Finance",
        lakehouse="Ops",
        schema_enabled=True,
        credential="explicit-credential",
    )


@pytest.fixture
def lakehouse_non_schema():
    from fablake import Lakehouse

    return Lakehouse(
        workspace="Finance",
        lakehouse="Ops",
        schema_enabled=False,
        credential="explicit-credential",
    )
