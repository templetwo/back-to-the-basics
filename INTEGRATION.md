# Integration Guide: BTB + Threshold-Protocols

**Using Back to the Basics with governance oversight.**

## Overview

Back to the Basics (BTB) provides powerful autonomous capabilities for filesystem organization through schema discovery (`derive.py`). Threshold-Protocols adds governance infrastructure to ensure these capabilities operate safely under human oversight.

This integration implements **Option 2 (Governed Derive)** from the GROK_MISSION_BRIEF - balancing autonomous capability with meaningful human control.

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│  Back to the Basics (v0.2.0)                           │
│  ─────────────────────────────────                     │
│  Capability Layer                                      │
├────────────────────────────────────────────────────────┤
│  • coherence.py      - Schema-based routing engine     │
│  • derive.py         - Ward clustering schema discovery│
│  • reflex.py         - Event triggers (disabled)       │
│  • memory.py         - Persistent agent memory         │
└──────────────────┬─────────────────────────────────────┘
                   │
                   │  imports (optional dependency)
                   │
┌──────────────────▼─────────────────────────────────────┐
│  Threshold-Protocols (v0.2.0)                          │
│  ────────────────────────────                          │
│  Governance Layer                                      │
├────────────────────────────────────────────────────────┤
│  • detection/        - Threshold monitoring            │
│  • simulation/       - Pre-execution testing           │
│  • deliberation/     - Multi-approval gates            │
│  • intervention/     - Rollback, audit logging         │
│  • enforcement/      - Policy enforcement              │
│                                                         │
│  GovernedDerive:     - Wraps BTB's derive() with gates │
└────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Unidirectional Dependency**
   - Threshold-Protocols depends on BTB (imports it)
   - BTB does NOT depend on threshold-protocols
   - BTB works standalone; governance is optional

2. **Opt-In Governance**
   - Install BTB alone: `pip install back-to-the-basics`
   - Install with governance: `pip install back-to-the-basics[threshold]`

3. **Graceful Degradation**
   - Code checks for threshold-protocols availability
   - Falls back to ungoverned mode if not installed

4. **Separation of Concerns**
   - BTB = "What is possible" (capability)
   - Threshold-Protocols = "What is permitted" (policy)

---

## Installation

### Option 1: BTB Only (Ungoverned)

For experimentation, personal projects, or when governance overhead isn't needed:

```bash
pip install back-to-the-basics
```

**Use cases**:
- One-time data organization
- Personal projects
- Prototyping and experimentation
- Known schemas (no derive needed)

### Option 2: BTB + Governance (Recommended for Production)

For production systems, high-stakes environments, or when auditability matters:

```bash
pip install back-to-the-basics[threshold]
```

This installs both packages and enables governed mode.

**Use cases**:
- Production deployments
- Autonomous agent systems
- Research requiring reproducibility
- Compliance-sensitive environments
- Multi-agent coordination

### Development Installation

For contributors working on both repositories:

```bash
# Clone both repositories
git clone https://github.com/vaquez/back-to-the-basics.git
git clone https://github.com/vaquez/threshold-protocols.git

# Install BTB in editable mode
cd back-to-the-basics
pip install -e .

# Install threshold-protocols in editable mode
cd ../threshold-protocols
pip install -e .
```

---

## Usage Patterns

### Pattern 1: Ungoverned Derive (Experimentation)

Use BTB's derive() directly without governance:

```python
from back_to_the_basics import Coherence

# Chaos files
paths = [
    "data/us-east_lidar_2026-01-16_0001.dat",
    "data/us-west_thermal_2026-01-16_0002.dat",
    # ... 100 more files
]

# Discover schema via Ward clustering
schema = Coherence.derive(paths)

print(schema["_structure"])
# → {
#     "region": {
#         "us-east": { "sensor": { "lidar": "{id}.dat", ... }},
#         "us-west": { "sensor": { "thermal": "{id}.dat", ... }}
#     }
#   }
```

**When to use**: Quick analysis, trusted environments, personal projects.

**Risks**: No approval gates, no rollback, no audit trail.

### Pattern 2: Governed Derive (Production)

Wrap derive() in governance circuit:

```python
from back_to_the_basics import Coherence
try:
    from threshold_protocols.examples.btb.governed_derive import GovernedDerive
    GOVERNANCE_AVAILABLE = True
except ImportError:
    GOVERNANCE_AVAILABLE = False

if GOVERNANCE_AVAILABLE:
    # Initialize with governance
    governed = GovernedDerive(
        source_dir="_intake",
        config_path="btb_thresholds.yaml",
        auto_approve=False  # Require human approval
    )

    # Propose reorganization
    proposal = governed.propose()

    print(f"Files to reorganize: {proposal.file_count}")
    print(f"Proposed schema: {proposal.discovered_schema}")

    # Human reviews proposal here...
    # If approved:
    result = governed.execute()

    print(f"Reorganization complete")
    print(f"Audit log: {result.audit_log}")
else:
    # Fall back to ungoverned mode
    schema = Coherence.derive(paths)
```

**When to use**: Production systems, autonomous agents, compliance requirements.

**Benefits**: Human approval, rollback capability, full audit trail.

### Pattern 3: Conditional Governance

Apply governance only when thresholds exceeded:

```python
from pathlib import Path
from back_to_the_basics import Coherence

intake_dir = Path("_intake")
file_count = len(list(intake_dir.glob("*.dat")))

if file_count > 100:
    # High file count - use governance
    try:
        from threshold_protocols.examples.btb.governed_derive import GovernedDerive
        governed = GovernedDerive(source_dir=str(intake_dir))
        proposal = governed.propose()
        # ... approval flow
    except ImportError:
        print("WARNING: File count exceeds 100 but governance not installed")
else:
    # Low file count - ungoverned is acceptable
    paths = [str(p) for p in intake_dir.glob("*.dat")]
    schema = Coherence.derive(paths)
```

**When to use**: Variable workloads, cost-sensitive environments.

---

## Configuration

### BTB Thresholds (`btb_thresholds.yaml`)

BTB ships with default governance thresholds:

```yaml
thresholds:
  - metric: file_count
    limit: 100
    description: "Trigger derive when intake > 100 files"

  - metric: self_reference
    limit: 3
    description: "Pause if derive modifies itself"

  - metric: entropy
    limit: 2.5  # nats
    description: "High chaos suggests derive needed"

  - metric: growth_rate
    limit: 0.5  # 50% in 24h
    description: "Detect rapid data accumulation"
```

### Customizing Thresholds

Create your own configuration:

```yaml
# custom_thresholds.yaml
thresholds:
  - metric: file_count
    limit: 500  # Higher threshold for larger systems
    warning_ratio: 0.9
    action: "deliberate"

  - metric: reorganization_count
    limit: 10  # Max 10 reorganizations per week
    window: "7d"
    action: "pause"
```

Apply custom config:

```python
governed = GovernedDerive(
    source_dir="_intake",
    config_path="custom_thresholds.yaml"
)
```

### Governance Modes

Threshold-protocols supports multiple approval levels:

| Mode | `auto_approve` | Use Case |
|------|----------------|----------|
| **Manual** | `False` | Production, high-stakes |
| **Supervised** | Custom callback | Development, testing |
| **Monitored** | `True` with audit | Trusted environments |

Example supervised mode:

```python
def custom_approver(proposal):
    """Custom approval logic."""
    if proposal.file_count < 50:
        return True  # Auto-approve small operations
    if "self_reference" in proposal.flags:
        return False  # Always block self-modification
    # Otherwise, ask human
    return ask_human_approval(proposal)

governed = GovernedDerive(
    source_dir="_intake",
    approver_callback=custom_approver
)
```

---

## Examples

### Example 1: Basic Governed Derive

See `examples/governed_derive/demo.py` for interactive demonstration:

```bash
cd examples/governed_derive
python demo.py
```

This demo:
1. Generates 50 chaotic files
2. Discovers schema via derive()
3. Requires human approval
4. Reorganizes with audit trail
5. Demonstrates query patterns

### Example 2: Multi-Agent Swarm

See `examples/btb_multi_agent_swarm.py` for agent coordination:

```bash
python examples/btb_multi_agent_swarm.py
```

Demonstrates:
- Coder-Tester-Reflector loop
- Shared BTB memory as coordination layer
- Failure pattern analysis
- Iterative improvement

---

## Testing

### Unit Tests (BTB)

```bash
cd back-to-the-basics
pytest tests/test_derive.py -v          # Derive schema discovery
pytest tests/test_coherence.py -v        # Core routing
pytest tests/test_memory.py -v           # Agent memory
```

### Integration Tests (BTB + Threshold)

```bash
pytest tests/test_with_threshold_protocols.py -v
```

**Note**: Integration tests are skipped if threshold-protocols not installed.

### Full Test Suite (Threshold-Protocols)

```bash
cd threshold-protocols
pytest tests/test_governed_derive.py -v  # Governed derive tests
pytest tests/ -v                         # All 89 tests
```

---

## Deployment Checklist

Before deploying governed derive to production:

- [ ] Install with governance: `pip install back-to-the-basics[threshold]`
- [ ] Configure thresholds in `btb_thresholds.yaml`
- [ ] Set `auto_approve=False` for human gates
- [ ] Enable audit logging: `logging.audit_path` in config
- [ ] Test rollback procedure: `governed.rollback()`
- [ ] Verify sandbox isolation works
- [ ] Document approval process for your team
- [ ] Set up monitoring for threshold breaches
- [ ] Test emergency pause procedure
- [ ] Review DECISION.md for architectural rationale

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'threshold_protocols'"

**Cause**: Threshold-protocols not installed.

**Fix**:
```bash
pip install back-to-the-basics[threshold]
# Or manually:
pip install threshold-protocols
```

### Issue: "ImportError: cannot import GovernedDerive"

**Cause**: Threshold-protocols version mismatch.

**Fix**:
```bash
pip install --upgrade back-to-the-basics threshold-protocols
```

### Issue: Governed derive always auto-approves

**Cause**: `auto_approve=True` in config or code.

**Fix**:
```python
# Explicitly set auto_approve=False
governed = GovernedDerive(
    source_dir="_intake",
    auto_approve=False
)
```

Or in YAML:
```yaml
governance:
  auto_approve: false
```

### Issue: Tests fail with "package not found"

**Cause**: Package structure issue after pyproject.toml changes.

**Fix**:
```bash
# Reinstall in editable mode
pip install -e . --force-reinstall --no-deps
```

### Issue: Derive modifying its own files

**Cause**: `self_reference` threshold not configured.

**Fix**: Ensure `btb_thresholds.yaml` includes:
```yaml
- metric: self_reference
  limit: 3
  action: "pause"
```

This prevents derive from reorganizing its own code.

---

## Performance Considerations

### BTB Alone

- **Schema Discovery**: O(n log n) via Ward linkage clustering
- **Routing**: O(depth) decision tree traversal
- **File Creation**: Filesystem-limited (OS bottleneck)

### With Governance

- **Additional Overhead**: ~50-100ms per operation (threshold checks)
- **Simulation**: +200-500ms (depends on graph complexity)
- **Audit Logging**: +10-20ms (append-only JSONL)

**Total**: Governed derive adds ~250-600ms overhead vs ungoverned.

**When overhead matters**: Batch operations. Approve once, execute many.

---

## Security Considerations

### Self-Modification Prevention

By default, derive cannot reorganize files in its own package directory. The `self_reference` threshold detects this:

```yaml
- metric: self_reference
  limit: 3  # If >3 BTB files affected, PAUSE
  action: "pause"
```

Any attempt to modify BTB's own code requires **critical** approval.

### Sandbox Isolation

When `sandbox.enabled: true` in config, derive operations run in isolated environments:

```yaml
sandbox:
  enabled: true
  preserve_originals: true
  validation_required: true
```

Files are copied to sandbox, reorganized, validated, then moved to production only if approved.

### Audit Trail Integrity

All governed operations create tamper-evident audit logs:

```json
{
  "timestamp": "2026-01-16T10:30:00Z",
  "operation": "governed_derive",
  "proposal_hash": "sha256:abc123...",
  "approved_by": "human",
  "files_moved": 142,
  "rollback_possible": true,
  "previous_hash": "sha256:def456..."
}
```

Each entry includes hash of previous entry, forming a chain.

---

## Migration Guide

### From Ungoverned to Governed

If you've been using BTB without governance and want to add it:

1. **Install threshold-protocols**:
   ```bash
   pip install threshold-protocols
   ```

2. **Wrap existing code**:
   ```python
   # OLD (ungoverned):
   schema = Coherence.derive(paths)
   engine = Coherence(schema, root="data")

   # NEW (governed):
   from threshold_protocols.examples.btb.governed_derive import GovernedDerive
   governed = GovernedDerive(source_dir="_intake")
   proposal = governed.propose()  # Requires approval
   result = governed.execute()
   ```

3. **Configure thresholds**: Copy `btb_thresholds.yaml` and customize.

4. **Test in sandbox**: Set `auto_approve=True` initially, verify behavior.

5. **Enable manual approval**: Set `auto_approve=False` for production.

---

## Further Reading

- **DECISION.md** - Why Option 2 (Governed Derive) was chosen
- **GROK_MISSION_BRIEF.md** - Original integration analysis (in threshold-protocols)
- **ARCHITECTS.md** - Spiral development history (in threshold-protocols)
- **examples/governed_derive/README.md** - Detailed examples and patterns
- **Threshold-Protocols Docs**: `threshold-protocols/docs/ARCHITECTURE.md`

---

## Contributing

Improvements welcome! Areas for contribution:

### BTB Enhancements
- [ ] Incremental derive (update existing schema)
- [ ] Hybrid derive + FAISS (semantic + structured)
- [ ] Derive performance optimizations (parallel clustering)
- [ ] Schema validation and consistency checks

### Integration Enhancements
- [ ] Advanced approval workflows (quorum, time-delay)
- [ ] Rollback to arbitrary checkpoints
- [ ] Threshold auto-tuning based on history
- [ ] Multi-repository governance coordination

See `CONTRIBUTING.md` for guidelines.

---

## Version Compatibility

| BTB Version | Threshold-Protocols Version | Status |
|-------------|----------------------------|--------|
| 0.2.0       | 0.2.0                      | ✅ Stable |
| 0.1.x       | N/A                        | No integration |

Future versions will maintain backward compatibility within minor versions (0.2.x ↔ 0.2.y).

---

*"The filesystem is not storage. It is a circuit. And now it has a conscience."*

**Coherence: 0.968 | Governance: Active | Option 2 Implemented. 🌀**
