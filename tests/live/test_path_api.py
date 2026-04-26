from __future__ import annotations

import os
from pathlib import Path

import pytest


pytestmark = pytest.mark.live_fablake


def test_live_path_api_roundtrip_and_listing_contract(live_lakehouse, live_test_root, live_config):
    alpha_dir = live_lakehouse.path(live_test_root.as_posix()) / "alpha"
    beta_dir = alpha_dir / "beta"
    text_path = beta_dir / "sample.txt"
    bytes_path = beta_dir / "payload.bin"

    beta_dir.mkdir(parents=True, exist_ok=True)
    text_path.write_text("hello-path-api", encoding="utf-8")
    bytes_path.write_bytes(b"\x00\x01\x02\x03")

    assert alpha_dir.is_dir()
    assert beta_dir.is_dir()
    assert text_path.exists()
    assert text_path.is_file()
    assert text_path.resolve(strict=True).as_posix() == text_path.as_posix()
    assert text_path.read_text(encoding="utf-8") == "hello-path-api"
    assert bytes_path.read_bytes() == b"\x00\x01\x02\x03"

    info = text_path.info()
    assert Path(info.name).name == "sample.txt"

    alpha_children = sorted(item.name for item in alpha_dir.iterdir())
    assert alpha_children == ["beta"]

    beta_children = sorted(item.name for item in beta_dir.iterdir())
    assert beta_children == ["payload.bin", "sample.txt"]

    globbed = sorted(item.name for item in beta_dir.glob("*.txt"))
    assert globbed == ["sample.txt"]

    rglobbed = sorted(item.as_posix() for item in alpha_dir.rglob("*.bin"))
    assert rglobbed == [bytes_path.as_posix()]

    renamed = text_path.rename("sample-renamed.txt")
    assert renamed.exists()
    assert not text_path.exists()
    assert renamed.read_text(encoding="utf-8") == "hello-path-api"

    listed_names = sorted(item.name for item in beta_dir.iterdir())
    assert listed_names == ["payload.bin", "sample-renamed.txt"]

    found_names = sorted(item.name for item in alpha_dir.find())
    assert found_names == ["payload.bin", "sample-renamed.txt"]

    table = live_lakehouse.table(schema="dbo", name=live_config.table_name.split(".", 1)[-1])
    assert str(table).endswith(f"/Tables/{live_config.table_name.replace('.', '/')}")
    assert live_lakehouse.fs.exists(table.relative_path, root="Tables")


def test_live_dummy_csv_and_parquet_roundtrip_via_filesystem(
    live_lakehouse,
    live_test_root,
    temp_dir_path,
):
    pd = pytest.importorskip("pandas")
    pl = pytest.importorskip("polars")
    pq = pytest.importorskip("pyarrow.parquet")

    local_csv = temp_dir_path / "orders.csv"
    local_parquet = temp_dir_path / "orders.parquet"
    remote_dir = live_test_root / "datasets"
    remote_csv = remote_dir / "orders.csv"
    remote_parquet = remote_dir / "orders.parquet"

    frame = pd.DataFrame(
        [
            {"order_id": 1, "customer": "Ada", "amount": 12.5},
            {"order_id": 2, "customer": "Linus", "amount": 7.25},
        ]
    )
    frame.to_csv(local_csv, index=False)
    frame.to_parquet(local_parquet, index=False)

    remote_dir.mkdir(parents=True, exist_ok=True)
    live_test_root.fs.put(str(local_csv), remote_csv.as_posix())
    live_test_root.fs.put(str(local_parquet), remote_parquet.as_posix())

    assert remote_csv.exists()
    assert remote_parquet.exists()

    with live_lakehouse.fs.open(str(remote_csv), "rb") as stream:
        csv_frame = pd.read_csv(stream)

    pandas_parquet_frame = pd.read_parquet(
        remote_parquet,
        engine="pyarrow",
        filesystem=live_lakehouse.fs,
    )

    with live_lakehouse.fs.open(remote_parquet, "rb") as stream:
        polars_parquet_frame = pl.read_parquet(stream)

    pyarrow_table = pq.read_table(remote_parquet, filesystem=live_lakehouse.fs)
    pyarrow_parquet_frame = pyarrow_table.to_pandas()

    assert csv_frame.to_dict(orient="records") == frame.to_dict(orient="records")
    assert pandas_parquet_frame.to_dict(orient="records") == frame.to_dict(orient="records")
    assert polars_parquet_frame.to_dicts() == frame.to_dict(orient="records")
    assert pyarrow_parquet_frame.to_dict(orient="records") == frame.to_dict(orient="records")


def test_live_direct_fablakepath_interop_with_fs_and_readers(
    live_lakehouse,
    live_test_root,
    temp_dir_path,
):
    pd = pytest.importorskip("pandas")
    pl = pytest.importorskip("polars")
    pq = pytest.importorskip("pyarrow.parquet")

    local_parquet = temp_dir_path / "direct-orders.parquet"
    remote_dir = live_test_root / "direct-interop"
    remote_parquet = remote_dir / "orders.parquet"

    frame = pd.DataFrame(
        [
            {"order_id": 11, "customer": "Grace", "amount": 21.0},
            {"order_id": 12, "customer": "Margaret", "amount": 34.5},
        ]
    )
    frame.to_parquet(local_parquet, index=False)

    remote_dir.mkdir(parents=True, exist_ok=True)
    live_test_root.fs.put(str(local_parquet), remote_parquet.as_posix())

    assert os.fspath(remote_parquet) == str(remote_parquet)

    with live_lakehouse.fs.open(remote_parquet, "rb") as stream:
        opened_bytes = stream.read()
    assert opened_bytes

    wrapped_listing = live_lakehouse.fs.ls(remote_dir)
    assert any(item.name == "orders.parquet" for item in wrapped_listing)

    pandas_frame = pd.read_parquet(
        remote_parquet,
        engine="pyarrow",
        filesystem=live_lakehouse.fs,
    )

    pyarrow_frame = pq.read_table(remote_parquet, filesystem=live_lakehouse.fs).to_pandas()

    try:
        polars_frame = pl.read_parquet(remote_parquet)
        polars_mode = "path"
    except Exception:
        with live_lakehouse.fs.open(remote_parquet, "rb") as stream:
            polars_frame = pl.read_parquet(stream)
        polars_mode = "stream"

    expected = frame.to_dict(orient="records")
    assert pandas_frame.to_dict(orient="records") == expected
    assert pyarrow_frame.to_dict(orient="records") == expected
    assert polars_frame.to_dicts() == expected

    # Polars direct path support depends on whether the installed build treats
    # custom ABFSS path-like objects as filesystem-aware URIs.
    assert polars_mode in {"path", "stream"}
