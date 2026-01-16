"""
Back to the Basics - MCP Server

Native Model Context Protocol integration for BTB.
Gives any MCP-compatible model direct access to filesystem-based memory
and schema discovery capabilities.

Tools:
- btb_remember: Store a memory (routes automatically via schema)
- btb_recall: Query memories by pattern or intent
- btb_reflect: Analyze memory topology (see your own mind)
- btb_map: Get the fMRI visualization
- btb_hotspots: Find data concentration areas
- btb_derive: Discover schema from existing files (chaos → structure)
- btb_schema: View or export current routing schema
- btb_transmit: Route a packet through schema (dry-run supported)

Resources:
- btb://topology - Current topology structure
- btb://stats - Memory statistics
- btb://recent/{count} - Recent memories
- btb://schema - Current routing schema
- btb://health - Server health status

Prompts:
- memory_review - Review and reflect on recent memories
- debug_session - Debug with memory context
- schema_discovery - Discover schema from directory

Copyright (c) 2026 Anthony J. Vasquez Sr.
Licensed under Apache-2.0
"""

from __future__ import annotations

import os
import io
import sys
import json
import traceback
from pathlib import Path
from glob import glob as glob_files
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("MCP SDK not installed. Run: pip install mcp")
    raise

# Import BTB engines
from memory import MemoryEngine
from visualizer import Visualizer
from coherence import Coherence

# Optional: Import derive for schema discovery
try:
    from derive import derive_schema, generate_explanation
    DERIVE_AVAILABLE = True
except ImportError:
    derive_schema = None  # type: ignore
    generate_explanation = None  # type: ignore
    DERIVE_AVAILABLE = False

# Optional: Import threshold-protocols for governance
try:
    from threshold_protocols.utils.circuit import GovernanceCircuit
    from threshold_protocols.detection.threshold_detector import ThresholdDetector
    GOVERNANCE_AVAILABLE = True
except ImportError:
    GovernanceCircuit = None  # type: ignore
    ThresholdDetector = None  # type: ignore
    GOVERNANCE_AVAILABLE = False


# =============================================================================
# SERVER INITIALIZATION
# =============================================================================

mcp = FastMCP("Back to the Basics")

# Configuration via environment
MEMORY_ROOT = os.environ.get("BTB_MEMORY_ROOT", "agent_brain")
CONFIG_PATH = os.environ.get("BTB_CONFIG", "btb_thresholds.yaml")

# Lazy-initialized engines
_memory_engine: Optional[MemoryEngine] = None
_visualizer: Optional[Visualizer] = None
_coherence: Optional[Coherence] = None


def get_memory_engine() -> MemoryEngine:
    """Get or create the memory engine."""
    global _memory_engine
    if _memory_engine is None:
        os.makedirs(MEMORY_ROOT, exist_ok=True)
        _memory_engine = MemoryEngine(root=MEMORY_ROOT)
    return _memory_engine


def get_visualizer() -> Visualizer:
    """Get or create the visualizer."""
    global _visualizer
    if _visualizer is None:
        _visualizer = Visualizer(MEMORY_ROOT)
    return _visualizer


def get_coherence(schema: Optional[Dict] = None) -> Coherence:
    """Get or create the coherence engine."""
    global _coherence
    if _coherence is None or schema is not None:
        if schema is None:
            # Default schema for agent memory
            schema = {
                "outcome": {
                    "success": {"tool": {"*": "{timestamp}_{summary}.json"}},
                    "failure": {"tool": {"*": "{timestamp}_{summary}.json"}},
                    "learning": {"insight_type": {"*": "{timestamp}_{summary}.json"}},
                    "interaction": {"sentiment": {"*": "{timestamp}_{summary}.json"}}
                }
            }
        _coherence = Coherence(schema, root=MEMORY_ROOT)
    return _coherence


def _capture_stdout(func, *args, **kwargs) -> str:
    """Capture stdout from a function call."""
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    try:
        func(*args, **kwargs)
    finally:
        sys.stdout = old_stdout
    return buffer.getvalue()


def _format_error(e: Exception) -> str:
    """Format an exception for user-friendly display."""
    return f"Error: {type(e).__name__}: {str(e)}"


# =============================================================================
# MEMORY TOOLS
# =============================================================================

@mcp.tool()
def btb_remember(
    content: str,
    outcome: str,
    tool: str = "conversation",
    summary: Optional[str] = None,
    task_type: Optional[str] = None,
    error_type: Optional[str] = None,
    domain: Optional[str] = None,
    insight_type: Optional[str] = None,
    sentiment: Optional[str] = None,
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
        The path where the memory was stored, or error message
    """
    try:
        engine = get_memory_engine()

        # Build metadata kwargs
        metadata: Dict[str, Any] = {}
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
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def btb_recall(
    pattern: Optional[str] = None,
    outcome: Optional[str] = None,
    tool: Optional[str] = None,
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
    try:
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
                "content": str(mem.get("content", ""))[:200],  # Truncate long content
                "timestamp": mem.get("timestamp", ""),
                "path": mem.get("_path", ""),
            })

        return json.dumps(results, indent=2, default=str)
    except Exception as e:
        return _format_error(e)


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
    try:
        engine = get_memory_engine()
        analysis = engine.reflect()

        # Format insights as readable text
        output = {
            "total_memories": analysis.get("total_memories", 0),
            "by_outcome": analysis.get("by_outcome", {}),
            "by_tool": analysis.get("by_tool", {}),
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
    except Exception as e:
        return _format_error(e)


# =============================================================================
# VISUALIZATION TOOLS
# =============================================================================

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
    try:
        viz = get_visualizer()
        return _capture_stdout(viz.map, max_depth=max_depth)
    except Exception as e:
        return _format_error(e)


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
    try:
        viz = get_visualizer()
        spots = viz.hotspots(top_n=top_n)

        return json.dumps([
            {"path": str(path), "file_count": count}
            for path, count in spots
        ], indent=2)
    except Exception as e:
        return _format_error(e)


# =============================================================================
# SCHEMA DISCOVERY TOOLS
# =============================================================================

@mcp.tool()
def btb_derive(
    directory: Optional[str] = None,
    pattern: str = "**/*",
    max_clusters: int = 5,
    explain: bool = True,
) -> str:
    """
    Discover schema from existing files in a directory.

    Analyzes file paths to find latent structure (key=value patterns,
    common groupings). This is entropy -> structure.

    Uses Ward linkage clustering when sklearn available.

    Args:
        directory: Directory to analyze (default: MEMORY_ROOT)
        pattern: Glob pattern to match files (default: "**/*")
        max_clusters: Maximum clusters to discover (default: 5)
        explain: Include human-readable explanation (default: True)

    Returns:
        JSON with discovered schema and statistics
    """
    if not DERIVE_AVAILABLE:
        return json.dumps({
            "error": "derive module not available",
            "suggestion": "Install scikit-learn for Ward clustering: pip install scikit-learn numpy"
        }, indent=2)

    try:
        target_dir = directory or MEMORY_ROOT
        target_path = Path(target_dir)

        if not target_path.exists():
            return json.dumps({
                "error": f"Directory not found: {target_dir}",
                "suggestion": "Check the path or use btb_remember to create memories first"
            }, indent=2)

        # Find all files matching pattern
        file_paths = list(str(p) for p in target_path.glob(pattern) if p.is_file())

        if not file_paths:
            return json.dumps({
                "error": "No files found",
                "directory": target_dir,
                "pattern": pattern,
                "suggestion": "Try a broader pattern like '**/*' or create files first"
            }, indent=2)

        # Derive schema
        result = derive_schema(file_paths, max_clusters=max_clusters)

        # Add explanation if requested
        if explain and generate_explanation:
            result["_explanation"] = generate_explanation(
                result.get("_structure", {}),
                result.get("_stats", {})
            )

        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return json.dumps({
            "error": _format_error(e),
            "traceback": traceback.format_exc()
        }, indent=2)


@mcp.tool()
def btb_schema(
    format: str = "json",
    include_stats: bool = True,
) -> str:
    """
    View or export the current routing schema.

    Shows the decision tree that routes data to destinations.

    Args:
        format: Output format - 'json', 'tree', or 'yaml' (default: json)
        include_stats: Include usage statistics (default: True)

    Returns:
        Schema in requested format
    """
    try:
        engine = get_memory_engine()
        schema = engine.schema

        if format == "tree":
            # ASCII tree visualization
            lines = ["ROUTING SCHEMA", "=" * 40]

            def render_tree(node: Any, prefix: str = "", depth: int = 0) -> None:
                if isinstance(node, dict):
                    for i, (key, value) in enumerate(node.items()):
                        is_last = (i == len(node) - 1)
                        connector = "\\-- " if is_last else "|-- "
                        lines.append(f"{prefix}{connector}{key}")
                        new_prefix = prefix + ("    " if is_last else "|   ")
                        render_tree(value, new_prefix, depth + 1)
                else:
                    lines.append(f"{prefix}    -> {node}")

            render_tree(schema)
            return "\n".join(lines)

        elif format == "yaml":
            try:
                import yaml
                return yaml.dump(schema, default_flow_style=False, sort_keys=False)
            except ImportError:
                return json.dumps({
                    "error": "PyYAML not installed",
                    "schema": schema
                }, indent=2)

        else:  # json
            output: Dict[str, Any] = {"schema": schema}

            if include_stats:
                # Count files per schema branch
                viz = get_visualizer()
                summary = viz.summary()
                output["stats"] = {
                    "total_files": summary.get("total_files", 0),
                    "total_size": summary.get("total_size_human", "0B"),
                    "top_directories": summary.get("top_by_files", [])[:5]
                }

            return json.dumps(output, indent=2, default=str)
    except Exception as e:
        return _format_error(e)


@mcp.tool()
def btb_transmit(
    packet: str,
    dry_run: bool = True,
    create_file: bool = False,
) -> str:
    """
    Route a packet through the schema to find its destination.

    This IS inference. The packet flows through the logic tree
    and lands where it belongs.

    Args:
        packet: JSON string of packet attributes (metadata)
        dry_run: If True, just return path without creating directories (default: True)
        create_file: If True and not dry_run, create an empty file at destination

    Returns:
        The computed path where this data belongs
    """
    try:
        # Parse packet
        try:
            packet_dict = json.loads(packet)
        except json.JSONDecodeError as e:
            return json.dumps({
                "error": f"Invalid JSON packet: {e}",
                "example": '{"outcome": "success", "tool": "code_interpreter", "timestamp": "20260116"}'
            }, indent=2)

        coherence = get_coherence()

        # Add timestamp if missing
        if "timestamp" not in packet_dict:
            packet_dict["timestamp"] = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Route packet
        path = coherence.transmit(packet_dict, dry_run=dry_run)

        result = {
            "destination": path,
            "dry_run": dry_run,
            "packet": packet_dict
        }

        # Create file if requested
        if not dry_run and create_file:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                json.dump(packet_dict, f, indent=2, default=str)
            result["file_created"] = True

        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return _format_error(e)


# =============================================================================
# GOVERNANCE TOOLS (Optional - requires threshold-protocols)
# =============================================================================

@mcp.tool()
def btb_check_threshold(
    directory: Optional[str] = None,
    config_path: Optional[str] = None,
) -> str:
    """
    Check if a directory has crossed governance thresholds.

    Uses threshold-protocols to detect when autonomous reorganization
    would require approval.

    Args:
        directory: Directory to check (default: MEMORY_ROOT)
        config_path: Path to threshold config YAML (default: btb_thresholds.yaml)

    Returns:
        JSON with threshold status and recommendations
    """
    if not GOVERNANCE_AVAILABLE:
        return json.dumps({
            "governance_available": False,
            "suggestion": "Install threshold-protocols for governance: pip install threshold-protocols>=0.2.0"
        }, indent=2)

    try:
        target_dir = directory or MEMORY_ROOT
        config = config_path or CONFIG_PATH

        # Load detector
        detector = ThresholdDetector(config_path=config)

        # Run detection
        result = detector.detect(target_dir)

        return json.dumps({
            "directory": target_dir,
            "crossed_thresholds": result.crossed,
            "severity": result.severity.value if hasattr(result.severity, 'value') else str(result.severity),
            "metrics": {
                name: {"value": m.value, "limit": m.limit, "crossed": m.crossed}
                for name, m in result.metrics.items()
            },
            "recommendation": "PAUSE" if result.crossed else "PROCEED"
        }, indent=2, default=str)
    except Exception as e:
        return _format_error(e)


# =============================================================================
# RESOURCES
# =============================================================================

@mcp.resource("btb://topology")
def get_topology() -> str:
    """Get the current memory topology structure."""
    try:
        viz = get_visualizer()
        return _capture_stdout(viz.map, max_depth=3)
    except Exception as e:
        return _format_error(e)


@mcp.resource("btb://stats")
def get_stats() -> str:
    """Get memory statistics."""
    try:
        engine = get_memory_engine()
        analysis = engine.reflect()
        return json.dumps(analysis, indent=2, default=str)
    except Exception as e:
        return _format_error(e)


@mcp.resource("btb://recent/{count}")
def get_recent_memories(count: str = "5") -> str:
    """Get the N most recent memories."""
    try:
        engine = get_memory_engine()
        memories = engine.recall(pattern=f"{MEMORY_ROOT}/**/*.json")[:int(count)]
        return json.dumps(memories, indent=2, default=str)
    except Exception as e:
        return _format_error(e)


@mcp.resource("btb://schema")
def get_current_schema() -> str:
    """Get the current routing schema."""
    try:
        engine = get_memory_engine()
        return json.dumps({"schema": engine.schema}, indent=2, default=str)
    except Exception as e:
        return _format_error(e)


@mcp.resource("btb://health")
def get_health() -> str:
    """Get server health status."""
    return json.dumps({
        "status": "healthy",
        "memory_root": MEMORY_ROOT,
        "memory_root_exists": os.path.exists(MEMORY_ROOT),
        "derive_available": DERIVE_AVAILABLE,
        "governance_available": GOVERNANCE_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }, indent=2)


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


@mcp.prompt()
def schema_discovery(directory: str = ".") -> str:
    """Generate a prompt for discovering schema from a directory."""
    return f"""Analyze the structure of files in "{directory}" and discover the latent schema.

Steps:
1. Use btb_derive(directory="{directory}") to find patterns
2. Review the discovered schema structure
3. Suggest how to use this schema for routing new data
4. Identify any anomalies or areas that need reorganization

Report your findings with specific file paths and statistics."""


@mcp.prompt()
def governed_derive_prompt(directory: str = ".") -> str:
    """Generate a prompt for governed schema discovery and reorganization."""
    return f"""Analyze "{directory}" for potential reorganization with governance checks.

Steps:
1. Use btb_derive(directory="{directory}") to discover the latent schema
2. Use btb_check_threshold(directory="{directory}") to verify governance status
3. If thresholds are crossed, pause and explain what requires approval
4. If thresholds are clear, propose a reorganization plan

This follows the Threshold Pause protocol: capability WITH oversight."""


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    """
    Main entrypoint for the BTB MCP Server.

    Called when running `btb` from command line (via pyproject.toml script entry).

    Supports:
    - --root: Set memory root directory
    - --transport: stdio (default), streamable-http, or sse
    - --port: Port for HTTP transports (default 8000)
    - --config: Path to threshold config YAML
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="BTB MCP Server - Filesystem-based agent memory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  btb                           # Start with defaults (stdio transport)
  btb --root ./my_memories      # Custom memory directory
  btb --transport sse --port 9000  # SSE transport on port 9000

Environment Variables:
  BTB_MEMORY_ROOT  Default memory directory (default: agent_brain)
  BTB_CONFIG       Path to threshold config (default: btb_thresholds.yaml)
        """
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Memory root directory (default: $BTB_MEMORY_ROOT or 'agent_brain')"
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
        help="Port for HTTP transports (default: 8000)"
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to threshold config YAML"
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version and exit"
    )

    args = parser.parse_args()

    if args.version:
        print("BTB MCP Server v0.2.0")
        print(f"  Derive available: {DERIVE_AVAILABLE}")
        print(f"  Governance available: {GOVERNANCE_AVAILABLE}")
        return

    # Set globals from args
    global MEMORY_ROOT, CONFIG_PATH
    if args.root:
        MEMORY_ROOT = args.root
    if args.config:
        CONFIG_PATH = args.config

    os.makedirs(MEMORY_ROOT, exist_ok=True)

    print(f"BTB MCP Server starting...")
    print(f"  Memory root: {MEMORY_ROOT}")
    print(f"  Transport: {args.transport}")
    print(f"  Derive: {'enabled' if DERIVE_AVAILABLE else 'disabled (install scikit-learn)'}")
    print(f"  Governance: {'enabled' if GOVERNANCE_AVAILABLE else 'disabled (install threshold-protocols)'}")

    # Run server
    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
