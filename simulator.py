# Note for Future Nishant -- Discrete minute-by-minute simulation engine (t = 0..120).
# Orchestrates vehicle availability updates, incident reveals, dispatching, and outage monitoring.

from collections import defaultdict, Counter
from models import Vehicle, Incident, Assignment
from coverage import quadrant
from dispatcher import guarded_assign, repair_pass


def simulate(
    vehicles: list[Vehicle],
    incidents: list[Incident],
    guard_enabled: bool = True,
    lam: float = 5.0,
    record_history: bool = False,
) -> tuple:
    """
    Simulates per-minute emergency dispatcher loop t = 0..120 per SPEC §4.5.
    Returns (all_assignments, outage_minutes, queue) or (all_assignments, outage_minutes, queue, history).
    """
    by_arrival = defaultdict(list)
    for inc in incidents:
        by_arrival[inc.arrival_min].append(inc)
    for t_key in by_arrival:
        by_arrival[t_key].sort(key=lambda i: i.id)

    queue: list[Incident] = []
    all_assignments: list[Assignment] = []
    outage_minutes = 0
    history = []

    vehicle_by_id = {v.id: v for v in vehicles}
    incident_by_id = {i.id: i for i in incidents}

    for t in range(121):
        # 1 complete
        for v in vehicles:
            if not v.idle and v.completion_time is not None and v.completion_time <= t:
                v.idle = True
                v.completion_time = None

        # 2 reveal
        queue.extend(by_arrival.get(t, []))

        # 3 sort the queue
        queue.sort(key=lambda i: (-i.priority, i.arrival_min, i.id))

        # 4 assign
        idle_before = [v for v in vehicles if v.idle]
        new_assignments = []
        if idle_before and queue:
            new_assignments = guarded_assign(idle_before, queue, t, guard_enabled, lam)
            if guard_enabled:
                new_assignments = repair_pass(new_assignments, idle_before)
            for a in new_assignments:
                v = vehicle_by_id[a.vehicle_id]
                v.idle = False
                v.x, v.y = (
                    incident_by_id[a.incident_id].x,
                    incident_by_id[a.incident_id].y,
                )
                v.completion_time = a.arrival_at_incident_min + 8
            served_ids = {a.incident_id for a in new_assignments}
            queue = [i for i in queue if i.id not in served_ids]
            all_assignments.extend(new_assignments)

        # 5 coverage check
        counts = Counter(quadrant(v.x, v.y) for v in vehicles if v.idle)
        is_outage = any(counts.get(q, 0) == 0 for q in range(4))
        if is_outage:
            outage_minutes += 1

        if record_history:
            frame = {
                "t": t,
                "vehicles": [
                    {
                        "id": v.id,
                        "x": v.x,
                        "y": v.y,
                        "idle": v.idle,
                        "completion_time": v.completion_time,
                        "quadrant": quadrant(v.x, v.y),
                    }
                    for v in vehicles
                ],
                "queue": [
                    {
                        "id": i.id,
                        "arrival_min": i.arrival_min,
                        "x": i.x,
                        "y": i.y,
                        "priority": i.priority,
                        "weight": i.weight,
                    }
                    for i in queue
                ],
                "dispatches": [
                    {
                        "incident_id": a.incident_id,
                        "vehicle_id": a.vehicle_id,
                        "dispatch_min": a.dispatch_min,
                        "arrival_at_incident_min": a.arrival_at_incident_min,
                        "response_time": a.response_time,
                        "incident_priority": a.incident_priority,
                        "incident_weight": a.incident_weight,
                        "target_x": incident_by_id[a.incident_id].x,
                        "target_y": incident_by_id[a.incident_id].y,
                    }
                    for a in new_assignments
                ],
                "quadrant_counts": {q: counts.get(q, 0) for q in range(4)},
                "outage_quadrants": [q for q in range(4) if counts.get(q, 0) == 0],
                "is_outage": is_outage,
                "cumulative_outage_minutes": outage_minutes,
            }
            history.append(frame)

    if record_history:
        return all_assignments, outage_minutes, queue, history
    return all_assignments, outage_minutes, queue
