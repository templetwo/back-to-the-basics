"""
Agentic Memory: The Cortex

A filesystem-based memory system for LLM agents.

Instead of stuffing memories into opaque vector databases,
the agent organizes its own experience semantically using
the Coherence Engine.

The agent can browse its own mind. The topology IS the insight.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from glob import glob as glob_files

from coherence import Coherence


# =============================================================================
# DEFAULT MEMORY SCHEMA
# =============================================================================
# This schema defines how experiences are routed into memory.
# The path structure encodes: outcome, tool used, domain, emotional valence.

MEMORY_SCHEMA = {
    "outcome": {
        "success": {
            "tool": {
                "code_interpreter": {
                    "task_type": {
                        "write": "{timestamp}_{summary}.json",
                        "debug": "{timestamp}_{summary}.json",
                        "refactor": "{timestamp}_{summary}.json",
                        "explain": "{timestamp}_{summary}.json",
                    }
                },
                "web_search": {
                    "domain": {
                        "technical": "{timestamp}_{summary}.json",
                        "research": "{timestamp}_{summary}.json",
                        "general": "{timestamp}_{summary}.json",
                    }
                },
                "file_operation": "{timestamp}_{summary}.json",
                "conversation": "{timestamp}_{summary}.json",
            }
        },
        "failure": {
            "tool": {
                "code_interpreter": {
                    "error_type": {
                        "syntax": "{timestamp}_{summary}.json",
                        "runtime": "{timestamp}_{summary}.json",
                        "logic": "{timestamp}_{summary}.json",
                        "timeout": "{timestamp}_{summary}.json",
                    }
                },
                "web_search": {
                    "reason": {
                        "no_results": "{timestamp}_{summary}.json",
                        "blocked": "{timestamp}_{summary}.json",
                        "irrelevant": "{timestamp}_{summary}.json",
                    }
                },
                "file_operation": "{timestamp}_{summary}.json",
                "unknown": "{timestamp}_{summary}.json",
            }
        },
        "learning": {
            "insight_type": {
                "pattern": "{timestamp}_{summary}.json",
                "correction": "{timestamp}_{summary}.json",
                "preference": "{timestamp}_{summary}.json",
                "fact": "{timestamp}_{summary}.json",
            }
        },
        "interaction": {
            "sentiment": {
                "positive": "{timestamp}_{summary}.json",
                "neutral": "{timestamp}_{summary}.json",
                "negative": "{timestamp}_{summary}.json",
            }
        }
    }
}


class MemoryEngine:
    """
    Agentic Memory using filesystem topology.

    The agent's memories are organized semantically in a directory tree.
    The structure itself encodes patterns - a deep failure/code/refactor
    path signals a struggle area.

    Unlike vector DBs, you can browse this. You can `ls` your own mind.
    """

    def __init__(self, root: str = "memories", schema: Dict = None):
        """
        Initialize the memory engine.

        Args:
            root: Root directory for memories
            schema: Memory routing schema (uses default if None)
        """
        self.root = root
        self.schema = schema or MEMORY_SCHEMA
        self.engine = Coherence(self.schema, root=root)
        os.makedirs(root, exist_ok=True)

    def remember(self,
                 content: Any,
                 outcome: str,
                 tool: str = None,
                 summary: str = None,
                 **metadata) -> str:
        """
        Store a memory. It routes itself to the right location.

        Args:
            content: The memory content (will be JSON serialized)
            outcome: 'success', 'failure', 'learning', or 'interaction'
            tool: The tool used (if applicable)
            summary: Brief summary for filename (auto-generated if None)
            **metadata: Additional routing keys (task_type, error_type, etc.)

        Returns:
            Path where the memory was stored
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Generate summary if not provided
        if summary is None:
            if isinstance(content, str):
                summary = content[:30].replace(" ", "_").replace("/", "-")
            else:
                summary = "memory"
        summary = self._sanitize(summary)

        # Build packet for routing
        packet = {
            "outcome": outcome,
            "timestamp": timestamp,
            "summary": summary,
            **metadata
        }
        if tool:
            packet["tool"] = tool

        # Route to find destination
        path = self.engine.transmit(packet, dry_run=False)

        # Ensure it's a JSON file
        if not path.endswith('.json'):
            path = path.rstrip('/') + f"/{timestamp}_{summary}.json"

        # Prepare memory document
        memory_doc = {
            "timestamp": datetime.now().isoformat(),
            "outcome": outcome,
            "tool": tool,
            "summary": summary,
            "content": content,
            "metadata": metadata,
            "_path": path
        }

        # Write to disk
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(memory_doc, f, indent=2, default=str)

        return path

    def recall(self, pattern: str = None, **intent) -> List[Dict]:
        """
        Recall memories by glob pattern or intent.

        Args:
            pattern: Direct glob pattern (e.g., "**/failure/**/*.json")
            **intent: Key-value pairs to generate pattern (e.g., outcome="failure")

        Returns:
            List of memory documents matching the query
        """
        if pattern is None:
            # Generate pattern from intent
            pattern = self.engine.receive(**intent)
            if not pattern.endswith('*.json'):
                pattern = pattern.rstrip('/*') + '/**/*.json'

        # Find matching files
        matches = glob_files(pattern, recursive=True)

        memories = []
        for path in sorted(matches, reverse=True):  # Newest first
            try:
                with open(path) as f:
                    doc = json.load(f)
                    doc['_path'] = path
                    memories.append(doc)
            except (json.JSONDecodeError, IOError):
                continue

        return memories

    def reflect(self, domain: str = None) -> Dict:
        """
        Reflect on memory patterns. Analyze the topology itself.

        This is the "browsing your own mind" operation.
        The structure of directories reveals patterns.

        Args:
            domain: Specific domain to reflect on (None = all)

        Returns:
            Analysis of memory distribution
        """
        base = Path(self.root)

        analysis = {
            "total_memories": 0,
            "by_outcome": {},
            "by_tool": {},
            "failure_hotspots": [],
            "success_patterns": [],
            "recent": [],
            "insights": []
        }

        # Count by outcome
        for outcome in ["success", "failure", "learning", "interaction"]:
            pattern = f"**/outcome={outcome}/**/*.json"
            matches = list(base.glob(pattern))
            count = len(matches)
            analysis["total_memories"] += count
            analysis["by_outcome"][outcome] = count

        # Count by tool
        for tool in ["code_interpreter", "web_search", "file_operation", "conversation"]:
            pattern = f"**/tool={tool}/**/*.json"
            matches = list(base.glob(pattern))
            analysis["by_tool"][tool] = len(matches)

        # Find failure hotspots (deep failure paths)
        failure_paths = list(base.glob("**/outcome=failure/**/*.json"))
        failure_areas = {}
        for fp in failure_paths:
            # Extract the tool/task from path
            parts = str(fp).split('/')
            key_parts = [p for p in parts if '=' in p and 'outcome' not in p]
            if key_parts:
                area = '/'.join(key_parts[:2])  # e.g., "tool=code_interpreter/task_type=refactor"
                failure_areas[area] = failure_areas.get(area, 0) + 1

        # Top failure areas
        analysis["failure_hotspots"] = sorted(
            failure_areas.items(), key=lambda x: -x[1]
        )[:5]

        # Find success patterns
        success_paths = list(base.glob("**/outcome=success/**/*.json"))
        success_areas = {}
        for sp in success_paths:
            parts = str(sp).split('/')
            key_parts = [p for p in parts if '=' in p and 'outcome' not in p]
            if key_parts:
                area = '/'.join(key_parts[:2])
                success_areas[area] = success_areas.get(area, 0) + 1

        analysis["success_patterns"] = sorted(
            success_areas.items(), key=lambda x: -x[1]
        )[:5]

        # Recent memories
        all_memories = list(base.glob("**/*.json"))
        all_memories.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        for mem_path in all_memories[:5]:
            try:
                with open(mem_path) as f:
                    doc = json.load(f)
                    analysis["recent"].append({
                        "summary": doc.get("summary", "?"),
                        "outcome": doc.get("outcome", "?"),
                        "when": doc.get("timestamp", "?")
                    })
            except (json.JSONDecodeError, IOError):
                continue

        # Generate insights
        if analysis["by_outcome"].get("failure", 0) > analysis["by_outcome"].get("success", 0):
            analysis["insights"].append("More failures than successes - consider reviewing approach")

        if analysis["failure_hotspots"]:
            top_failure = analysis["failure_hotspots"][0]
            analysis["insights"].append(f"Frequent failures in: {top_failure[0]} ({top_failure[1]} times)")

        if analysis["success_patterns"]:
            top_success = analysis["success_patterns"][0]
            analysis["insights"].append(f"Strong in: {top_success[0]} ({top_success[1]} successes)")

        return analysis

    def forget(self, pattern: str = None, before: datetime = None, **intent) -> int:
        """
        Forget (delete) memories matching criteria.

        Args:
            pattern: Glob pattern to match
            before: Delete memories before this time
            **intent: Key-value pairs to generate pattern

        Returns:
            Number of memories deleted
        """
        if pattern is None:
            pattern = self.engine.receive(**intent)
            if not pattern.endswith('*.json'):
                pattern = pattern.rstrip('/*') + '/**/*.json'

        matches = glob_files(pattern, recursive=True)
        deleted = 0

        for path in matches:
            try:
                if before:
                    with open(path) as f:
                        doc = json.load(f)
                        mem_time = datetime.fromisoformat(doc.get("timestamp", ""))
                        if mem_time >= before:
                            continue

                os.remove(path)
                deleted += 1
            except (json.JSONDecodeError, IOError, ValueError):
                continue

        return deleted

    def _sanitize(self, s: str) -> str:
        """Sanitize string for filename."""
        import re
        s = re.sub(r'[^\w\-.]', '_', str(s))
        return s[:50]  # Limit length


# =============================================================================
# DEMONSTRATION
# =============================================================================

if __name__ == "__main__":

    print("=" * 70)
    print("AGENTIC MEMORY: The Cortex")
    print("Browse your own mind. The topology IS the insight.")
    print("=" * 70)

    # Initialize
    memory = MemoryEngine(root="agent_memories")

    # ─────────────────────────────────────────────────────────────────────────
    # Simulate agent experiences
    # ─────────────────────────────────────────────────────────────────────────

    print("\n[REMEMBERING] Storing agent experiences...\n")

    experiences = [
        # Successes
        {
            "content": "Successfully refactored auth module, reduced complexity by 40%",
            "outcome": "success",
            "tool": "code_interpreter",
            "task_type": "refactor",
            "summary": "auth_refactor_win"
        },
        {
            "content": "Found critical security vulnerability via web search",
            "outcome": "success",
            "tool": "web_search",
            "domain": "technical",
            "summary": "security_find"
        },
        {
            "content": "Debugged race condition in payment processor",
            "outcome": "success",
            "tool": "code_interpreter",
            "task_type": "debug",
            "summary": "race_condition_fix"
        },

        # Failures
        {
            "content": "Syntax error when generating Python - forgot colon",
            "outcome": "failure",
            "tool": "code_interpreter",
            "error_type": "syntax",
            "summary": "colon_mistake"
        },
        {
            "content": "Refactor introduced subtle bug, broke tests",
            "outcome": "failure",
            "tool": "code_interpreter",
            "error_type": "logic",
            "summary": "refactor_broke_tests"
        },
        {
            "content": "Another refactor failure - didn't understand existing pattern",
            "outcome": "failure",
            "tool": "code_interpreter",
            "error_type": "logic",
            "summary": "refactor_misunderstanding"
        },
        {
            "content": "Web search returned no useful results for niche topic",
            "outcome": "failure",
            "tool": "web_search",
            "reason": "no_results",
            "summary": "niche_search_fail"
        },

        # Learnings
        {
            "content": "User prefers concise responses without emojis",
            "outcome": "learning",
            "insight_type": "preference",
            "summary": "no_emojis_pref"
        },
        {
            "content": "This codebase uses factory pattern extensively",
            "outcome": "learning",
            "insight_type": "pattern",
            "summary": "factory_pattern_used"
        },

        # Interactions
        {
            "content": "User expressed frustration with slow response",
            "outcome": "interaction",
            "sentiment": "negative",
            "summary": "user_frustrated"
        },
        {
            "content": "User praised the refactoring work",
            "outcome": "interaction",
            "sentiment": "positive",
            "summary": "user_happy"
        },
    ]

    for exp in experiences:
        path = memory.remember(**exp)
        print(f"  [{exp['outcome']:11}] {exp.get('summary', '?'):25} → ...{path[-50:]}")

    # ─────────────────────────────────────────────────────────────────────────
    # Recall by intent
    # ─────────────────────────────────────────────────────────────────────────

    print("\n" + "=" * 70)
    print("[RECALL] Querying memories by intent")
    print("=" * 70)

    # Have I failed before?
    print("\n  Query: 'Have I failed before?'")
    failures = memory.recall(outcome="failure")
    print(f"  Found: {len(failures)} failure memories")
    for f in failures[:3]:
        print(f"    - {f.get('summary')}: {f.get('content', '')[:50]}...")

    # What do I know about code?
    print("\n  Query: 'What have I done with code_interpreter?'")
    code_memories = memory.recall(tool="code_interpreter")
    print(f"  Found: {len(code_memories)} code memories")

    # What patterns have I learned?
    print("\n  Query: 'What patterns have I learned?'")
    patterns = memory.recall(outcome="learning", insight_type="pattern")
    print(f"  Found: {len(patterns)} pattern insights")
    for p in patterns:
        print(f"    - {p.get('content')}")

    # ─────────────────────────────────────────────────────────────────────────
    # Reflect on patterns
    # ─────────────────────────────────────────────────────────────────────────

    print("\n" + "=" * 70)
    print("[REFLECT] Analyzing memory topology")
    print("=" * 70 + "\n")

    reflection = memory.reflect()

    print(f"  Total memories: {reflection['total_memories']}")
    print(f"\n  By outcome:")
    for outcome, count in reflection['by_outcome'].items():
        bar = "#" * count
        print(f"    {outcome:12}: {bar} ({count})")

    print(f"\n  By tool:")
    for tool, count in reflection['by_tool'].items():
        if count > 0:
            bar = "#" * count
            print(f"    {tool:18}: {bar} ({count})")

    print(f"\n  Failure hotspots (where I struggle):")
    for area, count in reflection['failure_hotspots']:
        print(f"    - {area}: {count} failures")

    print(f"\n  Success patterns (where I shine):")
    for area, count in reflection['success_patterns']:
        print(f"    - {area}: {count} successes")

    print(f"\n  Insights:")
    for insight in reflection['insights']:
        print(f"    * {insight}")

    # ─────────────────────────────────────────────────────────────────────────
    # Show the filesystem structure
    # ─────────────────────────────────────────────────────────────────────────

    print("\n" + "=" * 70)
    print("[TOPOLOGY] The mind as browsable structure")
    print("=" * 70 + "\n")

    for root, dirs, files in os.walk("agent_memories"):
        level = root.replace("agent_memories", "").count(os.sep)
        indent = "  " * level
        folder = os.path.basename(root)
        if '=' in folder:
            key, val = folder.split('=', 1)
            print(f"{indent}{key}={val}/")
        else:
            print(f"{indent}{folder}/")

        # Only show files at leaf level
        if not dirs:
            subindent = "  " * (level + 1)
            for f in files:
                print(f"{subindent}{f}")

    print("\n" + "=" * 70)
    print("The agent can browse its own experience.")
    print("The topology reveals what vector DBs hide.")
    print("=" * 70)
