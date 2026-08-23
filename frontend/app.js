// Neurobrain X - Vanilla JS Reactive UI

const $ = s => document.querySelector(s);
const $$ = s => document.querySelectorAll(s);

const state = {
  graph: { nodes: [], edges: [], events: [] },
  incident: null,
  selectedEntityId: null,
  sim: { loss: 0.2, delay: 4, dup: 0.1 }
};

// Global Controllers
window.splineCtrl = new SplineController('spline-viewer');
window.attackReplay = new AttackReplay((replayState) => {
    // Forward replay state to Spline
    if (window.splineCtrl) window.splineCtrl.updateReplayState(replayState);
    
    // Highlight timeline row in UI
    $$('.event-row').forEach(row => row.classList.remove('highlighted-row'));
    if (replayState.activeEvent) {
        const rowId = `row-${replayState.activeEvent.event_id}`;
        const row = document.getElementById(rowId);
        if (row) {
            row.classList.add('highlighted-row');
            row.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
});
let is3DMode = false;

// Canvas Engine for 2D Fallback
const canvas = $("#graph-canvas");
const ctx = canvas.getContext("2d");
let layout = { nodes: new Map(), tick: 0 };

function resizeCanvas() {
  const rect = canvas.parentElement.getBoundingClientRect();
  canvas.width = rect.width;
  canvas.height = rect.height;
  drawGraph();
}
window.addEventListener("resize", resizeCanvas);

function initGraphLayout() {
  layout.nodes.clear();
  const floors = new Set();
  state.graph.nodes.forEach(n => floors.add(n.attrs.floor || 0));
  
  const sortedFloors = Array.from(floors).sort((a,b)=>a-b);
  const floorHeight = canvas.height / (sortedFloors.length || 1);
  
  // Track nodes per floor for even X spacing
  const floorCounts = new Map();
  sortedFloors.forEach(f => floorCounts.set(f, 0));
  
  // Sort nodes by ID for deterministic layout
  const sortedNodes = [...state.graph.nodes].sort((a,b) => a.entity_id.localeCompare(b.entity_id));
  
  sortedNodes.forEach(n => {
    const fIdx = sortedFloors.indexOf(n.attrs.floor || 0);
    const count = floorCounts.get(n.attrs.floor || 0);
    floorCounts.set(n.attrs.floor || 0, count + 1);
  });
  
  const currentCounts = new Map();
  sortedFloors.forEach(f => currentCounts.set(f, 0));
  
  sortedNodes.forEach(n => {
    const floor = n.attrs.floor || 0;
    const fIdx = sortedFloors.indexOf(floor);
    const count = floorCounts.get(floor);
    const curr = currentCounts.get(floor);
    currentCounts.set(floor, curr + 1);
    
    // Spread evenly across 80% of canvas width (10% padding on each side)
    const spacing = (canvas.width * 0.8) / (count > 1 ? count - 1 : 1);
    const x = canvas.width * 0.1 + (curr * spacing);
    const y = (fIdx * floorHeight) + (floorHeight * 0.5) + (Math.random()*20-10);
    
    layout.nodes.set(n.entity_id, { x, y, data: n });
  });
}

function drawGraph() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  // Draw floors
  const floors = new Set();
  state.graph.nodes.forEach(n => floors.add(n.attrs.floor || 0));
  const sortedFloors = Array.from(floors).sort((a,b)=>a-b);
  const floorHeight = canvas.height / (sortedFloors.length || 1);
  
  ctx.strokeStyle = '#111a26';
  ctx.fillStyle = '#111a26';
  ctx.font = '10px SFMono-Regular';
  sortedFloors.forEach((f, i) => {
    const y = (i * floorHeight);
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
    ctx.fillText(`FLOOR ${f}`, 10, y + 16);
  });

  // Collect incident edges for highlight
  const incidentEdges = new Set();
  const inferredGaps = [];
  if (state.incident && state.incident.best_path) {
    state.incident.best_path.edges.forEach(e => {
      if (e.is_inferred) inferredGaps.push(e);
      else incidentEdges.add(`${e.source}->${e.target}`);
    });
  }

  // Draw Edges
  state.graph.edges.forEach(e => {
    const a = layout.nodes.get(e.source);
    const b = layout.nodes.get(e.target);
    if (!a || !b) return;
    
    const isIncident = incidentEdges.has(`${e.source}->${e.target}`);
    
    ctx.beginPath();
    ctx.moveTo(a.x, a.y);
    ctx.lineTo(b.x, b.y);
    ctx.strokeStyle = isIncident ? '#ff3b5c' : '#1e2d40';
    ctx.lineWidth = isIncident ? 2 : 1;
    ctx.setLineDash([]);
    ctx.stroke();
  });

  // Draw Inferred Gaps
  inferredGaps.forEach(e => {
    const a = layout.nodes.get(e.source);
    const b = layout.nodes.get(e.target);
    if (!a || !b) return;
    
    ctx.beginPath();
    ctx.moveTo(a.x, a.y);
    ctx.lineTo(b.x, b.y);
    ctx.strokeStyle = '#ffae2b'; // Amber dashed
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);
    ctx.stroke();
  });
  ctx.setLineDash([]); // reset

  // Draw Nodes
  layout.nodes.forEach((pos, id) => {
    const isSelected = id === state.selectedEntityId;
    const isIncidentNode = state.incident && state.incident.best_path && state.incident.best_path.nodes.includes(id);
    
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, 6, 0, Math.PI * 2);
    ctx.fillStyle = isSelected ? '#32a8ff' : isIncidentNode ? '#ff3b5c' : '#101722';
    ctx.fill();
    ctx.strokeStyle = isSelected ? '#fff' : isIncidentNode ? '#fff' : '#3b5575';
    ctx.lineWidth = 1.5;
    ctx.stroke();
    
    if (isSelected || isIncidentNode) {
      ctx.fillStyle = '#fff';
      ctx.font = '10px SFMono-Regular';
      ctx.fillText(id, pos.x + 10, pos.y + 4);
    }
  });
}

// Click detection
canvas.addEventListener('click', e => {
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  
  let clicked = null;
  layout.nodes.forEach((pos, id) => {
    const dx = pos.x - x;
    const dy = pos.y - y;
    if (dx*dx + dy*dy < 100) clicked = id;
  });
  
  if (clicked) {
    state.selectedEntityId = clicked;
    $("#tab-entity").click();
  } else {
    state.selectedEntityId = null;
  }
  updateUI();
});

// API Calls
function showGlobalError(msg) {
  state.graph = { nodes: [], edges: [], events: [] };
  state.incident = null;
  $("#stat-nodes").textContent = `NODES: --`;
  $("#stat-edges").textContent = `EDGES: --`;
  $("#stat-events").textContent = `EVENTS: --`;
  $("#inspector-incident").innerHTML = `
    <div class="empty-state" style="color:var(--accent-red)">
      [ ${msg} ]<br>
      <button class="btn outline" style="margin-top:16px; width:auto; border-color:var(--accent-red); color:var(--accent-red);" onclick="fetchGraph()">RECONNECT ENGINE</button>
    </div>
  `;
  $("#timeline-events").innerHTML = `<div class="empty-state" style="color:var(--accent-red)">[ ${msg} ]</div>`;
  initGraphLayout();
  updateUI();
}

async function fetchGraph() {
  try {
    const res = await fetch('/api/graph');
    if (!res.ok) throw new Error("API Error");
    const data = await res.json();
    state.graph = data;
    state.incident = null;
    
    $("#stat-nodes").textContent = `NODES: ${data.nodes.length}`;
    $("#stat-edges").textContent = `EDGES: ${data.edges.length}`;
    
    initGraphLayout();
    updateUI();
  } catch (err) {
    showGlobalError("CONNECTION LOST");
  }
}

async function runIncident() {
  try {
    const iRes = await fetch('/api/incident');
    if (!iRes.ok) throw new Error("API Error");
    const iData = await iRes.json();
    
    state.graph = iData.graph;
    state.graph.events = iData.events;
    state.incident = iData;
    
    $("#stat-nodes").textContent = `NODES: ${iData.graph.nodes.length}`;
    $("#stat-edges").textContent = `EDGES: ${iData.graph.edges.length}`;
    $("#stat-events").textContent = `EVENTS: ${iData.events.length}`;
    
    initGraphLayout();
    $("#tab-incident").click();
    updateUI();
  } catch (err) {
    showGlobalError("CONNECTION LOST");
  }
}

async function runSimulate() {
  try {
    const {loss, delay, dup} = state.sim;
    const res = await fetch(`/api/resilience?loss=${loss}&delay=${delay}&duplicate=${dup}`);
    if (!res.ok) throw new Error("API Error");
    const data = await res.json();
    
    state.graph = data.graph;
    state.graph.events = data.events;
    state.incident = data;
    
    $("#stat-nodes").textContent = `NODES: ${data.graph.nodes.length}`;
    $("#stat-edges").textContent = `EDGES: ${data.graph.edges.length}`;
    $("#stat-events").textContent = `EVENTS: ${data.events.length}`;
    
    initGraphLayout();
    $("#tab-incident").click();
    updateUI();
  } catch (err) {
    showGlobalError("CONNECTION LOST");
  }
}

async function runBenchmark() {
  const res = await fetch('/api/benchmark');
  const data = await res.json();
  const tbody = $("#bench-table tbody");
  tbody.innerHTML = data.rows.map(r => `
    <tr>
      <td>${r.scenario}</td>
      <td>${r.events}</td>
      <td style="color:${r.path_found?'#10b981':'#ff3b5c'}">${r.path_found?"YES":"NO"}</td>
      <td>${r.score !== null ? r.score.toFixed(1) : "—"}</td>
      <td>${r.confidence !== null ? r.confidence.toFixed(1)+"%" : "—"}</td>
    </tr>
  `).join("");
  $("#benchmark-modal").classList.remove("hidden");
}

// UI Updating
function updateUI() {
  if (is3DMode) {
      if (window.splineCtrl) window.splineCtrl.updateState(state.graph, state.incident);
  } else {
      drawGraph();
  }
  renderInspector();
  renderTimeline();
}

function renderInspector() {
  const incTab = $("#inspector-incident");
  const entTab = $("#inspector-entity");
  
  if ($("#tab-incident").classList.contains("active")) {
    incTab.classList.remove("hidden");
    entTab.classList.add("hidden");
    
    if (!state.incident) {
      incTab.innerHTML = `<div class="empty-state">NO ACTIVE INCIDENT</div>`;
    } else if (!state.incident.best_path) {
      incTab.innerHTML = `
        <div class="empty-state" style="color:var(--accent-amber); margin-top:20px;">
          INCIDENT NOT RECONSTRUCTABLE<br>
          <span style="font-size:9px; color:var(--text-muted); display:block; margin-top:8px; font-weight:normal;">
            Telemetry degradation exceeded engine tolerance.
          </span>
        </div>
        <div class="kv-list" style="margin-top:24px;">
          <div class="kv-row"><div class="kv-key">Accepted</div><div class="kv-val">${state.incident.accepted_events} events</div></div>
          <div class="kv-row"><div class="kv-key">Telemetry Loss</div><div class="kv-val">${(state.incident.input.missing * 100).toFixed(0)}%</div></div>
        </div>
      `;
    } else {
      const p = state.incident.best_path;
      
      const isDanger = p.score > 50;
      
      let html = `
        <div class="score-box ${isDanger ? 'danger' : 'warning'}">
          <div class="val">${p.score.toFixed(1)}</div>
          <div class="lbl">Threat Score</div>
          <div class="metric-row">
            <div class="metric"><b>${p.confidence.toFixed(1)}%</b><span>CONFIDENCE</span></div>
            <div class="metric"><b>${p.nodes.length}</b><span>NODES</span></div>
          </div>
        </div>
        <div class="section-title">RECONSTRUCTED TRAJECTORY</div>
        <div class="path-viz">
      `;
      
      p.nodes.forEach((n, i) => {
        html += `<div class="path-node">${n}</div>`;
        if (i < p.nodes.length - 1) {
          const edge = p.edges[i];
          if (edge && edge.is_inferred) {
            html += `<div class="path-arrow inferred">- - - -</div>`;
          } else {
            html += `<div class="path-arrow">→</div>`;
          }
        }
      });
      
      html += `</div><div class="section-title">ANALYSIS ENGINE EXPLANATION</div><ul class="explanation">`;
      p.explanation.forEach(ex => {
        const isPenalty = ex.includes("Confidence reduced") || ex.includes("INFERRED_GAP");
        html += `<li class="${isPenalty?'penalty':''}">${ex}</li>`;
      });
      html += `</ul>`;
      
      incTab.innerHTML = html;
    }
  } else {
    incTab.classList.add("hidden");
    entTab.classList.remove("hidden");
    
    if (!state.selectedEntityId) {
      entTab.innerHTML = `<div class="empty-state">NO ENTITY SELECTED</div>`;
    } else {
      const n = state.graph.nodes.find(x => x.entity_id === state.selectedEntityId);
      if (n) {
        entTab.innerHTML = `
          <div class="kv-list">
            <div class="kv-row"><div class="kv-key">ID</div><div class="kv-val">${n.entity_id}</div></div>
            <div class="kv-row"><div class="kv-key">Type</div><div class="kv-val">${n.entity_type}</div></div>
            <div class="kv-row"><div class="kv-key">Floor</div><div class="kv-val">${n.attrs.floor || 'N/A'}</div></div>
            <div class="kv-row"><div class="kv-key">Network</div><div class="kv-val">${n.attrs.network_segment || 'N/A'}</div></div>
          </div>
        `;
      }
    }
  }
}

window.timelineFilter = 'ALL';
window.setTimelineFilter = (f) => {
  window.timelineFilter = f;
  renderTimeline();
};

function renderTimeline() {
  const container = $("#timeline-events");
  if (!state.graph.events || state.graph.events.length === 0) {
    container.innerHTML = `<div class="empty-state">NO EVENTS LOADED</div>`;
    return;
  }
  
  // Sort events chronologically
  let evs = [...state.graph.events].sort((a,b) => a.event_time - b.event_time);
  
  if (window.timelineFilter === 'ALERT') {
    evs = evs.filter(e => e.severity >= 0.5);
  }
  
  // Cap to recent 150 events to prevent massive DOM overhead
  evs = evs.slice(-150);
  
  if (evs.length === 0) {
    container.innerHTML = `<div class="empty-state">NO EVENTS MATCH FILTER</div>`;
    return;
  }
  
  let html = '';
  evs.forEach(e => {
    let sevClass = 'low-sev';
    if (e.severity >= 0.8) sevClass = 'high-sev';
    else if (e.severity >= 0.5) sevClass = 'med-sev';
    
    html += `
      <div class="event-row ${sevClass}" id="row-${e.event_id}">
        <div>+${(e.event_time - state.graph.events[0].event_time).toFixed(1)}s</div>
        <div>${e.event_type}</div>
        <div>${e.source}</div>
        <div style="color:var(--text-muted)">${e.destination ? '→ '+e.destination : ''}</div>
        <div>sev: ${e.severity.toFixed(2)}</div>
      </div>
    `;
  });
  
  container.innerHTML = html;
}

// Bind Inputs
["loss", "delay", "dup"].forEach(id => {
  const inp = $(`#inp-${id}`);
  inp.addEventListener("input", () => {
    const val = parseFloat(inp.value);
    state.sim[id] = val;
    $(`#val-${id}`).textContent = id === "delay" ? `${val}s` : `${Math.round(val*100)}%`;
  });
});

$("#btn-normal").onclick = fetchGraph;
$("#btn-attack").onclick = runIncident;
$("#btn-simulate").onclick = runSimulate; 
$("#btn-benchmark").onclick = runBenchmark;
$("#btn-close-bench").onclick = () => $("#benchmark-modal").classList.add("hidden");

$("#tab-incident").onclick = () => {
  $("#tab-incident").classList.add("active");
  $("#tab-entity").classList.remove("active");
  updateUI();
};
$("#tab-entity").onclick = () => {
  $("#tab-entity").classList.add("active");
  $("#tab-incident").classList.remove("active");
  updateUI();
};

// 3D/2D Toggle
$("#btn-toggle-3d").onclick = () => {
  is3DMode = !is3DMode;
  $("#btn-toggle-3d").textContent = is3DMode ? "SWITCH TO 2D CANVAS" : "SWITCH TO 3D SPLINE";
  if (is3DMode) {
      $("#graph-canvas").classList.add("hidden");
      $("#spline-placeholder").classList.remove("hidden");
  } else {
      $("#graph-canvas").classList.remove("hidden");
      $("#spline-placeholder").classList.add("hidden");
  }
  updateUI();
};

// Replay UI bindings
$("#btn-replay-play").onclick = () => {
    if (state.incident) {
        if (window.attackReplay.events.length === 0) window.attackReplay.loadIncident(state.incident);
        window.attackReplay.play();
    }
};
$("#btn-replay-pause").onclick = () => window.attackReplay.pause();
$("#btn-replay-next").onclick = () => window.attackReplay.next();
$("#btn-replay-reset").onclick = () => window.attackReplay.reset();

// Update Replay when new incident loads
const origRunIncident = runIncident;
runIncident = async () => {
    await origRunIncident();
    window.attackReplay.loadIncident(state.incident);
};
const origRunSimulate = runSimulate;
runSimulate = async () => {
    await origRunSimulate();
    window.attackReplay.loadIncident(state.incident);
};

// Start
setTimeout(() => {
  resizeCanvas();
  fetchGraph();
}, 100);
