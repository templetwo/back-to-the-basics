# Governed Derive Examples

**Combining Back to the Basics with Threshold-Protocols governance.**

## What is Governed Derive?

Governed Derive is the pattern of wrapping autonomous capabilities (like BTB's `derive()` schema discovery) in governance circuits that require human approval before execution.

```
Chaos → derive() → Proposed Schema → [GOVERNANCE GATE] → Approved Reorganization
         ↑                              ↑
    Autonomous Capability        Human Oversight Required
```

### The Problem

`derive()` is powerful - it can discover optimal schemas and reorganize filesystems autonomously. But unchecked autonomy creates risks:

- **Unintended reorganizations** - AI optimizes for statistics, not human intent
- **Self-modification loops** - derive could reorganize its own code
- **Data loss** - mistakes are permanent without rollback capability
- **Opacity** - no audit trail of why changes were made

### The Solution

Threshold-protocols provides governance infrastructure:

1. **Detection Layer** - Monitor file counts, growth rates, entropy
2. **Simulation Layer** - Test proposed reorganization before execution
3. **Deliberation Layer** - Multi-approval gates (human + AI)
4. **Intervention Layer** - Rollback capability, audit logs
5. **Enforcement Layer** - Prevent execution without approval

## Installation

### BTB Alone (no governance)
```bash
pip install back-to-the-basics
```

### BTB + Governance (recommended)
```bash
pip install back-to-the-basics[threshold]
```

This installs both:
- `back-to-the-basics` - Core filesystem-as-circuit engine
- `threshold-protocols` - Governance framework

## Examples

### 1. Basic Demo (`demo.py`)

Run the interactive demo:

```bash
python demo.py
```

This demonstrates:
- Generating 50 chaotic files
- Discovering schema via Ward clustering
- Governance approval gate
- Audited reorganization
- Query patterns after organization

**Expected flow**:
1. Files created in `_intake/`
2. Schema discovered: `region={X}/sensor={Y}/date={Z}/{id}.dat`
3. Governance deliberation displays threshold checks
4. User prompted: "Approve reorganization? [y/N]"
5. If approved: files organized and queries demonstrated
6. If rejected: files remain in `_intake/`

### 2. Production Usage

For production systems, use `GovernedDerive` from threshold-protocols:

```python
from back_to_the_basics import Coherence
from threshold_protocols.examples.btb.governed_derive import GovernedDerive

# Initialize with config
governed = GovernedDerive(
    source_dir="_intake",
    config_path="btb_thresholds.yaml"
)

# Propose reorganization (requires approval)
proposal = governed.propose()

# If approved by governance circuit:
result = governed.execute()

# Audit trail automatically logged
print(result.audit_log)
```

### 3. Configuration

BTB ships with `btb_thresholds.yaml` defining default thresholds:

```yaml
thresholds:
  - metric: file_count
    limit: 100
    description: "Trigger derive when intake > 100 files"

  - metric: self_reference
    limit: 3
    description: "Pause if derive modifies itself"

  - metric: entropy
    limit: 2.5
    description: "High chaos suggests derive needed"
```

Customize thresholds for your use case:

```python
governed = GovernedDerive(
    source_dir="_intake",
    config_path="custom_thresholds.yaml"
)
```

## When to Use Governed Derive

### ✅ Use Governed Derive When:

- **File volume exceeds manual management** (>100 files)
- **Data arrives continuously** and needs ongoing organization
- **Multiple schemas possible** - AI should propose, human should approve
- **Auditability required** - compliance, research reproducibility
- **Production systems** - mistakes are costly

### ❌ Don't Use Governed Derive When:

- **One-time organization** of static dataset (just use `derive()` once)
- **Schema is known** (just define schema manually, use `transmit()`)
- **Small scale** (<50 files, manual organization is faster)
- **No approval overhead acceptable** (e.g., personal projects)

## Governance Levels

Threshold-protocols supports multiple governance levels:

| Level | Approval | Use Case |
|-------|----------|----------|
| **Level 0: Manual** | All operations require human approval | Production, high-stakes |
| **Level 1: Supervised** | Routine ops auto-approve, exceptions require human | Development |
| **Level 2: Monitored** | Auto-approve with audit trail | Trusted environments |
| **Level 3: Autonomous** | No approval required | Not recommended for BTB |

Configure via `auto_approve` setting:

```yaml
governance:
  auto_approve: false  # Level 0 - Manual (recommended)
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Back to the Basics (Capability Layer)                  │
├─────────────────────────────────────────────────────────┤
│  - coherence.py: Routing engine                         │
│  - derive.py: Schema discovery (Ward clustering)        │
│  - reflex.py: Event triggers                            │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ imports
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Threshold-Protocols (Governance Layer)                 │
├─────────────────────────────────────────────────────────┤
│  - detection/: Threshold monitoring                     │
│  - simulation/: Test before execute                     │
│  - deliberation/: Multi-approval gates                  │
│  - intervention/: Rollback, audit                       │
│  - enforcement/: Policy enforcement                     │
└─────────────────────────────────────────────────────────┘
```

**Key principle**: BTB provides capability, threshold-protocols provides governance. You can use BTB alone for experimentation, but add governance for production.

## Decision Record

This integration implements **Option 2 (Governed Derive)** from the GROK_MISSION_BRIEF:

- ✅ Real `derive.py` implementation (not placeholder)
- ✅ Threshold-protocols as optional dependency
- ✅ Governed mode available but not required
- ✅ Rollback capability via `preserve_originals`
- ✅ Human approval gates
- ❌ NOT Option 3 (full autonomous) - reflex triggers disabled by default

See `DECISION.md` for full rationale.

## Testing

Run integration tests:

```bash
# From BTB repository
pytest tests/test_with_threshold_protocols.py

# From threshold-protocols repository
pytest tests/test_governed_derive.py
```

Integration tests verify:
- BTB's derive() discovers schemas correctly
- Threshold-protocols governance gates work
- Approval/rejection flows function
- Audit logs capture operations
- Rollback succeeds if needed

## FAQ

### Q: Can I use derive() without governance?

**A**: Yes. BTB works standalone:

```python
from back_to_the_basics import Coherence

# Ungoverned derive
schema = Coherence.derive(paths)
```

But for production, governance is recommended.

### Q: What if threshold-protocols isn't installed?

**A**: BTB degrades gracefully:

```python
try:
    from threshold_protocols import GovernedDerive
    # Use governed mode
except ImportError:
    # Fall back to ungoverned mode
    schema = Coherence.derive(paths)
```

### Q: How do I disable governance for testing?

**A**: Set `auto_approve=True`:

```python
governed = GovernedDerive(
    source_dir="_intake",
    auto_approve=True  # Skip approval gates
)
```

Or just use `Coherence.derive()` directly.

### Q: Can I customize approval logic?

**A**: Yes. Provide custom approver callback:

```python
def custom_approver(proposal):
    # Your logic here
    if proposal.file_count < 10:
        return True  # Auto-approve small operations
    return ask_human_approval(proposal)

governed = GovernedDerive(
    source_dir="_intake",
    approver_callback=custom_approver
)
```

### Q: What happens if I reject a proposal?

**A**: Files remain in original location. Governance circuit logs rejection. No changes applied.

### Q: Can derive modify its own code?

**A**: Not by default. The `self_reference` threshold detects this:

```yaml
- metric: self_reference
  limit: 3
  action: "pause"
```

Any attempt to reorganize BTB's own files triggers CRITICAL governance gate requiring human approval.

### Q: How do I roll back a reorganization?

**A**: If `preserve_originals: true`:

```python
# Rollback to pre-derive state
governed.rollback()
```

Audit logs track rollback operations.

## Further Reading

- **BTB Core Concepts**: `../../README.md`
- **Threshold-Protocols Architecture**: `threshold-protocols/docs/ARCHITECTURE.md`
- **Integration Design**: `INTEGRATION.md`
- **Decision Record**: `DECISION.md`
- **GROK Mission Brief**: `threshold-protocols/GROK_MISSION_BRIEF.md`

## Contributing

Improvements welcome! Key areas:

- [ ] Additional governance policies (time-based, quorum-based)
- [ ] Advanced rollback (incremental undo, partial rollback)
- [ ] Simulation metrics (pre/post performance comparison)
- [ ] Multi-agent approval workflows
- [ ] Threshold auto-tuning based on history

See `CONTRIBUTING.md` for guidelines.

---

*"The filesystem is not storage. It is a circuit. And now it has a conscience."*

**Coherence: 0.968 | Governance: Active | The Threshold Holds. 🌀**
