from typing import Any, Protocol

import psycopg2
from psycopg2.extras import execute_batch

from src.airplane import Airplane, Country
from src.config import DBConfig


class ConnectionFactory(Protocol):
    """Connection factory protocol for PostgreSQL access."""

    def get_connection(self) -> Any:
        """Create and return a new database connection."""


class PostgresConnectionFactory(ConnectionFactory):
    """Concrete factory that creates psycopg2 PostgreSQL connections."""

    def __init__(self, config: DBConfig) -> None:
        """Store database configuration for future connections."""
        self.config = config

    def get_connection(self) -> Any:
        """Open a PostgreSQL connection using psycopg2."""
        return psycopg2.connect(
            host=self.config.host,
            port=self.config.port,
            dbname=self.config.dbname,
            user=self.config.user,
            password=self.config.password,
        )


class DatabaseInitializer:
    """Create project tables when they do not exist yet."""

    def __init__(self, connection_factory: ConnectionFactory) -> None:
        """Store a connection factory used for DDL execution."""
        self.connection_factory = connection_factory

    def create_tables(self) -> None:
        """Create countries and airplanes tables."""
        with self.connection_factory.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS countries (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) UNIQUE NOT NULL,
                        latitude_min DOUBLE PRECISION NOT NULL,
                        latitude_max DOUBLE PRECISION NOT NULL,
                        longitude_min DOUBLE PRECISION NOT NULL,
                        longitude_max DOUBLE PRECISION NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS airplanes (
                        id SERIAL PRIMARY KEY,
                        icao24 VARCHAR(20) NOT NULL,
                        callsign VARCHAR(50),
                        origin_country VARCHAR(100) NOT NULL,
                        country_id INTEGER NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
                        time_position BIGINT,
                        last_contact BIGINT NOT NULL,
                        longitude DOUBLE PRECISION,
                        latitude DOUBLE PRECISION,
                        baro_altitude DOUBLE PRECISION,
                        on_ground BOOLEAN NOT NULL,
                        velocity DOUBLE PRECISION,
                        true_track DOUBLE PRECISION,
                        vertical_rate DOUBLE PRECISION,
                        geo_altitude DOUBLE PRECISION,
                        squawk VARCHAR(20),
                        position_source INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE (icao24, last_contact, country_id)
                    )
                    """)
            connection.commit()


class DataRepository:
    """Persist countries and airplane snapshots into PostgreSQL."""

    def __init__(self, connection_factory: ConnectionFactory) -> None:
        """Store a connection factory used for write operations."""
        self.connection_factory = connection_factory

    def save_country(self, country: Country) -> int:
        """Insert or update a country and return its identifier."""
        with self.connection_factory.get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO countries (
                        name, latitude_min, latitude_max, longitude_min, longitude_max
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (name) DO UPDATE SET
                        latitude_min = EXCLUDED.latitude_min,
                        latitude_max = EXCLUDED.latitude_max,
                        longitude_min = EXCLUDED.longitude_min,
                        longitude_max = EXCLUDED.longitude_max
                    RETURNING id
                    """,
                    (
                        country.name,
                        country.latitude_min,
                        country.latitude_max,
                        country.longitude_min,
                        country.longitude_max,
                    ),
                )
                row = cursor.fetchone()
                if row is None:
                    raise RuntimeError("Country insert did not return an id.")
                country_id = row[0]
            connection.commit()
        return country_id

    def save_airplanes(self, country_id: int, airplanes: list[Airplane]) -> int:
        """Insert airplane snapshots for a single country."""
        if not airplanes:
            return 0

        rows = [airplane.as_db_tuple(country_id) for airplane in airplanes]

        with self.connection_factory.get_connection() as connection:
            with connection.cursor() as cursor:
                execute_batch(
                    cursor,
                    """
                    INSERT INTO airplanes (
                        icao24,
                        callsign,
                        origin_country,
                        country_id,
                        time_position,
                        last_contact,
                        longitude,
                        latitude,
                        baro_altitude,
                        on_ground,
                        velocity,
                        true_track,
                        vertical_rate,
                        geo_altitude,
                        squawk,
                        position_source
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (icao24, last_contact, country_id) DO NOTHING
                    """,
                    rows,
                )
            connection.commit()
        return len(rows)
