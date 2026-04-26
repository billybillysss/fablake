from __future__ import annotations

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-live",
        action="store_true",
        default=False,
        help="Run live fablake integration tests (marked live_fablake).",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--run-live"):
        return

    skip_live = pytest.mark.skip(reason="Use --run-live to execute live fablake tests.")
    for item in items:
        if "live_fablake" in item.keywords:
            item.add_marker(skip_live)
