#!/usr/bin/env python
"""
Pi Monitor Agent (Python 2/3 Compatible)
=========================================
Lightweight system metrics collector for Raspberry Pi.
Works on OpenELEC and other systems with older Python versions.

Usage:
    python pi_monitor_agent_py2.py

Metrics endpoint:
    http://<pi-ip>:5555/metrics
"""

from __future__ import print_function

import json
import os
import socket
import time

# Python 2/3 compatible imports
try:
    from http.server import BaseHTTPRequestHandler, HTTPServer
except ImportError:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

try:
    from datetime import datetime
except ImportError:
    import datetime

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
            return round(int(f.read().strip()) / 1000.0, 1)
    except (IOError, OSError, ValueError):
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
        return round((1 - idle_delta / float(total_delta)) * 100, 1)
    except (IOError, OSError, ValueError):
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

        total = mem.get("MemTotal", 0) / 1024.0  # Convert to MB
        available = mem.get("MemAvailable", mem.get("MemFree", 0)) / 1024.0
        used = total - available
        percent = round((used / total) * 100, 1) if total > 0 else 0

        return {
            "total_mb": int(round(total)),
            "used_mb": int(round(used)),
            "available_mb": int(round(available)),
            "percent": percent,
        }
    except (IOError, OSError, ValueError):
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
            return "{0}d {1}h {2}m".format(days, hours, minutes)
        elif hours > 0:
            return "{0}h {1}m".format(hours, minutes)
        else:
            return "{0}m".format(minutes)
    except (IOError, OSError, ValueError):
        return "unknown"


def get_load_average():
    """Get system load average."""
    try:
        with open("/proc/loadavg") as f:
            loads = f.read().split()[:3]
        return [float(load) for load in loads]
    except (IOError, OSError, ValueError):
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
    except (IOError, OSError):
        # Try alternative for non-Pi systems
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        return line.split("=")[1].strip().strip('"')
        except (IOError, OSError):
            pass
        return "Unknown Model"


def collect_metrics():
    """Collect all system metrics into a dictionary."""
    try:
        timestamp = datetime.now().isoformat()
    except:
        timestamp = str(time.time())

    return {
        "hostname": HOSTNAME,
        "ip": get_network_ip(),
        "model": get_pi_model(),
        "timestamp": timestamp,
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
            self.wfile.write(response.encode("utf-8"))
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
    print("Pi Monitor Agent (Python 2/3 Compatible)")
    print("=" * 50)
    print("Hostname:  {0}".format(HOSTNAME))
    print("IP:        {0}".format(ip))
    print("Port:      {0}".format(PORT))
    print("Endpoint:  http://{0}:{1}/metrics".format(ip, PORT))
    print("=" * 50)
    print("Press Ctrl+C to stop")
    print("")

    server = HTTPServer(("0.0.0.0", PORT), MetricsHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
