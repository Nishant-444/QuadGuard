# Note for Future Nishant -- Evaluation and scoring computer for simulation runs.
# Calculates weighted response times, P3 incident statistics, total outages, and runtime metrics.

from models import Assignment, Incident

def compute(assignments: list[Assignment], outage_minutes: int,
            still_queued: list[Incident], runtime_sec: float) -> dict:
    if assignments:
        total_weight = sum(a.incident_weight for a in assignments)
        weighted_resp = sum(a.incident_weight * a.response_time for a in assignments) / total_weight if total_weight > 0 else 0.0
        p3_resps = [a.response_time for a in assignments if a.incident_priority == 3]
        p3_resp_mean = sum(p3_resps) / len(p3_resps) if p3_resps else 0.0
    else:
        weighted_resp = 0.0
        p3_resp_mean = 0.0

    return {
        "weighted_response_time": round(float(weighted_resp), 4),
        "coverage_outage_minutes": int(outage_minutes),
        "p3_response_time": round(float(p3_resp_mean), 4),
        "runtime_sec": round(float(runtime_sec), 4),
        "total_served": len(assignments),
        "total_queued_at_end": len(still_queued)
    }
