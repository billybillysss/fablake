class FabLakeError(Exception):
    """Base exception for the fablake library."""


class ResolutionError(FabLakeError):
    """Raised when workspace/lakehouse resolution fails."""


class TableIdentifierError(FabLakeError):
    """Raised when a table identifier is malformed."""


class SparkRequiredError(FabLakeError):
    """Raised when Spark is required but unavailable."""
