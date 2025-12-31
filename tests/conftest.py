# Pi Monitor - Pytest Configuration
# ===================================
#
# This file contains shared fixtures and configuration for pytest.
# Fixtures defined here are automatically available to all test modules.

import sys
from pathlib import Path

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_metrics():
    """Sample metrics data for testing."""
    return {
        "hostname": "test-pi",
        "timestamp": "2024-01-01T00:00:00Z",
        "cpu_percent": 25.5,
        "memory_percent": 45.2,
        "disk_percent": 60.0,
        "temperature": 42.5,
        "uptime_seconds": 3600,
    }


@pytest.fixture
def mock_proc_stat(tmp_path):
    """Create a mock /proc/stat file for CPU testing."""
    stat_file = tmp_path / "stat"
    stat_file.write_text(
        "cpu  10000 500 2000 50000 100 0 50 0 0 0\n"
        "cpu0 5000 250 1000 25000 50 0 25 0 0 0\n"
        "cpu1 5000 250 1000 25000 50 0 25 0 0 0\n"
    )
    return stat_file


@pytest.fixture
def mock_proc_meminfo(tmp_path):
    """Create a mock /proc/meminfo file for memory testing."""
    meminfo_file = tmp_path / "meminfo"
    meminfo_file.write_text(
        "MemTotal:        4000000 kB\n"
        "MemFree:         1000000 kB\n"
        "MemAvailable:    2000000 kB\n"
        "Buffers:          200000 kB\n"
        "Cached:           800000 kB\n"
    )
    return meminfo_file


@pytest.fixture
def mock_thermal_zone(tmp_path):
    """Create a mock thermal zone file for temperature testing."""
    thermal_dir = tmp_path / "thermal_zone0"
    thermal_dir.mkdir()
    temp_file = thermal_dir / "temp"
    temp_file.write_text("45000\n")  # 45.0 degrees Celsius
    return temp_file


# =============================================================================
# Configuration
# =============================================================================


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks integration tests")
    config.addinivalue_line("markers", "unit: marks unit tests")
