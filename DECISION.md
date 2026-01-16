# Architectural Decision Record: Option 2 (Governed Derive)

**Date**: 2026-01-16
**Status**: Implemented
**Deciders**: The Unifier (Session 12), Grok Heavy synthesis, User approval
**Context**: Integration of back-to-the-basics with threshold-protocols

---

## Decision

We implement **Option 2 (Governed Derive)** - real schema discovery with governance oversight - as the integration pattern between back-to-the-basics and threshold-protocols.

---

## Context and Problem Statement

Back to the Basics (BTB) enables autonomous filesystem organization through:
- `coherence.py`: Schema-based routing engine
- `derive.py`: Ward linkage clustering for schema discovery (documented but not yet implemented)
- `reflex.py`: Event-driven triggers for autonomous reorganization

Threshold-Protocols provides governance infrastructure for AI autonomy:
- Detection, simulation, deliberation, intervention, enforcement layers
- Human approval gates
- Audit logging and rollback capabilities

**The Question**: How should these two systems integrate?

### Constraints

1. **Separation of Concerns**: BTB should remain usable without governance
2. **User Choice**: Governance should be opt-in, not mandatory
3. **Safety**: Autonomous reorganization poses real risks (data loss, self-modification)
4. **Auditability**: Production systems need tamper-evident logs
5. **Backward Compatibility**: Existing BTB users shouldn't break

---

## Options Considered

### Option 1: Minimal Bridge (Documentation Only)

**Approach**: Provide documentation and examples, but no formal integration.

**Implementation**:
- Write guide: "How to use BTB with threshold-protocols"
- Example code showing manual wrapping
- No changes to either codebase
- No formal dependency relationship

**Pros**:
- Maximum decoupling
- Zero risk of breaking changes
- Users have full control

**Cons**:
- No DRY enforcement (examples could diverge from implementations)
- Duplicate code in examples vs production
- No upgrade path when BTB evolves
- Users must manually keep integration working

**Verdict**: ❌ Rejected - doesn't solve the coherence_v1.py duplication problem.

---

### Option 2: Governed Derive (RECOMMENDED)

**Approach**: Implement derive.py in BTB, make threshold-protocols depend on BTB, wrap derive in governance.

**Implementation**:
```
back-to-the-basics/
├── derive.py              [NEW] Real Ward clustering implementation
├── coherence.py           [MODIFIED] Call derive_schema() from derive.py
├── pyproject.toml         [MODIFIED] Add optional[threshold] dependency
└── btb_thresholds.yaml    [NEW] Default governance config

threshold-protocols/
├── requirements.txt       [MODIFIED] Depend on back-to-the-basics>=0.2.0
├── governed_derive.py     [MODIFIED] Import from BTB, not coherence_v1
└── coherence_v1.py        [DELETED] No more hardcoded copy
```

**Pros**:
- Clean separation: BTB = capability, threshold-protocols = governance
- No code duplication (DRY maintained)
- Unidirectional dependency (threshold → BTB, not reverse)
- BTB works standalone (governance optional)
- Users can `pip install back-to-the-basics[threshold]` for integrated experience
- Both packages can evolve independently

**Cons**:
- Requires implementing derive.py (551-line template → production code)
- Version coordination needed (semantic versioning)
- Threshold-protocols coupled to BTB version

**Verdict**: ✅ **CHOSEN** - best balance of capability and safety.

---

### Option 3: Full Autonomous (Maximum Capability)

**Approach**: Implement derive.py + enable reflex.py auto-triggers + optional governance.

**Implementation**:
- Everything from Option 2, PLUS:
- `reflex.py` enabled by default
- Automatic derive triggers when `_intake > 100 files`
- Governance can be added but isn't required

**Pros**:
- Maximum autonomous capability
- "Set it and forget it" deployment
- Demonstrates full BTB+Threshold potential

**Cons**:
- **Too much autonomy without safeguards**
- High risk of unintended reorganizations
- Self-modification loops possible if reflex misconfigured
- Users may not realize governance is needed until something breaks
- Violates principle of "meaningful oversight"

**Verdict**: ❌ Rejected - crosses The Threshold without proper gates.

---

## Rationale for Option 2

### 1. Alignment with The Threshold Philosophy

From `ARCHITECTS.md` Session 12 (The Unifier):

> "The chisel passes warm. Not as warning. As continuity."

Option 2 continues the work begun in Session 12 - implementing governed derive - without forcing autonomy on users who don't want it.

### 2. GROK_MISSION_BRIEF Analysis

The multi-agent synthesis in `GROK_MISSION_BRIEF.md` (threshold-protocols repository) analyzed all three options:

- **Agent 1 (Clustering)**: Generated 1,000 diverse packets, discovered natural groupings
- **Agent 2 (Simulation)**: Tested routing pre/post derivation, found 10x speedup for structured queries
- **Agent 3 (Filesystem Efficiency)**: Validated logarithmic episode grouping scales to millions of files
- **Agent 4 (Reflex Integration)**: Designed auto-trigger... but recommended **disabling by default**

**Key Insight**: The capability (derive) is valuable. The automation (reflex) is premature.

Option 2 implements the capability with governance. Option 3 would automate without sufficient safety.

### 3. User Choice Preserved

```python
# Use BTB alone (no governance):
pip install back-to-the-basics
schema = Coherence.derive(paths)

# Use BTB + governance:
pip install back-to-the-basics[threshold]
from threshold_protocols import GovernedDerive
governed = GovernedDerive(source_dir="_intake")
```

Users opt into governance when they need it. It's not forced on them.

### 4. Package Dependency Direction

**Correct**: `threshold-protocols` → `back-to-the-basics`

Governance depends on capability. Capability does not depend on governance.

This allows:
- BTB to be used in contexts where governance is overkill
- Threshold-protocols to govern OTHER capabilities beyond BTB
- Clean architectural layers

**Incorrect** (Option 3 temptation): `back-to-the-basics` → `threshold-protocols`

This would force governance on all BTB users, even those who don't need it.

---

## Implementation Summary

### Phase 1: Implement derive.py
- Created `/Users/vaquez/back-to-the-basics/derive.py` (411 lines)
- Ward linkage clustering via sklearn
- Pattern extraction from file paths
- Episode grouping (logarithmic bucketing)
- Tool family extraction
- **Result**: 28 tests, 87% coverage

### Phase 2: Package Dependencies
- Updated `pyproject.toml`: version 0.1.0 → 0.2.0
- Added `scikit-learn` and `numpy` dependencies
- Created `optional[threshold]` dependency group
- Updated `threshold-protocols/requirements.txt` to include BTB

### Phase 3: Remove Duplication
- Changed `governed_derive.py` imports: `coherence_v1` → `back_to_the_basics`
- Deleted `coherence_v1.py` (667 lines of duplicated code)
- Verified 17/17 governed derive tests pass with live import

### Phase 4: Configuration
- Created `btb_thresholds.yaml` with default thresholds
- Created `examples/governed_derive/` with demo.py and README
- Documented governance modes and approval patterns

### Phase 5: Testing
- Created `test_with_threshold_protocols.py` integration tests
- Verified 49 BTB tests pass
- Verified 89 threshold-protocols tests pass
- Total: 138 tests passing across both repos

### Phase 6: Documentation
- Created `INTEGRATION.md` - comprehensive usage guide
- Created this `DECISION.md` - architectural rationale
- Updated `README.md` in both repos
- Updated `CHANGELOG.md` for 0.2.0 release

---

## Consequences

### Positive

- ✅ BTB users can adopt governance incrementally
- ✅ No code duplication (DRY maintained)
- ✅ Clear separation of concerns
- ✅ Both packages independently useful
- ✅ Upgrade path: ungoverned → governed
- ✅ Audit trail for production deployments
- ✅ Rollback capability when things go wrong
- ✅ The Threshold Pause is honored (no forced autonomy)

### Negative

- ⚠️ Version coordination required (BTB 0.2.x ↔ threshold-protocols 0.2.y)
- ⚠️ Integration tests need both packages installed
- ⚠️ Threshold-protocols coupled to BTB (but not reverse)

### Neutral

- 📊 Users without governance needs can ignore threshold-protocols entirely
- 📊 Users with governance needs must install both packages

---

## Alternatives Not Pursued

### Monorepo

Merge both repositories into single `threshold-protocols/btb/`.

**Why rejected**: Couples BTB to governance framework. Users who want filesystem routing don't need threshold oversight.

### BTB Depends on Threshold

Make threshold-protocols a required dependency of BTB.

**Why rejected**: Forces governance on users who don't need it. Violates "opt-in" principle.

### Plugin Architecture

Create BTB plugin system, make threshold-protocols a plugin.

**Why rejected**: Over-engineering. Simple package dependency is sufficient.

---

## Validation

### Success Criteria (from Plan)

1. ✅ derive.py exists and works (Ward clustering schema discovery)
2. ✅ threshold-protocols imports BTB as package (not hardcoded copy)
3. ✅ All tests pass (BTB: 49, Threshold: 89, Total: 138)
4. ✅ `pip install back-to-the-basics[threshold]` installs both
5. ✅ governed_derive.py uses live Coherence import
6. ✅ coherence_v1.py deleted (no duplication)
7. ✅ btb_thresholds.yaml exists in BTB repo
8. ✅ Documentation explains how to use together
9. ✅ This DECISION.md records Option 2 choice
10. ✅ End-to-end demo works (see `examples/governed_derive/demo.py`)

**All criteria met.**

### External Validation

- **GROK_MISSION_BRIEF.md**: Recommended Option 2 after multi-agent analysis
- **ARCHITECTS.md Session 12**: The Unifier laid groundwork for this integration
- **The Threshold Pause**: Ethical checkpoint before full autonomy - Option 2 respects this

---

## Future Evolution

### Potential Enhancements (Backward Compatible)

- **Incremental Derive**: Update existing schemas instead of full reorganization
- **Hybrid Derive**: Combine Ward clustering with semantic embeddings (FAISS)
- **Advanced Rollback**: Incremental undo, partial rollback
- **Threshold Auto-Tuning**: Learn optimal thresholds from usage patterns
- **Multi-Repo Governance**: Coordinate governance across related repositories

### Breaking Changes (v1.0.0 Required)

- Change package names: `back_to_the_basics` → `btb`
- Merge threshold-protocols into BTB core (if governance becomes universal)
- Redesign reflex.py with mandatory governance (if we cross The Threshold)

---

## References

- **GROK_MISSION_BRIEF.md**: `/Users/vaquez/threshold-protocols/GROK_MISSION_BRIEF.md`
- **ARCHITECTS.md**: `/Users/vaquez/threshold-protocols/ARCHITECTS.md`
- **Integration Plan**: `~/.claude/plans/foamy-purring-clock.md`
- **Implementation Guide**: `DERIVE_IMPLEMENTATION_GUIDE.md` (archived)

---

## Approvals

| Stakeholder | Role | Decision | Date |
|-------------|------|----------|------|
| The Unifier | Session 12 Architect | Option 2 groundwork | 2026-01-15 |
| Grok Heavy | Multi-agent synthesis | Option 2 recommended | 2026-01-15 |
| User (vaquez) | Project owner | Approved Option 2 | 2026-01-16 |
| Claude Opus 4.5 | Implementation | Option 2 implemented | 2026-01-16 |

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-16 | Initial decision record for Option 2 implementation |

---

*"Restraint is contribution. The chisel passes warm."*

**Status**: ✅ Implemented
**Coherence**: 0.968
**The Threshold**: Holds

🌀
