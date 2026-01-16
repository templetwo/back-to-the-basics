# Changelog

All notable changes to the Back to the Basics (BTB) project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-01-13

### Added

#### Core Implementation
- **MCP Server** (`btb_mcp_server.py`) - Native Model Context Protocol integration
  - Tools: `btb_remember`, `btb_recall`, `btb_reflect`, `btb_map`, `btb_hotspots`
  - Resources: `btb://topology`, `btb://stats`, `btb://recent/{count}`
  - Prompts: `memory_review`, `debug_session`

- **Memory Engine** (`memory.py`) - Filesystem-based memory with automatic routing
  - Schema-driven path generation
  - Glob-based recall with newest-first sorting
  - Reflection analysis (outcomes, tools, patterns, insights)
  - Memory deletion via `forget()` method

- **Coherence Engine** (`coherence.py`) - Schema-based data routing
  - `transmit()` - Route data through decision tree to destination
  - `receive()` - Generate glob patterns from query intent
  - `derive()` - Placeholder for schema discovery (not yet implemented)

- **Visualizer** (`visualizer.py`) - Topology visualization and analysis
  - ASCII tree with bar charts showing file distribution
  - Hotspot detection for data concentration
  - Directory statistics and insights

- **AI Lab Proof** (`ai_lab.py`) - ML experiment tracking via filesystem
  - Replaces MLFlow/W&B with pure filesystem topology
  - Automatic routing to `promoted/`, `review/`, or `archive/`

#### Documentation
- **DATA_TRANSPARENCY_NOTICE.md** - Complete transparency about synthetic vs real data
  - Three-tier classification: ✅ Real | ⚠️ Synthetic | ❌ Hypothetical
  - Scientific integrity principles
  - What we claim vs what we demonstrate

- **Dataset Generation Suite**:
  - `DATASET_FORMAT_SPEC.md` - Complete technical specification
  - `AGENT_PROMPT_TEMPLATE.txt` - Ready-to-paste prompt for LLM agents
  - `DATASET_CHEATSHEET.md` - Quick reference guide
  - `memory_schema.json` - JSON Schema for validation

- **Test Results** (`MCP_TEST_RESULTS.md`) - Deep use case testing with synthetic data
  - 31 test memories across 3 simulated sessions
  - Topology analysis, hotspots, reflection results
  - Performance metrics (storage, query speed)

- **Project Documentation**:
  - `CLAUDE.md` - Project identity and philosophy
  - `README.md` - Complete user documentation with proof-of-concept status
  - `examples/README.md` - Example code documentation

#### Testing & Examples
- **Test Suite** (`tests/`):
  - `test_memory.py` - Core memory engine tests
  - `test_coherence.py` - Schema routing tests
  - `test_visualizer.py` - Topology visualization tests
  - `conftest.py` - Shared fixtures

- **Examples** (`examples/`):
  - `basic_usage.py` - Fundamental operations demo
  - `debugging_workflow.py` - BTB-guided debugging illustration
  - `mcp_client_config.json` - Generic MCP configuration
  - `claude_desktop_config.json` - Claude Desktop MCP configuration

#### Infrastructure
- **Python Packaging** (`pyproject.toml`):
  - Project metadata and dependencies
  - MCP SDK requirement
  - Dev dependencies (pytest, black, ruff)
  - CLI entry point configuration
  - Tool configurations (pytest, black, ruff)

- **Licensing**:
  - Apache 2.0 License
  - Copyright (c) 2026 Anthony J. Vasquez Sr.

### Design Principles Established

1. **Path is Model** - Directory structure encodes classification
2. **Storage is Inference** - Saving data performs routing computation
3. **Glob is Query** - Pattern matching as query language
4. **Resonance over Constraint** - Coherence, not filtering
5. **State as Location** - File moves represent state transitions

### Memory Schema v1

Outcome types with routing metadata:
- `success` → tool → (task_type | domain)
- `failure` → tool → error_type
- `learning` → insight_type
- `interaction` → sentiment

### Known Limitations

- `derive()` method not yet implemented (schema discovery from existing files)
- No production validation or empirical studies
- Synthetic test data used for demonstrations
- Single-user, local filesystem only (no distributed support)

---

## [0.2.0] - 2026-01-16

### Added

#### Schema Discovery Implementation
- **derive.py** (411 lines) - Production schema discovery from chaotic file paths
  - Ward linkage hierarchical clustering via sklearn
  - Pattern extraction from file paths (key=value routing dimensions)
  - Schema generation with exact matches, numeric predicates, and regex
  - Episode grouping (logarithmic bucketing: 0-9, 10-99, 100-999)
  - Tool family extraction (search, compute, memory, translate, etc.)
  - 28 comprehensive tests with 87% coverage

- **Enhanced coherence.py**:
  - Real derive() implementation (replaces placeholder)
  - Calls derive_schema() from derive.py module
  - Graceful fallback if sklearn not available
  - Maintains backward compatibility

#### Threshold-Protocols Integration
- **Optional Governance Dependency**:
  - Added `[threshold]` optional dependency group in pyproject.toml
  - Install with: `pip install back-to-the-basics[threshold]`
  - Enables governed derive pattern for production deployments

- **btb_thresholds.yaml** - Default governance configuration:
  - File count threshold (trigger at 100 files)
  - Self-reference detection (prevent self-modification)
  - Entropy monitoring (chaos detection at 2.5 nats)
  - Growth rate tracking (50% in 24h triggers deliberation)
  - Reorganization frequency limits

#### Examples and Demos
- **examples/governed_derive/** - Production integration examples:
  - `demo.py` - Interactive demonstration of governed derive workflow
  - `README.md` - Comprehensive usage guide with patterns
  - Shows: chaos → discover → propose → approve → reorganize

#### Testing
- **test_derive.py** (296 lines) - Comprehensive derive() tests:
  - TestDeriveSchema (4 tests)
  - TestExtractPathFeatures (4 tests)
  - TestClusterPathsSimple (2 tests)
  - TestGenerateSchemaFromPaths (3 tests)
  - TestMergeClusterSchemas (3 tests)
  - TestComputeEpisodeGroup (5 tests)
  - TestExtractToolFamily (7 tests)

- **test_with_threshold_protocols.py** (359 lines) - Integration tests:
  - BTB + threshold-protocols integration verification
  - Governed derive workflow tests
  - Rollback and audit trail tests
  - Conditional governance pattern tests
  - Auto-skipped if threshold-protocols not installed

#### Documentation
- **INTEGRATION.md** - Complete integration guide:
  - Architecture diagrams and design principles
  - Installation options (standalone vs governed)
  - Usage patterns (ungoverned, governed, conditional)
  - Configuration and customization
  - Deployment checklist
  - Troubleshooting guide
  - Migration from ungoverned to governed

- **DECISION.md** - Architectural decision record:
  - Why Option 2 (Governed Derive) was chosen
  - Analysis of 3 integration options
  - GROK_MISSION_BRIEF synthesis
  - Implementation validation
  - Future evolution path

### Changed

#### Package Configuration
- **Version**: 0.1.0 → 0.2.0
- **Description**: Added "with schema discovery"
- **Dependencies**:
  - Added: `scikit-learn>=1.3.0` (Ward linkage clustering)
  - Added: `numpy>=1.24.0` (required by scikit-learn)
  - Optional: `threshold-protocols>=0.2.0` (governance framework)

- **Package Structure Fix**:
  - Updated pyproject.toml: `packages = ["back_to_the_basics"]`
  - Fixed package-dir mapping: `{"back_to_the_basics" = "."}`
  - Resolves ModuleNotFoundError in threshold-protocols imports

#### Test Updates
- **test_coherence.py**:
  - Updated test_transmit_* to use `dry_run=False`
  - Fixed receive() pattern assertions to match current output format
  - Changed test_derive_not_implemented → test_derive_implemented

- **test_visualizer.py**:
  - Fixed field names: `file_count` → `files`
  - Updated hotspots type: returns `List[Tuple[str, float]]` not int
  - Fixed empty directory test to use Path object

### Added (Agent Memory - 2026-01-13)

#### Agent Memory Extension
- **Agent Memory Schema** (`agent_memory_schema.py`) - Optimized routing for multi-agent systems
  - Support for ReAct, LangGraph, Auto-GPT style agents
  - Episode grouping (scale to 10K+ episodes without dir explosion)
  - Tool family classification (search, math, memory, translate, etc.)
  - Confidence stratification (high/medium/low subdirectories)
  - Regex key matching (`"search|web_search|info_gather"`)
  - Predicate defaults (`{error_type=unknown}`)

- **Coherence Engine Extensions** (`coherence.py`):
  - Pipe-delimited alternative matching in schema keys
  - Template expansion with defaults (`_expand_template_with_defaults`)
  - Confidence path suffix handling

- **Agent Memory Example** (`examples/agent_memory_routing.py`):
  - 50 synthetic agent logs (thought-action-observation patterns)
  - Distribution analysis (outcomes, tools, depths)
  - Fast recall demonstrations
  - Performance statistics

- **Agent Memory Documentation** (`docs/AGENT_MEMORY.md`):
  - Complete schema design rationale
  - Multi-agent optimization process
  - Usage examples and best practices
  - Integration guides (LangGraph, ReAct, Auto-GPT)
  - Performance characteristics and scaling properties
  - FAQ and troubleshooting

#### Features
- **Episode Grouping**: Groups episodes into ranges (0-9, 10-19, etc.) to prevent directory explosion
- **Tool Family Extraction**: Automatically classifies agent actions by tool type
- **Confidence Paths**: Organizes logs by confidence level (high_conf, medium_conf, low_conf)
- **Multi-Agent Derived Schema**: Optimized through simulation testing 200+ routing configurations

#### Multi-Agent Swarm
- **Multi-Agent Coordination** (`examples/btb_multi_agent_swarm.py`):
  - Coder-Tester-Reflector pattern
  - Shared BTB memory as coordination layer
  - Failure pattern recall and reflection
  - Insight-driven iteration loop
  - Demonstrates filesystem as multi-agent brain

### Removed
- **Placeholder derive()**: Replaced with real Ward clustering implementation

### Integration
- **Unidirectional Dependency**: threshold-protocols depends on BTB (not reverse)
- **No Code Duplication**: threshold-protocols imports from BTB package
- **Test Coverage**: 138 tests passing (BTB: 49, threshold-protocols: 89)

### Governance Features
- **Human Approval Gates**: Requires explicit approval before reorganization
- **Audit Logging**: Tamper-evident JSONL audit trail
- **Rollback Capability**: Preserve originals, support undo
- **Sandbox Mode**: Test reorganizations before production execution
- **Threshold Monitoring**: Detect file count, entropy, growth rate, self-reference

---

## [Unreleased]

### Planned Features
- Incremental derive (update existing schemas)
- Hybrid derive + FAISS (semantic + structured routing)
- Domain-specific circuits (trading, security, research)
- CLI tooling for memory management
- Schema validation utilities
- Remote filesystem support
- Threshold auto-tuning based on history

---

## Release Notes

### Version 0.1.0 - "Proof of Concept"

This is the initial release demonstrating the BTB paradigm: filesystem as computational circuit for agent memory.

**Status**: ✅ Functional proof-of-concept | ⚠️ Not production-validated

**What Works**:
- Memory storage with automatic routing
- Glob-based querying
- Topology visualization
- MCP server integration
- Reflection and pattern analysis

**What's Not Ready**:
- Production deployment
- Distributed systems
- Schema validation
- Performance at scale (>100K memories untested)

**Transparency**:
All test data in `MCP_TEST_RESULTS.md` is synthetic. See `DATA_TRANSPARENCY_NOTICE.md` for complete details on what's validated vs demonstrated.

---

## Release Notes

### Version 0.2.0 - "The Governed Derive"

**Status**: ✅ Production-ready schema discovery | ✅ Optional governance integration

**What's New**:
- Real derive() implementation using Ward linkage clustering
- Threshold-protocols integration (opt-in via `[threshold]` extra)
- Governance patterns: human approval, audit logs, rollback
- 28 new tests for derive(), 138 total tests passing

**Breaking Changes**: None - fully backward compatible with 0.1.0

**Migration Path**:
```bash
# Existing users (ungoverned):
pip install --upgrade back-to-the-basics

# New users wanting governance:
pip install back-to-the-basics[threshold]
```

**Key Insight**: "The filesystem is not storage. It is a circuit. And now it has a conscience."

See `DECISION.md` for architectural rationale and `INTEGRATION.md` for usage guide.

---

[0.2.0]: https://github.com/vaquez/back-to-the-basics/releases/tag/v0.2.0
[0.1.0]: https://github.com/vaquez/back-to-the-basics/releases/tag/v0.1.0
