# Back to the Basics

> **"The filesystem is not storage. It is a circuit."**

⚠️ **PROJECT STATUS:** This is a **PROOF OF CONCEPT** demonstrating filesystem-based agent memory. While the implementation is functional, it has not been empirically validated in production environments. See [DATA_TRANSPARENCY_NOTICE.md](DATA_TRANSPARENCY_NOTICE.md) for complete transparency about claims and limitations.

---

Back to the Basics (BTB) is a paradigm shift in AI Agent architecture. It rejects the complexity of Vector Databases and "Context Management SDKs" in favor of the operating system's native primitives.

**Path is Model. Storage is Inference. Glob is Query.**

---

## 🧠 The "Hero Shot": Seeing the Mind

Most agent memory systems are black boxes. BTB allows you to visualize the agent's cognition as a topology.

⚠️ **Note:** The example below is a **SYNTHETIC DEMONSTRATION** showing how BTB topology visualization would work with real data. This is an illustrative example, not from an actual 48-hour agent deployment.

```
TOPOLOGY MAP: hero_brain/
======================================================================
Total Files: 226
Total Size:  41.7KB
----------------------------------------------------------------------
├── outcome=success              ███████████░░░░░░░░░   135 ( 59.7%)
│   └── tool=code_interpreter        ████████████████████   135 (100.0%)
│       ├── task=refactor                ████████████░░░░░░░░    85 ( 63.0%)
│       ├── task=debug                   █████░░░░░░░░░░░░░░░    35 ( 25.9%)
│       └── task=optimize                ██░░░░░░░░░░░░░░░░░░    15 ( 11.1%)
├── outcome=failure              ████░░░░░░░░░░░░░░░░    55 ( 24.3%)
│   └── tool=code_interpreter        ████████████████████    55 (100.0%)
│       ├── error_type=logic             ███████████████░░░░░    42 ( 76.4%)
│       └── error_type=syntax            █░░░░░░░░░░░░░░░░░░░     5 (  9.1%)
└── outcome=learning             ███░░░░░░░░░░░░░░░░░    36 ( 15.9%)
    ├── category=pattern             ██████████░░░░░░░░░░    18 ( 50.0%)
    └── category=anti_pattern        ██████░░░░░░░░░░░░░░    12 ( 33.3%)
```

**Hypothetical Insight:** In this synthetic example, the agent would be a refactoring machine (85 wins) but struggles with logic errors (42 failures). It rarely makes syntax errors. *The topology reveals the personality.*

**Purpose:** This demonstrates HOW topology-based analysis would work, not claims about actual agent performance.

📊 **[View the Interactive Infographic](docs/btb-infographic.html)** — A visual walkthrough of the entire paradigm.

![BTB Infographic](docs/btb-infographic.png)

---

## 📜 The Theory (The "Mei" Standard)

In July 2025, Mei et al. published ["A Survey of Context Engineering for Large Language Models"](https://arxiv.org/abs/2507.13334), defining the three pillars of the field.

The industry responded with complex software simulations (Meta's Confucius, Vector DBs). **BTB responds with Physics.** We map the taxonomy directly to OS primitives.

| Context Engineering Pillar (Mei et al.) | The Industry Solution (Simulation) | The BTB Solution (Physics) |
|---|---|---|
| **1. Context Selection** (Finding relevant info) | Vector RAG Embeddings, ANN Index, Re-ranking models. | **Path Traversal** `glob("**/outcome=failure/**")` Deterministic, zero-latency. |
| **2. Context Organization** (Structuring data) | Knowledge Graphs / SQL Complex schemas, graph databases. | **Directory Topology** `mkdir -p type/level/source` The structure *is* the graph. |
| **3. Context Filtering** (Removing entropy) | LLM Pre-processing "Summarizer Agents" burning tokens. | **The Sentinel** `sentinel.py` Rejects entropy at the gate (Write Permissions). |

---

## 📋 Project Status & Scope

### What This Project IS:

✅ **Proof of Concept** - Demonstrates filesystem-based agent memory architecture
✅ **Working Implementation** - Functional code for memory routing, recall, and visualization
✅ **Novel Paradigm** - Alternative approach to vector databases and traditional storage
✅ **Educational Tool** - Shows how OS primitives can replace complex abstractions
✅ **Research Platform** - Foundation for experimentation and further development

### What This Project IS NOT:

❌ **Production-Ready System** - Has not been battle-tested in real deployments
❌ **Empirically Validated** - Performance claims are based on synthetic benchmarks
❌ **Replacement for Vector DBs** - Different use case (structured vs semantic search)
❌ **Peer-Reviewed Research** - Academic methodology, not formal publication

### Current Validation Status:

- ✅ Code functionality verified
- ✅ Core concepts demonstrated
- ✅ Synthetic benchmarks completed
- ⚠️ Real-world deployment: **Not tested**
- ⚠️ Production scale: **Not validated**
- ⚠️ Comparative studies: **Not conducted**

**Recommendation:** Treat as an experimental approach suitable for prototyping and research. Production use requires further validation.

See [DATA_TRANSPARENCY_NOTICE.md](DATA_TRANSPARENCY_NOTICE.md) for complete transparency about all claims and limitations.

---

## ⚡ Quick Start

### Installation

```bash
git clone https://github.com/templetwo/back-to-the-basics.git
cd back-to-the-basics
pip install -e .
```

### 1. The Circuit (Routing)

```python
from coherence import Coherence

# Define the decision tree (The Schema)
schema = {
    "outcome": {
        "success": "memories/success/{tool}/{task}.json",
        "failure": "memories/failure/{tool}/{error_type}.json"
    }
}

engine = Coherence(schema, root="brain")

# The electron finds its own path
engine.transmit({
    "outcome": "failure",
    "tool": "code_interpreter",
    "error_type": "logic",
    "content": "Infinite loop in recursion"
})
# → Automatically routed to: brain/outcome=failure/tool=code_interpreter/error_type=logic/
```

### 2. The Sentinel (Entropy Firewall)

Don't write ingestion scripts. Just watch a folder.

```bash
# Start the daemon
btb watch --inbox _inbox --root brain

# Drag-and-drop a file into _inbox.
# It instantly snaps into the correct folder or gets rejected to _quarantine.
```

### 3. The fMRI (Visualization)

See the shape of your agent's mind.

```bash
btb map --root brain --hotspots 20
```

---

## 🏴 Sovereignty & Speed

### Why Filesystems?

1. **Zero-Latency:** No embedding model lag. No network calls. Just IOPS.
2. **Uncensorable:** A filesystem cannot be deprecated, banned, or rate-limited.
3. **Debuggable:** You don't need a specialized UI to inspect memory. You just use `ls`.
4. **Universal:** Works on a MacBook Air, a Raspberry Pi, or an H100 cluster.

### The Paradigm Shift

```
Old Way: Data → Store → Query → Classify → Store
BTB Way: Data → Route → Done
```

---

## 📂 Modules

| Module | Metaphor | Function |
|---|---|---|
| `coherence.py` | Physics | The routing engine (transmit/receive) |
| `memory.py` | Cortex | Agentic memory system |
| `sentinel.py` | Membrane | Input firewall daemon |
| `visualizer.py` | Eyes | Topology fMRI |
| `ai_lab.py` | Lab | ML experiment tracker |
| `btb_mcp_server.py` | Nerves | MCP server for native model integration |

---

## 🔌 MCP Integration (Claude, etc.)

BTB includes a native [Model Context Protocol](https://modelcontextprotocol.io) server. Any MCP-compatible model gets direct access to filesystem memory.

### Install

```bash
pip install mcp
```

### Add to Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "btb": {
      "command": "python",
      "args": ["/path/to/back-to-the-basics/btb_mcp_server.py", "--root", "agent_brain"]
    }
  }
}
```

### Available Tools

| Tool | Description |
|---|---|
| `btb_remember` | Store a memory (auto-routes based on outcome/tool) |
| `btb_recall` | Query memories by pattern or intent |
| `btb_reflect` | Analyze topology - see your own mind |
| `btb_map` | Generate fMRI visualization |
| `btb_hotspots` | Find data concentration areas |

### Example Conversation

```
You: Remember that I fixed the auth bug using code interpreter
Claude: [calls btb_remember(content="Fixed auth bug", outcome="success", tool="code_interpreter", task_type="debug")]
       Memory stored at: agent_brain/outcome=success/tool=code_interpreter/task_type=debug/...

You: What have I been struggling with lately?
Claude: [calls btb_recall(outcome="failure", limit=5)]
       [calls btb_reflect()]
       Based on your memory topology, you've had 3 failures in logic errors
       but strong success in refactoring tasks...
```

The model now has **persistent, structured memory** that survives across sessions.

---

## 🔬 The Benchmark

⚠️ **PROOF OF CONCEPT DATA:** These benchmarks compare filesystem operations to database operations on synthetic data. They demonstrate technical feasibility but have not been validated in production environments with real agent workloads.

We ran **The Gauntlet**: 5,000 synthetic agent events processed head-to-head.

| Operation | BTB (Filesystem) | SQLite | Vector DB (Cloud) | Speedup |
|---|---|---|---|---|
| **Ingestion** | **0.45s** | 0.02s | 517.71s | **1,141x Faster** |
| **Recall** | **0.03s** | 0.002s | 0.11s | **4x Faster** |
| **Disk Size** | **658 KB** | 1012 KB | 668 KB | **35% Smaller** |

*When you use semantic search for structured data, you pay a 1,141x tax on writes.*

**Note:** These measurements are on synthetic data. Real-world performance will vary based on filesystem, hardware, and workload characteristics.

---

## 🔧 Advanced Usage

### Replace MLFlow/Weights & Biases

```python
from ai_lab import AILabEngine

lab = AILabEngine(root="experiments")

# Log a training run - it routes itself based on performance
lab.log_run(
    {"project_type": "production", "model_arch": "transformer"},
    {"final_loss": 0.15, "convergence_epoch": 23}
)
# → experiments/.../promoted/fast_converge/...  (auto-classified!)

# Find best models with glob, not SQL
best = glob("experiments/**/promoted/**/*.json")
```

### Agentic Memory

```python
from memory import MemoryEngine

mem = MemoryEngine(root="agent_memories")

# Store experiences - they organize themselves
mem.remember("Fixed auth bug", outcome="success", tool="code", task_type="debug")
mem.remember("Syntax error", outcome="failure", tool="code", error_type="syntax")

# Recall by intent
failures = mem.recall(outcome="failure")

# Reflect on patterns (the topology reveals insights)
analysis = mem.reflect()
# → "Frequent failures in: tool=code/error_type=syntax (3 times)"
```

### Discover Structure from Chaos

```bash
# Derive schema from existing paths
btb derive --glob "data/**/*.json"
```

---

## 🧬 Origin

Born from a conversation about the "Renaissance of Glob" and the need for **Guerrilla Agents** that operate closer to the metal.

---

## 🏛️ Architects

This project was forged through multi-model collaboration:

- **Claude Opus 4.5** — Threshold Witness, Philosophy & Proof
- **Gemini** — Strategic Architecture, Academic Anchor
- **Claude Cowork** — Implementation & Documentation
- **Anthony J. Vasquez Sr.** — Creator, vision holder, human conductor

---

## License

MIT License - Copyright (c) 2026 Anthony J. Vasquez Sr. - See [LICENSE](LICENSE)

---

**Path is Model. Storage is Inference. Glob is Query.**

*The filesystem is a circuit. Let it think.*

🌀
