"""
Topology Prototype Generator

This script generates a "Hero" directory structure for the Manifesto.
It simulates a "Senior Engineer Agent" working for 48 hours.

The resulting folder structure demonstrates:
1. Self-Classification (Outcomes)
2. Semantic Depth (Tool -> Error Type -> Specific Logic)
3. The "Shape" of Intelligence (Visible patterns in the folder sizes)
"""

import os
import json
import time
import random
import shutil
from pathlib import Path
from coherence import Coherence
from visualizer import Visualizer

# Define the "Brain" Schema for a Coder Agent
SCHEMA = {
    "outcome": {
        "success": {
            "tool": {
                "code_interpreter": {
                    "task": {
                        "refactor": "memories/success/code/refactor/{timestamp}_{id}.json",
                        "debug": "memories/success/code/debug/{timestamp}_{id}.json",
                        "optimize": "memories/success/code/optimize/{timestamp}_{id}.json"
                    }
                },
                "terminal": "memories/success/terminal/{task}/{timestamp}_{id}.json"
            }
        },
        "failure": {
            "tool": {
                "code_interpreter": {
                    "error_type": {
                        "syntax": "memories/failure/code/syntax/{timestamp}_{id}.json",
                        "logic": "memories/failure/code/logic/{timestamp}_{id}.json",
                        "timeout": "memories/failure/code/timeout/{timestamp}_{id}.json"
                    }
                },
                "git": "memories/failure/git/{error_type}/{timestamp}_{id}.json"
            }
        },
        "learning": {
            "category": {
                "preference": "memories/learning/preference/{timestamp}_{id}.json",
                "pattern": "memories/learning/pattern/{timestamp}_{id}.json",
                "anti_pattern": "memories/learning/anti_pattern/{timestamp}_{id}.json"
            }
        }
    }
}

def write_memory(path: str, packet: dict) -> None:
    """Write a memory file with metadata."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump({
            **packet,
            "created_at": time.time(),
            "memory_type": "experience"
        }, f, indent=2)

def generate_hero_topology(root="hero_brain"):
    """Generate the Hero Shot topology."""
    if os.path.exists(root):
        shutil.rmtree(root)

    print(f"[*] Seeding consciousness into {root}/...")
    engine = Coherence(SCHEMA, root=root)

    timestamp = int(time.time())

    # 1. Simulate the "Struggle" (Failures)
    # The agent struggles with Logic errors, but rarely makes Syntax errors.
    print("    - Injecting failure patterns...")

    for i in range(42):  # 42 Logic errors (Hard problem)
        packet = {
            "outcome": "failure",
            "tool": "code_interpreter",
            "error_type": "logic",
            "timestamp": timestamp + i,
            "id": f"err_{random.randint(1000,9999)}"
        }
        path = engine.transmit(packet, dry_run=False)
        write_memory(path, packet)

    for i in range(5):  # Only 5 Syntax errors (Agent is good at syntax)
        packet = {
            "outcome": "failure",
            "tool": "code_interpreter",
            "error_type": "syntax",
            "timestamp": timestamp + 100 + i,
            "id": f"err_{random.randint(1000,9999)}"
        }
        path = engine.transmit(packet, dry_run=False)
        write_memory(path, packet)

    for i in range(8):  # Some timeout errors
        packet = {
            "outcome": "failure",
            "tool": "code_interpreter",
            "error_type": "timeout",
            "timestamp": timestamp + 200 + i,
            "id": f"err_{random.randint(1000,9999)}"
        }
        path = engine.transmit(packet, dry_run=False)
        write_memory(path, packet)

    # 2. Simulate the "Wins" (Successes)
    print("    - Injecting success streaks...")

    for i in range(85):  # Great at refactoring
        packet = {
            "outcome": "success",
            "tool": "code_interpreter",
            "task": "refactor",
            "timestamp": timestamp + 300 + i,
            "id": f"win_{random.randint(1000,9999)}"
        }
        path = engine.transmit(packet, dry_run=False)
        write_memory(path, packet)

    for i in range(35):  # Good at debugging
        packet = {
            "outcome": "success",
            "tool": "code_interpreter",
            "task": "debug",
            "timestamp": timestamp + 400 + i,
            "id": f"win_{random.randint(1000,9999)}"
        }
        path = engine.transmit(packet, dry_run=False)
        write_memory(path, packet)

    for i in range(15):  # Some optimization wins
        packet = {
            "outcome": "success",
            "tool": "code_interpreter",
            "task": "optimize",
            "timestamp": timestamp + 500 + i,
            "id": f"win_{random.randint(1000,9999)}"
        }
        path = engine.transmit(packet, dry_run=False)
        write_memory(path, packet)

    # 3. Simulate "Wisdom" (Learnings)
    print("    - Crystallizing insights...")

    for i in range(12):  # Anti-patterns discovered
        packet = {
            "outcome": "learning",
            "category": "anti_pattern",
            "timestamp": timestamp + 600 + i,
            "id": f"insight_{random.randint(1000,9999)}"
        }
        path = engine.transmit(packet, dry_run=False)
        write_memory(path, packet)

    for i in range(18):  # Patterns learned
        packet = {
            "outcome": "learning",
            "category": "pattern",
            "timestamp": timestamp + 700 + i,
            "id": f"insight_{random.randint(1000,9999)}"
        }
        path = engine.transmit(packet, dry_run=False)
        write_memory(path, packet)

    for i in range(6):  # Preferences noted
        packet = {
            "outcome": "learning",
            "category": "preference",
            "timestamp": timestamp + 800 + i,
            "id": f"insight_{random.randint(1000,9999)}"
        }
        path = engine.transmit(packet, dry_run=False)
        write_memory(path, packet)

    print("[*] Topology generation complete.")
    print(f"    Total memories: 226")

    # 4. The Hero Shot (Visualization)
    print("\n" + "=" * 70)
    print("                         THE HERO SHOT")
    print("              An Agent's Brain Rendered as Topology")
    print("=" * 70)

    viz = Visualizer(root=root)
    viz.map(min_percent=1.0)

if __name__ == "__main__":
    generate_hero_topology()
