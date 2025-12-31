#!/usr/bin/env python3
"""
Pi Monitor Dashboard
====================
Lightweight web dashboard for monitoring Raspberry Pi fleets.
Run this on one Pi to monitor all others.

Usage:
    1. Edit MONITORED_HOSTS below with your Pi IPs
    2. Run: python3 pi_monitor_dashboard.py
    3. Open: http://<this-pi-ip>:8080
"""

import json
import socket
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import urlopen
from urllib.error import URLError
from datetime import datetime

# =============================================================================
# Configuration - EDIT THIS LIST
# =============================================================================

MONITORED_HOSTS = [
    # Add your Raspberry Pi IP addresses or hostnames here:
    # "192.168.1.100",
    # "192.168.1.101",
    # "pihole.local",
    # "octopi.local",
]

AGENT_PORT = 5555       # Port where agents are running
DASHBOARD_PORT = 8080   # Port for this web dashboard
POLL_INTERVAL = 5       # Seconds between metric polls

# =============================================================================
# Shared State
# =============================================================================

pi_data = {}
data_lock = threading.Lock()

# =============================================================================
# Metrics Collection
# =============================================================================


def fetch_metrics(host):
    """Fetch metrics from a Pi agent."""
    try:
        url = f"http://{host}:{AGENT_PORT}/metrics"
        with urlopen(url, timeout=3) as response:
            data = json.loads(response.read().decode())
            data['status'] = 'online'
            data['last_seen'] = datetime.now().isoformat()
            return data
    except URLError:
        return {'hostname': host, 'status': 'offline', 'ip': host}
    except Exception as e:
        return {'hostname': host, 'status': 'error', 'error': str(e), 'ip': host}


def poll_all_hosts():
    """Background thread to poll all configured hosts."""
    while True:
        for host in MONITORED_HOSTS:
            metrics = fetch_metrics(host)
            with data_lock:
                pi_data[host] = metrics
        time.sleep(POLL_INTERVAL)


# =============================================================================
# HTML Dashboard
# =============================================================================

DASHBOARD_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🍓 Pi Monitor</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
            padding: 20px;
        }

        h1 {
            text-align: center;
            margin-bottom: 10px;
            font-size: 2em;
        }

        .subtitle {
            text-align: center;
            color: #888;
            margin-bottom: 30px;
            font-size: 0.9em;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }

        .card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
        }

        .card.offline {
            opacity: 0.5;
            border-color: #e74c3c;
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .hostname {
            font-size: 1.3em;
            font-weight: 600;
        }

        .status {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75em;
            font-weight: 500;
            text-transform: uppercase;
        }

        .status.online { background: #27ae60; color: white; }
        .status.offline { background: #e74c3c; color: white; }

        .info-row {
            display: flex;
            justify-content: space-between;
            font-size: 0.85em;
            color: #888;
            margin-bottom: 15px;
        }

        .metrics {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }

        .metric {
            background: rgba(0, 0, 0, 0.2);
            padding: 12px;
            border-radius: 10px;
        }

        .metric-label {
            font-size: 0.75em;
            color: #888;
            margin-bottom: 5px;
        }

        .metric-value {
            font-size: 1.4em;
            font-weight: 600;
        }

        .metric-bar {
            height: 4px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 2px;
            margin-top: 8px;
            overflow: hidden;
        }

        .metric-fill {
            height: 100%;
            border-radius: 2px;
            transition: width 0.5s ease;
        }

        .fill-cpu { background: linear-gradient(90deg, #3498db, #9b59b6); }
        .fill-mem { background: linear-gradient(90deg, #27ae60, #2ecc71); }
        .fill-disk { background: linear-gradient(90deg, #e67e22, #f39c12); }
        .fill-temp { background: linear-gradient(90deg, #e74c3c, #c0392b); }

        .temp-warn { color: #f39c12; }
        .temp-hot { color: #e74c3c; }

        .uptime {
            text-align: center;
            padding: 10px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            margin-top: 15px;
            font-size: 0.85em;
        }

        .uptime span { color: #3498db; font-weight: 600; }

        .no-hosts {
            text-align: center;
            padding: 60px 20px;
            color: #888;
        }

        .no-hosts h2 { margin-bottom: 20px; }

        .no-hosts code {
            display: block;
            background: rgba(0, 0, 0, 0.3);
            padding: 20px;
            border-radius: 8px;
            margin: 20px auto;
            max-width: 400px;
            text-align: left;
            font-size: 0.9em;
            color: #3498db;
        }

        .last-update {
            text-align: center;
            color: #666;
            font-size: 0.8em;
            margin-top: 30px;
        }

        @media (max-width: 600px) {
            .metrics { grid-template-columns: 1fr; }
            .card { padding: 15px; }
        }
    </style>
</head>
<body>
    <h1>🍓 Pi Monitor</h1>
    <p class="subtitle">Real-time Raspberry Pi Fleet Dashboard</p>

    <div id="dashboard" class="grid"></div>
    <p class="last-update">Last update: <span id="timestamp">-</span></p>

    <script>
        function getTempClass(temp) {
            if (temp >= 70) return 'temp-hot';
            if (temp >= 60) return 'temp-warn';
            return '';
        }

        function createCard(pi) {
            if (pi.status === 'offline') {
                return `
                    <div class="card offline">
                        <div class="card-header">
                            <span class="hostname">${escapeHtml(pi.hostname || pi.ip)}</span>
                            <span class="status offline">Offline</span>
                        </div>
                        <p style="color: #888; text-align: center; padding: 20px;">
                            Unable to connect to agent
                        </p>
                    </div>
                `;
            }

            const cpu = pi.cpu || {};
            const mem = pi.memory || {};
            const disk = pi.disk || {};
            const temp = cpu.temperature;
            const tempClass = temp ? getTempClass(temp) : '';
            const model = pi.model ? pi.model.replace('Raspberry Pi ', 'Pi ') : '';

            return `
                <div class="card">
                    <div class="card-header">
                        <span class="hostname">${escapeHtml(pi.hostname)}</span>
                        <span class="status online">Online</span>
                    </div>
                    <div class="info-row">
                        <span>${escapeHtml(pi.ip)}</span>
                        <span>${escapeHtml(model)}</span>
                    </div>
                    <div class="metrics">
                        <div class="metric">
                            <div class="metric-label">CPU Usage</div>
                            <div class="metric-value">${cpu.usage_percent || 0}%</div>
                            <div class="metric-bar">
                                <div class="metric-fill fill-cpu" style="width: ${cpu.usage_percent || 0}%"></div>
                            </div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Temperature</div>
                            <div class="metric-value ${tempClass}">${temp ? temp + '°C' : 'N/A'}</div>
                            <div class="metric-bar">
                                <div class="metric-fill fill-temp" style="width: ${temp ? Math.min(temp, 85) / 85 * 100 : 0}%"></div>
                            </div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Memory</div>
                            <div class="metric-value">${mem.percent || 0}%</div>
                            <div class="metric-bar">
                                <div class="metric-fill fill-mem" style="width: ${mem.percent || 0}%"></div>
                            </div>
                        </div>
                        <div class="metric">
                            <div class="metric-label">Disk</div>
                            <div class="metric-value">${disk.percent || 0}%</div>
                            <div class="metric-bar">
                                <div class="metric-fill fill-disk" style="width: ${disk.percent || 0}%"></div>
                            </div>
                        </div>
                    </div>
                    <div class="uptime">⏱️ Uptime: <span>${escapeHtml(pi.uptime || 'unknown')}</span></div>
                </div>
            `;
        }

        function escapeHtml(text) {
            if (!text) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function showNoHosts() {
            return `
                <div class="no-hosts" style="grid-column: 1 / -1;">
                    <h2>No Raspberry Pis Configured</h2>
                    <p>Edit the dashboard script and add your Pi IP addresses:</p>
                    <code>
MONITORED_HOSTS = [<br>
&nbsp;&nbsp;&nbsp;&nbsp;"192.168.1.100",<br>
&nbsp;&nbsp;&nbsp;&nbsp;"192.168.1.101",<br>
&nbsp;&nbsp;&nbsp;&nbsp;"pihole.local",<br>
]
                    </code>
                    <p style="margin-top: 20px;">Make sure the agent is running on each Pi.</p>
                </div>
            `;
        }

        async function updateDashboard() {
            try {
                const response = await fetch('/api/metrics');
                const data = await response.json();
                const dashboard = document.getElementById('dashboard');

                if (Object.keys(data).length === 0) {
                    dashboard.innerHTML = showNoHosts();
                } else {
                    dashboard.innerHTML = Object.values(data)
                        .sort((a, b) => (a.hostname || '').localeCompare(b.hostname || ''))
                        .map(createCard)
                        .join('');
                }

                document.getElementById('timestamp').textContent =
                    new Date().toLocaleTimeString();
            } catch (error) {
                console.error('Failed to fetch metrics:', error);
            }
        }

        // Initial load and periodic refresh
        updateDashboard();
        setInterval(updateDashboard, 5000);
    </script>
</body>
</html>'''


# =============================================================================
# HTTP Server
# =============================================================================

class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP handler for dashboard and API endpoints."""

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode('utf-8'))

        elif self.path == '/api/metrics':
            with data_lock:
                response = json.dumps(pi_data)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(response.encode())

        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')


# =============================================================================
# Utilities
# =============================================================================

def get_local_ip():
    """Get local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "localhost"


# =============================================================================
# Main
# =============================================================================

def main():
    """Start the dashboard server."""
    local_ip = get_local_ip()

    print("=" * 50)
    print("🍓 Pi Monitor Dashboard")
    print("=" * 50)
    print(f"Dashboard:  http://{local_ip}:{DASHBOARD_PORT}")
    print(f"Monitoring: {len(MONITORED_HOSTS)} host(s)")
    print()

    if not MONITORED_HOSTS:
        print("⚠️  No hosts configured!")
        print("   Edit this file and add Pi IPs to MONITORED_HOSTS")
        print()
    else:
        print("Configured hosts:")
        for host in MONITORED_HOSTS:
            print(f"  • {host}")
        print()

    print("=" * 50)
    print("Press Ctrl+C to stop")
    print()

    # Start background polling thread
    if MONITORED_HOSTS:
        poller = threading.Thread(target=poll_all_hosts, daemon=True)
        poller.start()

    # Start web server
    server = HTTPServer(('0.0.0.0', DASHBOARD_PORT), DashboardHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        server.shutdown()


if __name__ == '__main__':
    main()
