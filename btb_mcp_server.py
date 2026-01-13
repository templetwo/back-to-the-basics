"""
Back to the Basics - MCP Server

Native Model Context Protocol integration for BTB.
Gives any MCP-compatible model direct access to filesystem-based memory.

Tools:
- btb_remember: Store a memory (routes automatically)
- btb_recall: Query memories by pattern or intent
- btb_reflect: Analyze memory topology (see your own mind)
- btb_map: Get the fMRI visualization

Resources:
- btb://memories - Browse all memories
- btb://topology - Current topology structure

Copyright (c) 2026 Anthony J. Vasquez Sr.
"""

import os
import json
from pathlib import Path
from glob import glob as glob_files
from typing import Optional
from datetime import datetime

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("MCP SDK not installed. Run: pip install mcp")
    raise

# Import BTB engines
from memory import MemoryEngine
from visualizer import Visualizer


# =============================================================================
# SERVER INITIALIZATION
# =============================================================================

mcp = FastMCP("Back to the Basics")

# Default memory root - can be overridden via environment
MEMORY_ROOT = os.environ.get("BTB_MEMORY_ROOT", "agent_brain")

# Initialize engines lazily
_memory_engine: Optional[MemoryEngine] = None
_visualizer: Optional[Visualizer] = None


def get_memory_engine() -> MemoryEngine:
    """Get or create the memory engine."""
    global _memory_engine
    if _memory_engine is None:
        _memory_engine = MemoryEngine(root=MEMORY_ROOT)
    return _memory_engine


def get_visualizer() -> Visualizer:
    """Get or create the visualizer."""
    global _visualizer
    if _visualizer is None:
        _visualizer = Visualizer(MEMORY_ROOT)
    return _visualizer


# =============================================================================
# TOOLS
# =============================================================================

@mcp.tool()
def btb_remember(
    content: str,
    outcome: str,
    tool: str = "conversation",
    summary: str = None,
    task_type: str = None,
    error_type: str = None,
    domain: str = None,
    insight_type: str = None,
    sentiment: str = None,
) -> str:
    """
    Store a memory in the BTB filesystem brain.

    The memory automatically routes itself to the correct location
    based on the outcome and metadata provided.

    Args:
        content: The memory content (what happened, what you learned)
        outcome: One of 'success', 'failure', 'learning', 'interaction'
        tool: Tool used - 'code_interpreter', 'web_search', 'file_operation', 'conversation'
        summary: Brief summary for the memory (auto-generated if not provided)
        task_type: For successes - 'write', 'debug', 'refactor', 'explain'
        error_type: For failures - 'syntax', 'runtime', 'logic', 'timeout'
        domain: For web_search - 'technical', 'research', 'general'
        insight_type: For learning - 'pattern', 'correction', 'preference', 'fact'
        sentiment: For interaction - 'positive', 'neutral', 'negative'

    Returns:
        The path where the memory was stored
    """
    engine = get_memory_engine()

    # Build metadata kwargs
    metadata = {}
    if task_type:
        metadata["task_type"] = task_type
    if error_type:
        metadata["error_type"] = error_type
    if domain:
        metadata["domain"] = domain
    if insight_type:
        metadata["insight_type"] = insight_type
    if sentiment:
        metadata["sentiment"] = sentiment

    path = engine.remember(
        content=content,
        outcome=outcome,
        tool=tool,
        summary=summary,
        **metadata
    )

    return f"Memory stored at: {path}"


@mcp.tool()
def btb_recall(
    pattern: str = None,
    outcome: str = None,
    tool: str = None,
    limit: int = 10,
) -> str:
    """
    Recall memories from the BTB brain.

    Query by glob pattern or by intent (outcome/tool filters).
    Returns memories newest first.

    Args:
        pattern: Direct glob pattern (e.g., "**/failure/**/*.json")
        outcome: Filter by outcome ('success', 'failure', 'learning', 'interaction')
        tool: Filter by tool ('code_interpreter', 'web_search', etc.)
        limit: Maximum number of memories to return (default 10)

    Returns:
        JSON array of matching memories
    """
    engine = get_memory_engine()

    # Build pattern from intent if not provided
    if pattern is None:
        parts = [MEMORY_ROOT]
        if outcome:
            parts.append(f"**/outcome={outcome}")
        if tool:
            parts.append(f"**/tool={tool}")
        parts.append("**/*.json")
        pattern = "/".join(parts)

    memories = engine.recall(pattern=pattern)[:limit]

    # Simplify for response
    results = []
    for mem in memories:
        results.append({
            "summary": mem.get("summary", ""),
            "outcome": mem.get("outcome", ""),
            "tool": mem.get("tool", ""),
            "content": mem.get("content", "")[:200],  # Truncate long content
            "timestamp": mem.get("timestamp", ""),
            "path": mem.get("_path", ""),
        })

    return json.dumps(results, indent=2, default=str)


@mcp.tool()
def btb_reflect() -> str:
    """
    Reflect on memory patterns. See the shape of your own mind.

    Analyzes the memory topology to reveal:
    - Total memories by outcome
    - Success patterns (what you're good at)
    - Failure hotspots (where you struggle)
    - Recent activity
    - Auto-generated insights

    Returns:
        JSON analysis of memory distribution and patterns
    """
    engine = get_memory_engine()
    analysis = engine.reflect()

    # Format insights as readable text
    output = {
        "total_memories": analysis["total_memories"],
        "by_outcome": analysis["by_outcome"],
        "by_tool": analysis["by_tool"],
        "failure_hotspots": [
            f"{area}: {count} failures"
            for area, count in analysis.get("failure_hotspots", [])
        ],
        "success_patterns": [
            f"{area}: {count} successes"
            for area, count in analysis.get("success_patterns", [])
        ],
        "recent_memories": analysis.get("recent", []),
        "insights": analysis.get("insights", []),
    }

    return json.dumps(output, indent=2, default=str)


@mcp.tool()
def btb_map(max_depth: int = 4) -> str:
    """
    Generate an fMRI visualization of the memory topology.

    Shows the directory tree with bar charts indicating
    where data concentrates. The brain you can SEE.

    Args:
        max_depth: Maximum directory depth to display (default 4)

    Returns:
        ASCII topology map with statistics
    """
    viz = get_visualizer()

    # Capture the map output
    import io
    import sys

    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()

    try:
        viz.map(max_depth=max_depth)
    finally:
        sys.stdout = old_stdout

    return buffer.getvalue()


@mcp.tool()
def btb_hotspots(top_n: int = 10) -> str:
    """
    Find the hottest areas in memory (most data concentration).

    Identifies directories with disproportionate data accumulation.
    Useful for understanding where the agent's attention focuses.

    Args:
        top_n: Number of hotspots to return (default 10)

    Returns:
        JSON list of hotspot directories with file counts
    """
    viz = get_visualizer()
    spots = viz.hotspots(top_n=top_n)

    return json.dumps([
        {"path": path, "file_count": count}
        for path, count in spots
    ], indent=2)


# =============================================================================
# RESOURCES
# =============================================================================

@mcp.resource("btb://topology")
def get_topology() -> str:
    """Get the current memory topology structure."""
    viz = get_visualizer()

    import io
    import sys

    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()

    try:
        viz.map(max_depth=3)
    finally:
        sys.stdout = old_stdout

    return buffer.getvalue()


@mcp.resource("btb://stats")
def get_stats() -> str:
    """Get memory statistics."""
    engine = get_memory_engine()
    analysis = engine.reflect()
    return json.dumps(analysis, indent=2, default=str)


@mcp.resource("btb://recent/{count}")
def get_recent_memories(count: str = "5") -> str:
    """Get the N most recent memories."""
    engine = get_memory_engine()
    memories = engine.recall(pattern=f"{MEMORY_ROOT}/**/*.json")[:int(count)]
    return json.dumps(memories, indent=2, default=str)


# =============================================================================
# PROMPTS
# =============================================================================

@mcp.prompt()
def memory_review() -> str:
    """Generate a prompt to review and reflect on recent memories."""
    return """Please review my recent memories and provide insights:

1. What patterns do you see in my successes?
2. Where am I struggling (failure hotspots)?
3. What should I focus on improving?

Use btb_reflect() to analyze the topology, then provide actionable insights."""


@mcp.prompt()
def debug_session(error_description: str) -> str:
    """Generate a prompt for debugging with memory context."""
    return f"""I encountered an error: {error_description}

Before debugging, recall my past failures with btb_recall(outcome="failure").
Check if I've seen similar errors before and what I learned.

Then help me debug, and remember to store the outcome when we're done."""


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="BTB MCP Server")
    parser.add_argument(
        "--root",
        default="agent_brain",
        help="Memory root directory (default: agent_brain)"
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http", "sse"],
        default="stdio",
        help="Transport protocol (default: stdio)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP transport (default: 8000)"
    )

    args = parser.parse_args()

    # Set memory root
    MEMORY_ROOT = args.root
    os.makedirs(MEMORY_ROOT, exist_ok=True)

    print(f"🧠 BTB MCP Server starting...")
    print(f"   Memory root: {MEMORY_ROOT}")
    print(f"   Transport: {args.transport}")

    # Run server
    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.run(transport=args.transport)
