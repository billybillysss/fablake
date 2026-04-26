from __future__ import annotations

from typing import Any

from .._abfs import FabLakeFileSystem
from .._models import LakehouseBinding
from ..exceptions import ResolutionError
from ..path import LakehousePath
from .rules import require_schema_mode, validate_table_reference
from .table_path import LakehouseTable
from .tables import LakehouseTables


class Lakehouse:
    """Bound fablake Lakehouse context.

    The class provides a filesystem-first entry point for working with paths
    under the `Files` root and table locators under the `Tables` root.

    A `Lakehouse` instance must be created with either:

    - name binding: `workspace` + `lakehouse`
    - id binding: `workspace_id` + `lakehouse_id`
    """

    def __init__(
        self,
        *,
        workspace: str | None = None,
        workspace_id: str | None = None,
        lakehouse: str | None = None,
        lakehouse_id: str | None = None,
        schema_enabled: bool = True,
        **filesystem_kwargs,
    ) -> None:
        """Create a bound lakehouse context.

        Parameters
        ----------
        workspace:
            Workspace display name. Must be set together with `lakehouse`.
        workspace_id:
            Workspace identifier. Must be set together with `lakehouse_id`.
        lakehouse:
            Lakehouse display name.
        lakehouse_id:
            Lakehouse identifier.
        schema_enabled:
            Table mode. If `True`, `table(None, name)` resolves to `dbo/name`.
            If `False`, schema must be omitted and table paths are flat.
        **filesystem_kwargs:
            Additional keyword arguments forwarded to the underlying ABFS
            filesystem backend.

        Raises
        ------
        ResolutionError
            If name and id bindings are mixed or incomplete.
        """
        has_name_inputs = workspace is not None or lakehouse is not None
        has_id_inputs = workspace_id is not None or lakehouse_id is not None

        if has_name_inputs and has_id_inputs:
            raise ResolutionError(
                "Use either (workspace, lakehouse) names or "
                "(workspace_id, lakehouse_id) identifiers, not mixed values.",
            )

        if has_name_inputs:
            if workspace is None or lakehouse is None:
                raise ResolutionError(
                    "Provide both workspace and lakehouse when using name binding.",
                )
            workspace_value = str(workspace).strip()
            lakehouse_value = str(lakehouse).strip()
            if not workspace_value or not lakehouse_value:
                raise ResolutionError("workspace and lakehouse must be non-empty.")
            self._binding = LakehouseBinding(
                workspace=workspace_value,
                lakehouse=lakehouse_value,
                identifier_mode="name",
            )
            self._workspace = workspace_value
            self._lakehouse = lakehouse_value
        else:
            if workspace_id is None or lakehouse_id is None:
                raise ResolutionError(
                    "Provide both workspace_id and lakehouse_id when using ID binding.",
                )
            workspace_value = str(workspace_id).strip()
            lakehouse_value = str(lakehouse_id).strip()
            if not workspace_value or not lakehouse_value:
                raise ResolutionError("workspace_id and lakehouse_id must be non-empty.")
            self._binding = LakehouseBinding(
                workspace=workspace_value,
                lakehouse=lakehouse_value,
                identifier_mode="id",
            )
            self._workspace = None
            self._lakehouse = None

        self._schema_enabled = schema_enabled
        filesystem_kwargs = dict(filesystem_kwargs)

        self._filesystem = FabLakeFileSystem(
            workspace=self.binding.workspace,
            lakehouse=self.binding.lakehouse,
            identifier_mode=self.binding.identifier_mode,
            **filesystem_kwargs,
        )
        self._files = LakehousePath(self._filesystem, root="Files", path="")
        self._tables = LakehouseTables(self)

    @property
    def workspace(self) -> str | None:
        return self._workspace

    @property
    def workspace_id(self) -> str:
        return self._binding.workspace

    @property
    def lakehouse(self) -> str | None:
        return self._lakehouse

    @property
    def lakehouse_id(self) -> str:
        return self._binding.lakehouse

    @property
    def binding(self) -> LakehouseBinding:
        return self._binding

    @property
    def schema_enabled(self) -> bool | None:
        return self._schema_enabled

    @property
    def fs(self):
        return self._filesystem

    @property
    def storage_options(self) -> dict[str, Any]:
        return self._filesystem.storage_options

    @property
    def files(self) -> LakehousePath:
        return self._files

    @property
    def tables(self) -> LakehouseTables:
        return self._tables

    def path(self, path: str = "", *, root: str = "Files") -> LakehousePath:
        """Create a path object under the selected lakehouse root.

        Parameters
        ----------
        path:
            Logical path inside the selected root.
        root:
            Lakehouse root to use. Supported values are `Files` and `Tables`.
        """
        return LakehousePath(self._filesystem, root=root, path=path)

    def table(self, name: str, schema: str | None = None) -> LakehouseTable:
        """Create a table-root locator.

        Parameters
        ----------
        name:
            Table name as a single path segment.
        schema:
            Schema name for schema-enabled lakehouses. Use `None` to target the
            default schema (`dbo`). Must be `None` when `schema_enabled=False`.

        Returns
        -------
        LakehouseTable
            Table root locator under the `Tables` root.
        """
        schema_enabled = require_schema_mode(self._schema_enabled)
        normalized_schema, normalized_name = validate_table_reference(
            schema_enabled=schema_enabled,
            schema=schema,
            name=name,
        )

        if not schema_enabled:
            return LakehouseTable(
                self._filesystem,
                schema=None,
                name=normalized_name,
                schema_enabled=False,
            )

        return LakehouseTable(
            self._filesystem,
            schema=normalized_schema,
            name=normalized_name,
            schema_enabled=True,
        )
