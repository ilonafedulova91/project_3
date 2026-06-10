from dataclasses import dataclass
from getpass import getpass
from os import getenv

DEFAULT_COUNTRIES = [
    "Romania",
    "Germany",
    "France",
    "Spain",
    "Italy",
    "Poland",
    "Ukraine",
    "Turkey",
    "Greece",
    "United Kingdom",
]


@dataclass(slots=True)
class DBConfig:
    """Database connection settings loaded from environment variables."""

    host: str
    port: int
    dbname: str
    user: str
    password: str

    @classmethod
    def from_env(cls) -> "DBConfig":
        """Read PostgreSQL settings from environment variables or prompt for them."""
        host = getenv("DB_HOST") or "localhost"
        port = int(getenv("DB_PORT") or "5432")
        dbname = getenv("DB_NAME")
        user = getenv("DB_USER")
        password = getenv("DB_PASSWORD")

        if not dbname:
            dbname = input("Enter PostgreSQL database name: ").strip()
        if not user:
            user = input("Enter PostgreSQL user: ").strip()
        if password is None:
            password = getpass("Enter PostgreSQL password: ")

        if not dbname or not user:
            raise ValueError("Database name and user cannot be empty.")

        return cls(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
        )
