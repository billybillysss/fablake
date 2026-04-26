from __future__ import annotations


def test_top_level_lakehouse_import_works():
    from fablake import Lakehouse

    assert Lakehouse.__name__ == "Lakehouse"


def test_package_lakehouse_imports_work():
    from fablake.lakehouse import Lakehouse, LakehouseTable
    from fablake.lakehouse.rules import validate_table_reference

    assert Lakehouse.__name__ == "Lakehouse"
    assert LakehouseTable.__name__ == "LakehouseTable"
    assert callable(validate_table_reference)
