"""Tests for DBManager SQL execution flow."""

from src.db_manager import DBManager


class FakeCursor:
    """Simple cursor stub used to inspect SQL execution."""

    def __init__(self, results: list) -> None:
        """Store queued results for fetch operations."""
        self.results = results
        self.executed: list[tuple[str, tuple | None]] = []

    def execute(self, query: str, params: tuple | None = None) -> None:
        """Store executed query data."""
        self.executed.append((query, params))

    def fetchall(self):
        """Return all rows from the current result set."""
        return self.results.pop(0)

    def fetchone(self):
        """Return one row from the current result set."""
        return self.results.pop(0)

    def __enter__(self):
        """Support context manager protocol."""
        return self

    def __exit__(self, exc_type, exc, tb):
        """Support context manager protocol."""
        return False


class FakeConnection:
    """Simple connection stub wrapping a fake cursor."""

    def __init__(self, cursor: FakeCursor) -> None:
        """Store cursor instance."""
        self.cursor_instance = cursor

    def cursor(self) -> FakeCursor:
        """Return stored fake cursor."""
        return self.cursor_instance

    def __enter__(self):
        """Support context manager protocol."""
        return self

    def __exit__(self, exc_type, exc, tb):
        """Support context manager protocol."""
        return False


class FakeConnectionFactory:
    """Connection factory stub for unit tests."""

    def __init__(self, cursor: FakeCursor) -> None:
        """Store cursor used by every new connection."""
        self.cursor = cursor

    def get_connection(self) -> FakeConnection:
        """Return a fake connection."""
        return FakeConnection(self.cursor)


def test_get_avg_speed_returns_float() -> None:
    """DBManager should convert AVG result to float."""
    cursor = FakeCursor(results=[(245.5,)])
    manager = DBManager(FakeConnectionFactory(cursor))

    result = manager.get_avg_speed()

    assert result == 245.5


def test_get_aeroplanes_with_keyword_passes_ilike_parameter() -> None:
    """DBManager should wrap the keyword into ILIKE wildcards."""
    cursor = FakeCursor(results=[[("ACA123", "Canada", 250.0, 9000.0)]])
    manager = DBManager(FakeConnectionFactory(cursor))

    rows = manager.get_airplanes_with_keyword("ACA")

    assert rows == [("ACA123", "Canada", 250.0, 9000.0)]
    assert cursor.executed[0][1] == ("%ACA%",)
