"""Tests for CLI input helpers."""

from src.user_interaction import read_countries


def test_read_countries_returns_default_list(monkeypatch) -> None:
    """Default answer should return the predefined country list."""
    monkeypatch.setattr("builtins.input", lambda _: "y")

    countries = read_countries()

    assert len(countries) == 10


def test_read_countries_requires_minimum_of_four(monkeypatch) -> None:
    """Manual country input should stop only after four values."""
    answers = iter(["n", "Romania", "France", "Germany", "Spain", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    countries = read_countries()

    assert countries == ["Romania", "France", "Germany", "Spain"]
