# Pi Monitor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![No Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)]()

A lightweight, zero-dependency monitoring system for Raspberry Pi fleets. View CPU, memory, disk, and temperature metrics from all your Pis in a beautiful web dashboard.

<!-- Dashboard screenshot placeholder - add your own screenshot here -->
<!-- ![Dashboard Preview](docs/dashboard-preview.png) -->

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Quick Install (Recommended)](#quick-install-recommended)
  - [Manual Installation](#manual-installation)
  - [Running as a Service](#running-as-a-service)
- [Configuration](#configuration)
  - [Agent Configuration](#agent-configuration)
  - [Dashboard Configuration](#dashboard-configuration)
- [Usage](#usage)
  - [Starting the Agent](#starting-the-agent)
  - [Starting the Dashboard](#starting-the-dashboard)
  - [Managing Services](#managing-services)
- [API Documentation](#api-documentation)
  - [Agent API](#agent-api)
  - [Dashboard API](#dashboard-api)
- [Troubleshooting](#troubleshooting)
- [Resource Usage](#resource-usage)
- [Security Considerations](#security-considerations)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Overview

Pi Monitor is designed for hobbyists and system administrators who want to keep an eye on their Raspberry Pi fleet without the complexity and resource overhead of traditional monitoring solutions like Prometheus or Grafana.

**Why Pi Monitor?**

- **Zero external dependencies**: Uses only Python standard library - no pip packages needed
- **Minimal footprint**: Agent uses ~5MB RAM, dashboard uses ~8MB RAM
- **Simple deployment**: Single Python file per component
- **Works everywhere**: Runs on Pi Zero through Pi 5

## Features

| Feature | Description |
|---------|-------------|
| **Real-time Metrics** | CPU usage, temperature, memory, disk, load average, and uptime |
| **Zero Dependencies** | Only requires Python 3.7+ standard library |
| **Lightweight** | Agent: ~5MB RAM, Dashboard: ~8MB RAM |
| **Auto-refresh** | Dashboard updates every 5 seconds |
| **Responsive UI** | Works on desktop, tablet, and mobile browsers |
| **Systemd Integration** | Runs as a service, starts automatically on boot |
| **Easy Configuration** | Simple Python variables - no YAML or JSON configs |
| **Visual Indicators** | Color-coded status, temperature warnings, progress bars |

### Metrics Collected

| Metric | Description | Source |
|--------|-------------|--------|
| CPU Usage | Real-time percentage (0-100%) | `/proc/stat` |
| CPU Temperature | Temperature in Celsius | `/sys/class/thermal/thermal_zone0/temp` |
| Memory | Total, Used, Available, Percentage | `/proc/meminfo` |
| Disk | Total, Used, Free, Percentage | `os.statvfs('/')` |
| Load Average | 1, 5, 15 minute averages | `/proc/loadavg` |
| Uptime | Human-readable format (e.g., "5d 3h 22m") | `/proc/uptime` |
| Pi Model | Hardware model identifier | `/proc/device-tree/model` |
| Network IP | Primary local IP address | Socket detection |

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Pi Zero #1    │     │   Pi 4 #1       │     │   Pi 5 #1       │
│  (Agent :5555)  │     │  (Agent :5555)  │     │  (Agent :5555)  │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │ HTTP polling (every 5s)
                    ┌────────────▼────────────┐
                    │   Dashboard Server      │
                    │      (Port 8080)        │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Web Browser           │
                    │   Any device on LAN     │
                    └─────────────────────────┘
```

**How it works:**

1. **Agent** runs on each Raspberry Pi you want to monitor, exposing metrics via HTTP
2. **Dashboard** runs on one Pi (or any Linux machine), polling all agents every 5 seconds
3. **Web Browser** connects to the dashboard to view real-time metrics

## Prerequisites

### System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.7+ | 3.9+ |
| OS | Raspberry Pi OS (any version) | Latest Raspberry Pi OS |
| RAM | 512MB | 1GB+ |
| Network | LAN connectivity between Pis | - |

### Supported Hardware

- Raspberry Pi Zero / Zero W / Zero 2 W
- Raspberry Pi 3 Model A+ / B / B+
- Raspberry Pi 4 Model B (all RAM variants)
- Raspberry Pi 5
- Any Linux system with `/proc` and `/sys` filesystems

### Checking Prerequisites

```bash
# Check Python version (must be 3.7 or higher)
python3 --version

# Verify network connectivity between Pis
ping <other-pi-ip>
```

## Installation

### Quick Install (Recommended)

Clone the repository and use the installation script:

```bash
# Clone the repository (replace with your fork URL if applicable)
git clone https://github.com/JGRSGIS/pi-monitor.git
cd pi-monitor

# Install agent on each Pi you want to monitor
sudo ./install.sh agent

# Install dashboard on one Pi (your "monitoring server")
sudo ./install.sh dashboard

# Verify the installation
curl http://localhost:5555/metrics    # Test agent (should return JSON)
curl http://localhost:8080            # Test dashboard (should return HTML)
```

The install script will:

- Copy files to `/opt/pi-monitor/`
- Install systemd service files
- Enable and start the service automatically

### Manual Installation

#### Step 1: Install the Agent (on each Pi to monitor)

```bash
# Create installation directory
sudo mkdir -p /opt/pi-monitor

# Option A: Download the agent script directly
sudo curl -o /opt/pi-monitor/pi_monitor_agent.py \
    https://raw.githubusercontent.com/JGRSGIS/pi-monitor/main/agent/pi_monitor_agent.py

# Option B: Or copy from cloned repository
# sudo cp agent/pi_monitor_agent.py /opt/pi-monitor/

# Make it executable
sudo chmod +x /opt/pi-monitor/pi_monitor_agent.py

# Test the agent (runs in foreground, Ctrl+C to stop)
python3 /opt/pi-monitor/pi_monitor_agent.py
```

Verify it works by visiting `http://<pi-ip>:5555/metrics` in your browser or running:

```bash
curl http://localhost:5555/metrics
```

#### Step 2: Install the Dashboard (on one Pi)

```bash
# Create installation directory
sudo mkdir -p /opt/pi-monitor

# Option A: Download the dashboard script directly
sudo curl -o /opt/pi-monitor/pi_monitor_dashboard.py \
    https://raw.githubusercontent.com/JGRSGIS/pi-monitor/main/dashboard/pi_monitor_dashboard.py

# Option B: Or copy from cloned repository
# sudo cp dashboard/pi_monitor_dashboard.py /opt/pi-monitor/

# Make it executable
sudo chmod +x /opt/pi-monitor/pi_monitor_dashboard.py

# Configure monitored hosts (see Configuration section)
sudo nano /opt/pi-monitor/pi_monitor_dashboard.py

# Start the dashboard (runs in foreground, Ctrl+C to stop)
python3 /opt/pi-monitor/pi_monitor_dashboard.py
```

Visit `http://<dashboard-pi-ip>:8080` to see the dashboard.

#### Running Without Systemd

If your system doesn't use systemd (Docker containers, WSL, older systems), you can run the scripts directly:

```bash
# Run agent in background
nohup python3 /opt/pi-monitor/pi_monitor_agent.py > /var/log/pi-monitor-agent.log 2>&1 &

# Run dashboard in background
nohup python3 /opt/pi-monitor/pi_monitor_dashboard.py > /var/log/pi-monitor-dashboard.log 2>&1 &

# Check if running
pgrep -f pi_monitor

# Stop the services
pkill -f pi_monitor_agent.py
pkill -f pi_monitor_dashboard.py
```

### Running as a Service

To run Pi Monitor automatically on boot:

#### Agent Service

```bash
# Download service file
sudo curl -o /etc/systemd/system/pi-monitor-agent.service \
    https://raw.githubusercontent.com/JGRSGIS/pi-monitor/main/agent/pi-monitor-agent.service

# Reload systemd, enable, and start
sudo systemctl daemon-reload
sudo systemctl enable pi-monitor-agent
sudo systemctl start pi-monitor-agent

# Verify it's running
sudo systemctl status pi-monitor-agent
```

#### Dashboard Service

```bash
# Download service file
sudo curl -o /etc/systemd/system/pi-monitor-dashboard.service \
    https://raw.githubusercontent.com/JGRSGIS/pi-monitor/main/dashboard/pi-monitor-dashboard.service

# Reload systemd, enable, and start
sudo systemctl daemon-reload
sudo systemctl enable pi-monitor-dashboard
sudo systemctl start pi-monitor-dashboard

# Verify it's running
sudo systemctl status pi-monitor-dashboard
```

## Configuration

### Agent Configuration

Edit `/opt/pi-monitor/pi_monitor_agent.py` to change settings:

```python
# =============================================================================
# Configuration
# =============================================================================

PORT = 5555  # HTTP port for metrics endpoint (default: 5555)
```

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PORT` | int | `5555` | TCP port for the metrics HTTP endpoint |

After changing configuration, restart the service:

```bash
sudo systemctl restart pi-monitor-agent
```

### Dashboard Configuration

Edit `/opt/pi-monitor/pi_monitor_dashboard.py` to configure:

```python
# =============================================================================
# Configuration - EDIT THIS LIST
# =============================================================================

MONITORED_HOSTS = [
    # Add your Raspberry Pi IP addresses or hostnames here:
    "192.168.1.100",    # Living room Pi
    "192.168.1.101",    # Garage Pi
    "pihole.local",     # Pi-hole server
    "octopi.local",     # 3D printer controller
]

AGENT_PORT = 5555       # Port where agents are running
DASHBOARD_PORT = 8080   # Port for this web dashboard
POLL_INTERVAL = 5       # Seconds between metric polls
```

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MONITORED_HOSTS` | list | `[]` | List of IP addresses or hostnames to monitor |
| `AGENT_PORT` | int | `5555` | Port where agents are listening |
| `DASHBOARD_PORT` | int | `8080` | Port for the web dashboard |
| `POLL_INTERVAL` | int | `5` | Seconds between polling each agent |

After changing configuration, restart the service:

```bash
sudo systemctl restart pi-monitor-dashboard
```

### Firewall Configuration

If using `ufw` (Uncomplicated Firewall):

```bash
# On monitored Pis (allow agent connections)
sudo ufw allow 5555/tcp

# On dashboard Pi (allow web access)
sudo ufw allow 8080/tcp
```

If using `iptables`:

```bash
# On monitored Pis
sudo iptables -A INPUT -p tcp --dport 5555 -j ACCEPT

# On dashboard Pi
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
```

## Usage

### Starting the Agent

```bash
# Run directly (foreground)
python3 /opt/pi-monitor/pi_monitor_agent.py

# Run as systemd service (background)
sudo systemctl start pi-monitor-agent

# View logs
sudo journalctl -u pi-monitor-agent -f
```

**Example output:**

```
==================================================
Pi Monitor Agent
==================================================
Hostname:  raspberrypi
IP:        192.168.1.100
Port:      5555
Endpoint:  http://192.168.1.100:5555/metrics
==================================================
Press Ctrl+C to stop
```

### Starting the Dashboard

```bash
# Run directly (foreground)
python3 /opt/pi-monitor/pi_monitor_dashboard.py

# Run as systemd service (background)
sudo systemctl start pi-monitor-dashboard

# View logs
sudo journalctl -u pi-monitor-dashboard -f
```

**Example output:**

```
==================================================
Pi Monitor Dashboard
==================================================
Dashboard:  http://192.168.1.50:8080
Monitoring: 3 host(s)

Configured hosts:
  - 192.168.1.100
  - 192.168.1.101
  - pihole.local

==================================================
Press Ctrl+C to stop
```

### Managing Services

```bash
# Check status
sudo ./install.sh status
# Or manually:
sudo systemctl status pi-monitor-agent
sudo systemctl status pi-monitor-dashboard

# Start services
sudo systemctl start pi-monitor-agent
sudo systemctl start pi-monitor-dashboard

# Stop services
sudo systemctl stop pi-monitor-agent
sudo systemctl stop pi-monitor-dashboard

# Restart services (after config changes)
sudo systemctl restart pi-monitor-agent
sudo systemctl restart pi-monitor-dashboard

# View live logs
sudo journalctl -u pi-monitor-agent -f
sudo journalctl -u pi-monitor-dashboard -f

# Uninstall completely
sudo ./install.sh uninstall
```

## API Documentation

### Agent API

The agent exposes a simple REST API for retrieving system metrics.

#### GET `/metrics` or GET `/`

Returns current system metrics as JSON.

**Request:**

```bash
curl http://192.168.1.100:5555/metrics
```

**Response:**

```json
{
  "hostname": "raspberrypi",
  "ip": "192.168.1.100",
  "model": "Raspberry Pi 4 Model B Rev 1.4",
  "timestamp": "2025-01-01T12:00:00.000000",
  "cpu": {
    "usage_percent": 15.2,
    "temperature": 45.0,
    "load_average": [0.5, 0.3, 0.2]
  },
  "memory": {
    "total_mb": 3884,
    "used_mb": 512,
    "available_mb": 3372,
    "percent": 13.2
  },
  "disk": {
    "total_gb": 29.5,
    "used_gb": 8.2,
    "free_gb": 21.3,
    "percent": 27.8
  },
  "uptime": "5d 3h 22m"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `hostname` | string | System hostname |
| `ip` | string | Primary local IP address |
| `model` | string | Raspberry Pi hardware model |
| `timestamp` | string | ISO 8601 timestamp |
| `cpu.usage_percent` | float | CPU usage percentage (0-100) |
| `cpu.temperature` | float\|null | CPU temperature in Celsius (null if unavailable) |
| `cpu.load_average` | array | 1, 5, 15 minute load averages |
| `memory.total_mb` | int | Total RAM in megabytes |
| `memory.used_mb` | int | Used RAM in megabytes |
| `memory.available_mb` | int | Available RAM in megabytes |
| `memory.percent` | float | Memory usage percentage |
| `disk.total_gb` | float | Total disk space in gigabytes |
| `disk.used_gb` | float | Used disk space in gigabytes |
| `disk.free_gb` | float | Free disk space in gigabytes |
| `disk.percent` | float | Disk usage percentage |
| `uptime` | string | Human-readable uptime |

**Headers:**

- `Content-Type: application/json`
- `Access-Control-Allow-Origin: *` (CORS enabled)

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 404 | Unknown endpoint |

### Dashboard API

The dashboard provides an API for programmatic access to all monitored hosts.

#### GET `/api/metrics`

Returns metrics from all configured hosts.

**Request:**

```bash
curl http://192.168.1.50:8080/api/metrics
```

**Response:**

```json
{
  "192.168.1.100": {
    "hostname": "pi-living-room",
    "ip": "192.168.1.100",
    "status": "online",
    "last_seen": "2025-01-01T12:00:00.000000",
    "model": "Raspberry Pi 4 Model B Rev 1.4",
    "cpu": { ... },
    "memory": { ... },
    "disk": { ... },
    "uptime": "5d 3h 22m"
  },
  "192.168.1.101": {
    "hostname": "192.168.1.101",
    "status": "offline",
    "ip": "192.168.1.101"
  }
}
```

**Additional Fields (Dashboard):**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | "online", "offline", or "error" |
| `last_seen` | string | ISO 8601 timestamp of last successful poll |
| `error` | string | Error message (only when status is "error") |

#### GET `/`

Returns the HTML dashboard interface.

### Integration Examples

#### Python Script

```python
import urllib.request
import json

def get_pi_metrics(host, port=5555):
    """Fetch metrics from a Pi Monitor agent."""
    url = f"http://{host}:{port}/metrics"
    with urllib.request.urlopen(url, timeout=5) as response:
        return json.loads(response.read().decode())

# Example usage
metrics = get_pi_metrics("192.168.1.100")
print(f"CPU: {metrics['cpu']['usage_percent']}%")
print(f"Temp: {metrics['cpu']['temperature']}°C")
print(f"Memory: {metrics['memory']['percent']}%")
```

#### Bash Script

```bash
#!/bin/bash
# Get CPU temperature from a Pi

PI_IP="192.168.1.100"
TEMP=$(curl -s "http://${PI_IP}:5555/metrics" | python3 -c "import sys,json; print(json.load(sys.stdin)['cpu']['temperature'])")
echo "Temperature: ${TEMP}°C"

# Alert if temperature is high
if (( $(echo "$TEMP > 70" | bc -l) )); then
    echo "WARNING: High temperature!"
fi
```

#### Home Assistant Integration

```yaml
# configuration.yaml
sensor:
  - platform: rest
    name: "Pi Living Room CPU"
    resource: http://192.168.1.100:5555/metrics
    value_template: "{{ value_json.cpu.usage_percent }}"
    unit_of_measurement: "%"
    scan_interval: 30

  - platform: rest
    name: "Pi Living Room Temperature"
    resource: http://192.168.1.100:5555/metrics
    value_template: "{{ value_json.cpu.temperature }}"
    unit_of_measurement: "°C"
    scan_interval: 30
```

## Troubleshooting

### Agent Issues

<details>
<summary><strong>Agent not starting</strong></summary>

**Symptoms:** Service fails to start, or Python errors on startup.

**Solutions:**

1. Check Python version:

   ```bash
   python3 --version  # Must be 3.7+
   ```

2. Check for port conflicts:

   ```bash
   sudo lsof -i :5555
   # Kill conflicting process if needed
   ```

3. Run manually to see errors:

   ```bash
   python3 /opt/pi-monitor/pi_monitor_agent.py
   ```

4. Check service logs:

   ```bash
   sudo journalctl -u pi-monitor-agent -n 50 --no-pager
   ```

</details>

<details>
<summary><strong>Agent not responding to requests</strong></summary>

**Symptoms:** `curl http://localhost:5555/metrics` times out or connection refused.

**Solutions:**

1. Check if agent is running:

   ```bash
   sudo systemctl status pi-monitor-agent
   ```

2. Verify the port is listening:

   ```bash
   sudo ss -tlnp | grep 5555
   ```

3. Test localhost connection:

   ```bash
   curl -v http://localhost:5555/metrics
   ```

4. Check firewall:

   ```bash
   sudo ufw status
   sudo iptables -L -n | grep 5555
   ```

</details>

<details>
<summary><strong>Temperature shows "N/A"</strong></summary>

**Symptoms:** Dashboard shows "N/A" for temperature.

**This is normal for:**

- Raspberry Pi Zero (no thermal zone exposed)
- Virtual machines
- Some Pi models without thermal sensors

**Verify on the Pi:**

```bash
cat /sys/class/thermal/thermal_zone0/temp
# Should return a number like 45000 (= 45.0°C)
# "No such file" means temperature is unavailable
```

</details>

### Dashboard Issues

<details>
<summary><strong>Dashboard shows "Offline" for all Pis</strong></summary>

**Step-by-step debugging:**

1. Verify agent is running on target Pi:

   ```bash
   ssh pi@192.168.1.100
   sudo systemctl status pi-monitor-agent
   ```

2. Test network connectivity:

   ```bash
   ping 192.168.1.100
   ```

3. Test agent from dashboard Pi:

   ```bash
   curl http://192.168.1.100:5555/metrics
   ```

4. Check firewall on the agent Pi:

   ```bash
   ssh pi@192.168.1.100
   sudo ufw allow 5555/tcp
   ```

5. Verify `MONITORED_HOSTS` in dashboard config contains correct IPs.

</details>

<details>
<summary><strong>Dashboard page won't load</strong></summary>

**Solutions:**

1. Check dashboard is running:

   ```bash
   sudo systemctl status pi-monitor-dashboard
   ```

2. Verify port is listening:

   ```bash
   sudo ss -tlnp | grep 8080
   ```

3. Check firewall allows port 8080:

   ```bash
   sudo ufw allow 8080/tcp
   ```

4. Try accessing via localhost:

   ```bash
   curl http://localhost:8080
   ```

</details>

<details>
<summary><strong>Dashboard shows stale data</strong></summary>

**Symptoms:** Metrics don't update, or timestamp is old.

**Solutions:**

1. Check dashboard logs for polling errors:

   ```bash
   sudo journalctl -u pi-monitor-dashboard -f
   ```

2. Verify `POLL_INTERVAL` setting (default 5 seconds).

3. Check if agents are responding:

   ```bash
   curl http://<pi-ip>:5555/metrics
   ```

4. Restart dashboard:

   ```bash
   sudo systemctl restart pi-monitor-dashboard
   ```

</details>

### Network Issues

<details>
<summary><strong>Connection timeouts</strong></summary>

The dashboard uses a 3-second timeout when polling agents. If your network is slow:

1. Check network latency:

   ```bash
   ping -c 10 192.168.1.100
   ```

2. For high-latency networks, you may need to modify the timeout in `pi_monitor_dashboard.py`:

   ```python
   # Line ~55
   with urlopen(url, timeout=3) as response:  # Increase from 3
   ```

</details>

<details>
<summary><strong>Using hostnames instead of IPs</strong></summary>

Hostnames like `pihole.local` require mDNS (Avahi) to be working:

```bash
# Test hostname resolution
ping pihole.local

# If it fails, install avahi
sudo apt install avahi-daemon
sudo systemctl enable avahi-daemon
sudo systemctl start avahi-daemon
```

Or use IP addresses instead of hostnames in `MONITORED_HOSTS`.

</details>

## Resource Usage

Tested on Raspberry Pi Zero W (512MB RAM, single-core 1GHz):

| Component | RAM Usage | CPU (idle) | CPU (polling) |
|-----------|-----------|------------|---------------|
| Agent | ~5 MB | <0.1% | <1% |
| Dashboard (3 hosts) | ~8 MB | <0.5% | <2% |

Pi Monitor is designed to have negligible impact on your Pi's performance.

## Security Considerations

Pi Monitor is designed for **trusted local networks**. Be aware of these security aspects:

| Aspect | Current Behavior | Recommendation |
|--------|------------------|----------------|
| Authentication | None | Use firewall rules to restrict access |
| Encryption | None (HTTP) | Use behind a reverse proxy with HTTPS for remote access |
| CORS | Enabled (`*`) | Fine for local networks |
| Input Validation | Minimal | Agents only read system files, no user input |

**For production/public networks:**

1. Use firewall rules to restrict access to trusted IPs
2. Put the dashboard behind a reverse proxy (nginx/Caddy) with HTTPS
3. Add HTTP Basic Auth via your reverse proxy
4. Consider VPN for remote access

## Development

### Setting Up a Development Environment

```bash
# Clone the repository
git clone https://github.com/JGRSGIS/pi-monitor.git
cd pi-monitor

# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=agent --cov=dashboard --cov-report=html

# Run specific test file
pytest tests/test_agent.py -v
```

### Running Locally for Development

```bash
# Run agent directly (no installation needed)
python3 agent/pi_monitor_agent.py

# In another terminal, run dashboard
python3 dashboard/pi_monitor_dashboard.py
```

### Code Quality

```bash
# Run linting
flake8 agent/ dashboard/ tests/

# Format code (if black is installed)
black agent/ dashboard/ tests/

# Run pre-commit hooks
pre-commit run --all-files
```

### Project Structure

```
pi-monitor/
├── agent/
│   ├── pi_monitor_agent.py      # Agent script (runs on each Pi)
│   └── pi-monitor-agent.service # Systemd service file
├── dashboard/
│   ├── pi_monitor_dashboard.py  # Dashboard script (runs on one Pi)
│   └── pi-monitor-dashboard.service
├── tests/
│   ├── test_agent.py            # Agent unit tests
│   └── test_dashboard.py        # Dashboard unit tests
├── install.sh                   # Installation script
└── README.md
```

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes (keep zero-dependency philosophy in mind)
4. Test on actual Raspberry Pi hardware if possible
5. Commit with clear messages: `git commit -m 'Add amazing feature'`
6. Push to your fork: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Areas for Contribution

- Additional metrics (network I/O, GPU temp for Pi 4/5)
- Dark/light theme toggle
- Historical data graphing (in-memory, no database)
- Auto-discovery via mDNS
- Alert thresholds and notifications
- Documentation improvements

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built for the Raspberry Pi community. Zero external dependencies, just Python 3.**
