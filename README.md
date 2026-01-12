# Back to the Basics

> **The filesystem is not storage. It is a circuit.**

A paradigm shift in how we think about data organization. Instead of treating filesystems as passive warehouses, we treat them as active decision trees where **path is model**, **storage is inference**, and **glob is query**.

## The Core Insight

When data lands in a filesystem, it doesn't just "get stored." It walks a decision tree encoded in the directory structure. Where it lands IS its classification. The topology IS the computation.

```
Traditional:  Data → Store → Query → Classify → Store again
Back to Basics:  Data → Route → Done
```

## Installation

```bash
git clone https://github.com/vaquez/back-to-the-basics.git
cd back-to-the-basics
pip install -e .
```

## Quick Start

### 1. Define a Schema (The Decision Tree)

```python
from coherence import Coherence

schema = {
    "type": {
        "log": {
            "level": {
                "error": "logs/error/{timestamp}.json",
                "warning": "logs/warning/{timestamp}.json",
                "info": "logs/info/{timestamp}.json",
            }
        },
        "metric": {
            "domain": {
                "performance": "metrics/perf/{timestamp}.json",
                "business": "metrics/business/{timestamp}.json",
            }
        }
    }
}

engine = Coherence(schema, root="data")
```

### 2. Route Data (Storage = Classification)

```python
# Data finds its own place
path = engine.transmit({
    "type": "log",
    "level": "error",
    "timestamp": "20260112",
    "message": "Connection timeout"
})
# → data/type=log/level=error/logs/error/20260112.json
```

### 3. Query with Glob (No Database Needed)

```python
# Generate the pattern
pattern = engine.receive(type="log", level="error")
# → data/type=log/level=error/**/*.json

# Use it
from glob import glob
errors = glob(pattern, recursive=True)
```

## CLI Commands

```bash
# Discover structure from existing paths
btb derive --glob "data/**/*.json"

# Watch an inbox and auto-route files
btb watch --inbox _inbox --root data

# Visualize directory topology (fMRI for your filesystem)
btb map --root data

# Find hotspots (where data accumulates)
btb map --root data --hotspots 30
```

## Modules

| Module | Purpose | Metaphor |
|--------|---------|----------|
| `coherence.py` | Routing engine | The Physics |
| `memory.py` | Agentic memory system | The Cortex |
| `sentinel.py` | Input firewall daemon | The Membrane |
| `visualizer.py` | Topology visualization | The Eyes |
| `ai_lab.py` | ML experiment tracker | The Lab |
| `cli.py` | Command-line interface | The Voice |

## Use Cases

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

### Self-Organizing Inbox

```bash
# Start the sentinel
btb watch --inbox _inbox --root data

# Drop files into _inbox/ - they route automatically
# Valid files → data/type=.../level=.../
# Invalid files → _quarantine/reason/
```

## The Paradigm Shift

| Old Thinking | Back to Basics |
|--------------|----------------|
| Filesystem = Warehouse | Filesystem = Circuit |
| Path = Address | Path = Classification |
| Save = Store | Save = Infer |
| Query = SQL | Query = Glob |
| Schema = Database | Schema = Directory Tree |
| Constraint | Coherence |

## Why This Works

1. **Zero-Latency Inference**: Classification happens at write-time, not query-time
2. **Visual Debugging**: Debug your model with `ls` - see why data landed where it did
3. **No Database Required**: Pure filesystem, works anywhere
4. **Path as Provenance**: The path tells you WHY something is where it is
5. **Glob as Query**: Complex logic becomes simple pattern matching

## Philosophy

> "Constraining entropy to find meaning."

But reframed:

> "Achieving coherence to let meaning emerge."

We don't filter. We tune. A glob pattern isn't a constraint - it's a tuner that resonates with data vibrating at a particular frequency.

## License

MIT License - See [LICENSE](LICENSE)

## Contributing

This is a paradigm, not just a library. If you see applications we haven't thought of, open an issue or PR.

## Origin

Born from a conversation about the "Renaissance of Glob" - the recognition that disciplined file hierarchies + robust globbing is often faster, cheaper, and more debuggable than complex metadata layers.

---

**Path is Model. Storage is Inference. Glob is Query.**

The filesystem is a circuit. Let it think.
