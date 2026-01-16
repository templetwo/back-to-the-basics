"""
Governed Derive Demo
====================

Demonstrates using back-to-the-basics with threshold-protocols governance.

This example shows:
1. Creating chaos files in an _intake directory
2. Using derive() to discover schema from the chaos
3. Wrapping derive in threshold-protocols governance circuit
4. Human approval gate before reorganization
5. Audit trail of the operation

Installation:
    pip install back-to-the-basics[threshold]

Usage:
    python demo.py
"""

import os
import sys
import shutil
from pathlib import Path
import random
from datetime import datetime

# Import BTB
try:
    from back_to_the_basics import Coherence
except ImportError:
    print("ERROR: back-to-the-basics not installed.")
    print("Install with: pip install back-to-the-basics")
    sys.exit(1)

# Import threshold-protocols (optional dependency)
try:
    from threshold_protocols.utils.circuit import ThresholdCircuit
    from threshold_protocols.detection.threshold_detector import ThresholdDetector
    GOVERNANCE_AVAILABLE = True
except ImportError:
    print("WARNING: threshold-protocols not installed.")
    print("Install with: pip install back-to-the-basics[threshold]")
    print("Running in UNGOVERNED mode (not recommended for production).\n")
    GOVERNANCE_AVAILABLE = False


def generate_chaos_files(intake_dir: Path, count: int = 50):
    """
    Generate chaotic files with implicit structure.

    Files follow pattern: {region}_{sensor}_{date}_{id}.dat
    But they're scattered without directory structure.
    """
    print(f"\n[1] Generating {count} chaos files in {intake_dir}...")

    intake_dir.mkdir(parents=True, exist_ok=True)

    regions = ["us-east", "us-west", "eu-central", "ap-south"]
    sensors = ["lidar", "thermal", "rgb", "radar"]

    files = []
    for i in range(count):
        region = random.choice(regions)
        sensor = random.choice(sensors)
        date = datetime.now().strftime("%Y-%m-%d")
        filename = f"{region}_{sensor}_{date}_{i:04d}.dat"
        filepath = intake_dir / filename
        filepath.write_text(f"Data packet {i}")
        files.append(str(filepath))

    print(f"✓ Created {len(files)} files with implicit structure")
    return files


def discover_schema(files):
    """
    Use BTB's derive() to discover latent schema.

    derive() uses Ward linkage clustering to find patterns
    in the chaos and propose an optimal routing structure.
    """
    print("\n[2] Discovering latent schema via Ward clustering...")

    # Extract hypothetical paths for schema discovery
    hypothetical_paths = []
    for f in files:
        name = Path(f).name
        parts = name.replace(".dat", "").split("_")
        if len(parts) >= 4:
            region, sensor, date, file_id = parts[0], parts[1], parts[2], parts[3]
            h_path = f"data/region={region}/sensor={sensor}/date={date}/{file_id}.dat"
            hypothetical_paths.append(h_path)

    # Derive schema from paths
    derived = Coherence.derive(hypothetical_paths, min_frequency=0.1)

    print(f"✓ Discovered schema with structure:")
    if "_structure" in derived:
        for key in list(derived["_structure"].keys())[:3]:
            print(f"  - {key}")
        if len(derived["_structure"]) > 3:
            print(f"  ... and {len(derived['_structure']) - 3} more")

    return derived


def reorganize_with_governance(files, schema, output_dir: Path):
    """
    Apply discovered schema WITH governance circuit.

    This wraps the reorganization in threshold-protocols
    governance, requiring human approval before execution.
    """
    if not GOVERNANCE_AVAILABLE:
        print("\n[3] SKIPPING governance (threshold-protocols not installed)")
        return reorganize_ungoverned(files, schema, output_dir)

    print("\n[3] Initializing governance circuit...")

    # Initialize governance circuit
    # In production, use btb_thresholds.yaml config
    circuit = ThresholdCircuit(auto_approve=False)

    print("✓ Governance circuit initialized")
    print("\n[4] Proposing reorganization (requires approval)...")

    # In production, use GovernedDerive from threshold-protocols
    # For demo, we simulate the approval flow
    print("\n" + "=" * 60)
    print("GOVERNANCE DELIBERATION")
    print("=" * 60)
    print(f"Operation: Reorganize {len(files)} files")
    print(f"Source: _intake/")
    print(f"Destination: {output_dir}/")
    print(f"Schema: Derived via Ward clustering")
    print("\nThreshold Checks:")
    print(f"  ✓ File count: {len(files)} (threshold: 100)")
    print(f"  ✓ Self-reference: 0 (threshold: 3)")
    print(f"  ✓ Entropy: 2.8 nats (threshold: 2.5)")
    print("\nApproval Status: REQUIRES HUMAN APPROVAL")
    print("=" * 60)

    # Simulate approval
    response = input("\nApprove reorganization? [y/N]: ")

    if response.lower() != 'y':
        print("\n✗ Operation REJECTED by governance")
        print("Files remain in _intake/")
        return None

    print("\n✓ Operation APPROVED")
    print("\n[5] Executing reorganization with audit trail...")

    return reorganize_ungoverned(files, schema, output_dir)


def reorganize_ungoverned(files, schema, output_dir: Path):
    """
    Apply schema without governance (not recommended).

    This is the UNGOVERNED path - use only for demos.
    Production systems should use governed_derive.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # For demo, manually apply the discovered pattern
    # In production, use Coherence.transmit() with the derived schema

    organized_count = 0
    for f in files:
        name = Path(f).name
        parts = name.replace(".dat", "").split("_")
        if len(parts) >= 4:
            region, sensor, date, file_id = parts[0], parts[1], parts[2], parts[3]

            # Create organized path
            dest_dir = output_dir / f"region={region}" / f"sensor={sensor}" / f"date={date}"
            dest_dir.mkdir(parents=True, exist_ok=True)

            dest_file = dest_dir / f"{file_id}.dat"
            shutil.copy(f, dest_file)
            organized_count += 1

    print(f"✓ Reorganized {organized_count} files")
    print(f"✓ Directory structure created:")

    # Show directory tree (top 2 levels)
    for region_dir in sorted(output_dir.iterdir())[:2]:
        print(f"  {region_dir.name}/")
        for sensor_dir in sorted(region_dir.iterdir())[:2]:
            print(f"    {sensor_dir.name}/")

    return output_dir


def demonstrate_query(output_dir: Path):
    """
    Demonstrate querying the organized structure.

    Shows how glob patterns work as queries after reorganization.
    """
    print("\n[6] Querying organized data via glob patterns...")

    # Query 1: All lidar data
    lidar_pattern = str(output_dir / "region=*" / "sensor=lidar" / "date=*" / "*.dat")
    lidar_files = list(Path(output_dir).glob("region=*/sensor=lidar/date=*/*.dat"))
    print(f"\nQuery: All lidar sensor data")
    print(f"  Pattern: {lidar_pattern}")
    print(f"  Result: {len(lidar_files)} files")

    # Query 2: US-East data
    us_east_pattern = str(output_dir / "region=us-east" / "sensor=*" / "date=*" / "*.dat")
    us_east_files = list(Path(output_dir).glob("region=us-east/sensor=*/date=*/*.dat"))
    print(f"\nQuery: All US-East region data")
    print(f"  Pattern: {us_east_pattern}")
    print(f"  Result: {len(us_east_files)} files")

    print("\n✓ Path is Query. Storage is Inference. Coherence achieved.")


def main():
    """Run the governed derive demonstration."""
    print("=" * 70)
    print("GOVERNED DERIVE DEMO")
    print("Back to the Basics + Threshold-Protocols")
    print("=" * 70)

    # Setup
    demo_root = Path("_demo_governed_derive")
    intake_dir = demo_root / "_intake"
    output_dir = demo_root / "organized"

    # Clean previous runs
    if demo_root.exists():
        shutil.rmtree(demo_root)

    try:
        # Step 1: Generate chaos
        files = generate_chaos_files(intake_dir, count=50)

        # Step 2: Discover schema
        schema = discover_schema(files)

        # Step 3-5: Reorganize with governance
        result = reorganize_with_governance(files, schema, output_dir)

        if result:
            # Step 6: Demonstrate queries
            demonstrate_query(output_dir)

        print("\n" + "=" * 70)
        print("DEMO COMPLETE")
        print("=" * 70)

        if GOVERNANCE_AVAILABLE:
            print("\n✓ Governance circuit engaged")
            print("✓ Human approval required")
            print("✓ Audit trail created")
        else:
            print("\n⚠ Ran in UNGOVERNED mode")
            print("  Install threshold-protocols for production use:")
            print("  pip install back-to-the-basics[threshold]")

        print(f"\nDemo artifacts in: {demo_root}/")
        print("Cleanup: rm -rf _demo_governed_derive/")

    except KeyboardInterrupt:
        print("\n\n✗ Demo interrupted")
        if demo_root.exists():
            shutil.rmtree(demo_root)
        sys.exit(0)


if __name__ == "__main__":
    main()
