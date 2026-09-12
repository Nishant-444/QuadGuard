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
) -> tuple[list[Assignment], int, list[Incident]]:
    """
    Simulates per-minute emergency dispatcher loop t = 0..120 per SPEC §4.5.
    Returns (all_assignments, outage_minutes, queue).
    """
    by_arrival = defaultdict(list)
    for inc in incidents:
        by_arrival[inc.arrival_min].append(inc)
    for t_key in by_arrival:
        by_arrival[t_key].sort(key=lambda i: i.id)

    queue: list[Incident] = []
    all_assignments: list[Assignment] = []
    outage_minutes = 0

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
        if any(counts.get(q, 0) == 0 for q in range(4)):
            outage_minutes += 1

    return all_assignments, outage_minutes, queue
