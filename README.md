# QuadGuard

Online emergency-vehicle dispatcher that preserves quadrant coverage while minimizing priority-weighted response time.

## What it does

- Simulates 20 vehicles responding to 100 incidents on a 100×100 grid, minute-by-minute, causally — no future information used (SPEC.md §3).
- Assigns idle vehicles to queued incidents each minute via a guarded Hungarian match (SPEC.md §4): optimal cost-matching that's blocked from emptying any quadrant of idle vehicles unless the incident is priority-3.
- Outputs per-incident results, aggregate metrics, and a chart proving the guard actually reduces coverage outages versus not having one.

## Requirements

Python ≥ 3.10 (uses `list[X]` generic type hints natively). See `requirements.txt`.

## Quick Start

```bash
pip install -r requirements.txt
python main.py --seed 20260911 --out results/
```

## All CLI flags

| Flag         | Default                                 | Meaning                                                                 |
| ------------ | --------------------------------------- | ----------------------------------------------------------------------- |
| `--seed`     | `20260911`                              | RNG seed for the dev instance                                           |
| `--lam`      | _(λ sweep winner, see TASKS.md step 7)_ | priority-bonus weight in the assignment cost — SPEC.md §4.2             |
| `--no-guard` | off                                     | disable the coverage guard on the primary run, for debugging/comparison |
| `--out`      | `results/`                              | output directory, created if missing                                    |

## Expected console output

```
Generating environment (seed=20260911)...
Running simulation (guard=ON, lam=5.0)...
  t=0 .. t=120 complete.
Served: 100/100 incidents | Outage minutes: <N> | Weighted response time: <X.XX>
Running comparison pass (guard=OFF)...
Wrote results/assignments.csv, results/metrics.json, results/coverage_comparison.png
```

## Output

- `results/assignments.csv` — one row per served incident (schema: SPEC.md §8)
- `results/metrics.json` — aggregate scores (schema: SPEC.md §8)
- `results/coverage_comparison.png` — guard-on vs guard-off outage minutes

## If something's off

- **Outputs differ between runs with the same seed** → an unordered structure (a bare `set` or `dict` iteration) leaked into a draw or the queue sort; every step must be list-ordered and the RNG draw order must exactly match SPEC.md §1.
- **Guard seems to do nothing** → check the `DUMMY_COST` / `GUARD_PENALTY` ordering (SPEC.md §4.3), and confirm `quad_counts` is built from the _pre-assignment_ idle-vehicle snapshot, not a post-assignment one.
- **Comparison chart shows almost no difference** → check ARCHITECTURE.md's "why regenerate instead of reuse" note — a common bug is feeding the guard-off run the already-mutated vehicle objects from the guard-on run instead of a fresh instance.
- **Weighted response time worse than expected** → confirm the λ sweep (TASKS.md step 7) actually got wired into `main.py`'s default, not left at a placeholder.
- **Doesn't match SPEC §7's worked example** → this is the fastest way to catch a cost-matrix bug; debug against it before trusting a full 120-minute run.

## Docs

- `SPEC.md` — full functional/technical spec: rules, algorithm, exact constants, worked example, output schema
- `ARCHITECTURE.md` — module layout, dataclasses, exact function signatures, build sequence
- `TASKS.md` — ordered, time-boxed build checklist with verification criteria for every step
