from dataclasses import dataclass


@dataclass(slots=True)
class Country:
    """Country airspace boundaries returned by Nominatim."""

    name: str
    latitude_min: float
    latitude_max: float
    longitude_min: float
    longitude_max: float

    def bounds(self) -> dict[str, float]:
        """Return parameters compatible with the OpenSky bounding box query."""
        return {
            "lamin": self.latitude_min,
            "lamax": self.latitude_max,
            "lomin": self.longitude_min,
            "lomax": self.longitude_max,
        }


@dataclass(slots=True)
class Airplane:
    """Airplane snapshot parsed from the OpenSky REST API."""

    icao24: str
    callsign: str
    origin_country: str
    time_position: int | None
    last_contact: int
    longitude: float | None
    latitude: float | None
    baro_altitude: float | None
    on_ground: bool
    velocity: float | None
    true_track: float | None
    vertical_rate: float | None
    geo_altitude: float | None
    squawk: str | None
    position_source: int

    @classmethod
    def from_api_state(cls, state: list) -> "Airplane":
        """Build an airplane entity from a single OpenSky state vector."""
        if len(state) < 17:
            raise ValueError("State vector must contain at least 17 elements.")

        return cls(
            icao24=state[0],
            callsign=(state[1] or "").strip() or "Unknown",
            origin_country=state[2],
            time_position=state[3] if state[3] is not None else None,
            last_contact=state[4],
            longitude=cls._to_float(state[5]),
            latitude=cls._to_float(state[6]),
            baro_altitude=cls._to_float(state[13]),
            on_ground=bool(state[8]),
            velocity=cls._to_float(state[9]),
            true_track=cls._to_float(state[10]),
            vertical_rate=cls._to_float(state[11]),
            geo_altitude=cls._to_float(state[7]),
            squawk=state[14],
            position_source=state[16],
        )

    @staticmethod
    def _to_float(value: float | int | None) -> float | None:
        """Convert a numeric API value to float when present."""
        return float(value) if value is not None else None

    @classmethod
    def from_api_list(cls, states: list[list]) -> list["Airplane"]:
        """Convert multiple OpenSky state vectors into airplane entities."""
        airplanes: list["Airplane"] = []
        for state in states:
            try:
                airplanes.append(cls.from_api_state(state))
            except (TypeError, ValueError):
                continue
        return airplanes

    def as_db_tuple(self, country_id: int) -> tuple:
        """Return a tuple aligned with the airplanes insert query."""
        return (
            self.icao24,
            self.callsign,
            self.origin_country,
            country_id,
            self.time_position,
            self.last_contact,
            self.longitude,
            self.latitude,
            self.baro_altitude,
            self.on_ground,
            self.velocity,
            self.true_track,
            self.vertical_rate,
            self.geo_altitude,
            self.squawk,
            self.position_source,
        )
