# QuadGuard - Online Emergency Fleet Dispatcher with Coverage Preservation

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![NumPy](https://img.shields.io/badge/NumPy-2.5+-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org/)
[![SciPy](https://img.shields.io/badge/SciPy-1.18+-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)](https://scipy.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-11557c?style=for-the-badge)](https://matplotlib.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen?style=for-the-badge)](#)

**Version:** 1.0.0  
**Status:** Validated & Benchmarked  
**Core Domain:** Online Bipartite Matching, Emergency Fleet Optimization, Spatial Coverage Protection  
**Tech Stack:** Python 3.10+, NumPy, SciPy (`linear_sum_assignment`), Matplotlib, Pandas

---

## Project Overview

**QuadGuard** is an online emergency-vehicle dispatcher that preserves territorial quadrant coverage while minimizing priority-weighted response time across a spatial environment.

In emergency dispatching, optimizing purely for immediate response time frequently depletes local fleet availability in specific regions. When a cluster of non-critical incidents occurs in a single quadrant, unconstrained dispatchers assign all local units, leaving that area vulnerable to severe delays when subsequent life-threatening emergencies arrive.

QuadGuard solves this online bipartite matching problem by embedding **spatial coverage preservation directly into the bipartite matching cost matrix** using dummy vehicle columns, penalty guards, and an automated repair pass.

### Key Benchmark Highlights

- **74.8% Reduction in Outage Duration:** Reduces total system coverage outage minutes from **119 minutes down to 30 minutes** over a 120-minute simulation.
- **17.8% Faster Priority-3 Response:** Preserves idle units near potential emergency sites, reducing high-priority (P3) response time from **35.81 min down to 29.45 min**.
- **Real-Time Sub-Millisecond Speed:** Solves guarded bipartite matching in **< 1 ms per minute step** (~0.01s for the full 120-minute simulation).
- **Strict Causality:** Operates minute-by-minute using only currently revealed incidents and active vehicle states—never using future information.

---

## System Architecture & Dispatch Orchestration

```
Incident Arrival Queue ──► Per-Minute Loop (t = 0..120) ──► Guarded Bipartite Matching ──► Repair Pass ──► Fleet & Outage Metrics
```

### Request & Simulation Flow

```
1. COMPLETE: Update returning vehicles (completion_time <= t) to idle status.
2. REVEAL: Add newly arrived incidents (arrival_min == t) to active queue.
3. SORT: Order queue by (-priority, arrival_min, incident_id).
4. ASSIGN: Construct V × (V + I) cost matrix with DUMMY_COST & GUARD_PENALTY.
           Solve via scipy linear_sum_assignment (Hungarian method).
           Execute repair_pass for multi-vehicle simultaneous departure edge cases.
5. COVERAGE: Evaluate idle fleet counts across all 4 spatial quadrants.
             If any quadrant has 0 idle vehicles -> outage_minutes += 1.
```

---

## Core Technology Stack

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-2.5+-013243?style=flat-square&logo=numpy&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-1.18+-8CAAE6?style=flat-square&logo=scipy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.10+-11557c?style=flat-square)
![Pandas](https://img.shields.io/badge/Pandas-2.2+-150458?style=flat-square&logo=pandas&logoColor=white)

| Layer                   | Technology              | Version    | Purpose                                                     |
| ----------------------- | ----------------------- | ---------- | ----------------------------------------------------------- |
| **Language**            | Python                  | $\ge$ 3.10 | Core execution & native generic typing (`list[X]`)          |
| **Optimization Solver** | SciPy                   | $\ge$ 1.18 | `scipy.optimize.linear_sum_assignment` (Hungarian matching) |
| **RNG & Simulation**    | NumPy                   | $\ge$ 2.5  | Bit-generator seed consistency (`PCG64`)                    |
| **Data Export**         | Built-in `csv` / `json` | Standard   | Standardized results format (SPEC §8)                       |
| **Data Analysis**       | Pandas                  | $\ge$ 2.2  | Metric aggregation and output processing                    |
| **Visualization**       | Matplotlib              | $\ge$ 3.10 | Guard-ON vs Guard-OFF comparison chart generation           |

---

## Key Engineering Decisions & Trade-offs

### 1. Why Classical Optimization (Hungarian Algorithm) over AI / ML?

- **Guaranteed Mathematical Optimality**: Hungarian matching ($O(V^3)$) guarantees the exact globally optimal cost assignment for active units at every minute step.
- **Hard Safety Guarantees**: Emergency response rules require absolute non-negotiable compliance. QuadGuard guarantees that no quadrant is emptied for non-critical incidents, whereas AI/RL models are probabilistic black boxes prone to edge-case constraint violations.
- **Zero Training Data / Cold Start**: Operates immediately on any city grid without historical training, neural network tuning, or offline model pre-training.
- **Auditability**: Every assignment decision is transparently verifiable via $c_{ij} = d_{ij} - \lambda \cdot w_i + \text{Penalty}$.

### 2. Guarded Bipartite Cost Matrix ($V \times (V + I)$)

Standard Hungarian matching requires assigned pairs for all rows. To make vehicle dispatch optional (allowing vehicles to stay idle when dispatching penalizes system coverage), QuadGuard creates a $V \times (V + I)$ matrix featuring $V$ dummy columns:

$$\text{Cost Matrix Structure} = \begin{bmatrix} \text{Dummy Block } (V \times V) & \vert & \text{Real Incident Block } (V \times I) \end{bmatrix}$$

- **`DUMMY_COST = 200`**: Priced above any realistic distance cost (max grid distance $\approx 140.4$), ensuring vehicles prefer serving real incidents by default unless penalized.
- **`GUARD_PENALTY = 1000`**: Added to non-P3 incident costs for any vehicle that is the **last remaining idle vehicle** in its quadrant (`quad_counts == 1`). This reliably forces the solver to assign the vehicle to a dummy column (stay idle).
- **Priority-3 Override**: Priority-3 emergencies ($w=7$) bypass `GUARD_PENALTY`, guaranteeing immediate life-safety dispatch regardless of coverage state.

### 3. Repair Pass for Simultaneous Departures

When a quadrant has 2+ idle units, single-vehicle checks (`quad_counts == 1`) won't trigger for individual units. If the bipartite matching assigns _all_ idle units in that quadrant simultaneously in the same minute step, `repair_pass` identifies the batch departure and drops the lowest-priority assignment, keeping at least 1 vehicle in idle coverage.

---

## Parameter Calibration ($\lambda$ Sweep)

The priority bonus parameter $\lambda$ balances travel distance against incident weight. A parameter sweep was executed over $\lambda \in \{1.0, 3.0, 5.0, 10.0\}$ on the development instance (`seed = 20260911`):

|     $\lambda$      | Weighted Response Time (min) | Coverage Outage Minutes | P3 Response Time (min) | Incidents Served |
| :----------------: | :--------------------------: | :---------------------: | :--------------------: | :--------------: |
|      **1.0**       |           21.5835            |           34            |        31.9897         |     94 / 100     |
|      **3.0**       |           19.8853            |           34            |        31.2519         |     95 / 100     |
| **5.0 (Selected)** |         **20.3313**          |         **30**          |      **29.4511**       |   **91 / 100**   |
|      **10.0**      |           20.5487            |           30            |        29.7263         |     89 / 100     |

### Selection Rationale:

- **Baseline Outage Target**: $\lambda = 5.0$ minimizes coverage outage minutes to **30 minutes**.
- **P3 Efficiency**: $\lambda = 5.0$ achieves the fastest Priority-3 response time (**29.45 min**).
- **System Default**: Hard-coded as the default parameter across the system.

---

## Experimental Benchmark Results

Comparing QuadGuard (Guard ON, $\lambda = 5.0$) against an un-guarded baseline dispatcher (Guard OFF, $\lambda = 5.0$) on identical environment instances:

| Metric                      | Guard ON (QuadGuard) | Guard OFF (Baseline) | Performance Impact             |
| --------------------------- | :------------------: | :------------------: | ------------------------------ |
| **Coverage Outage Minutes** |      **30 min**      |     **119 min**      | **74.8% Reduction in Outages** |
| **Total Incidents Served**  |       91 / 100       |       98 / 100       | High Coverage Preserved        |
| **P3 Response Time**        |    **29.45 min**     |      35.81 min       | **17.8% Faster P3 Response**   |
| **Simulation Runtime**      |      ~0.01 sec       |      ~0.01 sec       | Real-Time Sub-Millisecond      |

---

## Project Directory Structure

```
QuadGuard/
├── main.py            # CLI entry point, orchestration & comparative benchmark runner
├── models.py          # Shared dataclasses (Vehicle, Incident, Assignment)
├── generator.py       # PCG64-seeded vehicle & incident distribution generator
├── simulator.py       # Per-minute causal simulation loop (SPEC §4.5)
├── dispatcher.py      # Bipartite guarded assignment solver & repair pass (SPEC §4.2, §4.4)
├── coverage.py        # Spatial quadrant evaluation & outage tracker (SPEC §5)
├── metrics.py         # Response time & system scoring computer (SPEC §6)
├── io_utils.py        # Standardized CSV & JSON export writers (SPEC §8)
├── visualize.py       # Guard-ON vs Guard-OFF outage comparison chart generator
├── requirements.txt   # Core Python library dependencies
├── WRITEUP.md         # Technical writeup and benchmark analysis
├── docs/
│   ├── SPEC.md        # Technical specification, math formulations & worked examples
│   ├── ARCHITECTURE.md# Module layout, function signatures & execution sequence
│   ├── TASKS.md       # Development step checklist & verification criteria
│   ├── walkthrough.md # Walkthrough & demonstration guide
│   ├── requirements.txt# Documentation dependencies
│   └── Applied_AI_Intelligent_Systems.pdf # Project reference document
└── results/           # Runtime output directory (CSV, JSON, PNG)
```

---

## Quick Start & CLI Reference

### 1. Installation

Ensure Python $\ge$ 3.10 is installed.

```bash
git clone https://github.com/Nishant-444/QuadGuard.git
cd QuadGuard
pip install -r requirements.txt
```

### 2. Run Simulation

Run the default simulation pass with default seed (`20260911`) and priority weight ($\lambda = 5.0$):

```bash
python main.py --seed 20260911 --out results/
```

### 3. Command Line Options

| Flag         | Default    | Type    | Description                                                      |
| ------------ | ---------- | ------- | ---------------------------------------------------------------- |
| `--seed`     | `20260911` | `int`   | RNG seed for PCG64 reproducible environment generation           |
| `--lam`      | `5.0`      | `float` | Priority bonus weight multiplier ($\lambda$) in cost calculation |
| `--no-guard` | `off`      | `flag`  | Disables coverage guard on the primary run (for comparison)      |
| `--out`      | `results/` | `str`   | Destination directory for output metrics, CSV logs, and chart    |

### 4. Sample Console Output

```
Generating environment (seed=20260911)...
Running simulation (guard=ON, lam=5.0)...
  t=0 .. t=120 complete.
Served: 91/100 incidents | Outage minutes: 30 | Weighted response time: 20.33
Running comparison pass (guard=OFF)...
Wrote results/assignments.csv, results/metrics.json, results/coverage_comparison.png
```

---

## Output Artifacts

Running the simulation generates the following artifacts in the specified `--out` directory (default `results/`):

1. **[`results/assignments.csv`](file:///home/nishant/Code/QuadGuard/results/assignments.csv)**: Record of all dispatched incidents (schema: `incident_id, priority, arrival_min, vehicle_id, dispatch_min, arrival_at_incident_min, response_time`).
2. **[`results/metrics.json`](file:///home/nishant/Code/QuadGuard/results/metrics.json)**: Aggregate scoring summary containing `weighted_response_time`, `coverage_outage_minutes`, `p3_response_time`, `runtime_sec`, `total_served`, and `total_queued_at_end`.
3. **[`results/coverage_comparison.png`](file:///home/nishant/Code/QuadGuard/results/coverage_comparison.png)**: Side-by-side comparative bar chart demonstrating total outage minutes with Guard ON vs. Guard OFF.

---

## Verification & Unit Testing

QuadGuard includes a hand-verifiable worked example test case in [`docs/SPEC.md`](file:///home/nishant/Code/QuadGuard/docs/SPEC.md#L190-L212):

- **Setup**: 3 vehicles ($V_0=(10,10)$, $V_2=(12,12)$ in SW; $V_1=(60,60)$ alone in NE). 2 priority-1 incidents ($I_0=(15,15)$, $I_1=(5,5)$) revealed at $t=0$. $\lambda=5$.
- **Expected Matching**: $V_2 \rightarrow I_0$, $V_0 \rightarrow I_1$, $V_1 \rightarrow \text{dummy}$ (stay idle to preserve NE coverage).
- **Verification Command**:
  ```bash
  python -m unittest discover -s .
  ```

---

## License & Author

**Author:** Nishant Sharma  
**GitHub:** [@Nishant-444](https://github.com/Nishant-444)  
**Repository:** [QuadGuard](https://github.com/Nishant-444/QuadGuard)  
**License:** ISC License
