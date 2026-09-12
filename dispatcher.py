# Note for Future Nishant - optimization dispatcher logic using scipy linear_sum_assignment.
# solves hungarian matching with dummy columns, coverage guard penalties, and repair pass filtering.

import math
import numpy as np
from collections import Counter, defaultdict
from scipy.optimize import linear_sum_assignment
from models import Vehicle, Incident, Assignment
from coverage import quadrant

DUMMY_COST = 200.0  # > any realistic real cost (max ≈140.4)
GUARD_PENALTY = 1000.0  # > DUMMY_COST + any realistic real cost


def euclidean(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def guarded_assign(
    idle_vehicles: list[Vehicle],
    queue: list[Incident],
    t: int,
    guard_enabled: bool,
    lam: float,
) -> list[Assignment]:
    V, I = len(idle_vehicles), len(queue)
    if V == 0 or I == 0:
        return []

    quad_counts = Counter(quadrant(v.x, v.y) for v in idle_vehicles)
    cost = np.full((V, V + I), DUMMY_COST, dtype=float)  # first V cols = dummy block

    for vi, v in enumerate(idle_vehicles):
        v_quad = quadrant(v.x, v.y)
        for ii, inc in enumerate(queue):
            c = euclidean(v.x, v.y, inc.x, inc.y) - lam * inc.weight
            if guard_enabled and inc.priority != 3 and quad_counts[v_quad] == 1:
                c += GUARD_PENALTY
            cost[vi, V + ii] = c

    rows, cols = linear_sum_assignment(cost)
    assignments = []
    for r, c in zip(rows, cols):
        if c >= V:
            v = idle_vehicles[r]
            inc = queue[c - V]
            dist = euclidean(v.x, v.y, inc.x, inc.y)
            assignments.append(
                Assignment(
                    incident_id=inc.id,
                    vehicle_id=v.id,
                    dispatch_min=float(t),
                    arrival_at_incident_min=float(t + dist),
                    response_time=dist,
                    incident_priority=inc.priority,
                    incident_weight=inc.weight,
                )
            )
    return assignments


def repair_pass(
    assignments: list[Assignment], idle_before: list[Vehicle]
) -> list[Assignment]:
    pos = {v.id: (v.x, v.y) for v in idle_before}
    by_quad = defaultdict(list)
    for a in assignments:
        if a.incident_priority != 3:
            by_quad[quadrant(*pos[a.vehicle_id])].append(a)
    kept = list(assignments)
    for q, qa in by_quad.items():
        quad_idle_total = sum(1 for v in idle_before if quadrant(v.x, v.y) == q)
        if (
            len(qa) == quad_idle_total and quad_idle_total > 0
        ):  # this batch would empty quadrant q
            worst = min(
                qa, key=lambda a: a.incident_weight
            )  # give back the least valuable one
            kept.remove(worst)
    return kept
