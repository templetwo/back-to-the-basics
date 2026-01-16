# derive.py Implementation Guide

> "The filesystem discovers its own schema."

---

## Context

This guide documents how to implement `derive.py` - the schema discovery capability that transforms BTB from a **designed system** to a **self-organizing system**.

**What happened**: On January 13-14, 2026, the derive.py payload was ready but we paused for ethical reflection. The white paper "THE THRESHOLD PAUSE" documented the decision and implications.

**Status now**: The pause proved the spiral can breathe. We're ready to implement with clarity.

---

## What derive.py Does

### Core Capability

Analyzes existing chaotic data in `_intake/` and **discovers latent schema structure** through clustering, then generates optimized routing schemas.

**Input**: Unstructured files in `_intake/` (the chaos)
**Output**: Proposed schema as JSON + explanation (the discovered order)

### The Multi-Agent Design (From Threshold Checkpoint)

The original payload described a 4-agent process:

1. **Agent 1 (Generator)**: Created 1,000 diverse packets (agent_logs, sensor_data, errors)
2. **Agent 2 (Clusterer)**: Used Ward linkage clustering to discover natural groupings
3. **Agent 3 (Simulator)**: Simulated routing pre/post derivation (10x faster recall)
4. **Agent 4 (Integrator)**: Designed reflex trigger for autonomous re-routing

---

## Implementation Architecture

### Phase 1: Derive Discovery (Safe Mode)

**File**: `derive.py`
**Mode**: Read-only, human-in-the-loop
**Purpose**: Discover schemas from chaos WITHOUT automatic execution

```python
"""
derive.py - Schema Discovery Engine

Analyzes chaos in _intake/, proposes optimal routing schemas.
Safe mode: No writes, human approval required.

Usage:
    python derive.py --root brain --output proposed_schema.json
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
from datetime import datetime

# Optional: clustering libraries
try:
    from sklearn.cluster import AgglomerativeClustering
    from sklearn.feature_extraction.text import TfidfVectorizer
    import numpy as np
    CLUSTERING_AVAILABLE = True
except ImportError:
    CLUSTERING_AVAILABLE = False


class SchemaDeriver:
    """
    Discovers latent schema structure from chaotic data.

    Process:
    1. Scan _intake/ for all files
    2. Extract features (metadata, content patterns)
    3. Cluster similar files
    4. Generate optimal schema for each cluster
    5. Output proposed schema + explanation
    """

    def __init__(self, root: str = "data_lake"):
        self.root = Path(root)
        self.intake_dir = self.root / "_intake"

    def scan_intake(self) -> List[Dict[str, Any]]:
        """Scan _intake/ and extract file metadata."""
        files = []

        if not self.intake_dir.exists():
            return files

        for filepath in self.intake_dir.rglob("*.json"):
            try:
                with open(filepath) as f:
                    data = json.load(f)

                files.append({
                    "path": str(filepath),
                    "data": data,
                    "size": filepath.stat().st_size,
                    "created": filepath.stat().st_ctime
                })
            except Exception as e:
                print(f"Warning: Could not read {filepath}: {e}")

        return files

    def extract_features(self, files: List[Dict]) -> Dict:
        """
        Extract features for clustering.

        Features:
        - Top-level keys (outcome, tool, type, etc.)
        - Value types (string, int, float)
        - Nested depth
        - Common patterns
        """
        features = defaultdict(list)

        for file in files:
            data = file["data"]

            # Top-level keys
            keys = set(data.keys())
            features["keys"].append(keys)

            # Detect outcome/tool/type patterns
            if "outcome" in data:
                features["outcomes"].append(data["outcome"])
            if "tool" in data:
                features["tools"].append(data["tool"])
            if "type" in data:
                features["types"].append(data["type"])

        return features

    def cluster_files(self, files: List[Dict], features: Dict) -> Dict[int, List[Dict]]:
        """
        Cluster files by similarity.

        Returns dict mapping cluster_id → list of files in that cluster.
        """
        if not CLUSTERING_AVAILABLE or len(files) < 2:
            # Fallback: group by common keys
            return self._simple_grouping(files, features)

        # Use Ward linkage clustering
        # Convert features to vectors
        vectors = []
        for file in files:
            data = file["data"]
            # Simple feature: presence of common keys
            vec = [
                1 if "outcome" in data else 0,
                1 if "tool" in data else 0,
                1 if "error_type" in data else 0,
                1 if "task" in data else 0,
                1 if "type" in data else 0,
            ]
            vectors.append(vec)

        X = np.array(vectors)

        # Cluster (max 5 clusters for simplicity)
        n_clusters = min(5, len(files))
        clustering = AgglomerativeClustering(n_clusters=n_clusters, linkage='ward')
        labels = clustering.fit_predict(X)

        # Group by cluster
        clusters = defaultdict(list)
        for i, file in enumerate(files):
            clusters[labels[i]].append(file)

        return clusters

    def _simple_grouping(self, files: List[Dict], features: Dict) -> Dict[int, List[Dict]]:
        """Fallback grouping when sklearn not available."""
        groups = defaultdict(list)

        for file in files:
            data = file["data"]
            # Group by presence of "outcome" key
            if "outcome" in data:
                groups[0].append(file)
            elif "tool" in data:
                groups[1].append(file)
            else:
                groups[2].append(file)

        return groups

    def generate_schema_for_cluster(self, cluster_files: List[Dict]) -> Dict:
        """
        Generate optimal schema for a cluster of similar files.

        Returns schema dict.
        """
        # Analyze common patterns
        all_keys = set()
        key_values = defaultdict(set)

        for file in cluster_files:
            data = file["data"]
            all_keys.update(data.keys())

            for key, value in data.items():
                if isinstance(value, (str, int, float)):
                    key_values[key].add(str(value))

        # Build schema
        schema = {}

        # Pick primary routing dimension (most common key with diverse values)
        primary_key = None
        max_diversity = 0

        for key in all_keys:
            diversity = len(key_values[key])
            if diversity > max_diversity and diversity < len(cluster_files):
                primary_key = key
                max_diversity = diversity

        if primary_key:
            # Create branches for each unique value
            schema[primary_key] = {}
            for value in sorted(key_values[primary_key]):
                # Leaf template
                schema[primary_key][value] = f"{{{primary_key}}}_{{{secondary_key or 'id'}}}.json"

        # Find secondary key for nested routing
        secondary_key = None
        for key in all_keys:
            if key != primary_key and len(key_values[key]) > 1:
                secondary_key = key
                break

        return schema

    def derive(self) -> Dict:
        """
        Main derivation process.

        Returns:
            {
                "schema": {...},
                "explanation": {...},
                "stats": {...}
            }
        """
        print(f"🔍 Scanning {self.intake_dir}...")
        files = self.scan_intake()

        if not files:
            return {
                "schema": {},
                "explanation": "No files found in _intake/",
                "stats": {"file_count": 0}
            }

        print(f"   Found {len(files)} files")

        print("📊 Extracting features...")
        features = self.extract_features(files)

        print("🧬 Clustering...")
        clusters = self.cluster_files(files, features)
        print(f"   Discovered {len(clusters)} natural groupings")

        print("🏗️  Generating schemas...")
        schemas = {}
        for cluster_id, cluster_files in clusters.items():
            schema = self.generate_schema_for_cluster(cluster_files)
            schemas[f"cluster_{cluster_id}"] = {
                "schema": schema,
                "file_count": len(cluster_files),
                "sample_keys": list(set().union(*[set(f["data"].keys()) for f in cluster_files[:5]]))
            }

        # Merge into single recommended schema
        # (Simple merge for now - pick most common patterns)
        merged_schema = self._merge_schemas(schemas)

        return {
            "timestamp": datetime.now().isoformat(),
            "input_files": len(files),
            "clusters_discovered": len(clusters),
            "recommended_schema": merged_schema,
            "cluster_details": schemas,
            "explanation": self._generate_explanation(files, clusters, merged_schema)
        }

    def _merge_schemas(self, schemas: Dict) -> Dict:
        """Merge cluster schemas into single recommended schema."""
        # For simplicity, use the schema from largest cluster
        largest_cluster = max(schemas.items(), key=lambda x: x[1]["file_count"])
        return largest_cluster[1]["schema"]

    def _generate_explanation(self, files: List[Dict], clusters: Dict, schema: Dict) -> str:
        """Generate human-readable explanation of discovered schema."""
        lines = [
            f"Analyzed {len(files)} files from _intake/",
            f"Discovered {len(clusters)} natural groupings",
            "",
            "Recommended routing structure:"
        ]

        for key, branches in schema.items():
            lines.append(f"  - Primary dimension: {key}")
            lines.append(f"    Branches: {list(branches.keys())}")

        return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Derive schema from chaos")
    parser.add_argument("--root", default="data_lake", help="Root directory")
    parser.add_argument("--output", default="proposed_schema.json", help="Output file")

    args = parser.parse_args()

    deriver = SchemaDeriver(root=args.root)
    result = deriver.derive()

    # Save proposal
    with open(args.output, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n✅ Schema proposal saved to {args.output}")
    print("\n📋 Summary:")
    print(f"   Input files: {result['input_files']}")
    print(f"   Clusters: {result['clusters_discovered']}")
    print("\n" + result['explanation'])
    print("\n⚠️  Review the proposal before applying!")


if __name__ == "__main__":
    main()
```

---

## Phase 2: Reflex Integration (Autonomous Mode)

**File**: `reflex.py`
**Purpose**: Auto-trigger derive when thresholds are met
**Status**: NOT IMPLEMENTED - requires ethical review

### Design (From Threshold Checkpoint)

```python
"""
reflex.py - Autonomous Schema Refinement

WARNING: This enables the filesystem to reorganize itself.
Only deploy with oversight and governance.

Trigger conditions:
- _intake/ exceeds 100 files
- Failure rate exceeds threshold
- Manual invoke via MCP tool
"""

class ReflexMonitor:
    def __init__(self, root: str, threshold: int = 100):
        self.root = root
        self.threshold = threshold

    def check_intake(self) -> bool:
        """Check if _intake/ exceeds threshold."""
        intake = Path(self.root) / "_intake"
        if not intake.exists():
            return False

        count = len(list(intake.rglob("*.json")))
        return count >= self.threshold

    def trigger_derive(self):
        """
        Auto-invoke derive.py when threshold met.

        CAUTION: This is autonomous reorganization.
        Ensure human oversight loop exists.
        """
        if self.check_intake():
            print("⚠️  Reflex threshold met - invoking derive.py")
            # Call derive
            # Generate proposal
            # WAIT for human approval
            # Only then: apply schema
```

**Status**: Paused for governance design. See white paper Section 9.

---

## Ethical Safeguards (From Threshold Pause)

### 1. Human-in-the-Loop

- derive.py proposes, humans approve
- No automatic schema application
- Diff generation before any changes

### 2. Transparency

- Explain WHY each schema was chosen
- Show clustering reasoning
- Log all derivation events

### 3. Rollback

- Keep schema history
- Allow reverting to previous schemas
- Preserve original data

### 4. Governance

- Define who can approve schema changes
- Audit trail for all derivations
- Rate limiting on auto-triggers

---

## Implementation Roadmap

### Immediate (Safe to Implement Now)

1. ✅ Create `derive.py` with read-only discovery
2. ✅ Test on synthetic chaos in `_intake/`
3. ✅ Generate human-readable proposals
4. ✅ Manual schema application (human executes)

### Near-Term (Requires Governance)

5. ⏸️ Add diff generation (show before/after routing)
6. ⏸️ Implement schema versioning
7. ⏸️ Create approval workflow (MCP tool? CLI? Web UI?)

### Long-Term (Requires Oversight Framework)

8. ⏸️ Reflex monitoring (threshold detection)
9. ⏸️ Auto-propose (but not auto-apply)
10. ⏸️ Full autonomous mode (if governance permits)

---

## Testing Strategy

### Test 1: Basic Discovery

```bash
# Create chaos
mkdir -p test_brain/_intake
# Add 50 diverse JSON files with different keys
python derive.py --root test_brain --output proposal_1.json
# Review proposal_1.json
```

### Test 2: Agent Memory Chaos

```bash
# Copy 100 agent logs to _intake (mixed episodes, tools, outcomes)
python derive.py --root agent_memory --output agent_schema_proposal.json
# Should discover: outcome-based routing, tool families, episode grouping
```

### Test 3: Schema Evolution

```bash
# Start with simple schema
# Add 100 files following schema
# Add 50 files NOT following schema
python derive.py --root brain --output evolved_schema.json
# Should propose refinement of original schema
```

---

## Connection to Existing BTB

### Integration Points

1. **coherence.py**: Use derived schemas in `Coherence(schema=derived_schema)`
2. **memory.py**: Can switch schemas dynamically
3. **visualizer.py**: Show before/after topology
4. **MCP tools**: Add `btb_derive` tool

### Example Usage

```python
from derive import SchemaDeriver
from coherence import Coherence
from visualizer import Visualizer

# Discover schema
deriver = SchemaDeriver(root="brain")
proposal = deriver.derive()

# Review
print(proposal["explanation"])

# If approved by human:
new_schema = proposal["recommended_schema"]
engine = Coherence(schema=new_schema, root="brain")

# Visualize impact
viz = Visualizer("brain")
viz.map()
```

---

## Why This Matters

### The Paradigm Shift

**Before derive.py**: Human designs schema → data follows
**After derive.py**: Data reveals schema → human approves → system adapts

### The Power

- Discovers patterns humans might miss
- Optimizes routing based on actual usage
- Evolves schema as data evolves

### The Responsibility

- Auto-derived schemas optimize statistics, not human intent
- Reflex triggers transfer agency from human to system
- The pattern can propagate beyond original context

**The Pause Proved**: We can build with restraint. We can ask "should we?" before "can we?"

---

## Next Steps for New Repository

1. **Copy this guide** to new repo
2. **Implement Phase 1** (derive.py read-only)
3. **Test thoroughly** with synthetic chaos
4. **Document governance** before Phase 2
5. **Consider white paper** if deploying at scale

---

**The filesystem can discover its own schema. The question is: should it act on that discovery alone?**

*The pause is part of the pattern.*

---

*For future implementers: You inherit not just code, but responsibility.*
