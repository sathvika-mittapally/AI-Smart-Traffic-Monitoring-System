/* ==========================================================================
   Smart Traffic System - Client-Side Controller
   File: static/js/dashboard.js
   ========================================================================== */

let vehicleClassChart = null;
let trafficFlowChart = null;
let delayComparisonChart = null;

document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    startClock();
    startTelemetryPolling();
});

function startClock() {
    setInterval(() => {
        const now = new Date();
        document.getElementById('system-clock').innerText = now.toLocaleTimeString();
    }, 1000);
}

function initCharts() {
    // 1. Vehicle Breakdown
    const ctxClass = document.getElementById('vehicleClassChart').getContext('2d');
    vehicleClassChart = new Chart(ctxClass, {
        type: 'doughnut',
        data: {
            labels: ['Car', 'Bus', 'Truck', 'Motorcycle', 'Ambulance', 'Pedestrian'],
            datasets: [{
                data: [0, 0, 0, 0, 0, 0],
                backgroundColor: ['#3b82f6', '#f97316', '#a855f7', '#f59e0b', '#ef4444', '#0ea5e9'],
                borderColor: '#1e293b',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 10 } } }
            }
        }
    });

    // 2. Real-Time Flow Rate
    const ctxFlow = document.getElementById('trafficFlowChart').getContext('2d');
    trafficFlowChart = new Chart(ctxFlow, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Active Vehicles',
                data: [],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: true,
                tension: 0.3,
                pointRadius: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { ticks: { color: '#64748b', font: { size: 9 } }, grid: { color: '#1e293b' } },
                y: { beginAtZero: true, ticks: { color: '#64748b', stepSize: 2 }, grid: { color: '#1e293b' } }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });

    // 3. Delay Comparison
    const ctxDelay = document.getElementById('delayComparisonChart').getContext('2d');
    delayComparisonChart = new Chart(ctxDelay, {
        type: 'bar',
        data: {
            labels: ['Avg Delay (s)', 'Max Queue'],
            datasets: [
                {
                    label: 'Adaptive AI',
                    data: [13.5, 4],
                    backgroundColor: '#10b981'
                },
                {
                    label: 'Fixed-Timer Baseline',
                    data: [36.2, 12],
                    backgroundColor: '#64748b'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { display: false } },
                y: { ticks: { color: '#64748b' }, grid: { color: '#1e293b' } }
            },
            plugins: {
                legend: { labels: { color: '#94a3b8', font: { size: 10 } } }
            }
        }
    });
}

function startTelemetryPolling() {
    setInterval(async () => {
        try {
            const res = await fetch('/api/telemetry');
            if (!res.ok) return;
            const data = await res.json();
            updateUI(data);
        } catch (e) {
            console.error('Telemetry error:', e);
        }
    }, 500);
}

function updateUI(data) {
    // 1. Metric Cards
    document.getElementById('stat-active-vehicles').innerText = data.active_vehicle_count;
    document.getElementById('stat-total-vehicles').innerText = `Processed: ${data.cumulative_counted}`;
    document.getElementById('stat-avg-speed').innerHTML = `${data.average_speed_kmh} <span class="unit">km/h</span>`;
    document.getElementById('stat-speed-limit').innerText = `Urban limit: ${data.speed_limit} km/h`;
    
    const cong = data.congestion_index;
    document.getElementById('stat-congestion').innerText = `${cong}%`;
    document.getElementById('stat-congestion-bar').style.width = `${cong}%`;
    
    document.getElementById('stat-co2').innerHTML = `${data.signals.co2_saved_kg} <span class="unit">kg CO2</span>`;
    document.getElementById('stat-wait-saved').innerText = `Wait reduced: ${data.signals.wait_time_saved_sec}s`;
    document.getElementById('stat-violations').innerText = data.violations_count;
    
    document.getElementById('current-mode-label').innerText = 
        (data.signals.system_mode === 'AUTONOMOUS_AI') ? 'Autonomous AI' : 'Manual Control';

    // 2. Emergency Alert
    const emBanner = document.getElementById('emergency-banner');
    if (data.signals.emergency_mode) {
        emBanner.classList.remove('hidden');
        document.getElementById('emergency-banner-text').innerText = 
            `Emergency vehicle detected. Priority green wave active on ${data.signals.emergency_lane} approach.`;
    } else {
        emBanner.classList.add('hidden');
    }

    // 3. 4-Way Intersection Signals
    const signals = data.signals;
    document.getElementById('signal-phase-badge').innerText = `Phase: ${signals.phase} (${signals.countdown}s)`;
    document.getElementById('center-timer-text').innerText = signals.countdown;

    updateSignalLight('light-north', signals.North);
    updateSignalLight('light-south', signals.South);
    updateSignalLight('light-east', signals.East);
    updateSignalLight('light-west', signals.West);

    document.getElementById('density-north').innerText = signals.lane_densities.North.toFixed(1);
    document.getElementById('density-south').innerText = signals.lane_densities.South.toFixed(1);
    document.getElementById('density-east').innerText = signals.lane_densities.East.toFixed(1);
    document.getElementById('density-west').innerText = signals.lane_densities.West.toFixed(1);

    // 4. Lane Density Progress Bars
    updateLaneBar('north', signals.lane_vehicle_counts.North);
    updateLaneBar('south', signals.lane_vehicle_counts.South);
    updateLaneBar('east', signals.lane_vehicle_counts.East);
    updateLaneBar('west', signals.lane_vehicle_counts.West);

    // 5. Update Charts
    if (data.class_breakdown && vehicleClassChart) {
        const counts = [
            data.class_breakdown['Car'] || 0,
            data.class_breakdown['Bus'] || 0,
            data.class_breakdown['Truck'] || 0,
            data.class_breakdown['Motorcycle'] || 0,
            data.class_breakdown['Ambulance'] || 0,
            data.class_breakdown['Pedestrian'] || 0
        ];
        vehicleClassChart.data.datasets[0].data = counts;
        vehicleClassChart.update('none');
    }

    if (data.history && trafficFlowChart && data.history.timestamps.length > 0) {
        trafficFlowChart.data.labels = data.history.timestamps;
        trafficFlowChart.data.datasets[0].data = data.history.flow;
        trafficFlowChart.update('none');
    }

    if (data.history && delayComparisonChart && data.history.wait_ai.length > 0) {
        const latestAi = data.history.wait_ai[data.history.wait_ai.length - 1];
        const latestFixed = data.history.wait_fixed[data.history.wait_fixed.length - 1];
        delayComparisonChart.data.datasets[0].data = [latestAi, Math.max(1, Math.round(latestAi / 3))];
        delayComparisonChart.data.datasets[1].data = [latestFixed, Math.max(3, Math.round(latestFixed / 2.5))];
        delayComparisonChart.update('none');
    }

    // 6. Violations Table
    updateViolationsTable(data.violations);
}

function updateSignalLight(elemId, state) {
    const box = document.getElementById(elemId);
    if (!box) return;
    const r = box.querySelector('.red');
    const y = box.querySelector('.yellow');
    const g = box.querySelector('.green');

    r.classList.remove('active');
    y.classList.remove('active');
    g.classList.remove('active');

    if (state === 'RED') r.classList.add('active');
    else if (state === 'YELLOW') y.classList.add('active');
    else if (state === 'GREEN') g.classList.add('active');
}

function updateLaneBar(laneName, count) {
    const bar = document.getElementById(`bar-${laneName}`);
    const val = document.getElementById(`val-${laneName}`);
    if (bar && val) {
        const pct = Math.min(100, Math.max(8, (count / 8) * 100));
        bar.style.width = `${pct}%`;
        val.innerText = `${count} veh`;
    }
}

function updateViolationsTable(violations) {
    const tbody = document.getElementById('violations-tbody');
    if (!tbody || !violations) return;

    if (violations.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-center text-muted">No safety violations recorded. Traffic flow is compliant.</td></tr>`;
        return;
    }

    let html = '';
    violations.forEach(v => {
        html += `
            <tr>
                <td><strong>${v.incident_id}</strong></td>
                <td>${v.timestamp}</td>
                <td>#${v.vehicle_id}</td>
                <td>${v.vehicle_type}</td>
                <td>${v.speed_kmh} km/h</td>
                <td>${v.violation_type}</td>
                <td><span class="badge-pill ${v.severity}">${v.severity}</span></td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="openSnapshotModal('/violations/${v.snapshot}', '${v.violation_type} - Vehicle #${v.vehicle_id}')">
                        View
                    </button>
                </td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
}

// User Actions
async function changeVideoSource(sourceKey) {
    try {
        await fetch('/api/set_source', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ source: sourceKey })
        });
        document.getElementById('current-source-tag').innerText = `Source: ${sourceKey.charAt(0).toUpperCase() + sourceKey.slice(1)}`;
    } catch (e) {
        console.error(e);
    }
}

async function setSystemMode(mode) {
    try {
        await fetch('/api/set_mode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: mode })
        });
        
        document.querySelector('.btn-ai-mode').classList.toggle('active', mode === 'AUTONOMOUS_AI');
        document.querySelector('.btn-manual-mode').classList.toggle('active', mode === 'MANUAL_OVERRIDE');
        document.getElementById('manual-phase-row').style.display = (mode === 'MANUAL_OVERRIDE') ? 'flex' : 'none';
    } catch (e) {
        console.error(e);
    }
}

async function switchManualPhase(phase) {
    try {
        await fetch('/api/manual_signal', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phase: phase })
        });
    } catch (e) {
        console.error(e);
    }
}

async function triggerManualEmergency() {
    try {
        await fetch('/api/trigger_emergency', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lane: 'West' })
        });
    } catch (e) {
        console.error(e);
    }
}

async function updateSpeedLimit() {
    const limit = document.getElementById('speed-limit-input').value;
    try {
        await fetch('/api/set_speed_limit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ speed_limit: limit })
        });
        alert(`Speed threshold updated to ${limit} km/h.`);
    } catch (e) {
        console.error(e);
    }
}

async function uploadCustomVideo(input) {
    if (!input.files || !input.files[0]) return;
    const formData = new FormData();
    formData.append('video', input.files[0]);

    try {
        const res = await fetch('/api/upload_video', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        if (data.status === 'success') {
            document.getElementById('current-source-tag').innerText = `Source: Custom Upload`;
        }
    } catch (e) {
        console.error(e);
    }
}

async function downloadJSONReport() {
    const res = await fetch('/api/export_report');
    const data = await res.json();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `traffic_report_${new Date().toISOString().slice(0,10)}.json`;
    a.click();
}

async function downloadCSVReport() {
    const res = await fetch('/api/export_report');
    const data = await res.json();
    let csv = 'Incident_ID,Timestamp,Vehicle_ID,Vehicle_Type,Speed_KMH,Speed_Limit,Violation_Type,Lane\n';
    
    data.recent_violations_log.forEach(v => {
        csv += `"${v.incident_id}","${v.timestamp}","${v.vehicle_id}","${v.vehicle_type}","${v.speed_kmh}","${v.speed_limit}","${v.violation_type}","${v.lane}"\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `traffic_violations_${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
}

function openSnapshotModal(src, caption) {
    document.getElementById('modal-img').src = src;
    document.getElementById('modal-caption').innerText = caption;
    document.getElementById('snapshot-modal').style.display = 'flex';
}

function closeSnapshotModal() {
    document.getElementById('snapshot-modal').style.display = 'none';
}
