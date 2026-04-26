from __future__ import annotations

import pytest


pytestmark = [pytest.mark.live_fablake, pytest.mark.smoke]


def test_live_smoke_connect_and_roundtrip_text(live_test_root):
    probe = live_test_root / "smoke.txt"
    probe.write_text("ok")

    assert probe.exists()
    assert probe.is_file()
    assert probe.read_text() == "ok"

    probe.unlink()
    assert not probe.exists()
