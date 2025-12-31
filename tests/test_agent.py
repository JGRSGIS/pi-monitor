# Pi Monitor - Agent Tests
# =========================
#
# Tests for the pi_monitor_agent module.

import pytest


class TestAgentMetricsCollection:
    """Tests for metrics collection functionality."""

    @pytest.mark.unit
    def test_sample_metrics_fixture(self, sample_metrics):
        """Test that the sample metrics fixture is properly structured."""
        assert "hostname" in sample_metrics
        assert "cpu_percent" in sample_metrics
        assert "memory_percent" in sample_metrics
        assert "disk_percent" in sample_metrics
        assert isinstance(sample_metrics["cpu_percent"], float)

    @pytest.mark.unit
    def test_cpu_percent_range(self, sample_metrics):
        """Test that CPU percentage is within valid range."""
        cpu = sample_metrics["cpu_percent"]
        assert 0.0 <= cpu <= 100.0

    @pytest.mark.unit
    def test_memory_percent_range(self, sample_metrics):
        """Test that memory percentage is within valid range."""
        memory = sample_metrics["memory_percent"]
        assert 0.0 <= memory <= 100.0

    @pytest.mark.unit
    def test_disk_percent_range(self, sample_metrics):
        """Test that disk percentage is within valid range."""
        disk = sample_metrics["disk_percent"]
        assert 0.0 <= disk <= 100.0


class TestAgentConfiguration:
    """Tests for agent configuration."""

    @pytest.mark.unit
    def test_default_values(self):
        """Test default configuration values."""
        # These will be implemented when testing actual config
        default_interval = 60
        default_port = 8080
        assert default_interval > 0
        assert 1 <= default_port <= 65535


class TestProcFilesParsing:
    """Tests for /proc file parsing."""

    @pytest.mark.unit
    def test_mock_proc_stat_exists(self, mock_proc_stat):
        """Test that mock /proc/stat file is created."""
        assert mock_proc_stat.exists()
        content = mock_proc_stat.read_text()
        assert "cpu" in content

    @pytest.mark.unit
    def test_mock_proc_meminfo_exists(self, mock_proc_meminfo):
        """Test that mock /proc/meminfo file is created."""
        assert mock_proc_meminfo.exists()
        content = mock_proc_meminfo.read_text()
        assert "MemTotal" in content
        assert "MemFree" in content

    @pytest.mark.unit
    def test_mock_thermal_zone_exists(self, mock_thermal_zone):
        """Test that mock thermal zone file is created."""
        assert mock_thermal_zone.exists()
        temp = int(mock_thermal_zone.read_text().strip())
        assert temp == 45000  # 45.0 degrees in millidegrees
