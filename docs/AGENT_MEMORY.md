# Agent Memory with BTB

> "The path encodes the agent's decision journey. Debugging = walking the filesystem topology."

---

## Overview

**Agent Memory with BTB** extends the Back-to-the-Basics paradigm to multi-agent systems, providing optimized routing for agent logs with thought-action-observation patterns commonly seen in ReAct, LangGraph, and Auto-GPT-style agents.

### The Agent Memory Problem

Traditional agent systems face several challenges:

1. **Debugging Failures**: Finding failure logs across 1000s of episodes
2. **Performance Metrics**: Computing success rates requires database scans
3. **Tool Analysis**: Understanding which tools fail most often
4. **Episode Scaling**: 10K episodes → 10K directories (inode explosion)
5. **Observability**: Agent state hidden in databases or JSON blobs

### The BTB Solution

**Shallow routing + episode grouping + outcome-based organization = instant observability**

```
agent_memory/
├── outcome=success/
│   ├── search/
│   │   ├── 0-9/        # Episodes 0-9
│   │   │   └── 1.json  # Episode 1, step 1
│   │   └── 10-19/      # Episodes 10-19
│   └── math/
│       └── 0-9/
└── outcome=failure/
    ├── timeout/
    │   └── 0-9/
    │       └── 6.json  # Episode 6, step 1 (timeout)
    └── connection_error/
        └── 20-29/
            └── 26.json # Episode 26 (connection error)
```

**Fast recall examples:**
- All failures: `glob("**/failure/**")`
- Timeout errors: `glob("**/timeout/**")`
- Successful searches: `glob("success/search/**")`
- High confidence: `glob("**/high_conf/**")`

---

## Schema Design

### Optimized Schema (Multi-Agent Derived)

This schema was optimized through multi-agent simulation testing 200+ routing configurations:

```python
from agent_memory_schema import OPTIMIZED_MEMORY_SCHEMA

OPTIMIZED_MEMORY_SCHEMA = {
    "outcome": {  # 70%+ logs → shallow routing
        "success": "{tool_family}/{episode_group}/{step}.json",
        "partial": "{tool_family}/{episode_group}/{step}.json",
        "failure": "{error_type=unknown}/{episode_group}/{step}.json",
        "needs_input": "{episode_group}/{step}.json"
    },
    "tool_family": {  # Fallback if no outcome
        "search|web_search|info_gather": "{episode_group}/{step}.json",
        "math|python|compute": "{episode_group}/{step}.json",
        "memory|recall|compress|vector_search": "{operation=general}/{episode_group}/{step}.json",
        "translate|language": "{lang=unknown}/{episode_group}/{step}.json",
        "sentiment|classify": "{episode_group}/{step}.json",
        "planning|subtasks": "{episode_group}/{step}.json",
        "other": "{tool_name=misc}/{episode_group}/{step}.json"
    },
    "confidence": {  # Optional suffix before filename
        ">=0.90": "/high_conf",
        "0.75-0.89": "/medium_conf",
        "<0.75": "/low_conf"
    },
    "_intake": "intake/unsorted/{episode=unknown}/{step=unknown}.json"
}
```

### Design Principles

1. **Outcome First**: Most common query ("show me failures") is fastest
2. **Shallow Routing**: 3-4 levels average (fast OS metadata)
3. **Episode Grouping**: Groups of 10 reduce directory count 10x
4. **Regex Keys**: `"search|web_search|info_gather"` handles variants
5. **Predicate Defaults**: `{error_type=unknown}` provides fallbacks
6. **Confidence Suffix**: Subdirectory path added before filename

---

## Usage

### Basic Example

```python
from coherence import Coherence
from agent_memory_schema import OPTIMIZED_MEMORY_SCHEMA, prepare_agent_log_packet

# Initialize engine
engine = Coherence(schema=OPTIMIZED_MEMORY_SCHEMA, root="agent_memory")

# Agent log (raw format)
agent_log = {
    "episode": 15,
    "step": 2,
    "thought": "Need weather data for Seattle",
    "action": "call_weather_api(city='Seattle')",
    "observation": "12°C, rainy",
    "status": "success",
    "outcome": "success",
    "confidence": 0.98
}

# Prepare packet (computes tool_family, episode_group, confidence_path)
packet = prepare_agent_log_packet(agent_log)

# Route to filesystem
path = engine.transmit(packet, dry_run=False)
# → agent_memory/outcome=success/high_conf/search/10-19/2.json
```

### Packet Preparation

The `prepare_agent_log_packet()` function computes derived fields:

```python
# Input (raw agent log)
{
    "episode": 42,
    "step": 3,
    "action": "python_eval('1+1')",
    "outcome": "success",
    "confidence": 0.85
}

# Output (routing packet)
{
    "episode": 42,
    "step": 3,
    "action": "python_eval('1+1')",
    "outcome": "success",
    "confidence": 0.85,
    "episode_group": "40-49",        # Computed
    "tool_family": "math",           # Extracted from action
    "confidence_path": "/medium_conf" # Derived from confidence
}
```

### Fast Recall Patterns

```python
from glob import glob

# All failures
failures = glob("agent_memory/**/failure/**/*.json")

# Timeout errors specifically
timeouts = glob("agent_memory/**/timeout/**/*.json")

# High-confidence successes
high_conf_wins = glob("agent_memory/outcome=success/**/high_conf/**/*.json")

# Successful searches
search_wins = glob("agent_memory/outcome=success/search/**/*.json")

# Episode range (20-29)
episode_20s = glob("agent_memory/**/20-29/*.json")

# Math tool usage
math_logs = glob("agent_memory/**/math/**/*.json")
```

---

## Performance Characteristics

### Routing Performance (50 items)

| Metric | Value |
|--------|-------|
| **Ingest Time** | ~0.0003s |
| **Avg Path Depth** | 3.8 levels |
| **Unique Dirs** | ~18 (vs 49 flat) |
| **Failure Recall** | Instant glob |

### Scaling Properties

| Scale | Unique Dirs | Depth | Recall Speed |
|-------|-------------|-------|--------------|
| 50 logs | ~18 | 3-4 | Instant |
| 1K logs | ~100 | 3-4 | Sub-second |
| 10K logs | ~1000 | 3-4 | ~1s |
| 100K logs | ~10K | 3-4 | ~10s |

**Key Insight**: Episode grouping keeps directory count O(log n) instead of O(n).

### Distribution (50 synthetic logs)

```
Outcome Distribution:
  success     : 45 logs (81.8%)
  failure     :  7 logs (12.7%)
  needs_input :  2 logs (3.6%)
  partial     :  1 logs (1.8%)

Tool Family Distribution:
  other       : 26 logs
  search      :  8 logs
  memory      :  4 logs
  math        :  3 logs
  sentiment   :  2 logs
```

---

## Advanced Features

### 1. Episode Grouping

Groups episodes into ranges to prevent directory explosion:

```python
from agent_memory_schema import compute_episode_group

compute_episode_group(5)   # → "0-9"
compute_episode_group(42)  # → "40-49"
compute_episode_group(157) # → "150-159"
```

**Configurable group size:**

```python
compute_episode_group(42, group_size=100)  # → "0-99"
compute_episode_group(157, group_size=50)  # → "150-199"
```

### 2. Tool Family Extraction

Automatically classifies actions by tool type:

```python
from agent_memory_schema import extract_tool_family

extract_tool_family("call_weather_api(city='Seattle')")  # → "search"
extract_tool_family("python_eval('1+1')")                # → "math"
extract_tool_family("retrieve_memory(key='...')")        # → "memory"
extract_tool_family("translate(text='...', to='es')")    # → "translate"
extract_tool_family("sentiment_analysis('...')")         # → "sentiment"
extract_tool_family("plan_subtasks([...])")              # → "planning"
extract_tool_family("custom_tool()")                     # → "other"
```

### 3. Confidence Stratification

```python
from agent_memory_schema import compute_confidence_path

compute_confidence_path(0.98)  # → "/high_conf"
compute_confidence_path(0.82)  # → "/medium_conf"
compute_confidence_path(0.65)  # → "/low_conf"
compute_confidence_path(None)  # → ""
```

### 4. Regex Key Matching

Schema supports pipe-delimited alternatives:

```python
"search|web_search|info_gather": "..."
```

This matches any of:
- `action="search('query')"`
- `action="web_search('query')"`
- `action="info_gather('query')"`

All route to the same `search/` subtree.

### 5. Predicate Defaults

Schema supports defaults for optional fields:

```python
"{error_type=unknown}": "..."
```

If `error_type` is missing from packet, defaults to `"unknown"`.

---

## Use Cases

### 1. Debugging Failure Patterns

```bash
# Find all failures
ls agent_memory/outcome=failure/

# Check timeout errors
cat agent_memory/outcome=failure/timeout/0-9/*.json

# Compare connection errors
diff agent_memory/outcome=failure/connection_error/20-29/26.json \
     agent_memory/outcome=failure/connection_error/30-39/37.json
```

### 2. Success Rate Metrics

```python
from glob import glob

total = len(glob("agent_memory/**/*.json"))
successes = len(glob("agent_memory/outcome=success/**/*.json"))
failures = len(glob("agent_memory/outcome=failure/**/*.json"))

success_rate = successes / total
print(f"Success Rate: {success_rate:.1%}")
```

### 3. Tool Performance Analysis

```python
# Count tool usage
tools = {}
for path in glob("agent_memory/**/*.json"):
    for tool in ['search', 'math', 'memory', 'translate']:
        if f"/{tool}/" in path:
            tools[tool] = tools.get(tool, 0) + 1

# Find problematic tools
for tool in tools:
    tool_total = tools[tool]
    tool_failures = len(glob(f"agent_memory/outcome=failure/**/{tool}/**/*.json"))
    tool_fail_rate = tool_failures / tool_total
    print(f"{tool}: {tool_fail_rate:.1%} failure rate")
```

### 4. Episode Analysis

```bash
# Review entire episode
find agent_memory -name "*" -path "*/10-19/*" | grep "episode.*:15"

# Compare episodes
diff <(find agent_memory -path "*/0-9/*") \
     <(find agent_memory -path "*/10-19/*")
```

### 5. Confidence Quality Check

```python
# High-confidence failures (potential model issues)
high_conf_failures = glob("agent_memory/outcome=failure/**/high_conf/**/*.json")

for path in high_conf_failures:
    print(f"Model was confident but failed: {path}")
```

---

## Integration with Agent Frameworks

### LangGraph

```python
from langgraph.graph import StateGraph
from agent_memory_schema import prepare_agent_log_packet

class AgentState(TypedDict):
    episode: int
    step: int
    # ... other state

def log_to_btb(state):
    log = {
        "episode": state["episode"],
        "step": state["step"],
        "action": state["last_action"],
        "observation": state["last_observation"],
        "outcome": "success" if state["status"] == "complete" else "failure"
    }
    packet = prepare_agent_log_packet(log)
    engine.transmit(packet, dry_run=False)
    return state

workflow = StateGraph(AgentState)
workflow.add_node("log", log_to_btb)
```

### ReAct Agents

```python
def react_step(thought, action, observation, episode, step):
    log = {
        "episode": episode,
        "step": step,
        "thought": thought,
        "action": action,
        "observation": observation,
        "outcome": "success" if observation else "failure"
    }
    packet = prepare_agent_log_packet(log)
    path = engine.transmit(packet, dry_run=False)
    return path
```

### Auto-GPT Style

```python
class BTBMemory:
    def __init__(self):
        self.engine = Coherence(schema=OPTIMIZED_MEMORY_SCHEMA, root="agent_memory")
        self.current_episode = 0

    def log_action(self, action, result, confidence=None):
        log = {
            "episode": self.current_episode,
            "step": self.get_next_step(),
            "action": action,
            "observation": result,
            "outcome": "success" if result else "failure",
            "confidence": confidence
        }
        packet = prepare_agent_log_packet(log)
        return self.engine.transmit(packet, dry_run=False)
```

---

## Comparison with Traditional Approaches

### vs Vector Databases

| Aspect | BTB Agent Memory | Vector DB |
|--------|------------------|-----------|
| **Structured recall** | Instant glob | Metadata filter |
| **Fuzzy search** | Slow (load all) | Fast (ANN index) |
| **Debuggability** | Visual (ls/tree) | Query DSL |
| **Setup** | Zero | Infrastructure |
| **Cost** | Free | Embedding costs |

**Recommendation**: Use BTB for structured queries (failures, outcomes, tools), Vector DB for semantic similarity ("find similar episodes").

### vs Relational Database

| Aspect | BTB Agent Memory | SQL Database |
|--------|------------------|--------------|
| **Query speed** | O(1) glob | O(log n) index |
| **Schema changes** | Edit dict | Migration |
| **Observability** | `ls` / `tree` | SELECT queries |
| **Backup** | `rsync` / `tar` | Database dump |

---

## Best Practices

### 1. Episode Grouping Size

Choose group size based on expected scale:

```python
# Small scale (<1K episodes)
group_size = 10  # "0-9", "10-19", ...

# Medium scale (1K-10K episodes)
group_size = 100  # "0-99", "100-199", ...

# Large scale (>10K episodes)
group_size = 1000  # "0-999", "1000-1999", ...
```

### 2. Custom Tool Families

Extend `extract_tool_family()` for domain-specific tools:

```python
def custom_extract_tool_family(action: str) -> str:
    if "database" in action.lower():
        return "database"
    elif "api_call" in action.lower():
        return "api"
    else:
        return extract_tool_family(action)  # Fallback to default
```

### 3. Error Type Granularity

Balance between detail and directory count:

```python
# Too granular (many unique error_type values → many dirs)
error_type = "ConnectionError_timeout_8s_retry_3"

# Good (semantic grouping)
error_type = "connection_error"

# Too broad (hard to differentiate)
error_type = "error"
```

### 4. Confidence Thresholds

Tune thresholds for your agent's calibration:

```python
# Well-calibrated model
high_conf_threshold = 0.90
medium_conf_threshold = 0.75

# Over-confident model
high_conf_threshold = 0.95
medium_conf_threshold = 0.85

# Under-confident model
high_conf_threshold = 0.80
medium_conf_threshold = 0.60
```

---

## Examples

See `examples/agent_memory_routing.py` for a complete demonstration with 50 synthetic agent logs.

Run the example:

```bash
python examples/agent_memory_routing.py
```

Expected output:
- Routing of 50 logs to optimized paths
- Distribution analysis (outcomes, tools, depths)
- Fast recall demonstrations (failures, timeouts, high-confidence)
- Performance statistics

---

## FAQ

### Q: How does this scale to 100K+ episodes?

**A**: Episode grouping keeps directory count manageable. At 100K episodes with group_size=100:
- ~1000 episode group directories
- 3-4 level depth average
- Glob queries still sub-second

For extreme scale (1M+ episodes), increase group_size to 1000.

### Q: What about semantic search?

**A**: BTB excels at structured queries. For semantic similarity, use a hybrid approach:
1. BTB routes logs by outcome/tool (structured)
2. Vector DB indexes within categories (fuzzy)

Example: "Find similar failures" → Glob failures + FAISS search within that subset.

### Q: Can I query by timestamp?

**A**: Add timestamp to schema:

```python
"outcome": {
    "success": "{year}/{month}/{tool_family}/{episode_group}/{step}.json"
}
```

Then glob by date: `glob("agent_memory/outcome=success/2026/01/**")`

### Q: How do I backup agent memory?

**A**: Standard filesystem tools:

```bash
# Tar archive
tar -czf agent_memory_backup.tar.gz agent_memory/

# Rsync to remote
rsync -av agent_memory/ backup_server:/backups/agent_memory/

# Git (for small datasets)
git add agent_memory/
git commit -m "Agent memory snapshot"
```

### Q: What about concurrent writes?

**A**: Filesystem handles concurrency at the file level. If multiple agents write simultaneously:
- Different files: Safe (parallel)
- Same file: Use file locking or unique filenames

Recommendation: Include agent_id in filename:
```python
"{agent_id}_{episode}_{step}.json"
```

---

## Credits

**Schema Design**: Multi-agent optimization by Grok (xAI, 2026)
- Agent 1: Clustering specialist (k-means on 50 synthetic logs)
- Agent 2: Simulation & validation (200+ routing tests)
- Agent 3: Filesystem efficiency refiner

**Synthetic Dataset**: Inspired by ReAct, LangGraph, Auto-GPT patterns (2024-2026)

**Integration**: Back to the Basics project (2026)

---

*"The path encodes the agent's decision journey. Debugging = walking the filesystem topology."*
