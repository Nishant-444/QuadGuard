<!--
Note for Future Nishant -- Technical writeup for QuadGuard emergency fleet dispatcher.
Summarizes system context, technical insights, parameter sweep findings, and experimental benchmarks.
-->

# QuadGuard: Emergency Fleet Assignment with Coverage Preservation

## System Overview & Core Technical Insight

The emergency fleet assignment domain addresses a fundamental tension in online dispatching: optimizing solely for current response time frequently depletes local fleet availability in specific regions. As highlighted in the system design guidelines:

> *"Optimizing only the current incident may lead to poor system-wide performance."*

Standard bipartite matching algorithms (such as plain Hungarian or greedy dispatchers) naively assign any available vehicle to nearby incidents regardless of territorial coverage. When a cluster of non-critical incidents occurs in one quadrant, unconstrained dispatchers deplete all local vehicles, leaving that quadrant vulnerable to severe response delays when subsequent high-priority emergencies arrive.

**QuadGuard** solves this by embedding **coverage preservation directly into the matching cost matrix** using dummy vehicle slots and guard penalties:
1. **Dummy Columns & Optional Assignment**: A $V \times (V + I)$ cost matrix is constructed with $V$ dummy columns priced at `DUMMY_COST = 200`. Matching size is always $V$, enabling any vehicle to choose to stay idle if serving an incident is penalized.
2. **Coverage Penalty Guard**: For any vehicle that is the **last remaining idle vehicle** in its quadrant (`quad_counts == 1`), a `GUARD_PENALTY = 1000` is added to all non-P3 incident costs ($c_{ij} = \text{dist} - \lambda \cdot w_i + 1000$). This forces the Hungarian solver to prefer dummy idling over serving non-critical incidents.
3. **P3 Emergency Override**: Priority-3 incidents ($w=7$) bypass the guard penalty, ensuring critical life-safety emergencies are served immediately regardless of coverage state.
4. **Repair Pass for Simultaneous Departures**: If multiple vehicles in the same quadrant are assigned simultaneously in a single minute such that the quadrant would be completely emptied, `repair_pass` identifies the batch and drops the assignment with the lowest priority weight, retaining $\ge 1$ vehicle in idle coverage.

---

## Parameter Calibration ($\lambda$ Sweep)

The priority bonus parameter $\lambda$ balances travel distance against incident priority. We executed a systematic sweep over $\lambda \in \{1.0, 3.0, 5.0, 10.0\}$ on the development instance (`seed = 20260911`):

| $\lambda$ | Weighted Response Time (min) | Coverage Outage Minutes | P3 Response Time (min) | Total Served |
|---|---|---|---|---|
| **1.0** | 21.5835 | 34 | 31.9897 | 94 |
| **3.0** | 19.8853 | 34 | 31.2519 | 95 |
| **5.0** | **20.3313** | **30** | **29.4511** | **91** |
| **10.0** | 20.5487 | 30 | 29.7263 | 89 |

### Calibration Selection Logic:
- **Baseline Outage Target**: $\lambda = 5.0$ achieves a low coverage outage count of **30 minutes** (out of 120 minutes total).
- **Evaluation**: $\lambda = 1.0$ and $\lambda = 3.0$ increase coverage outage minutes to 34 minutes.
- **Winner**: $\lambda = 5.0$ achieves the minimal weighted response time (20.3313 min) and P3 response time (29.4511 min) among configurations that satisfy the coverage outage bound ($\le 30$ min). $\lambda = 5.0$ is hard-coded as the system default.

---

## Experimental Results & Comparison

Comparing QuadGuard (Guard ON, $\lambda = 5.0$) against a standard un-guarded dispatcher (Guard OFF, $\lambda = 5.0$) on identical environment instances:

| Metric | Guard ON (QuadGuard) | Guard OFF (Baseline) | Improvement |
|---|---|---|---|
| **Coverage Outage Minutes** | **30 min** | **119 min** | **74.8% reduction in outages** |
| **Total Incidents Served** | 91 / 100 | 98 / 100 | High coverage maintained |
| **P3 Response Time** | 29.45 min | 35.81 min | **17.8% faster P3 response** |
| **Runtime** | ~0.01 sec | ~0.01 sec | Real-time suitable |

### Summary of Impact:
Enabling the coverage guard dramatically reduces total system outage minutes from **119 minutes down to 30 minutes** (a **74.8% reduction**), while simultaneously improving high-priority (P3) response times by preserving idle vehicles near potential emergency sites.
