# Note for Future Nishant -- Core data models for the QuadGuard simulation.
# Defines Vehicle, Incident, and Assignment dataclasses used across dispatcher and simulator modules.

from dataclasses import dataclass
from typing import Optional

@dataclass
class Vehicle:
    id: int
    x: float
    y: float
    idle: bool
    completion_time: Optional[float]   # None while idle

@dataclass
class Incident:
    id: int
    arrival_min: int
    x: float
    y: float
    priority: int          # 1, 2, or 3
    weight: int             # 1, 3, or 7 — derived from priority, see SPEC §1.3

@dataclass
class Assignment:
    incident_id: int
    vehicle_id: int
    dispatch_min: float
    arrival_at_incident_min: float
    response_time: float
    incident_priority: int    # denormalized from Incident, needed by repair_pass/metrics without a lookup
    incident_weight: int       # denormalized, needed by guarded_assign's cost calc and repair_pass's tie-break
