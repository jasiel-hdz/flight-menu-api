from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.flights.models import Flight
from core.flights.repositories import FlightRepository
from core.menus import models as _menus_models  # noqa: F401
from database import session_factory

SEED_FLIGHTS = (
    {"flight_number": "AM500", "departure_airport": "MEX", "arrival_airport": "CUN", "carrier": "AM"},
    {"flight_number": "AM412", "departure_airport": "MEX", "arrival_airport": "GDL", "carrier": "AM"},
    {"flight_number": "VB3207", "departure_airport": "MTY", "arrival_airport": "CUN", "carrier": "VB"},
    {"flight_number": "Y4550", "departure_airport": "MEX", "arrival_airport": "TIJ", "carrier": "Y4"},
)


def main() -> None:
    created = 0
    skipped = 0

    with session_factory() as db:
        repo = FlightRepository(db)
        for row in SEED_FLIGHTS:
            existing = repo.find_by_number_and_route(
                row["flight_number"],
                row["departure_airport"],
                row["arrival_airport"],
            )
            if existing is not None:
                skipped += 1
                continue
            db.add(Flight(**row))
            created += 1
        db.commit()

    print(f"flights seed done: created={created} skipped={skipped}")


if __name__ == "__main__":
    main()
