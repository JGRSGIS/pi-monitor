# Pi Monitor Dashboard

The dashboard runs on one Raspberry Pi and polls all configured agents, displaying metrics in a web-based UI.

## Files

| File | Description |
|------|-------------|
| `pi_monitor_dashboard.py` | Main dashboard script |
| `pi-monitor-dashboard.service` | Systemd service file |

## Quick Start

```bash
# 1. Edit the script to add your Pi IPs
nano pi_monitor_dashboard.py

# 2. Run directly
python3 pi_monitor_dashboard.py

# 3. Open in browser
# http://<this-pi-ip>:8080
```

## Configuration

Edit `pi_monitor_dashboard.py`:

```python
# Add your Raspberry Pi addresses
MONITORED_HOSTS = [
    "192.168.1.100",
    "192.168.1.101",
    "pihole.local",
]

# Optional settings
AGENT_PORT = 5555       # Port where agents listen
DASHBOARD_PORT = 8080   # This dashboard's port
POLL_INTERVAL = 5       # Seconds between polls
```

## Install as Service

```bash
sudo cp pi_monitor_dashboard.py /opt/pi-monitor/
sudo cp pi-monitor-dashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now pi-monitor-dashboard
```

## API

The dashboard also exposes a JSON API:

**Endpoint:** `GET /api/metrics`

Returns all collected metrics from all monitored hosts.
