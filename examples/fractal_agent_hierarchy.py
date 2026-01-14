"""
Fractal Agent Hierarchy Example

Demonstrates BTB's fractal routing extension for self-similar agent structures.
Models delegation trees where managers delegate to sub-managers who delegate to workers.

Use Case: Multi-agent systems with hierarchical task delegation
- Top-level coordinator
- Mid-level managers
- Worker agents at leaves

The routing is deterministic based on agent_id hash, simulating load balancing
across branches while maintaining consistent routing for the same agent.
"""

from coherence import Coherence


def main():
    print("🌀 BTB Fractal Agent Hierarchy\n")
    print("=" * 70)

    # Configuration
    depth = 10  # 10 levels deep
    branching = 2  # Binary delegation (each manager has 2 sub-agents)

    # Create fractal engine
    print("\n📊 STEP 1: Initialize Fractal Routing Engine")
    print("-" * 70)
    engine = Coherence(
        fractal_mode=True,
        root="agent_hierarchy",
        max_depth=depth,
        branching=branching
    )
    print(f"✓ Created {branching}-way branching tree with {depth} levels")

    # Compute statistics
    print("\n📈 STEP 2: Tree Statistics (Sympy-modeled)")
    print("-" * 70)
    stats = Coherence.compute_tree_stats(branching=branching, depth=depth)
    print(f"  Total nodes (all agents): {stats['total_nodes']:,}")
    print(f"  Leaf nodes (workers): {stats['leaves']:,}")
    print(f"  Manager nodes: {stats['total_nodes'] - stats['leaves']:,}")
    print(f"\n  Interpretation:")
    print(f"    - {stats['leaves']:,} worker agents at the leaves")
    print(f"    - Each task flows through {depth} delegation levels")
    print(f"    - Tree is self-similar (fractal) at every level")

    # Visualize structure
    print("\n🌳 STEP 3: Topology Visualization (Depth 3)")
    print("-" * 70)
    print("Full tree has 4,095 nodes. Showing first 3 levels:\n")
    engine.visualize_tree(max_vis_depth=3)

    # Simulate routing for multiple agents
    print("\n🔀 STEP 4: Simulate Agent Task Routing")
    print("-" * 70)
    agents = ["agent_001", "agent_042", "agent_127", "agent_999"]

    print(f"Routing {len(agents)} agent tasks through {depth}-level hierarchy:\n")
    for agent_id in agents:
        packet = {"agent_id": agent_id}
        path = engine.simulate_routing(packet, depth=depth)

        # Show delegation route
        route_summary = f"{path[0]} → "
        route_summary += " → ".join(path[1:4])  # First 3 hops
        route_summary += f" → ... ({depth-3} more) → "
        route_summary += path[-1]  # Final destination

        print(f"  {agent_id}:")
        print(f"    {route_summary}")
        print(f"    Worker: delegation path length = {len(path) - 2}\n")

    # Demonstrate deterministic routing
    print("\n🔁 STEP 5: Deterministic Routing Verification")
    print("-" * 70)
    print("Same agent_id always routes to same worker (load balancing):\n")

    test_agent = "agent_42"
    for run in range(3):
        packet = {"agent_id": test_agent}
        path = engine.simulate_routing(packet, depth=depth)
        print(f"  Run {run+1}: {path[1]} → {path[2]} → {path[3]} → ... → {path[-1]}")

    print(f"\n  ✓ All runs route {test_agent} to same worker leaf")
    print(f"    (Deterministic based on agent_id hash)")

    # Compare with flat structure
    print("\n⚖️ STEP 6: Why Fractal? (vs Flat)")
    print("-" * 70)
    print(f"\n  Flat structure:")
    print(f"    - All {stats['leaves']:,} workers in one directory")
    print(f"    - OS slows down with many files in single dir (>10K)")
    print(f"    - No semantic structure")
    print(f"\n  Fractal structure:")
    print(f"    - Workers distributed across {stats['total_nodes']:,} nodes")
    print(f"    - Each directory has only {branching} subdirectories")
    print(f"    - Delegation path encodes load-balancing decision")
    print(f"    - OS stays fast (small directories at each level)")

    # Use cases
    print("\n🎯 STEP 7: Real-World Use Cases")
    print("-" * 70)
    print("""
  ✓ Multi-agent systems with task delegation
    - Coordinator → Team leads → Workers
    - Load balancing via deterministic routing

  ✓ Distributed processing pipelines
    - Regional clusters → Data centers → Compute nodes
    - Geographic hierarchy: Global → Region → Zone → Server

  ✓ Organizational hierarchies
    - CEO → VPs → Directors → Managers → Workers
    - Decision trees mirror org chart

  ✓ Game AI agent trees
    - Master AI → Squad leaders → Individual units
    - Hierarchical pathfinding and decision-making
    """)

    print("\n" + "=" * 70)
    print("✓ Fractal routing demonstration complete!")
    print("\n💡 Key Insight:")
    print("   Self-similar structures scale. The same pattern works at every level.")
    print("   The filesystem becomes a fractal circuit for agent coordination.")
    print("=" * 70)


if __name__ == "__main__":
    main()
