"""
Tests for coherence.py - Schema-based routing engine
"""

import tempfile
from pathlib import Path
import pytest
from coherence import Coherence


class TestCoherence:
    """Test the Coherence routing engine."""

    @pytest.fixture
    def simple_schema(self):
        """Create a simple test schema."""
        return {
            "outcome": {
                "success": {
                    "tool": {
                        "code": "{summary}.json",
                        "search": "{summary}.json"
                    }
                },
                "failure": {
                    "error": {
                        "runtime": "{summary}.json",
                        "syntax": "{summary}.json"
                    }
                }
            }
        }

    @pytest.fixture
    def temp_coherence(self, simple_schema):
        """Create a temporary coherence engine."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Coherence(simple_schema, root=tmpdir)

    def test_transmit_success(self, temp_coherence):
        """Test routing a success packet."""
        path = temp_coherence.transmit({
            "outcome": "success",
            "tool": "code",
            "summary": "test_success"
        })

        assert Path(path).exists()
        assert "outcome=success" in path
        assert "tool=code" in path
        assert "test_success.json" in path

    def test_transmit_failure(self, temp_coherence):
        """Test routing a failure packet."""
        path = temp_coherence.transmit({
            "outcome": "failure",
            "error": "runtime",
            "summary": "test_error"
        })

        assert Path(path).exists()
        assert "outcome=failure" in path
        assert "error=runtime" in path

    def test_receive_pattern_generation(self, temp_coherence):
        """Test glob pattern generation from intent."""
        pattern = temp_coherence.receive(outcome="success", tool="code")

        assert "outcome=success" in pattern
        assert "tool=code" in pattern
        assert "**/*.json" in pattern

    def test_receive_all_pattern(self, temp_coherence):
        """Test receiving all memories."""
        pattern = temp_coherence.receive()
        assert "**/*.json" in pattern

    def test_numeric_comparison_routing(self):
        """Test numeric comparison in routing logic."""
        schema = {
            "metric": {
                ">0.5": "high/{name}.json",
                "<=0.5": "low/{name}.json"
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            engine = Coherence(schema, root=tmpdir)

            # High value
            path_high = engine.transmit({"metric": 0.8, "name": "high_score"})
            assert "metric=gt_0.5" in path_high

            # Low value
            path_low = engine.transmit({"metric": 0.3, "name": "low_score"})
            assert "metric=lte_0.5" in path_low

    def test_string_matching_routing(self):
        """Test string matching in routing."""
        schema = {
            "status": {
                "active": "{id}.json",
                "archived": "{id}.json"
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            engine = Coherence(schema, root=tmpdir)

            path = engine.transmit({"status": "active", "id": "test123"})
            assert "status=active" in path
            assert "test123.json" in path

    def test_nested_routing(self):
        """Test deep nesting in schema routing."""
        schema = {
            "level1": {
                "a": {
                    "level2": {
                        "x": {
                            "level3": {
                                "1": "{name}.json",
                                "2": "{name}.json"
                            }
                        }
                    }
                }
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            engine = Coherence(schema, root=tmpdir)

            path = engine.transmit({
                "level1": "a",
                "level2": "x",
                "level3": "1",
                "name": "deep_test"
            })

            assert "level1=a" in path
            assert "level2=x" in path
            assert "level3=1" in path
            assert "deep_test.json" in path

    def test_derive_not_implemented(self, temp_coherence):
        """Test that derive is not yet implemented."""
        with pytest.raises(NotImplementedError):
            temp_coherence.derive(["/some/path"])
