# Note for Future Nishant - FastAPI server providing simulation API endpoints and serving the web frontend.
import argparse
import time
import numpy as np
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from generator import build_vehicles, build_incidents
from simulator import simulate
from metrics import compute

app = FastAPI(title="QuadGuard API", description="Online Emergency Fleet Dispatcher API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimulationRequest(BaseModel):
    seed: int = 20260911
    lam: float = 5.0


@app.post("/api/run-simulation")
def run_simulation(req: SimulationRequest):
    seed = req.seed
    lam = req.lam

    # 1. Guard ON run
    rng_on = np.random.Generator(np.random.PCG64(seed))
    vehicles_on = build_vehicles(rng_on)
    incidents_on = build_incidents(rng_on)

    t0 = time.perf_counter()
    assignments_on, outages_on, queue_on, history_on = simulate(
        vehicles_on, incidents_on, guard_enabled=True, lam=lam, record_history=True
    )
    t1 = time.perf_counter()
    metrics_on = compute(assignments_on, outages_on, queue_on, t1 - t0)

    # 2. Guard OFF run
    rng_off = np.random.Generator(np.random.PCG64(seed))
    vehicles_off = build_vehicles(rng_off)
    incidents_off = build_incidents(rng_off)

    t2 = time.perf_counter()
    assignments_off, outages_off, queue_off, history_off = simulate(
        vehicles_off, incidents_off, guard_enabled=False, lam=lam, record_history=True
    )
    t3 = time.perf_counter()
    metrics_off = compute(assignments_off, outages_off, queue_off, t3 - t2)

    return {
        "seed": seed,
        "lam": lam,
        "total_incidents": len(incidents_on),
        "guard_on": {
            "metrics": metrics_on,
            "history": history_on,
        },
        "guard_off": {
            "metrics": metrics_off,
            "history": history_off,
        },
    }


# Mount static files for frontend app
app.mount("/", StaticFiles(directory="web", html=True), name="static")

if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser(description="QuadGuard Web Server")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address")
    args = parser.parse_args()

    print(f"Starting QuadGuard Server on http://{args.host}:{args.port}...")
    uvicorn.run(app, host=args.host, port=args.port)
