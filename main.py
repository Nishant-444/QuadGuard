# Note for Future Nishant -- CLI entry point for running QuadGuard simulations and comparison benchmarks.
# Parses arguments, runs primary and benchmark simulation passes, and outputs CSV/JSON/PNG results.

import argparse
import os
import time
import numpy as np

from generator import build_vehicles, build_incidents
from simulator import simulate
from metrics import compute
from io_utils import write_csv, write_json
from visualize import plot_guard_comparison


def main():
    parser = argparse.ArgumentParser(description="QuadGuard Emergency Fleet Dispatcher")
    parser.add_argument(
        "--seed", type=int, default=20260911, help="RNG seed for environment generation"
    )
    parser.add_argument(
        "--lam", type=float, default=5.0, help="Priority bonus weight in cost matrix"
    )
    parser.add_argument(
        "--no-guard", action="store_true", help="Disable coverage guard on primary run"
    )
    parser.add_argument(
        "--out", type=str, default="results/", help="Output directory path"
    )

    args = parser.parse_args()
    os.makedirs(args.out, exist_ok=True)

    print(f"Generating environment (seed={args.seed})...")

    # primary run
    rng = np.random.Generator(np.random.PCG64(args.seed))
    vehicles = build_vehicles(rng)
    incidents = build_incidents(rng)

    primary_guard_enabled = not args.no_guard
    guard_str = "ON" if primary_guard_enabled else "OFF"
    print(f"Running simulation (guard={guard_str}, lam={args.lam})...")

    t0 = time.perf_counter()
    assignments, outages_primary, queue = simulate(
        vehicles, incidents, guard_enabled=primary_guard_enabled, lam=args.lam
    )
    t1 = time.perf_counter()
    runtime_sec = t1 - t0

    metrics_dict = compute(assignments, outages_primary, queue, runtime_sec)
    print(f"  t=0 .. t=120 complete.")
    print(
        f"Served: {metrics_dict['total_served']}/{len(incidents)} incidents | Outage minutes: {metrics_dict['coverage_outage_minutes']} | Weighted response time: {metrics_dict['weighted_response_time']}"
    )

    csv_path = os.path.join(args.out, "assignments.csv")
    json_path = os.path.join(args.out, "metrics.json")
    write_csv(assignments, csv_path)
    write_json(metrics_dict, json_path)

    # comparison run (always run guard OFF with a ''FRESH'' generator instance)
    print("Running comparison pass (guard=OFF)...")
    rng_comp = np.random.Generator(np.random.PCG64(args.seed))
    vehicles_comp = build_vehicles(rng_comp)
    incidents_comp = build_incidents(rng_comp)

    _, outages_without_guard, _ = simulate(
        vehicles_comp, incidents_comp, guard_enabled=False, lam=args.lam
    )

    outage_with_guard = (
        outages_primary if primary_guard_enabled else outages_without_guard
    )
    if primary_guard_enabled:
        # hard assertion as specified in instructions
        assert (
            outage_with_guard <= outages_without_guard
        ), f"Guard failed to preserve coverage: Guard ON ({outage_with_guard}) > Guard OFF ({outages_without_guard})"

    png_path = os.path.join(args.out, "coverage_comparison.png")
    plot_guard_comparison(outage_with_guard, outages_without_guard, png_path)

    print(f"Wrote {csv_path}, {json_path}, {png_path}")


if __name__ == "__main__":
    main()
