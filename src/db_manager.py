from src.database import ConnectionFactory


class DBManager:
    """Read analytical data about countries and airplanes from PostgreSQL."""

    def __init__(self, connection_factory: ConnectionFactory) -> None:
        """Store a connection factory used for read queries."""
        self.connection_factory = connection_factory

    def get_countries_and_airplanes_count(self) -> list[tuple[str, int]]:
        """Return all countries with the number of airplanes in each airspace."""
        query = """
            SELECT c.name, COUNT(a.id) AS airplanes_count
            FROM countries AS c
            LEFT JOIN airplanes AS a ON a.country_id = c.id
            GROUP BY c.id, c.name
            ORDER BY airplanes_count DESC, c.name ASC
        """
        return self._fetch_all(query)

    def get_all_airplanes(self) -> list[tuple]:
        """Return all stored airplane records ordered by country and callsign."""
        query = """
            SELECT
                a.icao24,
                a.callsign,
                a.origin_country,
                c.name AS tracked_country,
                a.velocity,
                a.geo_altitude,
                a.last_contact
            FROM airplanes AS a
            INNER JOIN countries AS c ON c.id = a.country_id
            ORDER BY c.name ASC, a.callsign ASC, a.last_contact DESC
        """
        return self._fetch_all(query)

    def get_avg_speed(self) -> float | None:
        """Return average airplane speed excluding NULL values."""
        query = "SELECT AVG(velocity) FROM airplanes WHERE velocity IS NOT NULL"
        row = self._fetch_one(query)
        return float(row[0]) if row and row[0] is not None else None

    def get_airplanes_with_higher_speed(self) -> list[tuple]:
        """Return airplanes with a speed higher than the dataset average."""
        query = """
            SELECT callsign, origin_country, velocity
            FROM airplanes
            WHERE velocity > (
                SELECT AVG(velocity) FROM airplanes WHERE velocity IS NOT NULL
            )
            ORDER BY velocity DESC, callsign ASC
        """
        return self._fetch_all(query)

    def get_airplanes_with_keyword(self, keyword: str) -> list[tuple]:
        """Return airplanes whose callsign contains the provided keyword."""
        query = """
            SELECT callsign, origin_country, velocity, geo_altitude
            FROM airplanes
            WHERE callsign LIKE %s
            ORDER BY callsign ASC
        """
        return self._fetch_all(query, (f"%{keyword}%",))

    def get_storage_counts(self) -> tuple[int, int]:
        """Return the number of rows currently stored in countries and airplanes."""
        countries_row = self._fetch_one("SELECT COUNT(*) FROM countries")
        airplanes_row = self._fetch_one("SELECT COUNT(*) FROM airplanes")
        countries_count = int(countries_row[0]) if countries_row else 0
        airplanes_count = int(airplanes_row[0]) if airplanes_row else 0
        return countries_count, airplanes_count

    def _fetch_all(self, query: str, params: tuple | None = None) -> list[tuple]:
        """Execute a query and return all rows."""
        with self.connection_factory.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

    def _fetch_one(self, query: str, params: tuple | None = None) -> tuple | None:
        """Execute a query and return the first row."""
        with self.connection_factory.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()
