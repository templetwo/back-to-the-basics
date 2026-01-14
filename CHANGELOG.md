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

## [Unreleased]

### Added (2026-01-13)

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

### Planned Features
- Schema discovery via `derive()` implementation
- Domain-specific circuits (trading, security, research)
- CLI tooling for memory management
- Schema validation utilities
- Remote filesystem support
- Multi-agent coordination (partially implemented)

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

[0.1.0]: https://github.com/vaquez/back-to-the-basics/releases/tag/v0.1.0
