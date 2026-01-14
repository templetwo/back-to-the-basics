"""
Debugging Workflow with BTB Memory

Demonstrates how BTB memory guides systematic debugging
by learning from past successes and failures.
"""

from memory import MemoryEngine


def simulate_debugging_session():
    """
    Hypothetical example of how BTB memory would guide debugging.

    ⚠️ TRANSPARENCY: This is an ILLUSTRATIVE EXAMPLE, not a measured experiment.
    """
    memory = MemoryEngine(root="debugging_brain")

    print("🔍 BTB-Guided Debugging Workflow\n")
    print("=" * 70)

    # Step 1: Store past debugging experiences
    print("\n📚 STEP 1: Building Debug Memory (Past Sessions)")
    print("-" * 70)

    past_experiences = [
        {
            "content": "Fixed race condition in payment processor by adding mutex lock",
            "outcome": "success",
            "tool": "code_interpreter",
            "task_type": "debug",
            "summary": "race_condition_fix",
            "technique": "mutex_locking",
            "time_to_fix": "45min"
        },
        {
            "content": "Resolved database deadlock by reordering transaction locks",
            "outcome": "success",
            "tool": "code_interpreter",
            "task_type": "debug",
            "summary": "db_deadlock_fix",
            "technique": "lock_ordering",
            "time_to_fix": "30min"
        },
        {
            "content": "Fixed async/await timing issue using asyncio.gather()",
            "outcome": "success",
            "tool": "code_interpreter",
            "task_type": "debug",
            "summary": "async_timing_fix",
            "technique": "async_coordination",
            "time_to_fix": "20min"
        },
    ]

    for exp in past_experiences:
        path = memory.remember(**exp)
        print(f"  ✓ {exp['summary']}: {exp['technique']}")

    # Step 2: New bug encountered
    print("\n🐛 STEP 2: New Bug Encountered")
    print("-" * 70)
    print("ERROR: Intermittent payment failures during high load")
    print("SYMPTOMS:")
    print("  • Succeeds under normal load")
    print("  • Fails ~5% of the time under concurrent requests")
    print("  • No obvious error message")
    print("  • Database shows no issues")

    # Step 3: Query relevant memories
    print("\n🔍 STEP 3: Query Relevant Past Experiences")
    print("-" * 70)

    debug_successes = memory.recall(
        pattern="debugging_brain/outcome=success/tool=code_interpreter/task_type=debug/**/*.json"
    )

    print(f"Found {len(debug_successes)} past debugging wins:\n")
    for mem in debug_successes:
        relevance = "HIGH" if "race" in mem['content'].lower() else "MEDIUM"
        print(f"  [{relevance}] {mem['summary']}")
        print(f"         Technique: {mem.get('metadata', {}).get('technique', 'N/A')}")
        print(f"         Time: {mem.get('metadata', {}).get('time_to_fix', 'N/A')}")
        print()

    # Step 4: Apply systematic approach
    print("\n⚡ STEP 4: Apply Highest-Ranked Technique")
    print("-" * 70)
    print("Selected: race_condition_fix (mutex locking)")
    print("Reasoning: Symptoms match - intermittent, load-dependent, concurrent")
    print("\nApplying technique:")
    print("  1. Add transaction-level mutex lock to payment processor")
    print("  2. Test under concurrent load")
    print("  3. ✓ BUG FIXED - 0% failure rate after fix")

    # Step 5: Store the new success
    print("\n💾 STEP 5: Store New Success")
    print("-" * 70)

    new_success = memory.remember(
        content="Fixed payment processor race condition under high load using mutex lock",
        outcome="success",
        tool="code_interpreter",
        task_type="debug",
        summary="payment_race_fix",
        technique="mutex_locking",
        time_to_fix="15min",  # Faster because of memory guidance
        guided_by="race_condition_fix"
    )
    print(f"✓ Stored at: {new_success}")

    # Step 6: Reflection
    print("\n🧠 STEP 6: Pattern Recognition")
    print("-" * 70)

    analysis = memory.reflect()
    print(f"Total debugging wins: {analysis['by_outcome'].get('success', 0)}")
    print(f"\nMost successful technique: mutex_locking (used 2x)")
    print(f"Average time to fix: 27 minutes")
    print(f"\n💡 Insight: Race conditions are common in high-load scenarios.")
    print(f"   → Always check for mutex protection first.")

    print("\n" + "=" * 70)
    print("✓ Debugging workflow complete!")
    print("\n⚠️  TRANSPARENCY NOTE:")
    print("This example demonstrates HOW BTB memory would guide debugging.")
    print("Times and outcomes are ILLUSTRATIVE, not measured experiments.")


if __name__ == "__main__":
    simulate_debugging_session()
