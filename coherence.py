"""
Coherence Engine: Path as Model

The filesystem is a decision tree runtime.
- Storage IS classification
- The path IS the model
- Routing IS inference

Three modes:
1. transmit() - Data → Path (write-time routing)
2. receive()  - Intent → Glob (read-time tuning)
3. derive()   - Chaos → Schema (discover latent structure)

Extension: Fractal routing for self-similar agent hierarchies.
Models deep delegation trees (e.g., manager → sub-managers → workers).
"""

import os
import re
import random
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import defaultdict
from datetime import datetime

try:
    import sympy as sp
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False


class Coherence:
    """
    The Coherence Engine.

    Treats the filesystem as an active circuit, not a passive warehouse.
    Data flows through logic gates (directories) and finds its own place.
    """

    def __init__(self, schema: Optional[Dict] = None, root: str = "data_lake",
                 max_depth: int = 10, fractal_mode: bool = False, branching: int = 2):
        """
        Initialize with a routing schema or generate fractal schema.

        Args:
            schema: Routing schema (nested dict). If None, generates fractal schema.
            root: Root directory for data
            max_depth: Maximum recursion depth for fractal schemas
            fractal_mode: Enable fractal (self-similar) routing
            branching: Branching factor for fractal schemas (default 2 = binary)

        The schema IS the model. It's a nested dict that functions
        as a decision tree classifier.

        Example traditional schema:
        {
            "sensor": {
                "lidar": {
                    "altitude": {
                        ">100": "{timestamp}_high.parquet",
                        "<=100": "{timestamp}_low.parquet"
                    }
                },
                "thermal": "{timestamp}_thermal.tiff"
            }
        }

        Example fractal schema (auto-generated):
        Models agent hierarchies with self-similar delegation trees.
        Each level mirrors the structure (manager delegates to sub-managers, etc.)
        """
        self.root = root
        self.max_depth = max_depth
        self.fractal_mode = fractal_mode
        self.branching = branching

        if schema is None and fractal_mode:
            self.schema = self.generate_fractal_schema(depth=max_depth, branching=branching)
        elif schema is None:
            raise ValueError("Must provide schema or enable fractal_mode")
        else:
            self.schema = schema

    def transmit(self, packet: Dict[str, Any], dry_run: bool = True) -> str:
        """
        Route a packet through the schema to find its destination.

        This IS inference. The packet (electron) flows through the
        logic tree (topology) and lands where it belongs.

        Args:
            packet: Dict of attributes (the data's metadata)
            dry_run: If True, just return path. If False, create directories.

        Returns:
            The computed path where this data belongs.
        """
        path_segments = [self.root]
        current_node = self.schema

        while isinstance(current_node, dict):
            matched = False

            for key, branches in current_node.items():
                value = packet.get(key)

                if value is None:
                    # Missing metadata - route to intake
                    return os.path.join(self.root, "_intake", "missing_metadata",
                                       f"{packet.get('id', 'unknown')}_{datetime.now().isoformat()}")

                # Try to match this value against branches
                selected_branch, next_node = self._match_branch(value, branches)

                if selected_branch is not None:
                    # Sanitize the segment for filesystem
                    segment = f"{key}={self._sanitize(selected_branch)}"
                    path_segments.append(segment)
                    current_node = next_node
                    matched = True
                    break

            if not matched:
                # No matching logic - route to intake
                return os.path.join(self.root, "_intake", "no_match",
                                   f"{packet.get('id', 'unknown')}_{datetime.now().isoformat()}")

        # current_node is now the leaf (filename template)
        if isinstance(current_node, str):
            try:
                # Handle predicate paths with defaults like "{error_type=unknown}"
                template = self._expand_template_with_defaults(current_node, packet)
                filename = template.format(**packet)
            except KeyError as e:
                filename = f"missing_{e}_{datetime.now().isoformat()}"
        else:
            filename = f"{packet.get('id', 'data')}_{datetime.now().isoformat()}"

        # Handle confidence path suffix if present
        if 'confidence_path' in packet and packet['confidence_path']:
            path_segments.append(packet['confidence_path'].lstrip('/'))

        full_path = os.path.join(*path_segments, filename)

        if not dry_run:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

        return full_path

    def _expand_template_with_defaults(self, template: str, packet: Dict) -> str:
        """
        Expand template with predicate defaults.

        Handles patterns like "{error_type=unknown}" by providing defaults
        for missing keys in the packet.

        Example:
            template: "failure/{error_type=unknown}/{step}.json"
            packet: {"step": 5}  # no error_type
            result: "failure/unknown/5.json"
        """
        # Find all {key=default} patterns
        pattern = r'\{(\w+)=([^}]+)\}'
        matches = re.findall(pattern, template)

        for key, default in matches:
            if key not in packet:
                packet[key] = default
            # Replace {key=default} with {key} for standard formatting
            template = template.replace(f"{{{key}={default}}}", f"{{{key}}}")

        return template

    def _match_branch(self, value: Any, branches: Dict) -> tuple:
        """
        Match a value against possible branches.

        Supports:
        - Exact match (categorical): "lidar", "thermal"
        - Numeric predicates: ">100", "<=50", "10-100"
        - Regex patterns: "r/pattern/"
        - Pipe-delimited alternatives: "search|web_search|info_gather"
        - Predicate with default: "{error_type=unknown}"
        """
        # First try exact match
        if value in branches:
            return (str(value), branches[value])

        # Try predicate matching for numeric values
        if isinstance(value, (int, float)):
            for predicate, next_node in branches.items():
                if self._eval_predicate(value, predicate):
                    return (predicate, next_node)

        # Try regex matching for strings
        if isinstance(value, str):
            for pattern, next_node in branches.items():
                # Regex pattern: "r/pattern/"
                if pattern.startswith("r/") and pattern.endswith("/"):
                    regex = pattern[2:-1]
                    if re.match(regex, value):
                        return (pattern, next_node)

                # Pipe-delimited alternatives: "search|web_search|info_gather"
                if "|" in pattern:
                    alternatives = [alt.strip() for alt in pattern.split("|")]
                    if value in alternatives or any(alt in value for alt in alternatives):
                        # Return the matched alternative as the segment
                        matched_alt = next((alt for alt in alternatives if alt in value), alternatives[0])
                        return (matched_alt, next_node)

                # Predicate with default: "{error_type=unknown}"
                if pattern.startswith("{") and pattern.endswith("}") and "=" in pattern:
                    # This is handled in the leaf template, not branching
                    continue

        return (None, None)

    def _eval_predicate(self, value: float, predicate: str) -> bool:
        """
        Safely evaluate numeric predicates.

        Supports: >N, <N, >=N, <=N, N-M (range)
        """
        predicate = predicate.strip()

        # Range: "100-500"
        if re.match(r'^[\d.]+\s*-\s*[\d.]+$', predicate):
            low, high = map(float, predicate.split('-'))
            return low <= value <= high

        # Comparison operators
        match = re.match(r'^([><=!]+)\s*([\d.]+)$', predicate)
        if match:
            op, threshold = match.groups()
            threshold = float(threshold)
            ops = {
                '>': value > threshold,
                '<': value < threshold,
                '>=': value >= threshold,
                '<=': value <= threshold,
                '==': value == threshold,
                '!=': value != threshold,
            }
            return ops.get(op, False)

        return False

    def _sanitize(self, s: str) -> str:
        """Sanitize string for filesystem path segment."""
        # Convert comparison operators to readable names
        s = str(s)
        s = s.replace('>=', 'gte_')
        s = s.replace('<=', 'lte_')
        s = s.replace('>', 'gt_')
        s = s.replace('<', 'lt_')
        s = s.replace('==', 'eq_')
        s = s.replace('!=', 'ne_')
        return re.sub(r'[^\w\-.]', '', s)

    def receive(self, **intent) -> str:
        """
        Generate a glob pattern that resonates with the given intent.

        This is the tuner. You describe what you want, it returns
        the frequency (glob pattern) to tune into.

        Args:
            **intent: Key-value pairs describing what you want

        Returns:
            A glob pattern that matches your intent
        """
        segments = [self.root]
        current_node = self.schema
        keys_used = set()

        while isinstance(current_node, dict):
            matched = False

            for key, branches in current_node.items():
                keys_used.add(key)

                if key in intent:
                    # User specified this dimension - use their value
                    value = intent[key]
                    selected_branch, next_node = self._match_branch(value, branches)

                    if selected_branch is not None:
                        segments.append(f"{key}={self._sanitize(selected_branch)}")
                        current_node = next_node
                        matched = True
                        break
                    else:
                        # Value doesn't match schema - wildcard this level
                        segments.append(f"{key}=*")
                        # Pick any branch to continue
                        current_node = next(iter(branches.values()))
                        matched = True
                        break
                else:
                    # User didn't specify - wildcard
                    segments.append(f"{key}=*")
                    # Pick any branch to continue exploring schema
                    current_node = next(iter(branches.values()))
                    matched = True
                    break

            if not matched:
                break

        # Add wildcard for filename
        segments.append("*")

        return os.path.join(*segments)

    # =========================================================================
    # FRACTAL ROUTING EXTENSION
    # =========================================================================

    @classmethod
    def compute_tree_stats(cls, branching: int = 2, depth: int = 10) -> Dict:
        """
        Use sympy to model self-similar decision tree statistics.

        For a tree with branching factor b and depth d:
        - Total nodes: (b^(d+1) - 1) / (b - 1)
        - Leaf nodes (workers): b^d

        Args:
            branching: Branching factor (default 2 = binary tree)
            depth: Tree depth (number of levels)

        Returns:
            Dict with 'total_nodes' and 'leaves' counts

        Example:
            depth=10, branching=2 → 4095 total nodes, 1024 leaves
        """
        if not SYMPY_AVAILABLE:
            # Fallback to manual calculation
            total = (branching ** (depth + 1) - 1) // (branching - 1)
            leaves = branching ** depth
            return {'total_nodes': total, 'leaves': leaves}

        b, d = sp.symbols('b d')
        total_nodes = (b**(d+1) - 1) / (b - 1)
        leaves = b**d
        stats = {
            'total_nodes': int(total_nodes.subs({b: branching, d: depth})),
            'leaves': int(leaves.subs({b: branching, d: depth}))
        }
        return stats

    def generate_fractal_schema(self, depth: int, branching: int = 2) -> Dict:
        """
        Generate self-similar schema for agent hierarchies.

        Creates fractal (self-repeating) structure where each level
        mirrors the overall pattern. Models delegation trees:
        - Top manager delegates to sub-managers
        - Sub-managers delegate to workers
        - Pattern repeats at each level

        Args:
            depth: How many levels deep (0 = leaf file)
            branching: Number of branches at each level

        Returns:
            Nested dict schema with self-similar structure

        Example (depth=2, branching=2):
        {
            "delegation": {
                "branch_0": {
                    "delegation": {
                        "branch_0": "{agent_id}.json",
                        "branch_1": "{agent_id}.json"
                    }
                },
                "branch_1": {
                    "delegation": {
                        "branch_0": "{agent_id}.json",
                        "branch_1": "{agent_id}.json"
                    }
                }
            }
        }
        """
        def build(current_depth: int):
            if current_depth == 0:
                return "{agent_id}.json"
            return {
                "delegation": {
                    f"branch_{i}": build(current_depth - 1) for i in range(branching)
                }
            }
        return build(depth)

    def simulate_routing(self, packet: Dict[str, Any], depth: int = 10) -> List[str]:
        """
        Simulate routing through deep agent hierarchy.

        Traces path through fractal delegation tree, simulating how
        an agent task would flow from top manager down to worker leaf.

        Args:
            packet: Data packet (must contain 'agent_id' for determinism)
            depth: How many levels to traverse

        Returns:
            List of path segments showing delegation route

        Example output:
            ['agent_hierarchy', 'delegation=branch_1', 'delegation=branch_0',
             'delegation=branch_1', ..., 'agent_42.json']
        """
        path = [self.root]
        current_node = self.schema
        current_depth = 0

        while isinstance(current_node, dict) and current_depth < depth:
            key = next(iter(current_node))  # e.g., 'delegation'
            branches = current_node[key]

            # Deterministic branch selection based on agent_id hash
            choice_hash = hash(str(packet.get('agent_id', random.random()))) % len(branches)
            selected_branch = list(branches.keys())[choice_hash]

            path.append(f"{key}={selected_branch}")
            current_node = branches[selected_branch]
            current_depth += 1

        # Add filename at leaf
        if isinstance(current_node, str):
            path.append(current_node.format(**packet))

        return path

    def visualize_tree(self, node=None, prefix="", last=True, max_vis_depth=3, current_depth=0):
        """
        ASCII visualization of schema tree.

        Limited to max_vis_depth for readability (full fractal would be huge).

        Args:
            node: Current node (defaults to root schema)
            prefix: Current line prefix (for indentation)
            last: Is this the last sibling?
            max_vis_depth: Maximum depth to visualize
            current_depth: Current recursion depth

        Example output:
            delegation
            ├─ branch_0
            │   └─ delegation
            │       ├─ branch_0
            │       │   └─ ... (deeper levels truncated)
            │       └─ branch_1
            │           └─ ... (deeper levels truncated)
            └─ branch_1
                └─ delegation
                    ├─ branch_0
                    │   └─ ... (deeper levels truncated)
                    └─ branch_1
                        └─ ... (deeper levels truncated)
        """
        if current_depth > max_vis_depth:
            print(prefix + ("└─ " if last else "├─ ") + "... (deeper levels truncated)")
            return

        if node is None:
            node = self.schema

        if isinstance(node, str):
            print(prefix + ("└─ " if last else "├─ ") + node)
            return

        items = list(node.items())
        for i, (key, subnode) in enumerate(items):
            is_last = (i == len(items) - 1)
            print(prefix + ("└─ " if is_last else "├─ ") + key)
            new_prefix = prefix + ("    " if is_last else "│   ")
            self.visualize_tree(subnode, new_prefix, True, max_vis_depth, current_depth + 1)

    # =========================================================================
    # END FRACTAL EXTENSION
    # =========================================================================

    @classmethod
    def derive(cls, paths: List[str], min_frequency: float = 0.1) -> Dict:
        """
        Discover latent structure from a corpus of paths.

        Given chaos (messy paths), find the signal (implicit schema).
        This is entropy -> structure.

        Args:
            paths: List of file paths to analyze
            min_frequency: Minimum frequency for a pattern to be considered signal

        Returns:
            A schema dict inferred from the paths
        """
        # Parse all paths into segments
        parsed = []
        for p in paths:
            parts = Path(p).parts
            parsed.append(parts)

        if not parsed:
            return {}

        # Analyze each level for key=value patterns
        level_patterns = defaultdict(lambda: defaultdict(int))

        for path_parts in parsed:
            for i, part in enumerate(path_parts):
                # Check for key=value pattern
                if '=' in part:
                    key, value = part.split('=', 1)
                    level_patterns[i][(key, value)] += 1
                else:
                    level_patterns[i][(None, part)] += 1

        # Build schema from patterns
        total_paths = len(parsed)
        discovered_keys = {}

        for level, patterns in sorted(level_patterns.items()):
            for (key, value), count in patterns.items():
                freq = count / total_paths
                if freq >= min_frequency:
                    if key:
                        if key not in discovered_keys:
                            discovered_keys[key] = {'level': level, 'values': set()}
                        discovered_keys[key]['values'].add(value)

        # Convert to nested schema
        # (Simplified - a full implementation would build proper tree)
        result = {
            '_derived': True,
            '_path_count': total_paths,
            '_structure': {}
        }

        for key, info in sorted(discovered_keys.items(), key=lambda x: x[1]['level']):
            result['_structure'][key] = {
                'level': info['level'],
                'values': list(info['values']),
                'pattern': f"{key}={{value}}"
            }

        return result


# --- DEMONSTRATION ---

if __name__ == "__main__":

    # THE SCHEMA IS THE MODEL
    # This dict is a decision tree classifier
    schema = {
        "sensor": {
            "lidar": {
                "altitude": {
                    ">100": "{timestamp}_high_altitude.parquet",
                    "<=100": "{timestamp}_ground_proximity.parquet"
                }
            },
            "thermal": {
                "quality": {
                    "raw": "{timestamp}_thermal_raw.tiff",
                    "processed": "{timestamp}_thermal_calibrated.tiff"
                }
            },
            "rgb": "{timestamp}_rgb.jpg"
        }
    }

    engine = Coherence(schema, root="drone_data")

    print("=" * 60)
    print("COHERENCE ENGINE: Path as Model")
    print("=" * 60)

    # --- TRANSMIT: Route packets through the model ---
    print("\n[TRANSMIT] Routing packets to their destinations:\n")

    packets = [
        {"sensor": "lidar", "altitude": 450, "timestamp": "20260112_0900"},
        {"sensor": "lidar", "altitude": 50, "timestamp": "20260112_0901"},
        {"sensor": "thermal", "quality": "raw", "timestamp": "20260112_0902"},
        {"sensor": "thermal", "quality": "processed", "timestamp": "20260112_0903"},
        {"sensor": "rgb", "timestamp": "20260112_0904"},
        {"sensor": "unknown", "timestamp": "20260112_0905"},  # Will go to intake
    ]

    for packet in packets:
        path = engine.transmit(packet)
        print(f"  {packet}")
        print(f"  → {path}\n")

    # --- RECEIVE: Generate glob patterns from intent ---
    print("\n[RECEIVE] Generating glob patterns from intent:\n")

    intents = [
        {"sensor": "lidar"},
        {"sensor": "lidar", "altitude": 500},
        {"sensor": "thermal", "quality": "raw"},
        {},  # All data
    ]

    for intent in intents:
        pattern = engine.receive(**intent)
        print(f"  Intent: {intent or '(all)'}")
        print(f"  → Glob: {pattern}\n")

    # --- DERIVE: Discover structure from chaos ---
    print("\n[DERIVE] Discovering structure from existing paths:\n")

    existing_paths = [
        "data/region=us-east/sensor=lidar/date=2026-01-01/file1.parquet",
        "data/region=us-east/sensor=lidar/date=2026-01-02/file2.parquet",
        "data/region=us-west/sensor=thermal/date=2026-01-01/file3.tiff",
        "data/region=us-west/sensor=thermal/date=2026-01-02/file4.tiff",
        "data/region=eu-central/sensor=lidar/date=2026-01-01/file5.parquet",
    ]

    discovered = Coherence.derive(existing_paths)
    print(f"  Analyzed {discovered['_path_count']} paths")
    print(f"  Discovered structure:")
    for key, info in discovered['_structure'].items():
        print(f"    - {key}: {info['values']}")

    # --- FRACTAL: Agent hierarchy routing ---
    print("\n" + "=" * 60)
    print("[FRACTAL] Agent Hierarchy Routing Extension")
    print("=" * 60)

    # Create fractal engine for agent delegation
    fractal_engine = Coherence(fractal_mode=True, root="agent_hierarchy", max_depth=10, branching=2)

    # Compute tree statistics using sympy
    stats = Coherence.compute_tree_stats(branching=2, depth=10)
    print(f"\n[MODEL] Self-similar tree stats (depth=10, binary branching):")
    print(f"  Total nodes (agents): {stats['total_nodes']}")
    print(f"  Leaf nodes (workers): {stats['leaves']}")

    # Simulate routing through deep hierarchy
    print(f"\n[SIMULATE] Routing agent packet through 10-level hierarchy:")
    packet = {"agent_id": "agent_42"}
    sim_path = fractal_engine.simulate_routing(packet, depth=10)
    print(f"  Agent: {packet['agent_id']}")
    print(f"  Route: {' → '.join(sim_path[:4])} → ... → {sim_path[-1]}")
    print(f"  Total hops: {len(sim_path) - 2} delegation levels")

    # Visualize tree structure (limited depth for readability)
    print(f"\n[VISUALIZE] ASCII tree (depth 3 shown, full tree has {stats['total_nodes']} nodes):")
    fractal_engine.visualize_tree(max_vis_depth=3)

    print("\n" + "=" * 60)
    print("The filesystem is not storage. It is a circuit.")
    print("Extension: Fractal routing for self-similar agent hierarchies.")
    print("=" * 60)
