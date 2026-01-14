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
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List
from collections import defaultdict
from datetime import datetime


class Coherence:
    """
    The Coherence Engine.

    Treats the filesystem as an active circuit, not a passive warehouse.
    Data flows through logic gates (directories) and finds its own place.
    """

    def __init__(self, schema: Dict, root: str = "data_lake"):
        """
        Initialize with a routing schema.

        The schema IS the model. It's a nested dict that functions
        as a decision tree classifier.

        Example schema:
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
        """
        self.schema = schema
        self.root = root

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
                filename = current_node.format(**packet)
            except KeyError as e:
                filename = f"missing_{e}_{datetime.now().isoformat()}"
        else:
            filename = f"{packet.get('id', 'data')}_{datetime.now().isoformat()}"

        full_path = os.path.join(*path_segments, filename)

        if not dry_run:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

        return full_path

    def _match_branch(self, value: Any, branches: Dict) -> tuple:
        """
        Match a value against possible branches.

        Supports:
        - Exact match (categorical): "lidar", "thermal"
        - Numeric predicates: ">100", "<=50", "10-100"
        - Regex patterns: "r/pattern/"
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
                if pattern.startswith("r/") and pattern.endswith("/"):
                    regex = pattern[2:-1]
                    if re.match(regex, value):
                        return (pattern, next_node)

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

    print("\n" + "=" * 60)
    print("The filesystem is not storage. It is a circuit.")
    print("=" * 60)
