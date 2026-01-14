"""
Tests for visualizer.py - Topology visualization
"""

import tempfile
from pathlib import Path
import pytest
from visualizer import Visualizer
from memory import MemoryEngine


class TestVisualizer:
    """Test the topology visualizer."""

    @pytest.fixture
    def temp_visualizer(self):
        """Create a temporary visualizer with test data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some test memories
            memory = MemoryEngine(root=tmpdir)

            memory.remember(
                content="Success 1", outcome="success",
                tool="code_interpreter", task_type="debug", summary="s1"
            )
            memory.remember(
                content="Success 2", outcome="success",
                tool="code_interpreter", task_type="write", summary="s2"
            )
            memory.remember(
                content="Failure 1", outcome="failure",
                tool="code_interpreter", error_type="runtime", summary="f1"
            )

            yield Visualizer(tmpdir)

    def test_scan_tree(self, temp_visualizer):
        """Test that tree scanning works."""
        stats = temp_visualizer._scan_tree(temp_visualizer.root)

        assert stats is not None
        assert stats["file_count"] == 3
        assert len(stats["children"]) > 0

    def test_hotspots_detection(self, temp_visualizer):
        """Test hotspot detection."""
        hotspots = temp_visualizer.hotspots(threshold=0.1)

        assert isinstance(hotspots, list)
        assert len(hotspots) > 0

        # Check structure
        for path, count in hotspots:
            assert isinstance(path, str)
            assert isinstance(count, int)
            assert count > 0

    def test_map_output(self, temp_visualizer, capsys):
        """Test that map generates output."""
        temp_visualizer.map(max_depth=3)

        captured = capsys.readouterr()
        output = captured.out

        # Should contain tree structure indicators
        assert "├──" in output or "└──" in output
        # Should contain outcome directory
        assert "outcome=" in output

    def test_empty_directory(self):
        """Test visualizer on empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            viz = Visualizer(tmpdir)
            stats = viz._scan_tree(tmpdir)

            assert stats["file_count"] == 0
            assert stats["children"] == {}
