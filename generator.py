# Note for Future Nishant - seeded random data generator for simulation test cases.
# builds initial lists of 20 vehicles partitioned across 4 quadrants and 100 emergency incidents.

import numpy as np
from models import Vehicle, Incident

PRIORITY_WEIGHT = {1: 1, 2: 3, 3: 7}
QUAD_BOUNDS = [
    (0, 50, 0, 50),     # quad 0: sw
    (0, 50, 50, 100),   # quad 1: nw
    (50, 100, 0, 50),   # quad 2: se
    (50, 100, 50, 100)  # quad 3: ne
]

def build_vehicles(rng: np.random.Generator) -> list[Vehicle]:
    vehicles = []
    for xlo, xhi, ylo, yhi in QUAD_BOUNDS:
        for _ in range(5):
            x = float(rng.uniform(xlo, xhi))
            y = float(rng.uniform(ylo, yhi))
            vehicles.append(Vehicle(id=len(vehicles), x=x, y=y, idle=True, completion_time=None))
    return vehicles

def build_incidents(rng: np.random.Generator) -> list[Incident]:
    incidents = []
    for iid in range(100):
        arrival_min = int(rng.integers(0, 60))  # uniform int [0, 59]
        x = float(rng.uniform(0, 100))
        y = float(rng.uniform(0, 100))
        priority = int(rng.choice([1, 2, 3], p=[0.60, 0.30, 0.10]))
        incidents.append(Incident(
            id=iid,
            arrival_min=arrival_min,
            x=x,
            y=y,
            priority=priority,
            weight=PRIORITY_WEIGHT[priority]
        ))
    return incidents
