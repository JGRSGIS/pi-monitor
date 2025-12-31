#!/usr/bin/env python3
"""
Pi Monitor Agent
================
Lightweight system metrics collector for Raspberry Pi.
Runs on each Pi you want to monitor.

Usage:
    python3 pi_monitor_agent.py

Metrics endpoint:
    http://<pi-ip>:5555/metrics
"""

import json
import os
import socket
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# =============================================================================
# Configuration
# =============================================================================

PORT = 5555  # Change if needed

# =============================================================================
# Metrics Collection (reads directly from /proc and /sys)
# =============================================================================

HOSTNAME = socket.gethostname()


def get_cpu_temp():
    """Get CPU temperature from thermal zone."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return round(int(f.read().strip()) / 1000, 1)
    except (FileNotFoundError, PermissionError, ValueError):
        return None


def get_cpu_usage():
    """Get CPU usage percentage from /proc/stat."""
    try:
        with open("/proc/stat") as f:
            line = f.readline()
        values = list(map(int, line.split()[1:]))
        idle = values[3]
        total = sum(values)

        # Store previous values for delta calculation
        if not hasattr(get_cpu_usage, "prev"):
            get_cpu_usage.prev = (idle, total)
            time.sleep(0.1)
            return get_cpu_usage()

        prev_idle, prev_total = get_cpu_usage.prev
        get_cpu_usage.prev = (idle, total)

        idle_delta = idle - prev_idle
        total_delta = total - prev_total

        if total_delta == 0:
            return 0.0
        return round((1 - idle_delta / total_delta) * 100, 1)
    except (FileNotFoundError, PermissionError, ValueError):
        return 0.0


def get_memory_info():
    """Get memory usage from /proc/meminfo."""
    try:
        mem = {}
        with open("/proc/meminfo") as f:
            for line in f:
                parts = line.split()
                if parts[0] in ["MemTotal:", "MemAvailable:", "MemFree:"]:
                    mem[parts[0][:-1]] = int(parts[1])

        total = mem.get("MemTotal", 0) / 1024  # Convert to MB
        available = mem.get("MemAvailable", mem.get("MemFree", 0)) / 1024
        used = total - available
        percent = round((used / total) * 100, 1) if total > 0 else 0

        return {
            "total_mb": round(total),
            "used_mb": round(used),
            "available_mb": round(available),
            "percent": percent,
        }
    except (FileNotFoundError, PermissionError, ValueError):
        return {"total_mb": 0, "used_mb": 0, "available_mb": 0, "percent": 0}


def get_disk_info():
    """Get disk usage using os.statvfs."""
    try:
        stat = os.statvfs("/")
        total = (stat.f_blocks * stat.f_frsize) / (1024**3)  # GB
        free = (stat.f_bavail * stat.f_frsize) / (1024**3)
        used = total - free
        percent = round((used / total) * 100, 1) if total > 0 else 0

        return {
            "total_gb": round(total, 1),
            "used_gb": round(used, 1),
            "free_gb": round(free, 1),
            "percent": percent,
        }
    except OSError:
        return {"total_gb": 0, "used_gb": 0, "free_gb": 0, "percent": 0}


def get_uptime():
    """Get system uptime in human-readable format."""
    try:
        with open("/proc/uptime") as f:
            uptime_seconds = float(f.read().split()[0])

        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)

        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    except (FileNotFoundError, PermissionError, ValueError):
        return "unknown"


def get_load_average():
    """Get system load average."""
    try:
        with open("/proc/loadavg") as f:
            loads = f.read().split()[:3]
        return [float(load) for load in loads]
    except (FileNotFoundError, PermissionError, ValueError):
        return [0.0, 0.0, 0.0]


def get_network_ip():
    """Get local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "unknown"


def get_pi_model():
    """Get Raspberry Pi model string."""
    try:
        with open("/proc/device-tree/model") as f:
            return f.read().strip().replace("\x00", "")
    except (FileNotFoundError, PermissionError):
        return "Unknown Model"


def collect_metrics():
    """Collect all system metrics into a dictionary."""
    return {
        "hostname": HOSTNAME,
        "ip": get_network_ip(),
        "model": get_pi_model(),
        "timestamp": datetime.now().isoformat(),
        "cpu": {
            "usage_percent": get_cpu_usage(),
            "temperature": get_cpu_temp(),
            "load_average": get_load_average(),
        },
        "memory": get_memory_info(),
        "disk": get_disk_info(),
        "uptime": get_uptime(),
    }


# =============================================================================
# HTTP Server
# =============================================================================


class MetricsHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for the metrics endpoint."""

    def log_message(self, format, *args):
        """Suppress default logging for lightweight operation."""
        pass

    def do_GET(self):
        """Handle GET requests."""
        if self.path in ("/", "/metrics"):
            metrics = collect_metrics()
            response = json.dumps(metrics, indent=2)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response.encode())
        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Not Found")


# =============================================================================
# Main
# =============================================================================


def main():
    """Start the metrics server."""
    ip = get_network_ip()

    print("=" * 50)
    print("🍓 Pi Monitor Agent")
    print("=" * 50)
    print(f"Hostname:  {HOSTNAME}")
    print(f"IP:        {ip}")
    print(f"Port:      {PORT}")
    print(f"Endpoint:  http://{ip}:{PORT}/metrics")
    print("=" * 50)
    print("Press Ctrl+C to stop")
    print()

    server = HTTPServer(("0.0.0.0", PORT), MetricsHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
