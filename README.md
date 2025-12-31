# 🍓 Pi Monitor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![No Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)]()

A lightweight, zero-dependency monitoring system for Raspberry Pi fleets. View CPU, memory, disk, and temperature metrics from all your Pis in a beautiful web dashboard.

![Dashboard Preview](docs/dashboard-preview.png)

## ✨ Features

- **Zero dependencies** — Uses only Python standard library
- **Minimal footprint** — Agent uses ~5MB RAM, negligible CPU
- **Real-time updates** — Dashboard refreshes every 5 seconds
- **Responsive design** — Works on desktop, tablet, and mobile
- **Easy setup** — Single Python file per component
- **Systemd integration** — Runs as a service, starts on boot

## 📊 Metrics Collected

| Metric | Description |
|--------|-------------|
| CPU Usage | Real-time percentage |
| CPU Temperature | From thermal zone (°C) |
| Memory | Used / Total / Percentage |
| Disk | Used / Total / Percentage |
| Uptime | Human-readable format |
| Load Average | 1, 5, 15 minute averages |
| Pi Model | Auto-detected hardware |

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Pi Zero #1    │     │   Pi 4 #1       │     │   Pi 5 #1       │
│  (Agent :5555)  │     │  (Agent :5555)  │     │  (Agent :5555)  │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │ HTTP polling
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

## 🚀 Quick Start

### 1. Install Agent (on each Pi to monitor)

```bash
# Download and install
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/pi-monitor/main/install.sh | sudo bash -s agent

# Or manually:
sudo mkdir -p /opt/pi-monitor
sudo curl -o /opt/pi-monitor/pi_monitor_agent.py \
    https://raw.githubusercontent.com/YOUR_USERNAME/pi-monitor/main/agent/pi_monitor_agent.py
sudo chmod +x /opt/pi-monitor/pi_monitor_agent.py

# Test it
python3 /opt/pi-monitor/pi_monitor_agent.py
# Visit http://<pi-ip>:5555/metrics
```

### 2. Install Dashboard (on one Pi)

```bash
# Download
sudo mkdir -p /opt/pi-monitor
sudo curl -o /opt/pi-monitor/pi_monitor_dashboard.py \
    https://raw.githubusercontent.com/YOUR_USERNAME/pi-monitor/main/dashboard/pi_monitor_dashboard.py

# Configure your Pis
sudo nano /opt/pi-monitor/pi_monitor_dashboard.py
```

Edit the `MONITORED_HOSTS` list:

```python
MONITORED_HOSTS = [
    "192.168.1.100",    # Pi-hole
    "192.168.1.101",    # Media server
    "octopi.local",     # 3D printer
]
```

Start the dashboard:

```bash
python3 /opt/pi-monitor/pi_monitor_dashboard.py
# Visit http://<dashboard-ip>:8080
```

### 3. Run as Services (Optional)

```bash
# Install agent service
sudo curl -o /etc/systemd/system/pi-monitor-agent.service \
    https://raw.githubusercontent.com/YOUR_USERNAME/pi-monitor/main/agent/pi-monitor-agent.service
sudo systemctl daemon-reload
sudo systemctl enable --now pi-monitor-agent

# Install dashboard service  
sudo curl -o /etc/systemd/system/pi-monitor-dashboard.service \
    https://raw.githubusercontent.com/YOUR_USERNAME/pi-monitor/main/dashboard/pi-monitor-dashboard.service
sudo systemctl daemon-reload
sudo systemctl enable --now pi-monitor-dashboard
```

## ⚙️ Configuration

### Agent (`pi_monitor_agent.py`)

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `5555` | HTTP port for metrics endpoint |

### Dashboard (`pi_monitor_dashboard.py`)

| Variable | Default | Description |
|----------|---------|-------------|
| `MONITORED_HOSTS` | `[]` | List of Pi IPs/hostnames |
| `AGENT_PORT` | `5555` | Port where agents listen |
| `DASHBOARD_PORT` | `8080` | Web dashboard port |
| `POLL_INTERVAL` | `5` | Seconds between polls |

## 🔥 Firewall

If using `ufw`:

```bash
# On monitored Pis
sudo ufw allow 5555/tcp

# On dashboard Pi
sudo ufw allow 8080/tcp
```

## 🐛 Troubleshooting

<details>
<summary><strong>Agent not responding</strong></summary>

```bash
# Check if running
sudo systemctl status pi-monitor-agent

# View logs
sudo journalctl -u pi-monitor-agent -f

# Test endpoint
curl http://localhost:5555/metrics
```
</details>

<details>
<summary><strong>Dashboard shows "Offline"</strong></summary>

1. Verify agent is running: `systemctl status pi-monitor-agent`
2. Check connectivity: `ping <pi-ip>`
3. Test agent: `curl http://<pi-ip>:5555/metrics`
4. Check firewall on both Pis
</details>

<details>
<summary><strong>Temperature shows "N/A"</strong></summary>

Normal for some Pi models (Pi Zero, VMs). The thermal zone may not be exposed.
</details>

## 📈 Resource Usage

Tested on Raspberry Pi Zero W:

| Component | RAM | CPU (idle) |
|-----------|-----|------------|
| Agent | ~5 MB | <0.1% |
| Dashboard | ~8 MB | <0.5% |

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built for the Raspberry Pi community. Zero external dependencies, just Python 3.
