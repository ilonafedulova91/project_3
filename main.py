import sys

from dotenv import load_dotenv
from psycopg2 import OperationalError

from src.api_interaction import GetPlanesInfo
from src.config import DBConfig
from src.database import (DatabaseInitializer, DataRepository,
                          PostgresConnectionFactory)
from src.db_manager import DBManager
from src.service import FlightDataService
from src.user_interaction import read_countries, read_keyword


def main() -> None:
    """Run the coursework's cenario end to end."""
    load_dotenv()
    try:
        config = DBConfig.from_env()
        print(
            "Using PostgreSQL target: "
            f"host={config.host}, port={config.port}, dbname={config.dbname}, user={config.user}"
        )
        connection_factory = PostgresConnectionFactory(config)
        service = FlightDataService(
            api_client=GetPlanesInfo(),
            database_initializer=DatabaseInitializer(connection_factory),
            repository=DataRepository(connection_factory),
            db_manager=DBManager(connection_factory),
        )

        countries = read_countries()
        keyword = read_keyword()

        loading_stats = service.load_data(countries)
        report = service.build_report(keyword)
    except (ValueError, OperationalError) as error:
        print(
            "Database connection failed. Check DB_HOST, DB_PORT, DB_NAME, DB_USER, and DB_PASSWORD."
        )
        print(f"Details: {error}")
        sys.exit(1)

    print("Loaded countries and processed airplane rows:")
    for country_name, processed_count in loading_stats:
        print(f"- {country_name}: {processed_count}")

    countries_count, airplanes_count = service.db_manager.get_storage_counts()
    print("\nDatabase row counts after load:")
    print(f"- countries: {countries_count}")
    print(f"- airplanes: {airplanes_count}")

    if countries_count == 0 or airplanes_count == 0:
        print(
            "Warning: the app connected successfully, but the target database still has no data. "
            "Check that pgAdmin is connected to the same DB_HOST/DB_PORT/DB_NAME/user shown above."
        )

    print("\nCountries and airplanes count:")
    for row in report["countries_and_airplanes_count"]:
        print(row)

    print("\nAverage speed:")
    print(report["avg_speed"])

    print("\nAirplanes with higher speed than average:")
    for row in report["airplanes_with_higher_speed"]:
        print(row)

    if "airplanes_with_keyword" in report:
        print("\nAirplanes with keyword:")
        for row in report["airplanes_with_keyword"]:
            print(row)


if __name__ == "__main__":
    main()
