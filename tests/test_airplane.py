"""Tests for airplane parsing."""

from src.airplane import Airplane


def test_airplane_from_api_state_parses_values() -> None:
    """Airplane parser should map OpenSky positions correctly."""
    state = [
        "abcd12",
        "ACA123 ",
        "Canada",
        111,
        222,
        25.0,
        45.0,
        9000.0,
        False,
        250.0,
        180.0,
        5.0,
        None,
        9200.0,
        "7000",
        False,
        0,
    ]

    airplane = Airplane.from_api_state(state)

    assert airplane.callsign == "ACA123"
    assert airplane.baro_altitude == 9200.0
    assert airplane.geo_altitude == 9000.0
