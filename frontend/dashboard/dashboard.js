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
    
    // Phase 10 Renderers
    renderEnterpriseAssets(data.enterprise_assets);
    renderThreatPrediction(data.prediction);
    renderSecurityMemory(data.memory);
    renderPlaybook(data.playbook);
    
    renderTimeline();
}

function renderEnterpriseAssets(assets) {
    const container = document.getElementById('ui-enterprise-assets');
    if (!container) return;
    container.innerHTML = '';
    if (!assets) {
        container.innerHTML = '<div class="asset-box">No asset data available.</div>';
        return;
    }
    
    assets.forEach(a => {
        const d = document.createElement('div');
        d.className = 'asset-box';
        let color = 'var(--text-muted)';
        if (a.criticality === 'CRITICAL') color = 'var(--accent-red)';
        if (a.criticality === 'HIGH') color = 'var(--accent-amber)';
        
        d.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <strong>${a.asset}</strong>
                <span style="color:${color}; font-size:12px; font-weight:600;">${a.criticality}</span>
            </div>
            <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">
                Owner: ${a.owner} | Type: ${a.type}
            </div>
        `;
        container.appendChild(d);
    });
}

function renderThreatPrediction(prediction) {
    const container = document.getElementById('ui-prediction');
    if (!container) return;
    container.innerHTML = '';
    if (!prediction) {
        container.innerHTML = '<div class="prediction-box">No predictions available.</div>';
        return;
    }
    
    const d = document.createElement('div');
    d.className = 'prediction-box';
    
    const actions = prediction.predicted_actions.map(a => `<li>${a}</li>`).join('');
    const reasoning = prediction.reasoning.map(r => `<li>${r}</li>`).join('');
    
    d.innerHTML = `
        <div class="prediction-title">Confidence: ${prediction.confidence}%</div>
        <div style="font-size:13px; margin-bottom:8px;"><strong>Next Likely Actions:</strong><ul>${actions}</ul></div>
        <div style="font-size:13px; color:var(--text-muted);"><strong>Reasoning:</strong><ul>${reasoning}</ul></div>
    `;
    container.appendChild(d);
}

function renderSecurityMemory(memory) {
    const container = document.getElementById('ui-security-memory');
    if (!container) return;
    container.innerHTML = '';
    if (!memory || !memory.similar_incidents || memory.similar_incidents.length === 0) {
        container.innerHTML = '<div class="memory-box">No similar incidents found.</div>';
        return;
    }
    
    memory.similar_incidents.forEach(inc => {
        const d = document.createElement('div');
        d.className = 'memory-box';
        d.innerHTML = `
            <div class="memory-title">Match: ${(inc.incident_similarity * 100).toFixed(0)}% Similarity</div>
            <div style="font-size:13px; margin-bottom:4px;"><strong>Pattern:</strong> ${inc.previous_pattern}</div>
            <div style="font-size:13px; margin-bottom:4px;"><strong>Threat Family:</strong> ${inc.known_attack_family}</div>
            <div style="font-size:13px; color:var(--text-muted);"><strong>Historical Response:</strong><br/> - ${inc.recommended_response.join('<br/> - ')}</div>
        `;
        container.appendChild(d);
    });
}

function renderPlaybook(playbook) {
    const container = document.getElementById('ui-playbook');
    if (!container) return;
    container.innerHTML = '';
    if (!playbook || playbook.length === 0) {
        container.innerHTML = '<div class="playbook-step">No automated playbook steps generated.</div>';
        return;
    }
    
    playbook.forEach(step => {
        const d = document.createElement('div');
        d.className = 'playbook-step';
        d.textContent = step;
        container.appendChild(d);
    });
}

function renderAttackStatus(status) {
    const el = document.getElementById('ui-live-status');
    if (!el) return;
    if (status) {
        el.textContent = status;
        el.style.display = 'block';
    } else {
        el.style.display = 'none';
    }
}

function renderAttackPath(pathNodes, edges) {
    const container = document.getElementById('ui-attack-path');
    if (!container) return;
    container.innerHTML = '';
    if (!pathNodes || pathNodes.length === 0) return;
    
    pathNodes.forEach((node, idx) => {
        const d = document.createElement('div');
        d.className = 'path-node';
        // if anomalies exist for this node, add 'anomaly' class
        // simplistic check:
        d.textContent = node;
        container.appendChild(d);
        
        if (idx < pathNodes.length - 1) {
            const link = document.createElement('div');
            link.className = 'path-link';
            // if edge is inferred, add 'inferred' class
            if (edges && edges[idx] && edges[idx].is_inferred) {
                link.classList.add('inferred');
            }
            container.appendChild(link);
        }
    });
}

function renderDefenseStatus(defenseSteps) {
    const container = document.getElementById('ui-autonomous-defense');
    if (!container) return;
    container.innerHTML = '';
    if (!defenseSteps) return;
    
    defenseSteps.forEach(step => {
        const d = document.createElement('div');
        d.className = 'defense-item';
        d.innerHTML = `<span class="defense-tick">✓</span> ${step}`;
        container.appendChild(d);
    });
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
    // Upgraded: Integrates directly with the simulation engine API
    const scenario = document.getElementById("scenario-select") ? document.getElementById("scenario-select").value : "APT";
    fetch(`/api/incident?scenario=${scenario}`)
        .then(res => res.json())
        .then(data => {
            if (data.risk) {
                renderDashboard(data);
            }
            if (window.renderAttackStatus) renderAttackStatus("ACTIVE ATTACK DETECTED");
            if (data.best_path && window.renderAttackPath) {
                renderAttackPath(data.best_path.nodes, data.best_path.edges);
            }
        })
        .catch(err => {
            console.error("Failed to run investigation", err);
        });
});
