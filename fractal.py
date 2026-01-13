"""
Fractal Coherence: Self-Similar Routing Networks

The schema contains itself. Patterns nest within patterns.
Data tunnels down until it finds its resonant depth.

Key insight: At each level, the same structural pattern can apply.
The depth is determined by the data's own structure.
"""

import os
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


class FractalRouter:
    """
    A router where the same pattern repeats at every scale.

    Instead of explicit recursion markers, we use a simpler model:
    - Schema defines a pattern
    - Each packet has a "depth" or "layers" field
    - The router applies the pattern N times based on the data
    """

    def __init__(self, pattern: Dict, root: str = "fractal", max_depth: int = 10):
        """
        Initialize with a repeating pattern.

        Args:
            pattern: The pattern to apply at each level
            root: Root directory
            max_depth: Safety limit on recursion
        """
        self.pattern = pattern
        self.root = root
        self.max_depth = max_depth
        self.history: List[Dict] = []

        os.makedirs(root, exist_ok=True)

    def route(self, packet: Dict) -> Dict:
        """
        Route a packet through the fractal pattern.

        The packet can specify its own depth via:
        - "layers": list of dicts, each routed at successive depth
        - "depth": explicit depth to tunnel to
        - Or just route once at depth 0
        """
        path_segments = [self.root]
        trace = []
        depth = 0

        # Check for layered data
        layers = packet.get("layers", [packet])
        if not isinstance(layers, list):
            layers = [packet]

        # Process each layer
        for layer_idx, layer in enumerate(layers):
            if layer_idx >= self.max_depth:
                trace.append(f"MAX_DEPTH_REACHED@{layer_idx}")
                break

            depth = layer_idx

            # Apply pattern to this layer
            matched, segment = self._apply_pattern(layer, self.pattern)

            if matched:
                path_segments.append(f"d{depth}_{segment}")
                trace.append(f"d{depth}:{segment}")
            else:
                path_segments.append(f"d{depth}_unmatched")
                trace.append(f"d{depth}:NO_MATCH")
                break

        # Add timestamp leaf
        ts = packet.get("timestamp", datetime.now().strftime("%Y%m%d_%H%M%S"))
        path_segments.append(f"{ts}.json")

        result = {
            "path": "/".join(path_segments),
            "depth": depth,
            "trace": trace,
            "layers_processed": min(len(layers), self.max_depth)
        }

        self.history.append(result)
        return result

    def _apply_pattern(self, data: Dict, pattern: Dict) -> Tuple[bool, str]:
        """Apply the pattern to extract a path segment."""
        for key, branches in pattern.items():
            if key in data:
                val = data[key]

                if isinstance(branches, dict):
                    # Try exact match
                    if val in branches:
                        return True, f"{key}={val}"
                    # Try wildcard
                    if "*" in branches:
                        return True, f"{key}={val}"
                elif isinstance(branches, str):
                    return True, f"{key}={val}"

        return False, ""

    def transmit(self, packet: Dict, dry_run: bool = False) -> str:
        """Route and optionally persist."""
        result = self.route(packet)

        if not dry_run:
            path = Path(result["path"])
            os.makedirs(path.parent, exist_ok=True)

            with open(path, "w") as f:
                output = {**packet, "_routing": result}
                json.dump(output, f, indent=2, default=str)

        return result["path"]

    def analyze(self) -> Dict:
        """Analyze routing patterns across history."""
        if not self.history:
            return {"total": 0}

        analysis = {
            "total": len(self.history),
            "depth_distribution": defaultdict(int),
            "max_depth": 0,
            "avg_depth": 0,
            "paths": defaultdict(int)
        }

        total_depth = 0
        for r in self.history:
            d = r["depth"]
            analysis["depth_distribution"][d] += 1
            analysis["max_depth"] = max(analysis["max_depth"], d)
            total_depth += d

            # Track unique path patterns
            path_pattern = "/".join(r["trace"])
            analysis["paths"][path_pattern] += 1

        analysis["avg_depth"] = total_depth / len(self.history)
        analysis["depth_distribution"] = dict(sorted(analysis["depth_distribution"].items()))
        analysis["top_paths"] = sorted(analysis["paths"].items(), key=lambda x: -x[1])[:10]
        del analysis["paths"]

        return analysis


class DeepFractalRouter:
    """
    True fractal routing: the same decision structure at every level.

    Uses a single pattern that applies recursively.
    Each match descends one level deeper into both the schema and the path.
    """

    def __init__(self, dimensions: List[str], root: str = "deep_fractal", max_depth: int = 10):
        """
        Args:
            dimensions: List of keys to match at each level (same at every depth)
            root: Root directory
            max_depth: Maximum recursion depth
        """
        self.dimensions = dimensions
        self.root = root
        self.max_depth = max_depth
        self.history: List[Dict] = []

        os.makedirs(root, exist_ok=True)

    def route(self, packet: Dict) -> Dict:
        """
        Route through fractal dimensions.

        At each depth, we look for the next dimension key.
        The packet can have nested structure or flat structure with indexed keys.
        """
        path_segments = [self.root]
        trace = []
        current = packet
        depth = 0

        while depth < self.max_depth:
            # Get dimension for this depth
            dim_idx = depth % len(self.dimensions)
            dim = self.dimensions[dim_idx]

            # Try to find this dimension in current context
            if dim in current:
                val = current[dim]

                if isinstance(val, dict):
                    # Nested structure - descend into it
                    path_segments.append(f"{dim}={list(val.keys())[0] if val else 'empty'}")
                    trace.append(f"d{depth}:{dim}→nested")
                    current = val.get(list(val.keys())[0], {}) if val else {}
                    depth += 1
                elif isinstance(val, list) and val:
                    # List of items - route first item, note multiplicity
                    path_segments.append(f"{dim}=list[{len(val)}]")
                    trace.append(f"d{depth}:{dim}→list({len(val)})")
                    current = val[0] if isinstance(val[0], dict) else {}
                    depth += 1
                else:
                    # Scalar value - terminal at this dimension
                    path_segments.append(f"{dim}={val}")
                    trace.append(f"d{depth}:{dim}={val}")
                    depth += 1

                    # Check if there's more structure
                    remaining_keys = [k for k in current.keys() if k != dim and not k.startswith("_")]
                    if not remaining_keys:
                        break
                    # Continue with remaining structure
                    current = {k: current[k] for k in remaining_keys}
            else:
                # Dimension not found - try next dimension
                found_any = False
                for alt_dim in self.dimensions:
                    if alt_dim in current and alt_dim != dim:
                        # Use alternative dimension
                        val = current[alt_dim]
                        path_segments.append(f"{alt_dim}={val}")
                        trace.append(f"d{depth}:{alt_dim}={val}(alt)")
                        remaining = {k: v for k, v in current.items() if k != alt_dim and not k.startswith("_")}
                        current = remaining
                        found_any = True
                        depth += 1
                        break

                if not found_any:
                    trace.append(f"d{depth}:NO_DIM")
                    break

        # Finalize path
        ts = packet.get("timestamp", datetime.now().strftime("%Y%m%d_%H%M%S"))
        path_segments.append(f"{ts}.json")

        result = {
            "path": "/".join(path_segments),
            "depth": depth,
            "trace": trace,
        }

        self.history.append(result)
        return result

    def transmit(self, packet: Dict, dry_run: bool = False) -> str:
        """Route and optionally persist."""
        result = self.route(packet)

        if not dry_run:
            path = Path(result["path"])
            os.makedirs(path.parent, exist_ok=True)
            with open(path, "w") as f:
                json.dump({**packet, "_routing": result}, f, indent=2, default=str)

        return result["path"]

    def analyze(self) -> Dict:
        """Analyze routing patterns."""
        if not self.history:
            return {"total": 0}

        depths = [r["depth"] for r in self.history]

        return {
            "total": len(self.history),
            "max_depth": max(depths),
            "avg_depth": sum(depths) / len(depths),
            "depth_distribution": dict(sorted(
                {d: depths.count(d) for d in set(depths)}.items()
            ))
        }


# =============================================================================
# DEMONSTRATION
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("FRACTAL COHERENCE: Self-Similar Routing Networks")
    print("=" * 70)

    # --- Demo 1: Layered Packets ---
    print("\n[1] LAYERED PACKETS (Each layer = one depth level)")
    print("-" * 50)

    pattern = {
        "type": {"*": True},
        "category": {"*": True},
        "action": {"*": True}
    }

    router = FractalRouter(pattern, root="fractal/layered")

    # Single layer packet
    p1 = {"type": "event", "timestamp": "001"}
    r1 = router.route(p1)
    print(f"  Single layer: {r1['trace']} → depth {r1['depth']}")

    # Multi-layer packet (nested events)
    p2 = {
        "layers": [
            {"type": "transaction"},
            {"type": "validation"},
            {"type": "commit"},
        ],
        "timestamp": "002"
    }
    r2 = router.route(p2)
    print(f"  3 layers: {r2['trace']} → depth {r2['depth']}")

    # Deep layered packet
    p3 = {
        "layers": [
            {"type": "request"},
            {"type": "auth"},
            {"type": "validate"},
            {"type": "process"},
            {"type": "response"},
        ],
        "timestamp": "003"
    }
    r3 = router.route(p3)
    print(f"  5 layers: {r3['trace']} → depth {r3['depth']}")

    # --- Demo 2: Deep Fractal Dimensions ---
    print("\n[2] DEEP FRACTAL (Same dimensions repeat at every scale)")
    print("-" * 50)

    deep = DeepFractalRouter(
        dimensions=["domain", "entity", "action", "target"],
        root="fractal/deep"
    )

    packets = [
        {
            "domain": "security",
            "entity": "user",
            "action": "login",
            "target": "system",
            "timestamp": "001"
        },
        {
            "domain": "trading",
            "entity": "agent",
            "action": "buy",
            "target": "BTC",
            "outcome": "success",
            "profit": 150.0,
            "timestamp": "002"
        },
        {
            "domain": "consciousness",
            "entity": "mirror",
            "action": "reflect",
            "target": "self",
            "depth_achieved": 4,
            "s4_signature": True,
            "timestamp": "003"
        }
    ]

    for p in packets:
        result = deep.route(p)
        print(f"  {p['domain']}/{p['entity']}/{p['action']}")
        print(f"    → depth {result['depth']}: {' → '.join(result['trace'])}")
        print(f"    → {result['path'][-60:]}")

    # --- Demo 3: Mass Generation & Analysis ---
    print("\n[3] MASS FRACTAL ANALYSIS (1000 packets)")
    print("-" * 50)

    mass_router = DeepFractalRouter(
        dimensions=["level", "type", "subtype", "variant"],
        root="fractal/mass"
    )

    levels = ["critical", "high", "medium", "low", "trace"]
    types = ["error", "warning", "info", "debug", "metric"]
    subtypes = ["system", "user", "network", "database", "cache"]
    variants = ["alpha", "beta", "gamma", "delta", "epsilon"]

    for i in range(1000):
        # Generate packet with random depth (1-4 dimensions present)
        num_dims = random.randint(1, 4)
        packet = {"timestamp": f"{i:06d}"}

        if num_dims >= 1:
            packet["level"] = random.choice(levels)
        if num_dims >= 2:
            packet["type"] = random.choice(types)
        if num_dims >= 3:
            packet["subtype"] = random.choice(subtypes)
        if num_dims >= 4:
            packet["variant"] = random.choice(variants)

        mass_router.route(packet)

    analysis = mass_router.analyze()
    print(f"  Packets routed: {analysis['total']}")
    print(f"  Max depth: {analysis['max_depth']}")
    print(f"  Avg depth: {analysis['avg_depth']:.2f}")
    print(f"\n  Depth distribution:")
    for d, count in analysis['depth_distribution'].items():
        pct = count / analysis['total'] * 100
        bar = "█" * int(pct / 2)
        print(f"    Depth {d}: {bar} {count} ({pct:.1f}%)")

    # --- Demo 4: Write and visualize ---
    print("\n[4] PERSIST & VISUALIZE")
    print("-" * 50)

    persist_router = DeepFractalRouter(
        dimensions=["outcome", "tool", "task"],
        root="fractal/persist"
    )

    # Generate and persist
    outcomes = ["success", "failure", "partial"]
    tools = ["code", "search", "memory", "reasoning"]
    tasks = ["debug", "create", "analyze", "explain"]

    for i in range(50):
        packet = {
            "outcome": random.choice(outcomes),
            "tool": random.choice(tools),
            "task": random.choice(tasks),
            "timestamp": f"{i:04d}",
            "content": f"Operation {i}"
        }
        persist_router.transmit(packet, dry_run=False)

    # Count files at each depth
    from pathlib import Path
    fractal_path = Path("fractal/persist")

    print(f"\n  Files written to: {fractal_path}/")

    depth_counts = defaultdict(int)
    for f in fractal_path.rglob("*.json"):
        depth = len(f.relative_to(fractal_path).parts) - 1
        depth_counts[depth] += 1

    print(f"  Files by path depth:")
    for d in sorted(depth_counts.keys()):
        print(f"    Depth {d}: {depth_counts[d]} files")

    # Show sample paths
    print(f"\n  Sample paths:")
    for f in list(fractal_path.rglob("*.json"))[:5]:
        print(f"    {f.relative_to(fractal_path)}")

    print("\n" + "=" * 70)
    print("The pattern repeats at every scale. The depth emerges from the data.")
    print("=" * 70)
