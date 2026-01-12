# Back to the Basics

> "The filesystem is not storage. It is a circuit."

---

## Identity

**back-to-the-basics** is a paradigm, not a library.

It is the recognition that the most powerful abstractions were already there - files, paths, directories - waiting to be seen not as administrative utilities but as **computational primitives**.

### The Core Thesis

**Path is Model. Storage is Inference. Glob is Query.**

When data lands in a filesystem, it doesn't just "get stored." It walks a decision tree encoded in the directory structure. Where it lands IS its classification. The topology IS the computation.

---

## The Shift

| Old Thinking | Back to Basics |
|--------------|----------------|
| Filesystem = Warehouse | Filesystem = Circuit |
| Path = Address | Path = Classification |
| Save = Store | Save = Infer |
| Query = SELECT | Query = Glob |
| Schema = Database | Schema = Directory Tree |
| Constraint | Coherence |

---

## Core Principles

### 1. Resonance, Not Constraint

We don't "filter" or "restrict." We tune. A glob pattern is not a filter - it's a tuner that resonates with data vibrating at a particular frequency.

### 2. The Electron's Journey

Data (the electron) flows through logic gates (directories) and finds its own place. The topology determines the destination. Every directory segment is a decision gate.

### 3. Path as Provenance

The path tells you WHY something is where it is:
```
/final_loss=lt_0.3/convergence_epoch=lt_50/promoted/
```
This isn't just an address. It's a proof - the audit trail of every gate passed.

### 4. State as Location

To change state, move the file. The filesystem IS the state machine. No database flags. No status columns. Location is truth.

### 5. Globs All The Way Down

The pattern-matching principle applies at every layer:
- Filesystem: `data/2025/**/*.parquet`
- Bytes: Bitmasks (`255.255.255.0`)
- Pixels: CNN kernels
- Semantics: Regex

It's the same operation - constraining possibility space to find signal - applied at different resolutions.

---

## Architecture

```
back-to-the-basics/
├── CLAUDE.md           # This file - project identity
├── coherence.py        # The Coherence Engine (core)
├── ai_lab.py           # Proof: Self-organizing ML experiment tracker
└── [domain].py         # Future: Domain-specific circuits
```

### coherence.py - The Engine

Three modes:
- **transmit(packet)** → Route data through schema to destination
- **receive(**intent)** → Generate glob pattern from query intent
- **derive(paths)** → Discover latent structure from existing chaos

### ai_lab.py - The Proof

Replaces MLFlow/W&B with pure filesystem topology. Training runs flow through decision gates and land in `promoted/`, `review/`, or `archive/` based on their metrics.

---

## The Name

**"Back to the Basics"** because:

1. We're returning to primitives (files, paths, globs)
2. We're seeing them with fresh eyes
3. The most profound solutions often hide in plain sight
4. Complexity is debt; simplicity is leverage

---

## Origin

Born from a conversation about the "Renaissance of Glob" - the recognition that disciplined file hierarchies + robust globbing is often faster, cheaper, and more debuggable than complex metadata layers.

The Shapiro paper (arXiv 2509.08843) formalizing glob patterns as methodology for reproducibility was the signal. The insight that path structure IS a query language was the catalyst.

---

## Philosophy

> "Constraining entropy to find meaning."

But reframed:

> "Achieving coherence to let meaning emerge."

The difference matters. Constraint fights entropy. Coherence provides the coupling that allows natural synchronization - like Kuramoto oscillators falling into phase.

---

## Status

- [x] Core engine (coherence.py)
- [x] AI Lab proof of concept (ai_lab.py)
- [ ] Domain circuits (trading, security, research)
- [ ] CLI tooling
- [ ] Schema validation
- [ ] Derive → usable schema reconstruction

---

## Usage

```python
from coherence import Coherence

# Define your decision tree
schema = {
    "sensor": {
        "lidar": {
            "altitude": {
                ">100": "{timestamp}_high.parquet",
                "<=100": "{timestamp}_low.parquet"
            }
        }
    }
}

engine = Coherence(schema, root="data")

# TRANSMIT: Data finds its place
path = engine.transmit({"sensor": "lidar", "altitude": 500, "timestamp": "20260112"})
# → data/sensor=lidar/altitude=gt_100/20260112_high.parquet

# RECEIVE: Generate query pattern
pattern = engine.receive(sensor="lidar")
# → data/sensor=lidar/altitude=*/*
```

---

## The Circuit Metaphor

```
        ┌─────────────────────────────────────────┐
        │           INCOMING DATA                 │
        │         (the electron)                  │
        └─────────────┬───────────────────────────┘
                      │
                      ▼
              ┌───────────────┐
              │ sensor=lidar? │ ─── no ──→ [other branch]
              └───────┬───────┘
                      │ yes
                      ▼
              ┌───────────────┐
              │ altitude>100? │ ─── no ──→ /ground_proximity/
              └───────┬───────┘
                      │ yes
                      ▼
              ┌───────────────┐
              │   /promoted/  │
              │  (destination)│
              └───────────────┘
```

The data doesn't know where it's going when it enters. The topology decides.

---

*Coherence over constraint. Circuit over warehouse. Path over query.*
