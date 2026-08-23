// The backend does not currently have an endpoint for the command center demo,
// so in a real integration we'd expose `/api/command_center`.
// For the sake of this visualization within the static UI, we simulate the fetch 
// or require the backend to run it. 
// Since we want the frontend to display the data, let's just make a mock update function
// that would normally consume the JSON from `demo/run_command_center.py`.

// Helper to update the UI
function renderDashboard(data) {
    if (!data) return;
    
    // Risk Meter
    const rs = document.getElementById('ui-risk-score');
    const sev = document.getElementById('ui-severity');
    rs.textContent = data.risk.risk_score;
    sev.textContent = data.risk.severity;
    
    let color = 'var(--text)';
    if (data.risk.severity === 'CRITICAL') color = 'var(--accent-red)';
    if (data.risk.severity === 'HIGH') color = 'var(--accent-amber)';
    if (data.risk.severity === 'MEDIUM') color = 'var(--accent-blue)';
    if (data.risk.severity === 'LOW') color = 'var(--accent-green)';
    
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
        {q: "How did the attack unfold?", a: data.copilot.how},
        {q: "What should we do next?", a: data.copilot.what_next}
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
    
    // Timeline
    const timelineContainer = document.getElementById('ui-timeline');
    timelineContainer.innerHTML = '';
    data.timeline.forEach(t => {
        const d = document.createElement('div');
        d.className = 'timeline-item';
        d.innerHTML = `
            <div class="timeline-time">+${t.timestamp.toFixed(1)}s</div>
            <div class="timeline-event">${t.event}</div>
            <div class="timeline-nodes">${t.source} &rarr; ${t.destination || 'N/A'}</div>
        `;
        timelineContainer.appendChild(d);
    });
}

document.getElementById('btn-run').addEventListener('click', () => {
    // In the prototype without a specific FastAPI endpoint for this, 
    // we would call fetch('/api/command_center') here.
    alert("This prototype UI triggers the Python demo script in the terminal. See run_command_center.py output for live data integration.");
});
