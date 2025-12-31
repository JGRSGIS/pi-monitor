#!/bin/bash
#
# Pi Monitor Installation Script
# ==============================
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/pi-monitor/main/install.sh | sudo bash -s agent
#   curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/pi-monitor/main/install.sh | sudo bash -s dashboard
#
# Or locally:
#   sudo ./install.sh agent
#   sudo ./install.sh dashboard
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
INSTALL_DIR="/opt/pi-monitor"
REPO_URL="https://raw.githubusercontent.com/JGRSGIS/pi-monitor/main"

print_header() {
    echo ""
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  🍓 Pi Monitor Installer${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}Error: This script must be run as root (use sudo)${NC}"
        exit 1
    fi
}

get_local_ip() {
    hostname -I | awk '{print $1}'
}

install_agent() {
    echo -e "${YELLOW}Installing Pi Monitor Agent...${NC}"
    echo ""

    # Create directory
    mkdir -p "$INSTALL_DIR"

    # Download or copy agent
    if [[ -f "agent/pi_monitor_agent.py" ]]; then
        cp agent/pi_monitor_agent.py "$INSTALL_DIR/"
        echo "  ✓ Copied agent from local directory"
    else
        curl -sSL "${REPO_URL}/agent/pi_monitor_agent.py" -o "$INSTALL_DIR/pi_monitor_agent.py"
        echo "  ✓ Downloaded agent"
    fi

    chmod +x "$INSTALL_DIR/pi_monitor_agent.py"

    # Install systemd service
    if [[ -f "agent/pi-monitor-agent.service" ]]; then
        cp agent/pi-monitor-agent.service /etc/systemd/system/
    else
        curl -sSL "${REPO_URL}/agent/pi-monitor-agent.service" -o /etc/systemd/system/pi-monitor-agent.service
    fi
    echo "  ✓ Installed systemd service"

    # Enable and start
    systemctl daemon-reload
    systemctl enable pi-monitor-agent
    systemctl start pi-monitor-agent
    echo "  ✓ Started service"

    LOCAL_IP=$(get_local_ip)

    echo ""
    echo -e "${GREEN}✓ Agent installed successfully!${NC}"
    echo ""
    echo -e "  Metrics endpoint: ${YELLOW}http://${LOCAL_IP}:5555/metrics${NC}"
    echo ""
    echo "  Test with: curl http://localhost:5555/metrics"
    echo ""
}

install_dashboard() {
    echo -e "${YELLOW}Installing Pi Monitor Dashboard...${NC}"
    echo ""

    # Create directory
    mkdir -p "$INSTALL_DIR"

    # Download or copy dashboard
    if [[ -f "dashboard/pi_monitor_dashboard.py" ]]; then
        cp dashboard/pi_monitor_dashboard.py "$INSTALL_DIR/"
        echo "  ✓ Copied dashboard from local directory"
    else
        curl -sSL "${REPO_URL}/dashboard/pi_monitor_dashboard.py" -o "$INSTALL_DIR/pi_monitor_dashboard.py"
        echo "  ✓ Downloaded dashboard"
    fi

    chmod +x "$INSTALL_DIR/pi_monitor_dashboard.py"

    # Install systemd service
    if [[ -f "dashboard/pi-monitor-dashboard.service" ]]; then
        cp dashboard/pi-monitor-dashboard.service /etc/systemd/system/
    else
        curl -sSL "${REPO_URL}/dashboard/pi-monitor-dashboard.service" -o /etc/systemd/system/pi-monitor-dashboard.service
    fi
    echo "  ✓ Installed systemd service"

    # Enable and start
    systemctl daemon-reload
    systemctl enable pi-monitor-dashboard
    systemctl start pi-monitor-dashboard
    echo "  ✓ Started service"

    LOCAL_IP=$(get_local_ip)

    echo ""
    echo -e "${GREEN}✓ Dashboard installed successfully!${NC}"
    echo ""
    echo -e "${YELLOW}⚠ IMPORTANT: Configure your monitored hosts:${NC}"
    echo ""
    echo "  sudo nano $INSTALL_DIR/pi_monitor_dashboard.py"
    echo ""
    echo "  Add your Pi IP addresses to MONITORED_HOSTS, then restart:"
    echo ""
    echo "  sudo systemctl restart pi-monitor-dashboard"
    echo ""
    echo -e "  Dashboard URL: ${YELLOW}http://${LOCAL_IP}:8080${NC}"
    echo ""
}

uninstall() {
    echo -e "${YELLOW}Uninstalling Pi Monitor...${NC}"
    echo ""

    # Stop and disable services
    systemctl stop pi-monitor-agent 2>/dev/null || true
    systemctl stop pi-monitor-dashboard 2>/dev/null || true
    systemctl disable pi-monitor-agent 2>/dev/null || true
    systemctl disable pi-monitor-dashboard 2>/dev/null || true
    echo "  ✓ Stopped services"

    # Remove service files
    rm -f /etc/systemd/system/pi-monitor-agent.service
    rm -f /etc/systemd/system/pi-monitor-dashboard.service
    systemctl daemon-reload
    echo "  ✓ Removed service files"

    # Remove installation directory
    rm -rf "$INSTALL_DIR"
    echo "  ✓ Removed installation directory"

    echo ""
    echo -e "${GREEN}✓ Pi Monitor uninstalled${NC}"
    echo ""
}

show_status() {
    echo -e "${YELLOW}Pi Monitor Status${NC}"
    echo ""

    if systemctl is-active --quiet pi-monitor-agent 2>/dev/null; then
        echo -e "  Agent:     ${GREEN}● Running${NC}"
    elif systemctl is-enabled --quiet pi-monitor-agent 2>/dev/null; then
        echo -e "  Agent:     ${RED}○ Stopped (enabled)${NC}"
    else
        echo -e "  Agent:     ${RED}○ Not installed${NC}"
    fi

    if systemctl is-active --quiet pi-monitor-dashboard 2>/dev/null; then
        echo -e "  Dashboard: ${GREEN}● Running${NC}"
    elif systemctl is-enabled --quiet pi-monitor-dashboard 2>/dev/null; then
        echo -e "  Dashboard: ${RED}○ Stopped (enabled)${NC}"
    else
        echo -e "  Dashboard: ${RED}○ Not installed${NC}"
    fi

    echo ""
}

show_help() {
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  agent      Install the monitoring agent (run on each Pi)"
    echo "  dashboard  Install the web dashboard (run on one Pi)"
    echo "  uninstall  Remove Pi Monitor completely"
    echo "  status     Show service status"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  sudo $0 agent"
    echo "  sudo $0 dashboard"
    echo ""
}

# Main
print_header

case "${1:-}" in
    agent)
        check_root
        install_agent
        ;;
    dashboard)
        check_root
        install_dashboard
        ;;
    uninstall)
        check_root
        uninstall
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Error: Unknown command '${1:-}'${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
