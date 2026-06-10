from typing import NotRequired, TypedDict

from src.api_interaction import GetPlanesInfo
from src.database import DatabaseInitializer, DataRepository
from src.db_manager import DBManager


class ReportData(TypedDict):
    """Typed container for the report returned by the service layer."""

    countries_and_airplanes_count: list[tuple[str, int]]
    all_airplanes: list[tuple]
    avg_speed: float | None
    airplanes_with_higher_speed: list[tuple]
    airplanes_with_keyword: NotRequired[list[tuple]]


class FlightDataService:
    """Coordinate schema creation, API loading, and analytical output."""

    def __init__(
        self,
        api_client: GetPlanesInfo,
        database_initializer: DatabaseInitializer,
        repository: DataRepository,
        db_manager: DBManager,
    ) -> None:
        """Store application dependencies."""
        self.api_client = api_client
        self.database_initializer = database_initializer
        self.repository = repository
        self.db_manager = db_manager

    def load_data(self, country_names: list[str]) -> list[tuple[str, int]]:
        """Fetch countries and airplanes, then store them in PostgreSQL."""
        self.database_initializer.create_tables()
        loading_stats: list[tuple[str, int]] = []

        for country_name in country_names:
            country = self.api_client.get_coordinates(country_name)
            airplanes = self.api_client.get_planes(country)
            country_id = self.repository.save_country(country)
            processed_count = self.repository.save_airplanes(country_id, airplanes)
            loading_stats.append((country.name, processed_count))

        return loading_stats

    def build_report(self, keyword: str = "") -> ReportData:
        """Collect all required analytical queries from DBManager."""
        report: ReportData = {
            "countries_and_airplanes_count": self.db_manager.get_countries_and_airplanes_count(),
            "all_airplanes": self.db_manager.get_all_airplanes(),
            "avg_speed": self.db_manager.get_avg_speed(),
            "airplanes_with_higher_speed": self.db_manager.get_airplanes_with_higher_speed(),
        }
        if keyword:
            report["airplanes_with_keyword"] = (
                self.db_manager.get_airplanes_with_keyword(keyword)
            )
        return report
