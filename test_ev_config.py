
from ev_config import (
    BUSINESS_NAME,
    SAMPLE_STATIONS,
    TICKET_CATEGORIES,
    SUPPORT_TEAMS,
)

print("Business:", BUSINESS_NAME)
print("Total sample stations:", len(SAMPLE_STATIONS))
print("Ticket categories:", len(TICKET_CATEGORIES))
print("Support teams:", len(SUPPORT_TEAMS))

print("\nAvailable stations:")
for station in SAMPLE_STATIONS:
    print(
        station["station_id"],
        "-",
        station["station_name"],
        "-",
        station["city"],
    )
