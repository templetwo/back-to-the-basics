"""
BTB Multi-Agent Swarm Demo

Builds on btb_mcp_server.py tools for a coder-tester-reflector loop.
Simulates refactoring a Fibonacci function, handling failures via BTB memory.

Demonstrates:
- Multi-agent coordination via BTB memory
- Failure handling and pattern recall
- Reflection-driven iteration
- Topology-based debugging

Usage:
    python examples/btb_multi_agent_swarm.py

Requires: memory.py, visualizer.py, coherence.py in parent directory.
Sets up MEMORY_ROOT='swarm_brain' for isolation.

Copyright (c) 2026 Anthony J. Vasquez Sr.
"""

import io
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# BTB imports
from memory import MemoryEngine
from visualizer import Visualizer

# Configuration
MEMORY_ROOT = "swarm_brain"
_memory_engine: Optional[MemoryEngine] = None
_visualizer: Optional[Visualizer] = None


def get_memory_engine() -> MemoryEngine:
    """Lazy initialization of memory engine."""
    global _memory_engine
    if _memory_engine is None:
        os.makedirs(MEMORY_ROOT, exist_ok=True)
        _memory_engine = MemoryEngine(root=MEMORY_ROOT)
    return _memory_engine


def get_visualizer() -> Visualizer:
    """Lazy initialization of visualizer."""
    global _visualizer
    if _visualizer is None:
        _visualizer = Visualizer(MEMORY_ROOT)
    return _visualizer


# Simulated MCP tools (stubbed from btb_mcp_server.py for demo)
def btb_remember(content: str, outcome: str, tool: str = "refactor", **metadata) -> str:
    """Store memory via BTB memory engine."""
    engine = get_memory_engine()
    path = engine.remember(content=content, outcome=outcome, tool=tool, **metadata)
    return f"Stored at: {path}"


def btb_recall(
    pattern: Optional[str] = None,
    outcome: Optional[str] = None,
    tool: Optional[str] = None,
    limit: int = 5,
) -> List[Dict]:
    """Recall memories matching criteria."""
    engine = get_memory_engine()
    if pattern is None:
        parts = [MEMORY_ROOT]
        if outcome:
            parts.append(f"**/outcome={outcome}")
        if tool:
            parts.append(f"**/tool={tool}")
        parts.append("**/*.json")
        pattern = "/".join(parts)
    return engine.recall(pattern=pattern)[:limit]


def btb_reflect() -> Dict:
    """Reflect on memory patterns and generate insights."""
    engine = get_memory_engine()
    return engine.reflect()


def btb_map(max_depth: int = 4) -> str:
    """Generate topology map of memory."""
    viz = get_visualizer()
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    try:
        viz.map(max_depth=max_depth)
    finally:
        sys.stdout = old_stdout
    return buffer.getvalue()


# Simulated code execution (stub for demo; use real tool in production)
def simulate_code_execution(code: str) -> Dict[str, str]:
    """Execute Python code and return result."""
    try:
        exec_globals = {}
        exec(code, exec_globals)
        return {"status": "success", "output": str(exec_globals.get("result", "OK"))}
    except Exception as e:
        return {"status": "failure", "error": str(e)}


# Agent Classes
class CoderAgent:
    """
    Coder agent proposes code refactors.

    In production, this would call an LLM via MCP.
    For demo, uses hardcoded logic with simulated failure.
    """

    def refactor(
        self, original_code: str, goal: str, insights: Optional[List[str]] = None
    ) -> str:
        """
        Propose refactored code based on goal and insights.

        Args:
            original_code: Original code to refactor
            goal: Refactoring goal
            insights: Insights from Reflector (if any)

        Returns:
            Refactored code as string
        """
        if insights and any("off-by-one" in insight.lower() for insight in insights):
            # Apply insight: Fix to memoized fib
            refactored = """
def fib(n, memo=None):
    if memo is None:
        memo = {}
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fib(n-1, memo) + fib(n-2, memo)
    return memo[n]
result = fib(10)  # Should be 55
"""
        else:
            # Initial/failed attempt: Naive recursive with off-by-one
            refactored = """
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-3)  # Intentional error: n-3 instead of n-2
result = fib(10)  # Wrong: not 55
"""
        btb_remember(
            content=f"Proposed refactor for {goal}", outcome="interaction", tool="coder"
        )
        return refactored


class TesterAgent:
    """
    Tester agent runs tests and detects failures.

    Stores failures in BTB memory and recalls similar past failures.
    """

    def test(self, code: str, test_cases: List[Dict]) -> Dict:
        """
        Test code against test cases.

        Args:
            code: Code to test
            test_cases: List of dicts with 'input' and 'expected' keys

        Returns:
            Dict with status, details, and similar failures (if any)
        """
        result = simulate_code_execution(code)

        if result["status"] == "failure":
            similar = btb_recall(outcome="failure", tool="tester", limit=3)
            content = f"Test failed: {result['error']}. Similar past: {json.dumps([m.get('content', '') for m in similar])}"
            btb_remember(
                content=content, outcome="failure", tool="tester", error_type="runtime"
            )
            return {
                "status": "failure",
                "details": result["error"],
                "similar": similar,
            }

        # Check test cases
        passed = True
        for tc in test_cases:
            test_code = code + f"\nassert fib({tc['input']}) == {tc['expected']}"
            test_result = simulate_code_execution(test_code)
            if test_result["status"] != "success":
                passed = False
                break

        outcome = "success" if passed else "failure"
        btb_remember(
            content=f"Test result: {outcome}", outcome=outcome, tool="tester"
        )
        return {
            "status": outcome,
            "details": "All tests passed" if passed else "Some tests failed",
        }


class ReflectorAgent:
    """
    Reflector agent analyzes failures and generates insights.

    Uses BTB's reflect() and map() to understand failure patterns.
    """

    def reflect(self, failure_details: str) -> List[str]:
        """
        Reflect on failure and generate insights.

        Args:
            failure_details: Description of the failure

        Returns:
            List of insight strings
        """
        analysis = btb_reflect()
        map_view = btb_map(max_depth=3)

        # Extract insights from analysis
        insights = analysis.get("insights", [])

        # Add topology insights
        if "failure" in map_view:
            insights.append("High failure concentration detected in topology")

        # Simulate multi-hypothesis reasoning
        insights.extend(
            [
                "Check for off-by-one errors in recursion",
                "Consider adding memoization for efficiency",
                "Verify base cases are correct",
            ]
        )

        content = f"Reflected on failure: {failure_details}. Generated {len(insights)} insights."
        btb_remember(
            content=content, outcome="learning", tool="reflector", insight_type="pattern"
        )

        return insights


# Workflow: Simulate refactor task
def run_swarm(max_attempts: int = 3):
    """
    Run multi-agent swarm to refactor Fibonacci function.

    Demonstrates:
    - Coder proposes refactor
    - Tester validates
    - Reflector analyzes failures and provides insights
    - Loop until success or max attempts

    Args:
        max_attempts: Maximum number of refactor attempts
    """
    print("🤖 BTB Multi-Agent Swarm Demo")
    print("=" * 70)
    print("\nTask: Refactor naive Fibonacci to memoized O(n) version")
    print("Agents: Coder → Tester → Reflector (loop until success)\n")

    original_code = (
        "def fib(n):\n    if n <= 1: return n\n    return fib(n-1) + fib(n-2)"
    )
    goal = "Optimize Fibonacci to O(n) with memoization"
    test_cases = [
        {"input": 0, "expected": 0},
        {"input": 1, "expected": 1},
        {"input": 10, "expected": 55},
    ]

    coder = CoderAgent()
    tester = TesterAgent()
    reflector = ReflectorAgent()

    for attempt in range(1, max_attempts + 1):
        print(f"\n{'─' * 70}")
        print(f"ATTEMPT {attempt}/{max_attempts}")
        print(f"{'─' * 70}\n")

        # Coder proposes refactor
        insights = None if attempt == 1 else reflector.reflect("Previous test failed")
        if insights:
            print(f"💡 Reflector insights applied: {len(insights)} insights")
            for i, insight in enumerate(insights[:3], 1):
                print(f"   {i}. {insight}")
            print()

        refactored_code = coder.refactor(original_code, goal, insights)
        print("🔨 Coder proposed refactor:")
        print(refactored_code)

        # Tester validates
        print("\n🧪 Tester running validation...")
        test_result = tester.test(refactored_code, test_cases)
        print(f"   Status: {test_result['status'].upper()}")
        print(f"   Details: {test_result['details']}")

        if test_result["status"] == "success":
            print("\n" + "=" * 70)
            print("✅ SWARM SUCCEEDED!")
            print("=" * 70)
            print("\n📊 Final memory topology:")
            print(btb_map(max_depth=4))
            return refactored_code
        else:
            if "similar" in test_result:
                print(
                    f"   Similar failures recalled: {len(test_result['similar'])} memories"
                )

    print("\n" + "=" * 70)
    print("❌ MAX ATTEMPTS REACHED")
    print("=" * 70)
    print("\n🧠 Brain topology (for debugging):")
    print(btb_map(max_depth=4))
    return None


if __name__ == "__main__":
    print("\nStarting swarm simulation...\n")
    result = run_swarm(max_attempts=3)

    if result:
        print("\n✨ Final refactored code:")
        print(result)
    else:
        print("\n⚠️  Swarm did not converge. Check brain topology above.")

    print("\n💡 Key Takeaway:")
    print("   BTB memory enables multi-agent coordination through shared filesystem.")
    print("   Failures → Patterns → Insights → Success")
    print("   The topology IS the debugging interface.\n")
