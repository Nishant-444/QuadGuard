# Note for Future Nishant - i/o utility module for exporting simulation output.
# handles saving incident assignment logs to CSV and aggregate summary statistics to JSON.

import json
import csv
import os
from models import Assignment


def write_csv(assignments: list[Assignment], path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    fieldnames = [
        "incident_id",
        "priority",
        "arrival_min",
        "vehicle_id",
        "dispatch_min",
        "arrival_at_incident_min",
        "response_time",
    ]

    # arrival_min = arrival_at_incident_min - response_time.
    with open(path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for a in assignments:
            arrival_min = round(a.arrival_at_incident_min - a.response_time)
            writer.writerow(
                {
                    "incident_id": a.incident_id,
                    "priority": a.incident_priority,
                    "arrival_min": int(arrival_min),
                    "vehicle_id": a.vehicle_id,
                    "dispatch_min": round(a.dispatch_min, 4),
                    "arrival_at_incident_min": round(a.arrival_at_incident_min, 4),
                    "response_time": round(a.response_time, 4),
                }
            )


def write_json(metrics: dict, path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, mode="w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
