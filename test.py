import datetime
from datetime import date, timedelta

holiday_ranges = [
        
        # These change every fiscal year. Maybe this can also be info that gets read in from a file

        # Long weekends and federal holidays
        (date(2025,11,27),date(2025,11,30)),  # Thanksgiving
        (date(2025, 12, 25), date(2025, 12, 28)),  # Christmas
        (date(2025, 1, 1),  date(2025, 1, 4)),     # New Years
        (date(2025, 7, 3),  date(2025, 7, 6)),     # July 4th
        (date(2025, 10, 11), date(2025, 10, 13)),  # Columbus Day
        (date(2025, 1, 17), date(2025, 1, 19)),    # MLK Day
        (date(2025, 2, 14),  date(2025, 2, 16)),   # President's Day
        (date(2025, 5, 23),  date(2025, 5, 25)),   # Memorial Day
        (date(2025, 6, 19),  date(2025, 6, 21)),   # Juneteenth
        (date(2025, 9, 5),  date(2025, 9, 7)),     # Labor Day
        (date(2025, 11, 11), date(2025, 11, 11)),  # Veterans Day (single day)
        # Holiday leave periods (every year)
        (date(2025, 12, 15), date(2025, 12, 28)),  # Holiday leave 1
        # Holiday leave 2 spans across years → handle separately below
        (date(2025, 12, 29), date(2026, 1, 11)), # holiday leave 2
    ]

test_date = date(2025,12,31)

for start_date, end_date in holiday_ranges:
    if (start_date <= test_date <= end_date):
        print(False)

print(True)