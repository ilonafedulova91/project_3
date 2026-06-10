from abc import ABC, abstractmethod
from typing import Any

import requests

from src.airplane import Airplane, Country


class ApiInteraction(ABC):
    """Common interface for external API clients."""

    @abstractmethod
    def get_coordinates(self, country_name: str) -> Country:
        """Return a country with geographical bounds."""

    @abstractmethod
    def get_planes(self, country: Country) -> list[Airplane]:
        """Return airplanes currently present inside country bounds."""


class GetPlanesInfo(ApiInteraction):
    """Retrieve countries from Nominatim and flights from OpenSky."""

    def __init__(self) -> None:
        """Prepare endpoint URLs and default headers."""
        self.coordinates_url = "https://nominatim.openstreetmap.org/search"
        self.planes_url = "https://opensky-network.org/api/states/all"
        self.headers = {"User-Agent": "test-app"}

    def get_coordinates(self, country_name: str) -> Country:
        """Request a country's bounding box from Nominatim."""
        params: dict[str, str] = {"q": country_name, "format": "json", "limit": "1"}
        response = requests.get(
            url=self.coordinates_url,
            params=params,
            headers=self.headers,
            timeout=10,
        )
        response.raise_for_status()
        payload: list[dict[str, Any]] = response.json()
        if not payload:
            raise ValueError(f"Country '{country_name}' was not found in Nominatim.")

        bounds = payload[0]["boundingbox"]
        return Country(
            name=country_name,
            latitude_min=float(bounds[0]),
            latitude_max=float(bounds[1]),
            longitude_min=float(bounds[2]),
            longitude_max=float(bounds[3]),
        )

    def get_planes(self, country: Country) -> list[Airplane]:
        """Request airplanes inside the provided country's bounding box."""
        response = requests.get(
            url=self.planes_url,
            params=country.bounds(),
            timeout=10,
        )
        response.raise_for_status()
        states = response.json().get("states", [])
        return Airplane.from_api_list(states)
