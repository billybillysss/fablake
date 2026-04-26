from __future__ import annotations

import time
from pathlib import Path

import pytest


pytestmark = [pytest.mark.live_fablake, pytest.mark.slow]


def test_live_put_recursive_bulk_upload(live_test_root, live_config, temp_dir_path, record_property):
    bulk_root = live_test_root / "bulk"
    payload = b"x" * live_config.upload_size_bytes

    for index in range(live_config.upload_count):
        (temp_dir_path / f"dummy-{index:04d}.bin").write_bytes(payload)

    started = time.perf_counter()
    live_test_root.fs.put(str(temp_dir_path), bulk_root.as_posix(), recursive=True)
    elapsed = time.perf_counter() - started

    listing = bulk_root.find()
    found_names = {item.name for item in listing}

    assert len(found_names) == live_config.upload_count
    assert "dummy-0000.bin" in found_names
    assert f"dummy-{live_config.upload_count - 1:04d}.bin" in found_names

    if live_config.max_upload_seconds is not None:
        assert elapsed <= live_config.max_upload_seconds

    record_property("upload_count", live_config.upload_count)
    record_property("max_concurrency", live_config.max_concurrency)
    record_property("upload_size_bytes", live_config.upload_size_bytes)
    record_property("upload_elapsed_seconds", round(elapsed, 3))
