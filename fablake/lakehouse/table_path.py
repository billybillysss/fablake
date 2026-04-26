from __future__ import annotations

from .._abfs import FabLakeFileSystem


class LakehouseTable(str):
    """Table-root locator under the fablake `Tables` area.

    The object is path-like and stringifies to an ABFSS URI.
    """

    __slots__ = ("_filesystem", "schema", "name", "schema_enabled")

    def __new__(
        cls,
        filesystem: FabLakeFileSystem,
        schema: str | None,
        name: str,
        schema_enabled: bool = True,
    ) -> LakehouseTable:
        if schema_enabled:
            schema_name = schema or "dbo"
            relative_path = f"{schema_name}/{name}"
        else:
            relative_path = name

        uri = filesystem.to_url(relative_path, root="Tables")
        instance = str.__new__(cls, uri)
        object.__setattr__(instance, "_filesystem", filesystem)
        object.__setattr__(instance, "schema", schema)
        object.__setattr__(instance, "name", name)
        object.__setattr__(instance, "schema_enabled", schema_enabled)
        return instance

    @property
    def relative_path(self) -> str:
        """Return relative table path below the `Tables` root."""
        if self.schema_enabled:
            schema_name = self.schema or "dbo"
            return f"{schema_name}/{self.name}"
        return self.name

    @property
    def uri(self) -> str:
        """Return fully-qualified ABFSS URI for this table root."""
        return str(self)

    @property
    def identifier(self) -> str:
        """Return logical table identifier (`schema.name` or `name`)."""
        if self.schema_enabled:
            return f"{self.schema or 'dbo'}.{self.name}"
        return self.name

    def __str__(self) -> str:
        return str.__str__(self)

    def __repr__(self) -> str:
        return f"LakehouseTable('{self.identifier}')"

    def __fspath__(self) -> str:
        return str(self)
