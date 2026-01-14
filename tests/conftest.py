"""
Pytest configuration and shared fixtures.
"""

import pytest


@pytest.fixture
def sample_memories():
    """Sample memory dataset for testing."""
    return [
        {
            "content": "Implemented JWT authentication",
            "outcome": "success",
            "tool": "code_interpreter",
            "task_type": "write",
            "summary": "jwt_auth"
        },
        {
            "content": "Fixed race condition",
            "outcome": "success",
            "tool": "code_interpreter",
            "task_type": "debug",
            "summary": "race_fix"
        },
        {
            "content": "TypeError in async function",
            "outcome": "failure",
            "tool": "code_interpreter",
            "error_type": "runtime",
            "summary": "async_error"
        },
        {
            "content": "User prefers explicit errors",
            "outcome": "learning",
            "insight_type": "preference",
            "summary": "error_pref"
        },
        {
            "content": "User satisfied with fix",
            "outcome": "interaction",
            "sentiment": "positive",
            "summary": "user_happy"
        }
    ]
