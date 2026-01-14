"""
Tests for memory.py - Core memory engine functionality
"""

import json
import tempfile
from pathlib import Path
import pytest
from memory import MemoryEngine


class TestMemoryEngine:
    """Test the core memory storage and recall functionality."""

    @pytest.fixture
    def temp_memory(self):
        """Create a temporary memory root for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield MemoryEngine(root=tmpdir)

    def test_remember_success_code_interpreter(self, temp_memory):
        """Test storing a code_interpreter success memory."""
        path = temp_memory.remember(
            content="Implemented JWT authentication",
            outcome="success",
            tool="code_interpreter",
            task_type="write",
            summary="jwt_auth_impl"
        )

        assert Path(path).exists()
        assert "outcome=success" in path
        assert "tool=code_interpreter" in path
        assert "task_type=write" in path

        # Verify content
        with open(path) as f:
            data = json.load(f)
            assert data["content"] == "Implemented JWT authentication"
            assert data["outcome"] == "success"

    def test_remember_failure_with_error_type(self, temp_memory):
        """Test storing a failure memory with error classification."""
        path = temp_memory.remember(
            content="TypeError in async function",
            outcome="failure",
            tool="code_interpreter",
            error_type="runtime",
            summary="async_type_error"
        )

        assert Path(path).exists()
        assert "outcome=failure" in path
        assert "error_type=runtime" in path

    def test_remember_learning(self, temp_memory):
        """Test storing a learning insight."""
        path = temp_memory.remember(
            content="User prefers explicit error messages",
            outcome="learning",
            insight_type="preference",
            summary="error_msg_pref"
        )

        assert Path(path).exists()
        assert "outcome=learning" in path
        assert "insight_type=preference" in path

    def test_remember_interaction(self, temp_memory):
        """Test storing a user interaction."""
        path = temp_memory.remember(
            content="User praised debugging explanation",
            outcome="interaction",
            sentiment="positive",
            summary="user_happy"
        )

        assert Path(path).exists()
        assert "outcome=interaction" in path
        assert "sentiment=positive" in path

    def test_recall_by_outcome(self, temp_memory):
        """Test recalling memories by outcome."""
        # Store multiple memories
        temp_memory.remember(
            content="Success 1", outcome="success",
            tool="code_interpreter", task_type="write", summary="s1"
        )
        temp_memory.remember(
            content="Failure 1", outcome="failure",
            tool="code_interpreter", error_type="runtime", summary="f1"
        )
        temp_memory.remember(
            content="Success 2", outcome="success",
            tool="web_search", domain="technical", summary="s2"
        )

        # Recall successes
        successes = temp_memory.recall(pattern=f"{temp_memory.root}/outcome=success/**/*.json")
        assert len(successes) == 2

        # Recall failures
        failures = temp_memory.recall(pattern=f"{temp_memory.root}/outcome=failure/**/*.json")
        assert len(failures) == 1

    def test_recall_newest_first(self, temp_memory):
        """Test that recall returns newest memories first."""
        import time

        temp_memory.remember(
            content="First", outcome="success",
            tool="conversation", summary="first"
        )
        time.sleep(0.01)

        temp_memory.remember(
            content="Second", outcome="success",
            tool="conversation", summary="second"
        )

        memories = temp_memory.recall(pattern=f"{temp_memory.root}/**/*.json")
        assert len(memories) == 2
        assert memories[0]["content"] == "Second"
        assert memories[1]["content"] == "First"

    def test_reflect_basic(self, temp_memory):
        """Test basic reflection analysis."""
        # Store varied memories
        temp_memory.remember(
            content="S1", outcome="success",
            tool="code_interpreter", task_type="debug", summary="s1"
        )
        temp_memory.remember(
            content="S2", outcome="success",
            tool="code_interpreter", task_type="write", summary="s2"
        )
        temp_memory.remember(
            content="F1", outcome="failure",
            tool="code_interpreter", error_type="runtime", summary="f1"
        )

        analysis = temp_memory.reflect()

        assert analysis["total_memories"] == 3
        assert "success" in analysis["by_outcome"]
        assert "failure" in analysis["by_outcome"]
        assert analysis["by_outcome"]["success"] == 2
        assert analysis["by_outcome"]["failure"] == 1

    def test_forget_by_pattern(self, temp_memory):
        """Test memory deletion by pattern."""
        # Store a memory
        temp_memory.remember(
            content="To be deleted", outcome="failure",
            tool="code_interpreter", error_type="syntax", summary="delete_me"
        )

        # Verify it exists
        memories = temp_memory.recall(pattern=f"{temp_memory.root}/**/*delete_me*.json")
        assert len(memories) == 1

        # Delete it
        deleted = temp_memory.forget(pattern=f"{temp_memory.root}/**/*delete_me*.json")
        assert deleted == 1

        # Verify it's gone
        memories = temp_memory.recall(pattern=f"{temp_memory.root}/**/*delete_me*.json")
        assert len(memories) == 0

    def test_auto_summary_generation(self, temp_memory):
        """Test automatic summary generation when not provided."""
        path = temp_memory.remember(
            content="Fixed race condition in payment processor",
            outcome="success",
            tool="code_interpreter",
            task_type="debug"
            # No summary provided
        )

        assert Path(path).exists()
        # Summary should be auto-generated from content
        filename = Path(path).name
        assert "fixed_race" in filename.lower() or "memory_" in filename
