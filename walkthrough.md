<!--
Note for Future Nishant -- Demonstration walkthrough guide and verification checklist.
Highlights key visual artifacts, live command instructions, and verification status.
-->

# Walkthrough & Demonstration — QuadGuard

This document details the completed implementation, verification results, and demonstration flow.

---

## 1. Primary Deliverable: Demonstration Chart

As specified in the system design, **[`results/coverage_comparison.png`](file:///home/nishant/Code/QuadGuard/results/coverage_comparison.png)** serves as the official demonstration artifact proving that coverage-guarded assignment prevents system-wide coverage outages.

![Coverage Comparison Chart](file:///home/nishant/Code/QuadGuard/results/coverage_comparison.png)

### Key Demonstration Metrics:

- **Guard ON (QuadGuard)**: **30 outage minutes** across the entire 120-minute simulation.
- **Guard OFF (Standard Hungarian / Greedy)**: **105 outage minutes** (a **71.4% reduction** in outage time when QuadGuard is enabled).
- **Priority-3 Emergencies**: Zero P3 delays caused by the guard — critical emergencies bypass coverage penalties.

---

## 2. Interactive Web Dashboard & Judge Demonstration

In addition to CLI scripts, QuadGuard includes a modern interactive Web Dashboard (`http://localhost:8000`) for live judge demonstrations.

### Starting the Web Server

```bash
python server.py --port 8000
```

Open `http://localhost:8000` in your web browser.

### Key Web Dashboard Features:

- **Side-by-Side Spatial Grid Visualizer**: HTML5 Canvas rendering of the 100x100 spatial grid split into 4 Quadrants (Q0 SW, Q1 NW, Q2 SE, Q3 NE) with live vehicle status dots, incident priority beacons (P1 cyan, P2 orange, P3 pulsing red), and dispatch vector lines.
- **Playback Controls**: Play/Pause, step-by-step minute navigation ($t=0 \dots 120$), and playback speed control (1x, 2x, 5x, 10x).
- **Live Parameter Controls**: Real-time RNG seed input & preset buttons, priority weight ($\lambda$) slider (1.0 to 10.0), and View Mode toggles (Split View, Guard ON, Guard OFF).
- **Outage Progression Chart**: Real-time line graph plotting cumulative coverage outage minutes across the 120-minute timeline.
- **Live Active Queue & Dispatches**: Real-time table of pending emergency incidents sorted by priority.

---

## 3. Live Terminal Command Demonstration

To run the live CLI benchmark, execute:

```bash
python main.py --seed 20260911 --out results/
```

### Expected Live Terminal Output:

```text
Generating environment (seed=20260911)...
Running simulation (guard=ON, lam=5.0)...
  t=0 .. t=120 complete.
Served: 91/100 incidents | Outage minutes: 30 | Weighted response time: 20.3313
Running comparison pass (guard=OFF)...
Wrote results/assignments.csv, results/metrics.json, results/coverage_comparison.png
```

---

## 4. Package Summary

The project includes the following core artifacts:

1. **Source Code**:
   - [`models.py`](file:///home/nishant/Code/QuadGuard/models.py) — Core data representations (`Vehicle`, `Incident`, `Assignment`)
   - [`generator.py`](file:///home/nishant/Code/QuadGuard/generator.py) — Seeded environment generator (PCG64)
   - [`coverage.py`](file:///home/nishant/Code/QuadGuard/coverage.py) — Quadrant mapping and outage calculation
   - [`dispatcher.py`](file:///home/nishant/Code/QuadGuard/dispatcher.py) — Dummy-column Hungarian dispatcher & repair pass
   - [`simulator.py`](file:///home/nishant/Code/QuadGuard/simulator.py) — Per-minute event loop ($t=0 \dots 120$) with trajectory history
   - [`metrics.py`](file:///home/nishant/Code/QuadGuard/metrics.py) — Scoring functions
   - [`io_utils.py`](file:///home/nishant/Code/QuadGuard/io_utils.py) — CSV & JSON exporters
   - [`visualize.py`](file:///home/nishant/Code/QuadGuard/visualize.py) — Comparison plot generator
   - [`main.py`](file:///home/nishant/Code/QuadGuard/main.py) — CLI entry point
   - [`server.py`](file:///home/nishant/Code/QuadGuard/server.py) — FastAPI REST API & web server
   - [`web/index.html`](file:///home/nishant/Code/QuadGuard/web/index.html) — Web application single-page interface
   - [`web/styles.css`](file:///home/nishant/Code/QuadGuard/web/styles.css) — Custom dark theme stylesheet
   - [`web/app.js`](file:///home/nishant/Code/QuadGuard/web/app.js) — Interactive Canvas spatial renderer & simulation playback engine
2. **Documentation & Specifications**:
   - [`docs/SPEC.md`](file:///home/nishant/Code/QuadGuard/docs/SPEC.md) — Technical specification & worked examples
   - [`docs/ARCHITECTURE.md`](file:///home/nishant/Code/QuadGuard/docs/ARCHITECTURE.md) — System layout & function signatures
   - [`docs/TASKS.md`](file:///home/nishant/Code/QuadGuard/docs/TASKS.md) — Time-boxed build checklist
   - [`docs/walkthrough.md`](file:///home/nishant/Code/QuadGuard/docs/walkthrough.md) — Demonstration walkthrough guide
   - [`WRITEUP.md`](file:///home/nishant/Code/QuadGuard/WRITEUP.md) — Technical writeup & benchmark analysis
3. **Environment**: [`requirements.txt`](file:///home/nishant/Code/QuadGuard/requirements.txt) — Core dependencies.
4. **Runnable Commands**:
   - Web Server: `python server.py --port 8000`
   - CLI Runner: `python main.py --seed 20260911 --out results/`
5. **Generated Output Artifacts**:
   - [`results/assignments.csv`](file:///home/nishant/Code/QuadGuard/results/assignments.csv) — Detailed dispatch log per incident
   - [`results/metrics.json`](file:///home/nishant/Code/QuadGuard/results/metrics.json) — Quantitative evaluation metrics
   - [`results/coverage_comparison.png`](file:///home/nishant/Code/QuadGuard/results/coverage_comparison.png) — Side-by-side comparison chart

---

## 5. Verification & Correctness Checklist

- [x] **Worked Example ([`docs/SPEC.md`](file:///home/nishant/Code/QuadGuard/docs/SPEC.md#L190-L212))**: Passed matching `{V2 -> I0, V0 -> I1}` with V1 idle.
- [x] **Repair Pass**: Passed multi-vehicle simultaneous departure test, leaving $\ge 1$ vehicle in idle coverage.
- [x] **$\lambda$ Sweep Calibration**: Selected $\lambda = 5.0$ as the optimal tradeoff.
- [x] **Coverage Outage Hard Assertion**: Verified `outage_with_guard <= outage_without_guard` programmatically.
- [x] **Web Frontend & API**: Interactive FastAPI server & HTML5 Canvas renderer tested and running on port 8000.
