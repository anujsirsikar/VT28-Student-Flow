import csv
from datetime import datetime, date


def load_holiday_ranges(csv_path):
    holiday_ranges = []

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            start = datetime.strptime(row["start_date"], "%Y-%m-%d").date()
            end = datetime.strptime(row["end_date"], "%Y-%m-%d").date()

            holiday_ranges.append({
                "name": row["name"],
                "start": start,
                "end": end
            })

    return holiday_ranges


ranges = load_holiday_ranges("holidays.csv")

print(ranges)