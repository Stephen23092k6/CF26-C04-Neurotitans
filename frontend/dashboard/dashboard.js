let currentData = null;
let currentReplayStep = 0;
const replayChannel = window.BroadcastChannel ? new BroadcastChannel('neurobrain_replay') : null;

// Helper to update the UI
function renderDashboard(data) {
    if (!data) return;
    currentData = data;
    currentReplayStep = data.timeline.length;
    
    // Risk Meter
    const rs = document.getElementById('ui-risk-score');
    const sev = document.getElementById('ui-severity');
    const def = document.getElementById('ui-defense-status');
    rs.textContent = data.risk.risk_score;
    sev.textContent = data.risk.severity;
    
    let color = 'var(--text)';
    if (data.risk.severity === 'CRITICAL') { color = 'var(--accent-red)'; def.textContent = 'DEFENSE: ACTIVE ENGAGEMENT'; def.style.color = color; }
    if (data.risk.severity === 'HIGH') { color = 'var(--accent-amber)'; def.textContent = 'DEFENSE: ISOLATION'; def.style.color = color; }
    if (data.risk.severity === 'MEDIUM') { color = 'var(--accent-blue)'; def.textContent = 'DEFENSE: MONITORING'; def.style.color = color; }
    if (data.risk.severity === 'LOW') { color = 'var(--accent-green)'; def.textContent = 'DEFENSE: STANDBY'; def.style.color = color; }
    
    rs.style.color = color;
    sev.style.color = color;
    
    // Responses
    const respContainer = document.getElementById('ui-responses');
    respContainer.innerHTML = '';
    data.responses.forEach(r => {
        const d = document.createElement('div');
        d.className = 'response-action';
        d.textContent = `> ${r}`;
        respContainer.appendChild(d);
    });
    
    // Copilot Q&A
    const copilotContainer = document.getElementById('ui-copilot');
    copilotContainer.innerHTML = '';
    const qas = [
        {q: "Why was this flagged?", a: data.copilot.why},
        {q: "How did the attack unfold?", a: data.copilot.what_happened},
        {q: "What should we do next?", a: data.copilot.next_actions.join('\n')}
    ];
    
    qas.forEach(qa => {
        const b = document.createElement('div');
        b.className = 'qa-box';
        b.innerHTML = `<div class="qa-q">${qa.q}</div><div class="qa-a">${qa.a}</div>`;
        copilotContainer.appendChild(b);
    });
    
    // MITRE Grid
    const mitreContainer = document.getElementById('ui-mitre');
    mitreContainer.innerHTML = '';
    data.mitre.forEach(m => {
        const d = document.createElement('div');
        d.className = 'mitre-card';
        d.innerHTML = `<div class="mitre-id">${m.technique_id}</div><div class="mitre-name">${m.technique_name}</div>`;
        mitreContainer.appendChild(d);
    });
    
    renderTimeline();
}

function renderTimeline() {
    if (!currentData) return;
    const timelineContainer = document.getElementById('ui-timeline');
    const stepLabel = document.getElementById('ui-replay-step');
    timelineContainer.innerHTML = '';
    
    const visibleEvents = currentData.timeline.slice(0, currentReplayStep);
    stepLabel.textContent = `Step ${currentReplayStep}/${currentData.timeline.length}`;
    
    visibleEvents.forEach((t, i) => {
        const d = document.createElement('div');
        d.className = 'timeline-item';
        // highlight the last event if we are replaying
        if (i === currentReplayStep - 1 && currentReplayStep < currentData.timeline.length) {
            d.style.borderLeftColor = 'var(--accent-red)';
            d.style.backgroundColor = 'rgba(255,255,255,0.05)';
        }
        d.innerHTML = `
            <div class="timeline-time">+${t.timestamp.toFixed(1)}s</div>
            <div class="timeline-event">${t.event}</div>
            <div class="timeline-nodes">${t.source} &rarr; ${t.destination || 'N/A'}</div>
        `;
        timelineContainer.appendChild(d);
    });
    
    // Broadcast to Spline visualization layer
    if (replayChannel && currentData && currentReplayStep > 0 && currentReplayStep <= currentData.timeline.length) {
        const activeEvent = currentData.timeline[currentReplayStep - 1];
        const explanation = activeEvent.explanation || "";
        // The SplineController expects an object with 'source' and optionally metadata
        replayChannel.postMessage({
            type: 'replay_step',
            activeEvent: {
                source: activeEvent.source,
                destination: activeEvent.destination,
                event_type: activeEvent.event,
                metadata: {
                    impossible_context: explanation.includes("anomaly"),
                    spoofed_identity: explanation.includes("spoof")
                }
            }
        });
    }
}

document.getElementById('btn-replay-prev').addEventListener('click', () => {
    if (currentReplayStep > 1) {
        currentReplayStep--;
        renderTimeline();
    }
});

document.getElementById('btn-replay-next').addEventListener('click', () => {
    if (currentData && currentReplayStep < currentData.timeline.length) {
        currentReplayStep++;
        renderTimeline();
    }
});

document.getElementById('btn-run').addEventListener('click', () => {
    // In the prototype without a specific FastAPI endpoint for this, 
    // we would call fetch('/api/command_center') here.
    alert("This prototype UI triggers the Python demo script in the terminal. See run_command_center.py output for live data integration.");
});
