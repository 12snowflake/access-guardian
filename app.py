from datetime import date
import json

from flask import Flask, render_template_string
from models import session, Account, AuditLog

app = Flask(__name__)

PAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Access Guardian Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>

    <style>

        * { box-sizing: border-box; }

        body {
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            padding: 30px;
        }

        h1 {
            color: #1a1a2e;
        }

        h2 {
            color: #333;
            margin-top: 40px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        table {
            border-collapse: collapse;
            width: 100%;
            background: white;
            box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        }

        th, td {
            padding: 10px 14px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }

        th {
            background: #1a1a2e;
            color: white;
        }

        tr.acc-row:hover { background: #fafcff; cursor: pointer; }

        .active{ color:green; font-weight:bold; }
        .revoked{ color:red; font-weight:bold; }
        .suspicious_attempt{ color:red; font-weight:bold; }
        .auto_revoke{ color:#ff8c00; font-weight:bold; }
        .low{ color:green; font-weight:bold; }
        .medium{ color:orange; font-weight:bold; }
        .high{ color:#ff6600; font-weight:bold; }
        .critical{ color:red; font-weight:bold; }

        /* --- Alert Banner --- */
        .alert-banner {
            background: #d90429;
            color: white;
            padding: 14px 20px;
            border-radius: 8px;
            font-weight: bold;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 2px 6px rgba(217,4,41,0.4);
        }

        /* --- Dashboard Cards --- */

        .cards-container {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-top: 16px;
        }

        .card {
            background: white;
            border-radius: 10px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.1);
            padding: 18px 20px;
            border-left: 5px solid #1a1a2e;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .card-icon { font-size: 28px; opacity: 0.85; }

        .card-label {
            font-size: 13px;
            color: #777;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }

        .card-value {
            font-size: 32px;
            font-weight: bold;
            color: #1a1a2e;
        }

        .card.total { border-left-color: #1a1a2e; }
        .card.privileged { border-left-color: #2b6cb0; }
        .card.critical { border-left-color: #d90429; }
        .card.critical .card-value { color: #d90429; }
        .card.threats { border-left-color: #ff8c00; }
        .card.threats .card-value { color: #ff8c00; }

        /* --- Charts --- */
        .charts-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-top: 16px;
        }

        .chart-card {
            background: white;
            border-radius: 10px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.1);
            padding: 18px 20px;
        }

        .chart-card h3 {
            margin-top: 0;
            color: #1a1a2e;
            font-size: 15px;
        }

        /* --- Business Impact Panel --- */
        .impact-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 14px;
            margin-top: 16px;
        }

        .impact-card {
            background: white;
            border-radius: 10px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.1);
            padding: 16px 18px;
            border-top: 4px solid #d90429;
        }

        .impact-card.high { border-top-color: #ff6600; }

        .impact-card .impact-name {
            font-weight: bold;
            color: #1a1a2e;
            display: flex;
            justify-content: space-between;
        }

        .impact-card .impact-org { color: #777; font-size: 13px; margin-bottom: 8px; }
        .impact-card .impact-text { font-size: 14px; color: #444; }
        .impact-card .impact-reco {
            margin-top: 10px;
            font-size: 13px;
            background: #f4f6f8;
            border-left: 3px solid #2b6cb0;
            padding: 6px 10px;
            border-radius: 4px;
        }

        .empty-note { color: #888; font-style: italic; margin-top: 10px; }

        /* --- Search / Filters --- */
        .toolbar {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-top: 16px;
            margin-bottom: 4px;
            align-items: center;
        }

        .toolbar input[type="text"], .toolbar select {
            padding: 9px 12px;
            border-radius: 6px;
            border: 1px solid #ccd3da;
            font-size: 14px;
            background: white;
        }

        .toolbar input[type="text"] { min-width: 220px; }

        .toolbar .result-count { color: #777; font-size: 13px; margin-left: auto; }

        /* --- Badges --- */
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }

        .badge.normal { background: #e6f4ea; color: #1e7e34; }
        .badge.unusual { background: #fff4e0; color: #b76e00; }
        .badge.suspicious { background: #fde2e2; color: #c0392b; }

        /* --- Expandable detail row --- */
        tr.detail-row { display: none; background: #fbfcfe; }
        tr.detail-row.open { display: table-row; }
        tr.detail-row td { padding: 16px 20px; }

        .detail-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 14px;
        }

        .detail-block h4 {
            margin: 0 0 6px 0;
            font-size: 13px;
            text-transform: uppercase;
            color: #777;
            letter-spacing: 0.5px;
        }

        .detail-block p, .detail-block ul { margin: 0; font-size: 14px; color: #333; }
        .detail-block ul { padding-left: 18px; }
        .toggle-btn {
            border: none;
            background: #1a1a2e;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 12px;
            cursor: pointer;
        }

        /* --- Security Actions Panel --- */
        .actions-list { margin-top: 16px; display: flex; flex-direction: column; gap: 10px; }

        .action-item {
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.1);
            padding: 12px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
        }

        .action-item .who { font-weight: bold; color: #1a1a2e; }
        .action-item .what { color: #444; font-size: 14px; }
        .action-item .org-tag { color: #888; font-size: 12px; }

        /* --- Threat Timeline --- */

        .timeline {
            position: relative;
            margin-top: 24px;
            padding-left: 30px;
        }

        .timeline::before {
            content: '';
            position: absolute;
            left: 9px;
            top: 6px;
            bottom: 6px;
            width: 2px;
            background: #ddd;
        }

        .timeline-item {
            position: relative;
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.1);
            padding: 12px 16px;
            margin-bottom: 16px;
        }

        .timeline-item::before {
            content: '';
            position: absolute;
            left: -25px;
            top: 18px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #1a1a2e;
            border: 2px solid white;
            box-shadow: 0 0 0 2px #ddd;
        }

        .timeline-item.suspicious_attempt::before { background: red; }
        .timeline-item.auto_revoke::before { background: #ff8c00; }

        .timeline-time { font-size: 13px; color: #888; font-weight: bold; }

        .timeline-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .timeline-account { font-size: 13px; color: #555; }
        .timeline-event { font-size: 16px; margin: 4px 0; }
        .timeline-details { font-size: 14px; color: #555; }

        /* --- Flowchart --- */
        .flowchart {
            background: white;
            border-radius: 10px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.1);
            padding: 30px;
            margin-top: 16px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .fc-node {
            padding: 10px 18px;
            border-radius: 8px;
            color: white;
            font-weight: bold;
            font-size: 14px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.15);
            min-width: 180px;
        }

        .fc-arrow { color: #999; font-size: 20px; line-height: 1.2; }

        .fc-navy   { background: #1a1a2e; }
        .fc-blue   { background: #2b6cb0; }
        .fc-purple { background: #6a4c93; }
        .fc-amber  { background: #ff8c00; }
        .fc-green  { background: #1e7e34; }
        .fc-orange { background: #e67700; }
        .fc-red    { background: #d90429; }

        .fc-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 24px;
            width: 100%;
            max-width: 720px;
            margin: 6px 0;
        }

        .fc-row .fc-node { width: 100%; }
        .fc-col { display: flex; flex-direction: column; align-items: center; gap: 4px; }

    </style>

</head>

<body>

{% if critical_risk > 0 %}
<div class="alert-banner">
    ⚠️ {{ critical_risk }} account(s) at CRITICAL risk — immediate review recommended.
</div>
{% endif %}

<h1>🔐 Access Guardian</h1>

<p>
Auto-expiring privileged access monitor for third-party vendor accounts
</p>

<h2>📊 Overview</h2>

<div class="cards-container">

    <div class="card total">
        <div>
            <div class="card-label">Total Accounts</div>
            <div class="card-value">{{ total_accounts }}</div>
        </div>
        <div class="card-icon">👥</div>
    </div>

    <div class="card privileged">
        <div>
            <div class="card-label">Privileged Accounts</div>
            <div class="card-value">{{ privileged_accounts }}</div>
        </div>
        <div class="card-icon">🛡️</div>
    </div>

    <div class="card critical">
        <div>
            <div class="card-label">Critical Risk</div>
            <div class="card-value">{{ critical_risk }}</div>
        </div>
        <div class="card-icon">🚨</div>
    </div>

    <div class="card threats">
        <div>
            <div class="card-label">Threats Today</div>
            <div class="card-value">{{ threats_today }}</div>
        </div>
        <div class="card-icon">⚡</div>
    </div>

</div>

<div class="charts-container">
    <div class="chart-card">
        <h3>🟢🔴 Active vs Revoked</h3>
        <canvas id="statusPie" height="180"></canvas>
    </div>
    <div class="chart-card">
        <h3>📶 Accounts by Risk Level</h3>
        <canvas id="riskBar" height="180"></canvas>
    </div>
</div>

<h2>💥 Business Impact Panel</h2>

<div class="impact-grid">
{% for acc in accounts %}
    {% if acc.risk_level.lower() in ["critical", "high"] %}
    <div class="impact-card {{ acc.risk_level.lower() }}">
        <div class="impact-name"><span>{{ acc.name }}</span><span class="{{ acc.risk_level.lower() }}">{{ acc.risk_level }}</span></div>
        <div class="impact-org">{{ acc.org }} &middot; {{ acc.role }}</div>
        <div class="impact-text">{{ acc.business_impact }}</div>
        <div class="impact-reco">🤖 {{ acc.ai_recommendation }}</div>
    </div>
    {% endif %}
{% endfor %}
</div>
{% if critical_risk == 0 and high_risk == 0 %}
<p class="empty-note">No high/critical business-impact accounts right now.</p>
{% endif %}

<h2>👤 Account Status</h2>

<div class="toolbar">
    <input type="text" id="searchInput" placeholder="🔍 Search employee by name...">

    <select id="statusFilter">
        <option value="all">All Statuses</option>
        <option value="active">Active</option>
        <option value="revoked">Revoked</option>
    </select>

    <select id="riskFilter">
        <option value="all">All Risk Levels</option>
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
        <option value="critical">Critical</option>
    </select>

    <select id="orgFilter">
        <option value="all">All Organizations</option>
        {% for org in orgs %}
        <option value="{{ org }}">{{ org }}</option>
        {% endfor %}
    </select>

    <span class="result-count" id="resultCount"></span>
</div>

<table id="accountsTable">

<tr>
    <th>Name</th>
    <th>Organization</th>
    <th>Role</th>
    <th>Access Level</th>
    <th>Contract End</th>
    <th>Status</th>
    <th>Login Behaviour</th>
    <th>Risk Score</th>
    <th>Risk Level</th>
    <th></th>
</tr>

{% for acc in accounts %}

<tr class="acc-row" data-name="{{ acc.name.lower() }}" data-status="{{ acc.status }}" data-risk="{{ acc.risk_level.lower() }}" data-org="{{ acc.org }}" onclick="toggleDetail('detail-{{ acc.id }}')">

    <td>{{ acc.name }}</td>
    <td>{{ acc.org }}</td>
    <td>{{ acc.role }}</td>
    <td>{{ acc.access_level }}</td>
    <td>{{ acc.contract_end }}</td>

    <td class="{{ acc.status }}">{{ acc.status.upper() }}</td>

    <td>
        {% if acc.login_behaviour == "Suspicious" %}
        <span class="badge suspicious">🚨 Suspicious</span>
        {% elif acc.login_behaviour == "Unusual" %}
        <span class="badge unusual">⚠️ Unusual</span>
        {% else %}
        <span class="badge normal">✅ Normal</span>
        {% endif %}
    </td>

    <td>{{ acc.risk_score }}</td>

    <td class="{{ acc.risk_level.lower() }}">{{ acc.risk_level }}</td>

    <td><button class="toggle-btn" onclick="event.stopPropagation(); toggleDetail('detail-{{ acc.id }}')">Details</button></td>

</tr>

<tr class="detail-row" id="detail-{{ acc.id }}">
    <td colspan="10">
        <div class="detail-grid">
            <div class="detail-block">
                <h4>🧠 Risk Reasons</h4>
                <ul>
                {% for reason in (acc.risk_reasons or 'No risk factors detected').split(' | ') %}
                    <li>{{ reason }}</li>
                {% endfor %}
                </ul>
            </div>
            <div class="detail-block">
                <h4>🛠️ Security Actions Taken</h4>
                <ul>
                {% for action in (acc.security_actions or 'No action taken').split(' | ') %}
                    <li>{{ action }}</li>
                {% endfor %}
                </ul>
            </div>
            <div class="detail-block">
                <h4>🤖 AI Recommendation</h4>
                <p>{{ acc.ai_recommendation }}</p>
            </div>
            <div class="detail-block">
                <h4>💥 Business Impact</h4>
                <p>{{ acc.business_impact }}</p>
            </div>
        </div>
    </td>
</tr>

{% endfor %}

</table>

<h2>🛠️ Security Actions Taken</h2>

<div class="actions-list">
{% for acc in accounts %}
    <div class="action-item">
        <div>
            <div class="who">{{ acc.name }} <span class="org-tag">&middot; {{ acc.org }}</span></div>
            <div class="what">{{ acc.security_actions }}</div>
        </div>
        <span class="badge {{ 'suspicious' if acc.risk_level == 'Critical' else ('unusual' if acc.risk_level == 'High' else 'normal') }}">{{ acc.risk_level }}</span>
    </div>
{% endfor %}
</div>

<h2>📜 Threat Timeline</h2>

<div class="timeline">

{% for log in logs %}

<div class="timeline-item {{ log.event_type }}">

    <div class="timeline-header">
        <span class="timeline-time">{{ log.timestamp }}</span>
        <span class="timeline-account">{{ log.account_name }} &middot; {{ log.org }}</span>
    </div>

    <div class="timeline-event {{ log.event_type }}">
        {{ log.event_type.replace('_', ' ').title() }}
    </div>

    <div class="timeline-details">
        {{ log.details }}
    </div>

</div>

{% endfor %}

</div>

<h2>🗺️ Access Control Flowchart</h2>

<div class="flowchart">

    <div class="fc-node fc-navy">USER LOGIN REQUEST</div>
    <div class="fc-arrow">▼</div>
    <div class="fc-node fc-navy">Identity Verification</div>
    <div class="fc-arrow">▼</div>
    <div class="fc-node fc-navy">Fetch User Information</div>
    <div class="fc-arrow">▼</div>
    <div class="fc-node fc-purple">Behaviour Analysis Engine</div>
    <div class="fc-arrow">▼</div>

    <div class="fc-row">
        <div class="fc-col">
            <div class="fc-node fc-blue">Contract Check</div>
            <div class="fc-arrow">▼</div>
            <div class="fc-node fc-amber">Expired?</div>
        </div>
        <div class="fc-col">
            <div class="fc-node fc-blue">Access Level</div>
            <div class="fc-arrow">▼</div>
            <div class="fc-node fc-amber">Privileged?</div>
        </div>
        <div class="fc-col">
            <div class="fc-node fc-blue">Login Behaviour</div>
            <div class="fc-arrow">▼</div>
            <div class="fc-node fc-amber">Suspicious?</div>
        </div>
    </div>

    <div class="fc-arrow">▼</div>
    <div class="fc-node fc-purple">AI Risk Score Engine</div>
    <div class="fc-arrow">▼</div>
    <div class="fc-node fc-purple">Risk Score (0–100)</div>
    <div class="fc-arrow">▼</div>

    <div class="fc-row">
        <div class="fc-col">
            <div class="fc-node fc-green">Low</div>
            <div class="fc-arrow">▼</div>
            <div class="fc-node fc-green">Allow Access</div>
        </div>
        <div class="fc-col">
            <div class="fc-node fc-orange">Medium</div>
            <div class="fc-arrow">▼</div>
            <div class="fc-node fc-orange">Monitor User</div>
        </div>
        <div class="fc-col">
            <div class="fc-node fc-red">Critical</div>
            <div class="fc-arrow">▼</div>
            <div class="fc-node fc-red">Auto Revoke</div>
        </div>
    </div>

    <div class="fc-arrow">▼</div>
    <div class="fc-node fc-navy">Audit Log Created</div>
    <div class="fc-arrow">▼</div>
    <div class="fc-node fc-navy">Security Dashboard</div>

</div>

<script>
    // --- Search + Filters ---
    const searchInput = document.getElementById('searchInput');
    const statusFilter = document.getElementById('statusFilter');
    const riskFilter = document.getElementById('riskFilter');
    const orgFilter = document.getElementById('orgFilter');
    const resultCount = document.getElementById('resultCount');

    function applyFilters() {
        const term = searchInput.value.toLowerCase();
        const status = statusFilter.value;
        const risk = riskFilter.value;
        const org = orgFilter.value;

        const rows = document.querySelectorAll('#accountsTable tr.acc-row');
        let visible = 0;

        rows.forEach(row => {
            const matchesName = row.dataset.name.includes(term);
            const matchesStatus = (status === 'all' || row.dataset.status === status);
            const matchesRisk = (risk === 'all' || row.dataset.risk === risk);
            const matchesOrg = (org === 'all' || row.dataset.org === org);

            const show = matchesName && matchesStatus && matchesRisk && matchesOrg;
            row.style.display = show ? '' : 'none';

            const detailRow = row.nextElementSibling;
            if (detailRow && detailRow.classList.contains('detail-row') && !show) {
                detailRow.classList.remove('open');
                detailRow.style.display = 'none';
            }

            if (show) visible++;
        });

        resultCount.textContent = visible + ' account(s) shown';
    }

    searchInput.addEventListener('input', applyFilters);
    statusFilter.addEventListener('change', applyFilters);
    riskFilter.addEventListener('change', applyFilters);
    orgFilter.addEventListener('change', applyFilters);
    applyFilters();

    // --- Expand/collapse detail rows ---
    function toggleDetail(id) {
        const row = document.getElementById(id);
        if (!row) return;
        const isOpen = row.classList.contains('open');
        row.classList.toggle('open', !isOpen);
        row.style.display = !isOpen ? 'table-row' : 'none';
    }

    // --- Charts ---
    const statusData = {{ status_chart | tojson }};
    const riskData = {{ risk_chart | tojson }};

    new Chart(document.getElementById('statusPie'), {
        type: 'doughnut',
        data: {
            labels: ['Active', 'Revoked'],
            datasets: [{
                data: [statusData.active, statusData.revoked],
                backgroundColor: ['#1e7e34', '#d90429']
            }]
        },
        options: { plugins: { legend: { position: 'bottom' } } }
    });

    new Chart(document.getElementById('riskBar'), {
        type: 'bar',
        data: {
            labels: ['Low', 'Medium', 'High', 'Critical'],
            datasets: [{
                label: 'Accounts',
                data: [riskData.low, riskData.medium, riskData.high, riskData.critical],
                backgroundColor: ['#1e7e34', '#e67700', '#ff6600', '#d90429']
            }]
        },
        options: {
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
        }
    });
</script>

</body>
</html>
"""


@app.route("/")
def dashboard():

    accounts = session.query(Account).all()

    logs = (
        session.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .all()
    )

    # --- Dashboard card metrics ---

    total_accounts = len(accounts)

    # NOTE: adjust these access_level strings to match your models.py values
    privileged_levels = {"privileged", "admin", "elevated"}
    privileged_accounts = sum(
        1
        for acc in accounts
        if acc.access_level and acc.access_level.lower() in privileged_levels
    )

    critical_risk = sum(
        1
        for acc in accounts
        if acc.risk_level and acc.risk_level.lower() == "critical"
    )

    high_risk = sum(
        1
        for acc in accounts
        if acc.risk_level and acc.risk_level.lower() == "high"
    )

    # NOTE: adjust these event_type strings to match what counts as a "threat" for you
    threat_event_types = {"suspicious_attempt", "auto_revoke"}
    today = date.today()
    threats_today = sum(
        1
        for log in logs
        if log.event_type in threat_event_types and log.timestamp.date() == today
    )

    # --- Chart data ---
    status_chart = {
        "active": sum(1 for acc in accounts if acc.status == "active"),
        "revoked": sum(1 for acc in accounts if acc.status == "revoked"),
    }

    risk_chart = {
        "low": sum(1 for acc in accounts if (acc.risk_level or "Low").lower() == "low"),
        "medium": sum(1 for acc in accounts if (acc.risk_level or "").lower() == "medium"),
        "high": sum(1 for acc in accounts if (acc.risk_level or "").lower() == "high"),
        "critical": sum(1 for acc in accounts if (acc.risk_level or "").lower() == "critical"),
    }

    # --- Filter dropdown data ---
    orgs = sorted({acc.org for acc in accounts if acc.org})

    return render_template_string(
        PAGE_TEMPLATE,
        accounts=accounts,
        logs=logs,
        total_accounts=total_accounts,
        privileged_accounts=privileged_accounts,
        critical_risk=critical_risk,
        high_risk=high_risk,
        threats_today=threats_today,
        status_chart=status_chart,
        risk_chart=risk_chart,
        orgs=orgs,
    )


if __name__ == "__main__":
    app.run(debug=True)
