// QuadGuard Interactive Simulation & Visualization Engine (Minimalist Black & White)

class QuadGuardApp {
  constructor() {
    this.simData = null;
    this.currentMinute = 0;
    this.isPlaying = false;
    this.playbackSpeed = 2; // default 2x
    this.viewMode = 'split'; // 'split', 'guard', 'noguard'
    this.animTimer = null;

    this.initDOMElements();
    this.bindEvents();
    this.fetchSimulation(20260911, 5.0);
  }

  initDOMElements() {
    // Inputs & Control Bar
    this.seedInput = document.getElementById('seed-input');
    this.btnRandSeed = document.getElementById('btn-rand-seed');
    this.lamSlider = document.getElementById('lam-slider');
    this.lamVal = document.getElementById('lam-val');
    this.btnRunSim = document.getElementById('btn-run-sim');

    // View controls
    this.btnViewSplit = document.getElementById('btn-view-split');
    this.btnViewGuard = document.getElementById('btn-view-guard');
    this.btnViewNoGuard = document.getElementById('btn-view-noguard');
    this.simWorkspace = document.getElementById('sim-workspace');
    this.panelGuardOn = document.getElementById('panel-guard-on');
    this.panelGuardOff = document.getElementById('panel-guard-off');

    // Playback controls
    this.btnPlayPause = document.getElementById('btn-play-pause');
    this.btnPrevStep = document.getElementById('btn-prev-step');
    this.btnNextStep = document.getElementById('btn-next-step');
    this.timelineSlider = document.getElementById('timeline-slider');
    this.currTimeDisplay = document.getElementById('curr-time-display');
    this.speedSelect = document.getElementById('speed-select');

    // Canvases
    this.canvasOn = document.getElementById('canvas-guard-on');
    this.ctxOn = this.canvasOn.getContext('2d');
    this.canvasOff = document.getElementById('canvas-guard-off');
    this.ctxOff = this.canvasOff.getContext('2d');

    this.chartCanvas = document.getElementById('chart-outage');
    this.chartCtx = this.chartCanvas.getContext('2d');

    // Overlays
    this.overlayOn = document.getElementById('overlay-guard-on');
    this.overlayOff = document.getElementById('overlay-guard-off');

    // Badges & Metrics
    this.badgeOnOutage = document.getElementById('badge-on-outage');
    this.badgeOffOutage = document.getElementById('badge-off-outage');

    this.metricOnOutage = document.getElementById('metric-on-outage');
    this.metricOffOutage = document.getElementById('metric-off-outage');
    this.metricOutageImpact = document.getElementById('metric-outage-impact');

    this.metricOnP3 = document.getElementById('metric-on-p3');
    this.metricOffP3 = document.getElementById('metric-off-p3');
    this.metricP3Impact = document.getElementById('metric-p3-impact');

    this.metricOnServed = document.getElementById('metric-on-served');
    this.metricOffServed = document.getElementById('metric-off-served');

    this.metricOnWresp = document.getElementById('metric-on-wresp');
    this.metricOffWresp = document.getElementById('metric-off-wresp');

    // Queue elements
    this.queueTime = document.getElementById('queue-time');
    this.queueCount = document.getElementById('queue-count');
    this.queueTbody = document.getElementById('queue-tbody');
  }

  bindEvents() {
    this.btnRandSeed.addEventListener('click', () => {
      const randSeed = Math.floor(Math.random() * 89999999) + 10000000;
      this.seedInput.value = randSeed;
      this.runSimulationFromInputs();
    });

    this.lamSlider.addEventListener('input', (e) => {
      this.lamVal.textContent = parseFloat(e.target.value).toFixed(1);
    });

    this.btnRunSim.addEventListener('click', () => {
      this.runSimulationFromInputs();
    });

    // View modes
    this.btnViewSplit.addEventListener('click', () => this.setViewMode('split'));
    this.btnViewGuard.addEventListener('click', () => this.setViewMode('guard'));
    this.btnViewNoGuard.addEventListener('click', () => this.setViewMode('noguard'));

    // Playback
    this.btnPlayPause.addEventListener('click', () => this.togglePlayPause());
    this.btnPrevStep.addEventListener('click', () => this.stepTime(-1));
    this.btnNextStep.addEventListener('click', () => this.stepTime(1));

    this.timelineSlider.addEventListener('input', (e) => {
      this.currentMinute = parseInt(e.target.value, 10);
      this.updateUI();
    });

    this.speedSelect.addEventListener('change', (e) => {
      this.playbackSpeed = parseFloat(e.target.value);
      if (this.isPlaying) {
        this.restartPlayLoop();
      }
    });

    // Keyboard controls
    window.addEventListener('keydown', (e) => {
      if (e.target.tagName === 'INPUT') return;
      if (e.code === 'Space') {
        e.preventDefault();
        this.togglePlayPause();
      } else if (e.code === 'ArrowLeft') {
        this.stepTime(-1);
      } else if (e.code === 'ArrowRight') {
        this.stepTime(1);
      }
    });
  }

  runSimulationFromInputs() {
    const seed = parseInt(this.seedInput.value, 10) || 20260911;
    const lam = parseFloat(this.lamSlider.value) || 5.0;
    this.fetchSimulation(seed, lam);
  }

  async fetchSimulation(seed, lam) {
    this.btnRunSim.disabled = true;
    this.btnRunSim.innerHTML = '<span class="btn-icon">⌛</span> Running...';

    try {
      const response = await fetch('/api/run-simulation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seed, lam }),
      });

      if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
      this.simData = await response.json();

      this.currentMinute = 0;
      this.renderSummaryMetrics();
      this.updateUI();
    } catch (err) {
      console.error("Failed to run simulation:", err);
      alert("Error fetching simulation data from backend. Ensure server.py is running.");
    } finally {
      this.btnRunSim.disabled = false;
      this.btnRunSim.innerHTML = '<span class="btn-icon">▶</span> Re-Run Simulation';
    }
  }

  setViewMode(mode) {
    this.viewMode = mode;
    this.btnViewSplit.classList.toggle('active', mode === 'split');
    this.btnViewGuard.classList.toggle('active', mode === 'guard');
    this.btnViewNoGuard.classList.toggle('active', mode === 'noguard');

    if (mode === 'split') {
      this.simWorkspace.classList.remove('single-view');
      this.panelGuardOn.style.display = 'flex';
      this.panelGuardOff.style.display = 'flex';
    } else if (mode === 'guard') {
      this.simWorkspace.classList.add('single-view');
      this.panelGuardOn.style.display = 'flex';
      this.panelGuardOff.style.display = 'none';
    } else if (mode === 'noguard') {
      this.simWorkspace.classList.add('single-view');
      this.panelGuardOn.style.display = 'none';
      this.panelGuardOff.style.display = 'flex';
    }
    this.updateUI();
  }

  togglePlayPause() {
    this.isPlaying = !this.isPlaying;
    if (this.isPlaying) {
      this.btnPlayPause.textContent = '⏸ Pause';
      this.restartPlayLoop();
    } else {
      this.btnPlayPause.textContent = '▶ Play';
      if (this.animTimer) clearInterval(this.animTimer);
    }
  }

  restartPlayLoop() {
    if (this.animTimer) clearInterval(this.animTimer);
    const intervalMs = Math.max(50, 400 / this.playbackSpeed);
    this.animTimer = setInterval(() => {
      if (this.currentMinute < 120) {
        this.currentMinute++;
        this.updateUI();
      } else {
        this.togglePlayPause();
      }
    }, intervalMs);
  }

  stepTime(delta) {
    if (this.isPlaying) this.togglePlayPause();
    this.currentMinute = Math.max(0, Math.min(120, this.currentMinute + delta));
    this.updateUI();
  }

  renderSummaryMetrics() {
    if (!this.simData) return;

    const mOn = this.simData.guard_on.metrics;
    const mOff = this.simData.guard_off.metrics;

    // Outage Card
    this.metricOnOutage.textContent = `${mOn.coverage_outage_minutes} min`;
    this.metricOffOutage.textContent = `${mOff.coverage_outage_minutes} min`;

    const outageRed = mOff.coverage_outage_minutes > 0
      ? (((mOff.coverage_outage_minutes - mOn.coverage_outage_minutes) / mOff.coverage_outage_minutes) * 100).toFixed(1)
      : 0;
    this.metricOutageImpact.innerHTML = `<span class="impact-tag success">${outageRed}% Outage Reduction</span>`;

    // P3 Response
    const p3On = mOn.p3_response_time != null ? mOn.p3_response_time.toFixed(2) : 'N/A';
    const p3Off = mOff.p3_response_time != null ? mOff.p3_response_time.toFixed(2) : 'N/A';
    this.metricOnP3.textContent = `${p3On} min`;
    this.metricOffP3.textContent = `${p3Off} min`;

    if (mOn.p3_response_time != null && mOff.p3_response_time != null) {
      const p3Diff = (((mOff.p3_response_time - mOn.p3_response_time) / mOff.p3_response_time) * 100).toFixed(1);
      const tagClass = p3Diff >= 0 ? 'info' : 'neutral';
      this.metricP3Impact.innerHTML = `<span class="impact-tag ${tagClass}">${Math.abs(p3Diff)}% ${p3Diff >= 0 ? 'Faster P3' : 'Slower P3'}</span>`;
    }

    // Incidents Served
    this.metricOnServed.textContent = `${mOn.total_served}/${this.simData.total_incidents}`;
    this.metricOffServed.textContent = `${mOff.total_served}/${this.simData.total_incidents}`;

    // Weighted Response
    this.metricOnWresp.textContent = `${mOn.weighted_response_time.toFixed(2)}`;
    this.metricOffWresp.textContent = `${mOff.weighted_response_time.toFixed(2)}`;
  }

  updateUI() {
    if (!this.simData) return;

    this.currTimeDisplay.textContent = this.currentMinute;
    this.timelineSlider.value = this.currentMinute;

    const frameOn = this.simData.guard_on.history[this.currentMinute];
    const frameOff = this.simData.guard_off.history[this.currentMinute];

    // Render Canvas & Quadrants
    if (this.viewMode !== 'noguard') {
      this.renderFrameCanvas(this.ctxOn, this.canvasOn, frameOn, true);
      this.updateQuadrantUI('on', frameOn);
    }
    if (this.viewMode !== 'guard') {
      this.renderFrameCanvas(this.ctxOff, this.canvasOff, frameOff, false);
      this.updateQuadrantUI('off', frameOff);
    }

    // Render Chart
    this.renderOutageChart();

    // Render Queue
    this.renderQueueTable(frameOn.queue);
  }

  updateQuadrantUI(prefix, frame) {
    const counts = frame.quadrant_counts;
    const isOutage = frame.is_outage;

    for (let q = 0; q < 4; q++) {
      const statEl = document.getElementById(`q${q}-stat-${prefix}`);
      const countEl = document.getElementById(`q${q}-count-${prefix}`);
      const count = counts[q] || 0;
      countEl.textContent = count;

      if (count === 0) {
        statEl.classList.add('outage-alert');
      } else {
        statEl.classList.remove('outage-alert');
      }
    }

    const overlay = prefix === 'on' ? this.overlayOn : this.overlayOff;
    overlay.classList.toggle('active', isOutage);

    const badge = prefix === 'on' ? this.badgeOnOutage : this.badgeOffOutage;
    badge.textContent = `Outage: ${frame.cumulative_outage_minutes} min`;
  }

  renderFrameCanvas(ctx, canvas, frame, isGuardOn) {
    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);

    // Coordinate translation functions (Grid 0..100 -> Canvas pixels)
    const mapX = (x) => (x / 100) * width;
    const mapY = (y) => height - (y / 100) * height; // invert Y

    // 1. Draw Quadrant Grid Background & Boundaries (Minimalist Grayscale)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
    ctx.lineWidth = 1;

    // Grid lines (every 10 units)
    for (let i = 10; i < 100; i += 10) {
      ctx.beginPath();
      ctx.moveTo(mapX(i), 0); ctx.lineTo(mapX(i), height);
      ctx.moveTo(0, mapY(i)); ctx.lineTo(width, mapY(i));
      ctx.stroke();
    }

    // Quadrant Partition Lines (x=50, y=50)
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(mapX(50), 0); ctx.lineTo(mapX(50), height);
    ctx.moveTo(0, mapY(50)); ctx.lineTo(width, mapY(50));
    ctx.stroke();

    // Quadrant Outage Fill (Grayscale Hash/Fill)
    const quadBounds = [
      [0, 50, 0, 50],     // Q0 SW
      [0, 50, 50, 100],   // Q1 NW
      [50, 100, 0, 50],   // Q2 SE
      [50, 100, 50, 100]  // Q3 NE
    ];

    quadBounds.forEach(([xlo, xhi, ylo, yhi], q) => {
      if (frame.quadrant_counts[q] === 0) {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
        ctx.fillRect(mapX(xlo), mapY(yhi), mapX(xhi - xlo), mapY(ylo) - mapY(yhi));
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1;
        ctx.strokeRect(mapX(xlo), mapY(yhi), mapX(xhi - xlo), mapY(ylo) - mapY(yhi));
      }
    });

    // Quadrant Labels
    ctx.font = '600 12px JetBrains Mono';
    ctx.fillStyle = '#a3a3a3';
    ctx.fillText('Q1 (NW)', 12, 24);
    ctx.fillText('Q3 (NE)', width - 70, 24);
    ctx.fillText('Q0 (SW)', 12, height - 12);
    ctx.fillText('Q2 (SE)', width - 70, height - 12);

    // 2. Draw Active Dispatches (dashed vector lines)
    if (frame.dispatches) {
      frame.dispatches.forEach((d) => {
        const vehicle = frame.vehicles.find((v) => v.id === d.vehicle_id);
        if (vehicle) {
          ctx.beginPath();
          ctx.moveTo(mapX(vehicle.x), mapY(vehicle.y));
          ctx.lineTo(mapX(d.target_x), mapY(d.target_y));
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = d.incident_priority === 3 ? 2 : 1.5;
          ctx.setLineDash([4, 4]);
          ctx.stroke();
          ctx.setLineDash([]);
        }
      });
    }

    // 3. Draw Unserved Incidents in Queue
    if (frame.queue) {
      frame.queue.forEach((inc) => {
        const cx = mapX(inc.x);
        const cy = mapY(inc.y);

        if (inc.priority === 3) {
          // P3 Beacon (Solid White circle with outer ring)
          ctx.beginPath();
          ctx.arc(cx, cy, 10, 0, Math.PI * 2);
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 1.5;
          ctx.stroke();

          ctx.beginPath();
          ctx.arc(cx, cy, 6, 0, Math.PI * 2);
          ctx.fillStyle = '#ffffff';
          ctx.fill();
        } else if (inc.priority === 2) {
          // P2 Medium Gray Diamond/Circle
          ctx.beginPath();
          ctx.arc(cx, cy, 5.5, 0, Math.PI * 2);
          ctx.fillStyle = '#a3a3a3';
          ctx.fill();
        } else {
          // P1 Dark Gray Circle
          ctx.beginPath();
          ctx.arc(cx, cy, 4.5, 0, Math.PI * 2);
          ctx.fillStyle = '#525252';
          ctx.fill();
        }
      });
    }

    // 4. Draw Vehicles (Black & White Circles)
    if (frame.vehicles) {
      frame.vehicles.forEach((v) => {
        const vx = mapX(v.x);
        const vy = mapY(v.y);

        ctx.beginPath();
        ctx.arc(vx, vy, 7, 0, Math.PI * 2);
        if (v.idle) {
          ctx.fillStyle = '#ffffff'; // Solid White for Idle Coverage Unit
          ctx.fill();
          ctx.strokeStyle = '#000000';
          ctx.lineWidth = 1.5;
          ctx.stroke();
        } else {
          ctx.fillStyle = '#404040'; // Medium Gray for Responding Unit
          ctx.fill();
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 1.5;
          ctx.stroke();
        }

        // Vehicle ID Label
        ctx.font = '600 10px JetBrains Mono';
        ctx.fillStyle = '#ffffff';
        ctx.fillText(`V${v.id}`, vx + 9, vy + 3);
      });
    }
  }

  renderOutageChart() {
    if (!this.simData) return;

    const ctx = this.chartCtx;
    const width = this.chartCanvas.width;
    const height = this.chartCanvas.height;

    ctx.clearRect(0, 0, width, height);

    const padLeft = 40;
    const padBottom = 30;
    const padTop = 15;
    const padRight = 20;

    const plotW = width - padLeft - padRight;
    const plotH = height - padTop - padBottom;

    const historyOn = this.simData.guard_on.history;
    const historyOff = this.simData.guard_off.history;

    const maxOutage = Math.max(
      10,
      historyOff[120].cumulative_outage_minutes,
      historyOn[120].cumulative_outage_minutes
    );

    // Axes
    ctx.strokeStyle = '#404040';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padLeft, padTop); ctx.lineTo(padLeft, height - padBottom);
    ctx.lineTo(width - padRight, height - padBottom);
    ctx.stroke();

    // Axis Labels
    ctx.font = '10px JetBrains Mono';
    ctx.fillStyle = '#a3a3a3';
    ctx.fillText('0', padLeft - 15, height - padBottom + 3);
    ctx.fillText(`${maxOutage}`, padLeft - 25, padTop + 10);
    ctx.fillText('t=0', padLeft, height - 10);
    ctx.fillText('t=60', padLeft + plotW / 2 - 10, height - 10);
    ctx.fillText('t=120', padLeft + plotW - 25, height - 10);

    const getX = (t) => padLeft + (t / 120) * plotW;
    const getY = (val) => height - padBottom - (val / maxOutage) * plotH;

    // Draw Guard OFF Line (Dashed Gray)
    ctx.strokeStyle = '#737373';
    ctx.lineWidth = 2;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    historyOff.forEach((frame) => {
      const x = getX(frame.t);
      const y = getY(frame.cumulative_outage_minutes);
      if (frame.t === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
    ctx.setLineDash([]);

    // Draw Guard ON Line (Solid White)
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 3;
    ctx.beginPath();
    historyOn.forEach((frame) => {
      const x = getX(frame.t);
      const y = getY(frame.cumulative_outage_minutes);
      if (frame.t === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Current Time Vertical Tracker Line
    const curX = getX(this.currentMinute);
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 1;
    ctx.setLineDash([2, 2]);
    ctx.beginPath();
    ctx.moveTo(curX, padTop);
    ctx.lineTo(curX, height - padBottom);
    ctx.stroke();
    ctx.setLineDash([]);
  }

  renderQueueTable(queue) {
    this.queueTime.textContent = this.currentMinute;
    this.queueCount.textContent = queue.length;

    if (!queue || queue.length === 0) {
      this.queueTbody.innerHTML = '<tr><td colspan="4" class="empty-cell">No unserved incidents in queue</td></tr>';
      return;
    }

    this.queueTbody.innerHTML = queue
      .slice(0, 10)
      .map((inc) => {
        const pClass = `p${inc.priority}`;
        const pText = inc.priority === 3 ? 'P3 (Critical)' : inc.priority === 2 ? 'P2 (Med)' : 'P1 (Low)';
        return `
          <tr>
            <td>#${inc.id}</td>
            <td><span class="priority-tag ${pClass}">${pText}</span></td>
            <td>${inc.arrival_min} min</td>
            <td>(${inc.x.toFixed(1)}, ${inc.y.toFixed(1)})</td>
          </tr>
        `;
      })
      .join('');
  }
}

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  window.app = new QuadGuardApp();
});
