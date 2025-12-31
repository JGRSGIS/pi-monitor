# Pi Monitor Agent

The agent runs on each Raspberry Pi you want to monitor. It collects system metrics and exposes them via a simple HTTP endpoint.

## Files

| File | Description |
|------|-------------|
| `pi_monitor_agent.py` | Main agent script |
| `pi-monitor-agent.service` | Systemd service file |

## Quick Start

```bash
# Run directly
python3 pi_monitor_agent.py

# Or install as service
sudo cp pi_monitor_agent.py /opt/pi-monitor/
sudo cp pi-monitor-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now pi-monitor-agent
```

## API

**Endpoint:** `GET /metrics`

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

## Configuration

Edit `pi_monitor_agent.py` to change the port:

```python
PORT = 5555  # Default
```
