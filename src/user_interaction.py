from src.config import DEFAULT_COUNTRIES


def read_countries() -> list[str]:
    """Read a country list from the console or use the default list of ten."""
    answer = (
        input("Use default countries list (10 countries)? Enter y or n: ")
        .strip()
        .lower()
    )
    if answer in {"", "y", "yes"}:
        return DEFAULT_COUNTRIES.copy()

    countries: list[str] = []
    print("Enter at least 4 countries. Press Enter on an empty line to finish.")

    while True:
        country = input("Country name: ").strip()
        if not country:
            if len(countries) >= 4:
                return countries
            print("You need to enter at least 4 countries.")
            continue
        countries.append(country)


def read_keyword() -> str:
    """Read an optional callsign filter keyword."""
    return input(
        "Enter callsign keyword for search in DBManager (or press Enter to skip): "
    ).strip()
