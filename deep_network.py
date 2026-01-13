"""
Deep Network: Stress-Testing the Coherence Engine

Generates deep, self-similar topologies to see how
complex decision spaces emerge from simple seed patterns.

The Seed Pattern (OODA Loop):
Observe -> Orient -> Decide -> Act

This pattern repeats at every depth, creating a fractal decision tree.
"""

import os
import json
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

from coherence import Coherence
from visualizer import Visualizer


# =============================================================================
# FRACTAL SCHEMA GENERATORS
# =============================================================================

def build_ooda_schema(max_depth: int) -> Dict:
    """
    Build a fractal schema based on OODA loop.

    At each depth:
    - observe: what is perceived
    - orient: how it's interpreted
    - decide: what action to take
    - act: the execution

    The pattern repeats, creating nested decision trees.
    """
    if max_depth <= 0:
        return "{timestamp}.json"

    observe_states = ["signal", "noise", "pattern", "anomaly"]
    orient_states = ["threat", "opportunity", "neutral", "unknown"]
    decide_states = ["engage", "avoid", "analyze", "wait"]
    act_states = ["execute", "defer", "escalate", "log"]

    def build_level(depth: int) -> Dict:
        if depth >= max_depth:
            return "{timestamp}.json"

        return {
            "observe": {
                state: {
                    "orient": {
                        o_state: {
                            "decide": {
                                d_state: {
                                    "act": {
                                        a_state: build_level(depth + 1)
                                        for a_state in act_states
                                    }
                                }
                                for d_state in decide_states
                            }
                        }
                        for o_state in orient_states
                    }
                }
                for state in observe_states
            }
        }

    return build_level(0)


def build_dimension_schema(dimensions: List[Tuple[str, List[str]]], max_depth: int) -> Dict:
    """
    Build a schema from a list of dimensions.

    Each dimension is a (name, values) tuple.
    The schema cycles through dimensions at each depth.
    """
    def build_level(depth: int) -> Dict:
        if depth >= max_depth:
            return "{timestamp}.json"

        dim_idx = depth % len(dimensions)
        dim_name, dim_values = dimensions[dim_idx]

        return {
            dim_name: {
                val: build_level(depth + 1)
                for val in dim_values
            }
        }

    return build_level(0)


# =============================================================================
# PACKET GENERATORS
# =============================================================================

def generate_ooda_packet(depth: int, bias: Dict[str, float] = None) -> Dict:
    """
    Generate a packet for the OODA schema.

    Args:
        depth: How many OODA cycles to include
        bias: Optional dict to bias certain choices (e.g., {"observe": {"signal": 0.5}})
    """
    observe_states = ["signal", "noise", "pattern", "anomaly"]
    orient_states = ["threat", "opportunity", "neutral", "unknown"]
    decide_states = ["engage", "avoid", "analyze", "wait"]
    act_states = ["execute", "defer", "escalate", "log"]

    def weighted_choice(options: List[str], key: str, subkey: str = None) -> str:
        if bias and key in bias:
            weights = [bias[key].get(opt, 1.0) for opt in options]
        else:
            weights = [1.0] * len(options)
        total = sum(weights)
        weights = [w/total for w in weights]
        return random.choices(options, weights=weights)[0]

    packet = {
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
        "observe": weighted_choice(observe_states, "observe"),
        "orient": weighted_choice(orient_states, "orient"),
        "decide": weighted_choice(decide_states, "decide"),
        "act": weighted_choice(act_states, "act"),
    }

    return packet


def generate_dimension_packet(dimensions: List[Tuple[str, List[str]]], depth: int) -> Dict:
    """Generate a packet for dimension-based schema."""
    packet = {"timestamp": datetime.now().strftime("%Y%m%d_%H%M%S_%f")}

    for i in range(depth):
        dim_idx = i % len(dimensions)
        dim_name, dim_values = dimensions[dim_idx]
        packet[dim_name] = random.choice(dim_values)

    return packet


# =============================================================================
# DEEP NETWORK SIMULATION
# =============================================================================

class DeepNetwork:
    """
    A deep routing network for stress-testing coherence.
    """

    def __init__(self, schema: Dict, root: str = "deep_network"):
        self.schema = schema
        self.root = root
        self.engine = Coherence(schema, root=root)
        self.stats = {
            "total": 0,
            "paths": defaultdict(int),
            "depths": defaultdict(int),
        }

    def stream(self, packet_generator, count: int, dry_run: bool = False) -> Dict:
        """Stream packets through the network."""
        start = time.time()

        for i in range(count):
            packet = packet_generator()
            path = self.engine.transmit(packet, dry_run=True)  # Get path first

            # Actually write the file if not dry_run
            if not dry_run:
                file_path = Path(path)
                os.makedirs(file_path.parent, exist_ok=True)
                with open(file_path, "w") as f:
                    json.dump(packet, f, indent=2, default=str)

            # Track stats
            self.stats["total"] += 1
            depth = path.count("/") - 1
            self.stats["depths"][depth] += 1

            # Track path prefixes (first 3 levels)
            parts = path.split("/")[1:4]  # Skip root
            prefix = "/".join(parts)
            self.stats["paths"][prefix] += 1

        duration = time.time() - start

        return {
            "count": count,
            "duration": duration,
            "rate": count / duration if duration > 0 else 0,
            "depth_distribution": dict(sorted(self.stats["depths"].items())),
            "top_paths": sorted(self.stats["paths"].items(), key=lambda x: -x[1])[:10]
        }

    def visualize(self, max_depth: int = 10, min_percent: float = 1.0):
        """Visualize the network topology."""
        viz = Visualizer(root=self.root)
        viz.map(max_depth=max_depth, min_percent=min_percent)


# =============================================================================
# DEMONSTRATION
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("DEEP NETWORK: Stress-Testing the Coherence Engine")
    print("=" * 70)

    # Clean up
    import shutil
    if os.path.exists("deep_network"):
        shutil.rmtree("deep_network")

    # --- Test 1: OODA Loop Network ---
    print("\n[1] OODA LOOP NETWORK (4 dimensions x 4 values = 256 paths per depth)")
    print("-" * 50)

    # Build schema (just 1 level deep for now - 256 paths)
    ooda_schema = {
        "observe": {
            "signal": {
                "orient": {
                    "threat": "ooda/signal/threat/{timestamp}.json",
                    "opportunity": "ooda/signal/opportunity/{timestamp}.json",
                    "neutral": "ooda/signal/neutral/{timestamp}.json",
                    "unknown": "ooda/signal/unknown/{timestamp}.json",
                }
            },
            "noise": {
                "orient": {
                    "threat": "ooda/noise/threat/{timestamp}.json",
                    "opportunity": "ooda/noise/opportunity/{timestamp}.json",
                    "neutral": "ooda/noise/neutral/{timestamp}.json",
                    "unknown": "ooda/noise/unknown/{timestamp}.json",
                }
            },
            "pattern": {
                "orient": {
                    "threat": "ooda/pattern/threat/{timestamp}.json",
                    "opportunity": "ooda/pattern/opportunity/{timestamp}.json",
                    "neutral": "ooda/pattern/neutral/{timestamp}.json",
                    "unknown": "ooda/pattern/unknown/{timestamp}.json",
                }
            },
            "anomaly": {
                "orient": {
                    "threat": "ooda/anomaly/threat/{timestamp}.json",
                    "opportunity": "ooda/anomaly/opportunity/{timestamp}.json",
                    "neutral": "ooda/anomaly/neutral/{timestamp}.json",
                    "unknown": "ooda/anomaly/unknown/{timestamp}.json",
                }
            }
        }
    }

    network = DeepNetwork(ooda_schema, root="deep_network/ooda")

    def ooda_gen():
        return generate_ooda_packet(depth=1)

    print("  Streaming 1000 packets through OODA network...")
    result = network.stream(ooda_gen, count=1000, dry_run=False)

    print(f"  Rate: {result['rate']:.1f} packets/sec")
    print(f"  Depth distribution: {result['depth_distribution']}")
    print(f"  Top paths:")
    for path, count in result['top_paths'][:5]:
        print(f"    {path}: {count}")

    # --- Test 2: Deep Dimension Network ---
    print("\n[2] 6-DIMENSIONAL NETWORK")
    print("-" * 50)

    dimensions = [
        ("layer", ["input", "hidden", "output"]),
        ("operation", ["forward", "backward", "update"]),
        ("precision", ["fp32", "fp16", "int8"]),
        ("status", ["active", "idle", "error"]),
        ("priority", ["high", "medium", "low"]),
        ("mode", ["train", "eval", "inference"]),
    ]

    dim_schema = build_dimension_schema(dimensions, max_depth=6)
    deep_net = DeepNetwork(dim_schema, root="deep_network/dimensions")

    def dim_gen():
        return generate_dimension_packet(dimensions, depth=6)

    print("  Streaming 2000 packets through 6D network...")
    result2 = deep_net.stream(dim_gen, count=2000, dry_run=False)

    print(f"  Rate: {result2['rate']:.1f} packets/sec")
    print(f"  Depth distribution: {result2['depth_distribution']}")

    # --- Visualize ---
    print("\n[3] TOPOLOGY VISUALIZATION")
    print("-" * 50)

    print("\n  OODA Network:")
    network.visualize(max_depth=5, min_percent=2.0)

    print("\n  6D Network:")
    deep_net.visualize(max_depth=6, min_percent=2.0)

    # --- Count total files ---
    print("\n[4] FILE STATISTICS")
    print("-" * 50)

    total_files = sum(1 for _ in Path("deep_network").rglob("*.json"))
    total_size = sum(f.stat().st_size for f in Path("deep_network").rglob("*.json"))

    print(f"  Total files created: {total_files}")
    print(f"  Total size: {total_size / 1024:.1f} KB")
    print(f"  Average file size: {total_size / total_files:.0f} bytes")

    print("\n" + "=" * 70)
    print("The network is deep. The topology reveals the distribution.")
    print("=" * 70)
