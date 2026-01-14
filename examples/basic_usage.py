"""
Basic BTB Memory Usage Example

Demonstrates fundamental operations:
- Storing memories
- Recalling memories
- Reflecting on patterns
"""

from memory import MemoryEngine


def main():
    # Initialize memory engine
    memory = MemoryEngine(root="example_brain")

    print("🧠 BTB Memory - Basic Usage Example\n")
    print("=" * 50)

    # Store some memories
    print("\n1. STORING MEMORIES")
    print("-" * 50)

    path1 = memory.remember(
        content="Successfully implemented JWT authentication with refresh tokens",
        outcome="success",
        tool="code_interpreter",
        task_type="write",
        summary="jwt_auth_impl"
    )
    print(f"✓ Stored success: {path1}")

    path2 = memory.remember(
        content="Fixed race condition in payment processor by adding mutex lock",
        outcome="success",
        tool="code_interpreter",
        task_type="debug",
        summary="race_condition_fix"
    )
    print(f"✓ Stored debug success: {path2}")

    path3 = memory.remember(
        content="TypeError when passing None to json.dumps() without default handler",
        outcome="failure",
        tool="code_interpreter",
        error_type="runtime",
        summary="json_none_error"
    )
    print(f"✓ Stored failure: {path3}")

    path4 = memory.remember(
        content="User prefers explicit error messages over generic ones",
        outcome="learning",
        insight_type="preference",
        summary="explicit_errors_pref"
    )
    print(f"✓ Stored learning: {path4}")

    # Recall memories
    print("\n2. RECALLING MEMORIES")
    print("-" * 50)

    # All successes
    successes = memory.recall(pattern="example_brain/outcome=success/**/*.json")
    print(f"\nFound {len(successes)} successes:")
    for mem in successes:
        print(f"  • {mem['summary']}: {mem['content'][:50]}...")

    # All failures
    failures = memory.recall(pattern="example_brain/outcome=failure/**/*.json")
    print(f"\nFound {len(failures)} failures:")
    for mem in failures:
        print(f"  • {mem['summary']}: {mem['content'][:50]}...")

    # Debugging wins specifically
    debug_wins = memory.recall(
        pattern="example_brain/outcome=success/tool=code_interpreter/task_type=debug/**/*.json"
    )
    print(f"\nFound {len(debug_wins)} debugging successes:")
    for mem in debug_wins:
        print(f"  • {mem['summary']}")

    # Reflect on patterns
    print("\n3. REFLECTION ANALYSIS")
    print("-" * 50)

    analysis = memory.reflect()

    print(f"\nTotal memories: {analysis['total_memories']}")
    print("\nBy outcome:")
    for outcome, count in analysis['by_outcome'].items():
        print(f"  {outcome}: {count}")

    print("\nBy tool:")
    for tool, count in analysis['by_tool'].items():
        print(f"  {tool}: {count}")

    if analysis.get('insights'):
        print("\n💡 Auto-generated insights:")
        for insight in analysis['insights']:
            print(f"  • {insight}")

    print("\n" + "=" * 50)
    print("✓ Example complete! Check ./example_brain/ to see the topology.")


if __name__ == "__main__":
    main()
